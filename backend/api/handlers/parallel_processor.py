"""
Handler para processamento paralelo de operações independentes
Reduz latência total executando tarefas em paralelo quando possível
"""
import asyncio
from typing import Optional, Tuple, Any, List, Dict
from loguru import logger


async def prepare_context_parallel(
    context_manager: Any,
    memory_service: Any,
    session_id: Optional[str],
    user_input: str
) -> Tuple[str, list, str]:
    """
    Prepara contexto e memórias em paralelo
    
    Args:
        context_manager: Gerenciador de contexto
        memory_service: Serviço de memória
        session_id: ID da sessão (None para criar nova)
        user_input: Entrada do usuário
        
    Returns:
        Tupla (session_id, contexto, memoria_contexto)
    """
    # Cria sessão se necessário (síncrono, mas rápido)
    if not session_id:
        session_id = await context_manager.create_session()
    
    # Executa em paralelo: adicionar mensagem + buscar memórias
    async def add_message():
        await context_manager.add_message(session_id, "user", user_input)
        return await context_manager.get_context(session_id)
    
    async def get_memories():
        if memory_service:
            return await memory_service.get_memories_for_context(user_input)
        return ""
    
    # Executa ambas as operações em paralelo
    contexto, memoria_contexto = await asyncio.gather(
        add_message(),
        get_memories()
    )
    
    logger.debug("✅ Contexto e memórias preparados em paralelo")
    
    return session_id, contexto, memoria_contexto


async def process_with_parallel_prep(
    stt_service: Any,
    context_manager: Any,
    memory_service: Any,
    plugin_manager: Any,
    web_search_tool: Any,
    llm_service: Any,
    audio_data: Optional[bytes],
    texto: Optional[str],
    session_id: Optional[str],
    privacy_mode_service: Optional[Any] = None
) -> Tuple[str, str, list, str, Optional[List[Dict]], Optional[Any]]:
    """
    Processa entrada (áudio ou texto) com preparação paralela
    
    Args:
        stt_service: Serviço de STT
        context_manager: Gerenciador de contexto
        memory_service: Serviço de memória
        plugin_manager: Gerenciador de plugins
        web_search_tool: Tool de busca web
        llm_service: Serviço de LLM
        audio_data: Dados do áudio (se processamento de áudio)
        texto: Texto (se processamento de texto)
        session_id: ID da sessão
        
    Returns:
        Tupla (texto_transcrito, session_id, contexto, memoria_contexto, tools, tool_executor)
    """
    # Se for áudio, transcreve primeiro (bloqueante, mas necessário)
    if audio_data:
        logger.info("Etapa 1: Transcrição (STT)")
        texto_transcrito, confianca, duracao = stt_service.transcribe_audio(audio_data)
        
        if not texto_transcrito or not texto_transcrito.strip():
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="Não foi possível transcrever o áudio."
            )
        
        logger.info(f"Transcrito: '{texto_transcrito}'")
    else:
        texto_transcrito = texto
    
    # Prepara contexto, memórias e tools em paralelo
    async def prep_context():
        return await prepare_context_parallel(
            context_manager, memory_service, session_id, texto_transcrito
        )
    
    async def prep_tools():
        from backend.api.handlers.tools_preparer import prepare_tools_for_llm
        # Obtém LLM ativo do privacy_mode_service se disponível
        active_llm = llm_service
        if privacy_mode_service:
            active_llm = privacy_mode_service.get_active_llm_service() or llm_service
        return prepare_tools_for_llm(plugin_manager, web_search_tool, active_llm, privacy_mode_service)
    
    # Executa preparações em paralelo
    (session_id, contexto, memoria_contexto), (tools, tool_executor) = await asyncio.gather(
        prep_context(),
        prep_tools()
    )
    
    logger.debug("✅ Contexto, memórias e tools preparados em paralelo")
    
    return texto_transcrito, session_id, contexto, memoria_contexto, tools, tool_executor


async def save_memories_parallel(
    memory_service: Any,
    user_input: str,
    assistant_response: str
):
    """
    Salva memórias em paralelo (não bloqueia resposta)
    
    Args:
        memory_service: Serviço de memória
        user_input: Entrada do usuário
        assistant_response: Resposta do assistente
    """
    if memory_service:
        try:
            # Executa em background (não aguarda)
            asyncio.create_task(
                memory_service.extract_and_save_memory(user_input, assistant_response)
            )
            logger.debug("💾 Salvamento de memórias iniciado em background")
        except Exception as e:
            logger.warning(f"Erro ao salvar memórias em background: {e}")

