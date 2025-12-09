"""
Handler para endpoint WebSocket /ws/listen
"""
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from backend.services import ContextManager
from backend.api.routes.websocket_utils import safe_send_json
from backend.api.routes.websocket_handlers import (
    handle_control_message,
    handle_audio_data
)


async def handle_listen_websocket(
    websocket: WebSocket,
    context_manager: Optional[ContextManager]
) -> None:
    """
    Handler para endpoint /ws/listen
    
    Args:
        websocket: Conexão WebSocket
        context_manager: Gerenciador de contexto
    """
    await websocket.accept()
    
    # Verifica se serviços estão inicializados
    if not context_manager:
        await websocket.send_json({
            "type": "error",
            "message": "Servidor ainda não está pronto. Aguarde alguns segundos."
        })
        await websocket.close()
        logger.error("WebSocket rejeitado: serviços não inicializados")
        return
    
    session_id = None
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"🔌 Nova conexão WebSocket estabelecida de {client_ip}")
    
    try:
        # Envia mensagem de boas-vindas
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado ao assistente Jonh"
        })
        logger.debug(f"✅ Mensagem de boas-vindas enviada para {client_ip}")
        
        while True:
            try:
                # Recebe dados do cliente
                data = await websocket.receive()
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "disconnect" in error_msg or "close" in error_msg or "cannot call" in error_msg:
                    logger.info(f"🔌 Conexão WebSocket fechada por {client_ip} (session: {session_id})")
                    break
                raise
            
            # Verifica se é mensagem de desconexão
            msg_keys = list(data.keys())
            
            # Se receber apenas 'type' e 'code', é mensagem de desconexão do Starlette
            if set(msg_keys) == {"type", "code"} or (data.get("type") == "websocket.disconnect"):
                logger.info(f"🔌 Cliente {client_ip} desconectou (session: {session_id})")
                break
            
            # Processa diferentes tipos de mensagem
            if "text" in data:
                # Mensagem de controle (JSON)
                logger.debug(f"📨 Mensagem de controle recebida de {client_ip}: {data['text'][:100]}")
                session_id = await handle_control_message(websocket, data["text"], session_id)
                
            elif "bytes" in data:
                # Dados de áudio
                audio_size = len(data["bytes"])
                logger.info(f"🎤 Áudio recebido de {client_ip}: {audio_size} bytes (session: {session_id})")
                session_id = await handle_audio_data(
                    websocket,
                    data["bytes"],
                    session_id
                )
            else:
                logger.warning(f"⚠️ Tipo de mensagem desconhecido recebido de {client_ip}: {msg_keys}")
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket desconectado normalmente (session: {session_id})")
    
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {e}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        # Tenta enviar mensagem de erro de forma segura
        await safe_send_json(websocket, {
            "type": "error",
            "message": str(e)
        })
    
    finally:
        # Sempre limpa a sessão quando conexão fecha
        if session_id and context_manager:
            try:
                await context_manager.delete_session(session_id)
                logger.debug(f"🗑️ Sessão {session_id} removida")
            except Exception as e:
                logger.warning(f"Erro ao remover sessão {session_id}: {e}")

