"""
Handler para endpoint WebSocket /ws/stream
"""
import json
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from backend.services import ContextManager
from backend.api.routes.websocket_handlers import handle_audio_data


async def handle_stream_websocket(
    websocket: WebSocket,
    context_manager: ContextManager
) -> None:
    """
    Handler para endpoint /ws/stream
    
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
        logger.error("WebSocket streaming rejeitado: serviços não inicializados")
        return
    
    logger.info("Nova conexão WebSocket de streaming estabelecida")
    
    audio_buffer = bytearray()
    session_id = await context_manager.create_session()
    
    try:
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Streaming iniciado"
        })
        
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                # Adiciona ao buffer
                audio_buffer.extend(data["bytes"])
                
                # Quando buffer atingir tamanho suficiente, processa
                # (implementação simplificada - na versão real, detectaria silêncio)
                if len(audio_buffer) > 100000:  # ~1 segundo de áudio
                    session_id = await handle_audio_data(
                        websocket,
                        bytes(audio_buffer),
                        session_id
                    )
                    audio_buffer.clear()
            
            elif "text" in data:
                msg = json.loads(data["text"])
                if msg.get("type") == "stop":
                    break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket streaming desconectado (session: {session_id})")
    
    finally:
        if session_id:
            await context_manager.delete_session(session_id)

