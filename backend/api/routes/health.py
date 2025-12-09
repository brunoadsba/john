"""
Rotas de health check
"""
from datetime import datetime
from fastapi import APIRouter
from loguru import logger

from backend.config import settings

router = APIRouter(tags=["health"])

# Instâncias dos serviços (serão inicializadas no startup)
stt_service = None
llm_service = None
tts_service = None
context_manager = None


def init_health_services(stt, llm, tts, ctx):
    """Inicializa serviços para health check"""
    global stt_service, llm_service, tts_service, context_manager
    stt_service = stt
    llm_service = llm
    tts_service = tts
    context_manager = ctx


@router.get("/health")
async def health_check():
    """
    Health check da aplicação
    
    Verifica status de todos os serviços
    """
    servicos_status = {
        "stt": "offline",
        "llm": "offline",
        "tts": "offline",
        "context": "offline"
    }
    
    try:
        if stt_service and stt_service.is_ready():
            servicos_status["stt"] = "online"
    except Exception as e:
        logger.error(f"STT health check falhou: {e}")
    
    try:
        if llm_service and llm_service.is_ready():
            servicos_status["llm"] = "online"
    except Exception as e:
        logger.error(f"LLM health check falhou: {e}")
    
    try:
        if tts_service and tts_service.is_ready():
            servicos_status["tts"] = "online"
    except Exception as e:
        logger.error(f"TTS health check falhou: {e}")
    
    if context_manager:
        servicos_status["context"] = "online"
    
    # Determina status geral
    all_online = all(status == "online" for status in servicos_status.values())
    status_geral = "healthy" if all_online else "degraded"
    
    return {
        "status": status_geral,
        "versao": "1.0.0",
        "servicos": servicos_status,
        "timestamp": datetime.now().isoformat(),
        "configuracao": {
            "whisper_model": settings.whisper_model,
            "ollama_model": settings.ollama_model,
            "piper_voice": settings.piper_voice
        }
    }

