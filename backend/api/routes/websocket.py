"""
Rotas WebSocket para comunicação em tempo real
"""
import json
import asyncio
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from backend.services import (
    WhisperSTTService,
    BaseLLMService,
    PiperTTSService,
    ContextManager
)


router = APIRouter(tags=["websocket"])

# Instâncias dos serviços (serão inicializadas no startup)
stt_service: Optional[WhisperSTTService] = None
llm_service: Optional[BaseLLMService] = None
tts_service: Optional[PiperTTSService] = None
context_manager: Optional[ContextManager] = None


def init_services(stt, llm, tts, ctx):
    """Inicializa os serviços"""
    global stt_service, llm_service, tts_service, context_manager
    stt_service = stt
    llm_service = llm
    tts_service = tts
    context_manager = ctx


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
    await websocket.accept()
    session_id = None
    
    logger.info("Nova conexão WebSocket estabelecida")
    
    try:
        # Envia mensagem de boas-vindas
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado ao assistente Jonh"
        })
        
        while True:
            # Recebe dados do cliente
            data = await websocket.receive()
            
            # Processa diferentes tipos de mensagem
            if "text" in data:
                # Mensagem de controle (JSON)
                await handle_control_message(websocket, data["text"], session_id)
                
            elif "bytes" in data:
                # Dados de áudio
                session_id = await handle_audio_data(
                    websocket,
                    data["bytes"],
                    session_id
                )
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado (session: {session_id})")
        if session_id:
            context_manager.delete_session(session_id)
    
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()


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
            new_session_id = context_manager.create_session()
            await websocket.send_json({
                "type": "session_started",
                "session_id": new_session_id
            })
            logger.info(f"Nova sessão criada via WebSocket: {new_session_id}")
            return new_session_id
        
        elif msg_type == "end_session":
            # Encerra sessão
            if session_id:
                context_manager.delete_session(session_id)
            await websocket.send_json({
                "type": "session_ended"
            })
            return None
        
        elif msg_type == "ping":
            # Responde ping
            await websocket.send_json({
                "type": "pong"
            })
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
    try:
        # Cria sessão se não existir
        if not session_id:
            session_id = context_manager.create_session()
            await websocket.send_json({
                "type": "session_created",
                "session_id": session_id
            })
        
        # Envia status de processamento
        await websocket.send_json({
            "type": "processing",
            "stage": "transcribing"
        })
        
        # 1. Transcreve áudio
        texto_transcrito, confianca, duracao = stt_service.transcribe_audio(audio_data)
        
        await websocket.send_json({
            "type": "transcription",
            "text": texto_transcrito,
            "confidence": confianca
        })
        
        # 2. Gera resposta com LLM
        await websocket.send_json({
            "type": "processing",
            "stage": "generating"
        })
        
        context_manager.add_message(session_id, "user", texto_transcrito)
        contexto = context_manager.get_context(session_id)
        
        resposta_texto, tokens = llm_service.generate_response(
            texto_transcrito,
            contexto
        )
        
        context_manager.add_message(session_id, "assistant", resposta_texto)
        
        await websocket.send_json({
            "type": "response",
            "text": resposta_texto,
            "tokens": tokens
        })
        
        # 3. Sintetiza áudio
        await websocket.send_json({
            "type": "processing",
            "stage": "synthesizing"
        })
        
        audio_resposta = tts_service.synthesize(resposta_texto)
        
        # Envia áudio
        await websocket.send_bytes(audio_resposta)
        
        await websocket.send_json({
            "type": "complete",
            "session_id": session_id
        })
        
        logger.info(
            f"WebSocket: processamento completo - "
            f"'{texto_transcrito}' -> '{resposta_texto}'"
        )
        
        return session_id
    
    except Exception as e:
        logger.error(f"Erro ao processar áudio no WebSocket: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        return session_id


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket para streaming contínuo de áudio
    
    Recebe chunks de áudio em tempo real e processa incrementalmente
    """
    await websocket.accept()
    logger.info("Nova conexão WebSocket de streaming estabelecida")
    
    audio_buffer = bytearray()
    session_id = context_manager.create_session()
    
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
            context_manager.delete_session(session_id)

