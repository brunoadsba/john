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
    feedback_service: Optional[any] = None
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
        
        if not texto_transcrito or texto_transcrito.strip() == "":
            logger.warning("⚠️ Transcrição vazia - áudio pode estar sem fala ou muito baixo")
        
        if not await safe_send_json(websocket, {
            "type": "transcription",
            "text": texto_transcrito,
            "confidence": confianca
        }):
            logger.warning("Conexão fechada antes de enviar transcrição")
            return session_id
        logger.debug("📤 Transcrição enviada ao cliente")
        
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
        
        # Prepara tools e tool executor
        tools, tool_executor = prepare_tools_for_websocket(plugin_manager, web_search_tool)
        
        # Gera resposta com LLM (passa memórias e tools)
        resposta_texto, tokens = llm_service.generate_response(
            texto_transcrito,
            contexto,
            memorias_contexto=memoria_contexto,
            tools=tools,
            tool_executor=tool_executor
        )
        llm_time = (time.time() - llm_start) * 1000  # em milissegundos
        logger.info(f"✅ Resposta gerada: '{resposta_texto[:100]}...' ({tokens} tokens)")
        logger.debug(f"⏱️ LLM levou {llm_time:.0f}ms")
        
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
                "ttsTime": None  # Será preenchido após TTS
            }
        }
        if conversation_id is not None:
            response_data["conversation_id"] = conversation_id
        
        if not await safe_send_json(websocket, response_data):
            logger.warning("Conexão fechada antes de enviar resposta")
            return session_id
        logger.debug("📤 Resposta enviada ao cliente")
        
        # 3. Sintetiza áudio
        if not await safe_send_json(websocket, {
            "type": "processing",
            "stage": "synthesizing"
        }):
            logger.warning("Conexão fechada antes de sintetizar áudio")
            return session_id
        logger.debug("📤 Status 'synthesizing' enviado")
        
        tts_start = time.time()
        logger.info("🔊 Iniciando síntese de voz...")
        audio_resposta = await tts_service.synthesize(resposta_texto)
        tts_time = (time.time() - tts_start) * 1000  # em milissegundos
        logger.info(f"✅ Áudio sintetizado: {len(audio_resposta)} bytes")
        logger.debug(f"⏱️ TTS levou {tts_time:.0f}ms")
        
        if not await safe_send_bytes(websocket, audio_resposta):
            logger.warning("Conexão fechada antes de enviar áudio")
            return session_id
        logger.debug("📤 Áudio enviado ao cliente")
        
        # Atualiza métricas com TTS time
        await safe_send_json(websocket, {
            "type": "complete",
            "metrics": {
                "sttTime": int(stt_time),
                "llmTime": int(llm_time),
                "ttsTime": int(tts_time)
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

