"""
Handler de Wake Word WebSocket
Processamento de detecção de wake word em tempo real
"""
import json
import time
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from backend.services import OpenWakeWordService
from backend.config.settings import settings
from backend.api.routes.websocket_utils import safe_send_json


# Instância do serviço (será inicializada no startup)
wake_word_service: Optional[OpenWakeWordService] = None


def init_wake_word_handler(ww_service):
    """Inicializa o serviço de wake word"""
    global wake_word_service
    wake_word_service = ww_service


async def handle_wake_word_websocket(websocket: WebSocket):
    """
    WebSocket para detecção de wake word em tempo real
    
    Protocolo:
    1. Cliente conecta
    2. Servidor envia confirmação
    3. Cliente envia chunks de áudio continuamente (16-bit PCM, 16kHz)
    4. Servidor processa com OpenWakeWord
    5. Quando detecta wake word, retorna sinal para cliente
    6. Cliente recebe notificação e inicia gravação completa
    
    Formato do áudio esperado:
    - 16-bit PCM
    - 16kHz sample rate
    - Mono
    - Chunks de ~1280 bytes (~80ms de áudio)
    """
    await websocket.accept()
    
    # Verifica se serviço está inicializado
    if not wake_word_service:
        await websocket.send_json({
            "type": "error",
            "message": "Serviço de wake word não está disponível"
        })
        await websocket.close()
        logger.error("WebSocket wake word rejeitado: serviço não inicializado")
        return
    
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"🔌 Conexão wake word estabelecida de {client_ip}")
    
    # Debounce: evita múltiplas detecções seguidas (como Alexa)
    last_wake_word_time = 0.0
    debounce_interval = settings.wake_word_debounce_seconds
    
    # Estado de conversa: previne ativação durante resposta do assistente
    is_processing = False
    processing_start_time = 0.0
    processing_timeout = 10.0  # Timeout máximo para processamento
    
    try:
        # Envia mensagem de boas-vindas
        await websocket.send_json({
            "type": "connected",
            "message": "Wake word detection ativo",
            "models": wake_word_service.get_loaded_models(),
            "threshold": wake_word_service.threshold
        })
        logger.debug(f"✅ Mensagem de boas-vindas enviada para {client_ip}")
        
        while True:
            try:
                # Recebe dados do cliente
                data = await websocket.receive()
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "disconnect" in error_msg or "close" in error_msg or "cannot call" in error_msg:
                    logger.info(f"🔌 Conexão wake word fechada por {client_ip}")
                    break
                raise
            
            # Verifica se é mensagem de desconexão
            msg_keys = list(data.keys())
            if set(msg_keys) == {"type", "code"} or (data.get("type") == "websocket.disconnect"):
                logger.info(f"🔌 Cliente {client_ip} desconectou do wake word")
                break
            
            # Processa chunks de áudio
            if "bytes" in data:
                audio_chunk = data["bytes"]
                
                # Processa com OpenWakeWord
                try:
                    results = wake_word_service.detect(audio_chunk)
                    
                    # Verifica se detectou alguma wake word
                    for wake_word, (detected, confidence) in results.items():
                        if detected:
                            current_time = time.time()
                            
                            # 1. Filtro de confiança: exige confiança mínima configurável
                            min_confidence = max(wake_word_service.threshold, settings.wake_word_min_confidence)
                            
                            if confidence < min_confidence:
                                logger.debug(
                                    f"⚠️ Wake word '{wake_word}' detectado mas confiança baixa: "
                                    f"{confidence:.3f} < {min_confidence:.3f} - IGNORADO"
                                )
                                continue
                            
                            # 2. Verifica se está processando (evita ativação durante resposta)
                            if is_processing:
                                time_since_processing = current_time - processing_start_time
                                if time_since_processing < processing_timeout:
                                    logger.debug(
                                        f"⏸️ Wake word detectado mas sistema está processando "
                                        f"(há {time_since_processing:.2f}s) - IGNORADO"
                                    )
                                    continue
                                else:
                                    # Timeout: reseta estado de processamento
                                    is_processing = False
                                    logger.debug("⏱️ Timeout de processamento atingido, resetando estado")
                            
                            # 3. Debounce: evita múltiplas detecções seguidas
                            time_since_last = current_time - last_wake_word_time
                            
                            if time_since_last < debounce_interval:
                                logger.debug(
                                    f"⏱️ Wake word detectado mas muito recente "
                                    f"({time_since_last:.2f}s < {debounce_interval}s) - IGNORADO (debounce)"
                                )
                                continue
                            
                            # Mapeia "alexa" para "john" para compatibilidade
                            display_wake_word = wake_word
                            if wake_word == "alexa" or wake_word == "alexa_v0.1":
                                display_wake_word = "john"
                                logger.info(f"🔄 Wake word 'alexa' mapeado para 'john'")
                            
                            logger.info(
                                f"🎯 Wake word '{display_wake_word}' detectado! "
                                f"Confiança: {confidence:.3f} (threshold: {wake_word_service.threshold}, "
                                f"mínimo exigido: {min_confidence:.3f})"
                            )
                            
                            # Atualiza tempo da última detecção
                            last_wake_word_time = current_time
                            
                            # Marca que sistema está processando (previne novas ativações)
                            is_processing = True
                            processing_start_time = current_time
                            
                            # Envia notificação para cliente
                            await safe_send_json(websocket, {
                                "type": "wake_word_detected",
                                "wake_word": display_wake_word,
                                "confidence": confidence,
                                "timestamp": current_time
                            })
                            break  # Apenas uma detecção por chunk
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar chunk de áudio: {e}")
                    # Não envia erro para não interromper o fluxo
            
            elif "text" in data:
                # Mensagem de controle
                try:
                    msg = json.loads(data["text"])
                    msg_type = msg.get("type")
                    
                    if msg_type == "stop":
                        logger.info(f"Cliente {client_ip} solicitou parada do wake word")
                        break
                    elif msg_type == "ping":
                        await safe_send_json(websocket, {"type": "pong"})
                    elif msg_type == "get_status" or msg_type == "get_wake_word_stats":
                        await safe_send_json(websocket, {
                            "type": "status" if msg_type == "get_status" else "wake_word_stats",
                            "stats": wake_word_service.get_stats()
                        })
                    elif msg_type == "reset_processing":
                        # Permite resetar estado de processamento (útil para testes)
                        is_processing = False
                        logger.info(f"🔄 Estado de processamento resetado por {client_ip}")
                        await safe_send_json(websocket, {
                            "type": "processing_reset"
                        })
                    elif msg_type == "stop_wake_word":
                        logger.info(f"🛑 Cliente {client_ip} solicitou parar wake word")
                        break
                    else:
                        logger.warning(f"Tipo de mensagem desconhecido no wake word: {msg_type}")
                
                except json.JSONDecodeError:
                    logger.error("Mensagem JSON inválida no wake word")
            
            else:
                logger.warning(f"⚠️ Tipo de mensagem desconhecido no wake word: {msg_keys}")
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket wake word desconectado normalmente de {client_ip}")
    
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket wake word: {e}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        await safe_send_json(websocket, {
            "type": "error",
            "message": str(e)
        })
    
    finally:
        logger.debug(f"🔌 Conexão wake word finalizada de {client_ip}")

