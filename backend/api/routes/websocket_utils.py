"""
Utilitários para WebSocket
Funções auxiliares para envio seguro de mensagens
"""
from fastapi import WebSocket
from loguru import logger


async def safe_send_json(websocket: WebSocket, data: dict) -> bool:
    """
    Envia mensagem JSON de forma segura, verificando se conexão está aberta
    
    Args:
        websocket: Conexão WebSocket
        data: Dados a enviar (serão serializados como JSON)
    
    Returns:
        True se mensagem foi enviada, False se conexão estava fechada
    """
    try:
        # Verifica estado da conexão
        if websocket.client_state.name != "CONNECTED":
            logger.debug("Conexão WebSocket não está mais conectada, ignorando envio")
            return False
        
        await websocket.send_json(data)
        return True
    except (RuntimeError, ConnectionError) as e:
        error_msg = str(e).lower()
        if "websocket.close" in str(e) or "closed" in error_msg or "disconnect" in error_msg:
            logger.debug("Conexão WebSocket fechada durante envio, ignorando")
            return False
        else:
            logger.warning(f"Erro ao enviar mensagem WebSocket: {e}")
            raise


async def safe_send_bytes(websocket: WebSocket, data: bytes) -> bool:
    """
    Envia bytes de forma segura, verificando se conexão está aberta
    
    Args:
        websocket: Conexão WebSocket
        data: Bytes a enviar
    
    Returns:
        True se dados foram enviados, False se conexão estava fechada
    """
    try:
        # Verifica estado da conexão
        if websocket.client_state.name != "CONNECTED":
            logger.debug("Conexão WebSocket não está mais conectada, ignorando envio de bytes")
            return False
        
        await websocket.send_bytes(data)
        return True
    except (RuntimeError, ConnectionError) as e:
        error_msg = str(e).lower()
        if "websocket.close" in str(e) or "closed" in error_msg or "disconnect" in error_msg:
            logger.debug("Conexão WebSocket fechada durante envio de bytes, ignorando")
            return False
        else:
            logger.warning(f"Erro ao enviar bytes WebSocket: {e}")
            raise

