"""
Handler para processamento completo de áudio (STT -> LLM -> TTS)
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
from backend.api.handlers.feedback_collector import collect_conversation_feedback
from backend.services.response_sanitizer import get_sanitizer


async def process_audio_complete(
    stt_service: Any,
    llm_service: Any,
    tts_service: Any,
    context_manager: Any,
    memory_service: Any,
    plugin_manager: Any,
    web_search_tool: Any,
    reward_model_service: Optional[Any],
    rlhf_service: Optional[Any],
    feedback_service: Optional[Any],
    audio_data: bytes,
    session_id: Optional[str]
) -> Tuple[Response, str, float]:
    """
    Processa áudio completo: STT -> LLM -> TTS
    
    Args:
        stt_service: Serviço de STT
        llm_service: Serviço de LLM
        tts_service: Serviço de TTS
        context_manager: Gerenciador de contexto
        memory_service: Serviço de memória
        plugin_manager: Gerenciador de plugins
        web_search_tool: Tool de busca web (compatibilidade)
        reward_model_service: Modelo de recompensa (opcional)
        rlhf_service: Serviço RLHF (opcional)
        feedback_service: Serviço de feedback (opcional)
        audio_data: Dados do áudio
        session_id: ID da sessão (None para criar nova)
        
    Returns:
        Tupla (Response, session_id, tempo_total)
    """
    start_time = time.time()
    
    # 1. STT + Preparação paralela (contexto, memórias, tools)
    logger.info("Etapa 1: Transcrição e preparação paralela")
    texto_transcrito, session_id, contexto, memoria_contexto, tools, tool_executor = await process_with_parallel_prep(
        stt_service=stt_service,
        context_manager=context_manager,
        memory_service=memory_service,
        plugin_manager=plugin_manager,
        web_search_tool=web_search_tool,
        llm_service=llm_service,
        audio_data=audio_data,
        texto=None,
        session_id=session_id
    )
    
    # 2. LLM - Gera resposta
    logger.info("Etapa 2: Geração de resposta (LLM)")
    
    # Processa com LLM usando handler
    resposta_texto, tokens = await process_with_llm(
        llm_service=llm_service,
        texto=texto_transcrito,
        contexto=contexto,
        memoria_contexto=memoria_contexto,
        tools=tools,
        tool_executor=tool_executor,
        reward_model_service=reward_model_service,
        rlhf_service=rlhf_service
    )
    
    # 2.5. Sanitiza resposta (remove tokens de treinamento, números excessivos, etc)
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
    
    # Salva memórias em paralelo (não bloqueia resposta)
    await save_memories_parallel(
        memory_service, texto_transcrito, resposta_texto
    )
    
    await context_manager.add_message(session_id, "assistant", resposta_texto)
    logger.info(f"Resposta: '{resposta_texto}'")
    
    # 4. Text-to-Speech
    logger.info("Etapa 3: Síntese de voz (TTS)")
    audio_resposta = await tts_service.synthesize(resposta_texto)
    
    tempo_total = time.time() - start_time
    
    # Coleta conversa usando handler
    await collect_conversation_feedback(
        feedback_service, session_id, texto_transcrito, resposta_texto,
        tokens, tempo_total, None
    )
    
    logger.info(
        f"Processamento completo em {tempo_total:.2f}s: "
        f"STT -> '{texto_transcrito}' -> LLM -> '{resposta_texto}' -> TTS"
    )
    
    # Retorna áudio com headers informativos
    response = Response(
        content=audio_resposta,
        media_type="audio/wav",
        headers={
            "X-Transcription": sanitize_header_value(texto_transcrito),
            "X-Response-Text": sanitize_header_value(resposta_texto),
            "X-Session-ID": session_id,
            "X-Processing-Time": str(tempo_total),
            "X-Tokens-Used": str(tokens)
        }
    )
    
    return response, session_id, tempo_total

