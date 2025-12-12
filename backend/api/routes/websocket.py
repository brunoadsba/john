"""
Rotas WebSocket para comunicação em tempo real
"""
from typing import Optional
from fastapi import APIRouter, WebSocket
from loguru import logger

from backend.services import ContextManager
from backend.api.routes.websocket_handlers import init_handlers
from backend.api.routes.websocket_wake_word_handler import (
    init_wake_word_handler,
    handle_wake_word_websocket
)
from backend.api.handlers.websocket_listen_handler import handle_listen_websocket
from backend.api.handlers.websocket_stream_handler import handle_stream_websocket


router = APIRouter(tags=["websocket"])

# Instâncias dos serviços (serão inicializadas no startup)
context_manager: Optional[ContextManager] = None


def init_services(stt, llm, tts, ww, ctx, memory=None, web_search=None, feedback=None, privacy_svc=None):
    """
    Inicializa os serviços em todos os módulos
    
    Args:
        web_search: PluginManager ou web_search_tool (compatibilidade)
        feedback: Serviço de feedback (opcional)
        privacy_svc: Serviço de modo privacidade (opcional)
    """
    global context_manager
    context_manager = ctx
    
    # Inicializa handlers
    init_handlers(stt, llm, tts, ctx, memory, web_search, feedback, privacy_svc)
    init_wake_word_handler(ww)


@router.websocket("/ws/listen")
async def websocket_listen(websocket: WebSocket):
    """
    WebSocket para comunicação em tempo real
    
    Protocolo:
    1. Cliente conecta
    2. Servidor envia confirmação
    3. Cliente envia áudio em chunks ou completo
    4. Servidor processa e retorna resposta
    5. Loop continua até desconexão
    """
    await handle_listen_websocket(websocket, context_manager)


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket para streaming contínuo de áudio
    
    Recebe chunks de áudio em tempo real e processa incrementalmente
    """
    await handle_stream_websocket(websocket, context_manager)


@router.websocket("/ws/wake_word")
async def websocket_wake_word(websocket: WebSocket):
    """
    WebSocket para detecção de wake word em tempo real
    
    Delega para o handler especializado
    """
    await handle_wake_word_websocket(websocket)
