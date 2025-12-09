"""
Rotas para streaming de respostas LLM usando Server-Sent Events (SSE)
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
import json
import asyncio

from backend.api.handlers.parallel_processor import process_with_parallel_prep
from backend.api.handlers.response_cache_handler import get_cached_response

router = APIRouter(tags=["streaming"])

# Instâncias dos serviços (serão inicializadas no startup)
llm_service = None
context_manager = None
memory_service = None
plugin_manager = None
web_search_tool = None
intent_detector = None
response_cache = None


def init_services(
    llm,
    ctx,
    memory=None,
    plugin_mgr=None,
    intent_detector_instance=None,
    response_cache_instance=None
):
    """Inicializa os serviços"""
    global llm_service, context_manager, memory_service, plugin_manager, web_search_tool, intent_detector, response_cache
    llm_service = llm
    context_manager = ctx
    memory_service = memory
    intent_detector = intent_detector_instance
    response_cache = response_cache_instance
    
    # Aceita PluginManager ou web_search_tool antigo (compatibilidade)
    from backend.core.plugin_manager import PluginManager
    if isinstance(plugin_mgr, PluginManager):
        plugin_manager = plugin_mgr
        web_search_plugin = plugin_manager.get_plugin("web_search")
        if web_search_plugin:
            web_search_tool = web_search_plugin
        else:
            web_search_tool = None
    else:
        plugin_manager = None
        web_search_tool = None


async def stream_llm_response(
    texto: str,
    session_id: Optional[str] = None
):
    """
    Gera stream de resposta do LLM
    
    Args:
        texto: Texto da pergunta
        session_id: ID da sessão (opcional)
        
    Yields:
        Eventos SSE com tokens de texto
    """
    try:
        # Verifica cache primeiro (não faz streaming de cache)
        if response_cache:
            cached_result = await get_cached_response(response_cache, texto)
            if cached_result:
                resposta_texto, tokens = cached_result
                # Envia resposta completa de uma vez (não faz streaming de cache)
                yield f"data: {json.dumps({'type': 'complete', 'text': resposta_texto, 'tokens': tokens, 'cached': True})}\n\n"
                return
        
        # Prepara contexto, memórias e tools em paralelo
        _, session_id, contexto, memoria_contexto, tools, tool_executor = await process_with_parallel_prep(
            stt_service=None,
            context_manager=context_manager,
            memory_service=memory_service,
            plugin_manager=plugin_manager,
            web_search_tool=web_search_tool,
            llm_service=llm_service,
            audio_data=None,
            texto=texto,
            session_id=session_id
        )
        
        # Adiciona mensagem do usuário ao contexto
        await context_manager.add_message(session_id, "user", texto)
        
        # Inicia streaming
        resposta_completa = ""
        total_tokens = 0
        
        yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
        
        # Stream de tokens do LLM
        async for token in llm_service.generate_response_stream(
            prompt=texto,
            contexto=contexto,
            memorias_contexto=memoria_contexto,
            tools=None,  # Tools não suportados em streaming ainda
            tool_executor=None,
            system_prompt_override=None
        ):
            resposta_completa += token
            total_tokens += 1  # Estimativa (não temos contagem exata em streaming)
            
            # Envia token via SSE
            yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
        
        # Adiciona resposta completa ao contexto
        await context_manager.add_message(session_id, "assistant", resposta_completa)
        
        # Envia evento de conclusão
        yield f"data: {json.dumps({'type': 'complete', 'text': resposta_completa, 'tokens': total_tokens, 'cached': False})}\n\n"
        
    except Exception as e:
        logger.error(f"Erro no streaming: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.get("/api/stream_text")
async def stream_text(
    texto: str = Query(..., description="Texto da pergunta"),
    session_id: Optional[str] = Query(None, description="ID da sessão")
):
    """
    Endpoint para streaming de resposta LLM usando Server-Sent Events (SSE)
    
    Args:
        texto: Texto da pergunta
        session_id: ID da sessão (opcional)
        
    Returns:
        StreamingResponse com eventos SSE
    """
    if not llm_service or not context_manager:
        raise HTTPException(
            status_code=503,
            detail="Serviços não inicializados. Aguarde alguns segundos."
        )
    
    return StreamingResponse(
        stream_llm_response(texto, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Desabilita buffering no nginx
        }
    )

