"""
Handler para processamento de texto (LLM -> TTS)
"""
import time
from typing import Optional, Tuple, Any
from loguru import logger
from fastapi.responses import Response

from backend.api.utils.headers import sanitize_header_value
from backend.api.handlers.context_preparer import save_memories_from_response
from backend.api.handlers.parallel_processor import (
    process_with_parallel_prep,
    save_memories_parallel
)
from backend.api.handlers.llm_processor import process_with_llm
from backend.api.handlers.architecture_handler import (
    handle_architecture_intent,
    format_architecture_plugin_result
)
from backend.api.handlers.feedback_collector import collect_conversation_feedback
from backend.api.handlers.response_cache_handler import (
    get_cached_response,
    set_cached_response
)


async def process_text_complete(
    llm_service: Any,
    tts_service: Any,
    context_manager: Any,
    memory_service: Any,
    intent_detector: Any,
    plugin_manager: Any,
    web_search_tool: Any,
    reward_model_service: Optional[Any],
    rlhf_service: Optional[Any],
    feedback_service: Optional[Any],
    texto: str,
    session_id: Optional[str],
    system_prompt: Optional[str] = None,
    response_cache: Optional[Any] = None
) -> Tuple[Response, str, float]:
    """
    Processa texto completo: LLM -> TTS
    
    Args:
        llm_service: Serviço de LLM
        tts_service: Serviço de TTS
        context_manager: Gerenciador de contexto
        memory_service: Serviço de memória
        intent_detector: Detector de intenções
        plugin_manager: Gerenciador de plugins
        web_search_tool: Tool de busca web (compatibilidade)
        reward_model_service: Modelo de recompensa (opcional)
        rlhf_service: Serviço RLHF (opcional)
        feedback_service: Serviço de feedback (opcional)
        texto: Texto do usuário
        session_id: ID da sessão (None para criar nova)
        system_prompt: System prompt customizado (opcional)
        
    Returns:
        Tupla (Response, session_id, tempo_total)
    """
    start_time = time.time()
    
    # 0. Verifica cache de respostas (antes de processar)
    if response_cache and not system_prompt:  # Não usa cache com system_prompt customizado
        cached_result = await get_cached_response(response_cache, texto)
        if cached_result:
            resposta_texto, tokens = cached_result
            logger.info(f"✅ Usando resposta do cache: '{resposta_texto[:50]}...'")
            
            # Adiciona ao contexto
            await context_manager.add_message(session_id or "cache", "assistant", resposta_texto)
            
            # TTS
            logger.info("Etapa 2: Síntese de voz (TTS)")
            audio_resposta = await tts_service.synthesize(resposta_texto)
            
            tempo_total = time.time() - start_time
            
            # Coleta conversa
            await collect_conversation_feedback(
                feedback_service, session_id, texto, resposta_texto,
                tokens, tempo_total, "cache"
            )
            
            logger.info(
                f"Processamento completo (cache) em {tempo_total:.2f}s: "
                f"TEXTO -> CACHE -> '{resposta_texto}' -> TTS"
            )
            
            response = Response(
                content=audio_resposta,
                media_type="audio/wav",
                headers={
                    "X-Input-Text": sanitize_header_value(texto),
                    "X-Response-Text": sanitize_header_value(resposta_texto),
                    "X-Session-ID": session_id or "cache",
                    "X-Processing-Time": str(tempo_total),
                    "X-Tokens-Used": str(tokens),
                    "X-Cache-Hit": "true"
                }
            )
            
            return response, session_id or "cache", tempo_total
    
    # 1. Prepara contexto, memórias e tools em paralelo
    logger.info("Etapa 0: Preparação paralela (contexto, memórias, tools)")
    _, session_id, contexto, memoria_contexto, tools, tool_executor = await process_with_parallel_prep(
        stt_service=None,  # Não precisa de STT para texto
        context_manager=context_manager,
        memory_service=memory_service,
        plugin_manager=plugin_manager,
        web_search_tool=web_search_tool,
        llm_service=llm_service,
        audio_data=None,
        texto=texto,
        session_id=session_id
    )
    
    # 1.5. Detecta intenção de arquitetura usando handler
    architecture_result = await handle_architecture_intent(
        intent_detector, plugin_manager, texto
    )
    
    # 2. LLM - Gera resposta
    logger.info("Etapa 1: Geração de resposta (LLM)")
    
    # Se detectou intenção de arquitetura, chama plugin diretamente
    if architecture_result:
        architecture_intent, plugin_result = architecture_result
        logger.info(f"🔧 Architecture Advisor detectado: {architecture_intent}")
        
        try:
            # Formata resultado usando handler
            if plugin_result.get("success"):
                resposta_texto = format_architecture_plugin_result(plugin_result, architecture_intent)
                tokens = 0  # Não usou tokens do LLM
                
                # Adiciona ao contexto
                await context_manager.add_message(session_id, "assistant", resposta_texto)
                
                # TTS
                logger.info("Etapa 2: Síntese de voz (TTS)")
                audio_resposta = await tts_service.synthesize(resposta_texto)
                
                tempo_total = time.time() - start_time
                
                # Coleta conversa usando handler
                await collect_conversation_feedback(
                    feedback_service, session_id, texto, resposta_texto,
                    tokens, tempo_total, "architecture_advisor"
                )
                
                logger.info(
                    f"Processamento completo em {tempo_total:.2f}s: "
                    f"INTENT → Architecture Advisor → '{resposta_texto}' → TTS"
                )
                
                response = Response(
                    content=audio_resposta,
                    media_type="audio/wav",
                    headers={
                        "X-Input-Text": sanitize_header_value(texto),
                        "X-Response-Text": sanitize_header_value(resposta_texto),
                        "X-Session-ID": session_id,
                        "X-Processing-Time": str(tempo_total),
                        "X-Tokens-Used": str(tokens),
                        "X-Architecture-Intent": sanitize_header_value(architecture_intent) if architecture_intent else ""
                    }
                )
                
                return response, session_id, tempo_total
            else:
                logger.warning(f"Plugin retornou erro: {plugin_result.get('message')}")
                # Continua com fluxo normal se plugin falhar
        except Exception as e:
            logger.error(f"Erro ao executar Architecture Advisor: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Continua com fluxo normal se houver erro
    
    # Processa com LLM usando handler (tools já preparados em paralelo)
    resposta_texto, tokens = await process_with_llm(
        llm_service=llm_service,
        texto=texto,
        contexto=contexto,
        memoria_contexto=memoria_contexto,
        tools=tools,
        tool_executor=tool_executor,
        system_prompt_override=system_prompt,
        reward_model_service=reward_model_service,
        rlhf_service=rlhf_service
    )
    
    # Salva memórias em paralelo (não bloqueia resposta)
    await save_memories_parallel(
        memory_service, texto, resposta_texto
    )
    
    # Armazena no cache (se disponível e não for system_prompt customizado)
    if response_cache and not system_prompt:
        await set_cached_response(response_cache, texto, resposta_texto, tokens)
    
    await context_manager.add_message(session_id, "assistant", resposta_texto)
    logger.info(f"Resposta: '{resposta_texto}'")
    
    # 3. Text-to-Speech
    logger.info("Etapa 2: Síntese de voz (TTS)")
    audio_resposta = await tts_service.synthesize(resposta_texto)
    
    tempo_total = time.time() - start_time
    
    # Detecta tool usada (simplificado)
    used_tool = None
    if tools and tool_executor:
        used_tool = "web_search" if "pesquis" in texto.lower() or "busca" in texto.lower() else None
    
    # Coleta conversa usando handler
    await collect_conversation_feedback(
        feedback_service, session_id, texto, resposta_texto,
        tokens, tempo_total, used_tool
    )
    
    logger.info(
        f"Processamento completo em {tempo_total:.2f}s: "
        f"TEXTO -> '{texto}' -> LLM -> '{resposta_texto}' -> TTS"
    )
    
    # Retorna áudio com headers informativos
    response = Response(
        content=audio_resposta,
        media_type="audio/wav",
        headers={
            "X-Input-Text": sanitize_header_value(texto),
            "X-Response-Text": sanitize_header_value(resposta_texto),
            "X-Session-ID": session_id,
            "X-Processing-Time": str(tempo_total),
            "X-Tokens-Used": str(tokens)
        }
    )
    
    return response, session_id, tempo_total

