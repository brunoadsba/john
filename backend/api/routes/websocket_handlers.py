"""
Handlers de mensagens WebSocket
Processamento de mensagens de controle e dados de áudio
"""
import json
from typing import Optional
from fastapi import WebSocket
from loguru import logger

from backend.services import (
    WhisperSTTService,
    BaseLLMService,
    PiperTTSService,
    ContextManager
)
from backend.api.routes.websocket_utils import safe_send_json
from backend.api.handlers.websocket_audio_processor import process_audio_complete


# Instâncias dos serviços (serão inicializadas no startup)
stt_service: Optional[WhisperSTTService] = None
llm_service: Optional[BaseLLMService] = None
tts_service: Optional[PiperTTSService] = None
context_manager: Optional[ContextManager] = None
memory_service = None
plugin_manager = None  # Novo: PluginManager
web_search_tool = None  # Mantido para compatibilidade
feedback_service = None  # Serviço de feedback para coleta de dados


def init_handlers(stt, llm, tts, ctx, memory=None, web_search=None, feedback=None):
    """
    Inicializa os serviços nos handlers
    
    Args:
        web_search: PluginManager ou web_search_tool (compatibilidade)
        feedback: Serviço de feedback (opcional)
    """
    global stt_service, llm_service, tts_service, context_manager, memory_service, plugin_manager, web_search_tool, feedback_service
    stt_service = stt
    llm_service = llm
    tts_service = tts
    context_manager = ctx
    memory_service = memory
    feedback_service = feedback
    
    # Aceita PluginManager ou web_search_tool antigo (compatibilidade)
    from backend.core.plugin_manager import PluginManager
    if isinstance(web_search, PluginManager):
        plugin_manager = web_search
        # Tenta obter web_search_tool do plugin para compatibilidade
        web_search_plugin = plugin_manager.get_plugin("web_search")
        if web_search_plugin:
            web_search_tool = web_search_plugin
    else:
        # Modo antigo (compatibilidade)
        plugin_manager = None
        web_search_tool = web_search


async def handle_control_message(
    websocket: WebSocket,
    message: str,
    session_id: Optional[str]
) -> Optional[str]:
    """
    Processa mensagens de controle (JSON)
    
    Args:
        websocket: Conexão WebSocket
        message: Mensagem JSON
        session_id: ID da sessão atual
        
    Returns:
        ID da sessão (pode ser novo)
    """
    try:
        data = json.loads(message)
        msg_type = data.get("type")
        
        if msg_type == "start_session":
            # Inicia nova sessão
            new_session_id = await context_manager.create_session()
            await safe_send_json(websocket, {
                "type": "session_started",
                "session_id": new_session_id
            })
            logger.info(f"Nova sessão criada via WebSocket: {new_session_id}")
            return new_session_id
        
        elif msg_type == "end_session":
            # Encerra sessão
            if session_id:
                await context_manager.delete_session(session_id)
            await safe_send_json(websocket, {
                "type": "session_ended"
            })
            return None
        
        elif msg_type == "ping":
            # Responde ping
            await safe_send_json(websocket, {
                "type": "pong"
            })
            return session_id
        
        elif msg_type == "reset_processing":
            # Reseta estado de processamento (para wake word)
            # Esta lógica será implementada no wake_word handler
            return session_id
        
        else:
            logger.warning(f"Tipo de mensagem desconhecido: {msg_type}")
            return session_id
    
    except json.JSONDecodeError:
        logger.error("Mensagem JSON inválida")
        return session_id


async def handle_audio_data(
    websocket: WebSocket,
    audio_data: bytes,
    session_id: Optional[str]
) -> str:
    """
    Processa dados de áudio recebidos
    
    Args:
        websocket: Conexão WebSocket
        audio_data: Bytes do áudio
        session_id: ID da sessão (ou None)
        
    Returns:
        ID da sessão
    """
    return await process_audio_complete(
        websocket=websocket,
        audio_data=audio_data,
        session_id=session_id,
        stt_service=stt_service,
        llm_service=llm_service,
        tts_service=tts_service,
        context_manager=context_manager,
        memory_service=memory_service,
        plugin_manager=plugin_manager,
        web_search_tool=web_search_tool,
        feedback_service=feedback_service
    )

