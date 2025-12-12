"""
Processamento completo de áudio via WebSocket
"""
import time
from typing import Optional
from fastapi import WebSocket
from loguru import logger

from backend.services import (
    WhisperSTTService,
    BaseLLMService,
    PiperTTSService,
    ContextManager
)
from backend.api.routes.websocket_utils import safe_send_json, safe_send_bytes
from backend.api.handlers.websocket_tools_preparer import prepare_tools_for_websocket
from backend.api.handlers.feedback_collector import collect_conversation_feedback
from backend.services.response_sanitizer import get_sanitizer
from backend.scripts.capture_assistant_responses import capture_response


async def process_audio_complete(
    websocket: WebSocket,
    audio_data: bytes,
    session_id: Optional[str],
    stt_service: WhisperSTTService,
    llm_service: BaseLLMService,
    tts_service: PiperTTSService,
    context_manager: ContextManager,
    memory_service: Optional[any],
    plugin_manager: Optional[any],
    web_search_tool: Optional[any],
    feedback_service: Optional[any] = None,
    privacy_mode_service: Optional[any] = None
) -> str:
    """
    Processa dados de áudio recebidos via WebSocket (STT → LLM → TTS)
    
    Args:
        websocket: Conexão WebSocket
        audio_data: Bytes do áudio
        session_id: ID da sessão (ou None)
        stt_service: Serviço de STT
        llm_service: Serviço de LLM
        tts_service: Serviço de TTS
        context_manager: Gerenciador de contexto
        memory_service: Serviço de memória (opcional)
        plugin_manager: PluginManager (opcional)
        web_search_tool: WebSearchTool (opcional, compatibilidade)
        
    Returns:
        ID da sessão
    """
    try:
        logger.info(f"🎵 Iniciando processamento de áudio: {len(audio_data)} bytes")
        
        # Cria sessão se não existir
        if not session_id:
            session_id = await context_manager.create_session()
            logger.info(f"🆕 Nova sessão criada automaticamente: {session_id}")
            if not await safe_send_json(websocket, {
                "type": "session_created",
                "session_id": session_id
            }):
                logger.warning("Conexão fechada antes de criar sessão")
                return session_id
        else:
            logger.debug(f"📝 Usando sessão existente: {session_id}")
        
        # 1. Transcreve áudio
        if not await safe_send_json(websocket, {
            "type": "processing",
            "stage": "transcribing"
        }):
            logger.warning("Conexão fechada durante processamento")
            return session_id
        logger.debug("📤 Status 'transcribing' enviado")
        
        stt_start = time.time()
        logger.info("🎙️ Iniciando transcrição de áudio...")
        texto_transcrito, confianca, duracao = stt_service.transcribe_audio(audio_data)
        stt_time = (time.time() - stt_start) * 1000  # em milissegundos
        logger.info(f"✅ Transcrição concluída: '{texto_transcrito}' (confiança: {confianca:.2f}, duração: {duracao:.2f}s)")
        logger.debug(f"⏱️ STT levou {stt_time:.0f}ms")
        
        # Sempre envia transcrição, mesmo se vazia (para atualizar status no mobile)
        texto_transcrito_clean = texto_transcrito if texto_transcrito else ""
        
        if not texto_transcrito or texto_transcrito.strip() == "":
            logger.warning("⚠️ Transcrição vazia - áudio pode estar sem fala ou muito baixo")
            # Usa texto genérico para não confundir o usuário
            texto_transcrito_clean = "[áudio sem fala detectada]"
        
        if not await safe_send_json(websocket, {
            "type": "transcription",
            "text": texto_transcrito_clean,
            "confidence": confianca
        }):
            logger.warning("Conexão fechada antes de enviar transcrição")
            return session_id
        logger.debug("📤 Transcrição enviada ao cliente")
        
        # Se transcrição está vazia, retorna resposta padrão sem processar LLM
        if not texto_transcrito or texto_transcrito.strip() == "":
            logger.info("⚠️ Transcrição vazia detectada, retornando mensagem padrão")
            resposta_texto = "Não consegui entender o áudio. Pode repetir, por favor?"
            tokens = 0
            llm_time = 0
        else:
            # 2. Gera resposta com LLM
            if not await safe_send_json(websocket, {
                "type": "processing",
                "stage": "generating"
            }):
                logger.warning("Conexão fechada antes de gerar resposta")
                return session_id
            logger.debug("📤 Status 'generating' enviado")
            
            await context_manager.add_message(session_id, "user", texto_transcrito)
            contexto = await context_manager.get_context(session_id)
            logger.debug(f"💭 Contexto recuperado: {len(contexto)} mensagens")
            
            # Busca memórias relevantes
            memoria_contexto = ""
            if memory_service:
                memoria_contexto = await memory_service.get_memories_for_context(texto_transcrito)
                # Extrai e salva memórias da conversa
                await memory_service.extract_and_save_memory(texto_transcrito, "")
            
            logger.info("🤖 Gerando resposta com LLM...")
            llm_start = time.time()
            
            # Obtém LLM ativo do privacy_mode_service se disponível
            active_llm = llm_service
            if privacy_mode_service:
                active_llm = privacy_mode_service.get_active_llm_service() or llm_service
                logger.debug(f"🔒 Usando LLM ativo: {type(active_llm).__name__} (privacidade: {privacy_mode_service.get_privacy_mode()})")
            
            # Prepara tools e tool executor (filtra plugins se em modo privacidade)
            tools, tool_executor = prepare_tools_for_websocket(plugin_manager, web_search_tool, privacy_mode_service)
            
            # Gera resposta com LLM ativo (passa memórias e tools)
            resposta_texto, tokens = active_llm.generate_response(
                texto_transcrito,
                contexto,
                memorias_contexto=memoria_contexto,
                tools=tools,
                tool_executor=tool_executor
            )
            llm_time = (time.time() - llm_start) * 1000  # em milissegundos
            logger.info(f"✅ Resposta gerada: '{resposta_texto[:100]}...' ({tokens} tokens)")
            logger.debug(f"⏱️ LLM levou {llm_time:.0f}ms")
        
        # Sanitiza resposta antes de enviar para TTS e salvar
        sanitizer = get_sanitizer()
        resposta_texto_original = resposta_texto
        resposta_texto = sanitizer.sanitize(resposta_texto)
        
        # Verifica qualidade após sanitização
        if not sanitizer.is_quality_response(resposta_texto):
            logger.warning(f"⚠️ Resposta de baixa qualidade após sanitização. Original: '{resposta_texto_original[:100]}...'")
            # Se ficou muito ruim, usa mensagem de contingência
            if len(resposta_texto.strip()) < 20:
                resposta_texto = "Desculpe, tive um probleminha técnico. Pode repetir a pergunta?"
        
        if resposta_texto != resposta_texto_original:
            logger.info(f"🔧 Resposta sanitizada: '{resposta_texto_original[:50]}...' -> '{resposta_texto[:50]}...'")
        
        await context_manager.add_message(session_id, "assistant", resposta_texto)
        
        # Extrai e salva memórias da resposta também
        if memory_service:
            await memory_service.extract_and_save_memory(texto_transcrito, resposta_texto)
        
        # Coleta conversa para feedback (em background, não bloqueia resposta)
        conversation_id = None
        processing_time = (time.time() - stt_start) / 1000.0  # Tempo total até agora
        
        # Detecta tool usada (simplificado - baseado em palavras-chave)
        used_tool = None
        if tools and tool_executor:
            texto_lower = texto_transcrito.lower()
            if "pesquis" in texto_lower or "busca" in texto_lower or "google" in texto_lower:
                used_tool = "web_search"
            elif "arquitet" in texto_lower or "design" in texto_lower or "sistema" in texto_lower:
                used_tool = "architecture_advisor"
        
        if feedback_service and texto_transcrito and resposta_texto:
            try:
                conversation_id = await collect_conversation_feedback(
                    feedback_service=feedback_service,
                    session_id=session_id,
                    user_input=texto_transcrito,
                    assistant_response=resposta_texto,
                    tokens_used=tokens,
                    processing_time=processing_time,
                    used_tool=used_tool
                )
                if conversation_id:
                    logger.debug(f"💾 Conversa coletada: conversation_id={conversation_id}")
            except Exception as e:
                logger.warning(f"Erro ao coletar conversa: {e}")
        
        # Envia resposta com conversation_id (se disponível)
        response_data = {
            "type": "response",
            "text": resposta_texto,
            "tokens": tokens,
            "metrics": {
                "sttTime": int(stt_time),
                "llmTime": int(llm_time),
                "ttsTime": None  # TTS desabilitado - resposta apenas em texto
            }
        }
        if conversation_id is not None:
            response_data["conversation_id"] = conversation_id
        
        if not await safe_send_json(websocket, response_data):
            logger.warning("Conexão fechada antes de enviar resposta")
            return session_id
        logger.debug("📤 Resposta enviada ao cliente")
        
        # NOTA: TTS desabilitado - agente responde apenas via texto
        # O áudio do usuário ainda é processado (STT), mas a resposta é apenas textual
        logger.info("ℹ️ TTS desabilitado - resposta apenas em texto")
        tts_time = 0  # TTS não foi executado
        
        # Captura resposta para análise (em background, não bloqueia)
        try:
            contexto_list = [{"role": msg["role"], "content": msg["content"]} for msg in contexto] if contexto else []
            
            # Extrai nomes das tools usadas
            tools_names = []
            if tools:
                for tool in tools:
                    if isinstance(tool, dict) and 'function' in tool:
                        func_name = tool.get('function', {}).get('name')
                        if func_name:
                            tools_names.append(func_name)
            
            # Detecta tool usada pela resposta (simplificado)
            if not tools_names:
                texto_lower = texto_transcrito.lower()
                if "pesquis" in texto_lower or "busca" in texto_lower:
                    tools_names.append("web_search")
                elif "arquitet" in texto_lower or "design" in texto_lower:
                    tools_names.append("architecture_advisor")
            
            capture_response(
                user_input=texto_transcrito,
                assistant_response=resposta_texto_original,
                session_id=session_id,
                tokens=tokens,
                processing_time=(time.time() - stt_start),
                tools_used=tools_names if tools_names else None,
                sanitized_response=resposta_texto if resposta_texto != resposta_texto_original else None,
                context_messages=contexto_list,
                audio_data=None,  # Sem áudio
                audio_duration=None  # Sem duração de áudio
            )
        except Exception as e:
            logger.debug(f"Erro ao capturar resposta (não crítico): {e}")
        
        # Atualiza métricas (sem TTS)
        await safe_send_json(websocket, {
            "type": "complete",
            "metrics": {
                "sttTime": int(stt_time),
                "llmTime": int(llm_time),
                "ttsTime": None  # TTS desabilitado
            }
        })
        
        logger.info(f"✅ Processamento completo para sessão {session_id}")
        return session_id
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar áudio: {e}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        await safe_send_json(websocket, {
            "type": "error",
            "message": f"Erro ao processar áudio: {str(e)}"
        })
        return session_id

