"""
Rotas de health check
"""
from datetime import datetime
from fastapi import APIRouter
from loguru import logger
from typing import Optional, Any

from backend.config import settings

router = APIRouter(tags=["health"])

# Instâncias dos serviços (serão inicializadas no startup)
stt_service = None
llm_service = None
tts_service = None
context_manager = None
plugin_manager = None
memory_service = None
response_cache = None


def init_health_services(stt, llm, tts, ctx, plugins=None, memory=None, cache=None):
    """Inicializa serviços para health check"""
    global stt_service, llm_service, tts_service, context_manager
    global plugin_manager, memory_service, response_cache
    stt_service = stt
    llm_service = llm
    tts_service = tts
    context_manager = ctx
    plugin_manager = plugins
    memory_service = memory
    response_cache = cache


@router.get("/health")
async def health_check():
    """
    Health check da aplicação
    
    Verifica status de todos os serviços, plugins e componentes
    """
    servicos_status = {
        "stt": "offline",
        "llm": "offline",
        "tts": "offline",
        "context": "offline"
    }
    
    # Verifica STT
    try:
        if stt_service and stt_service.is_ready():
            servicos_status["stt"] = "online"
    except Exception as e:
        logger.error(f"STT health check falhou: {e}")
    
    # Verifica LLM
    try:
        if llm_service and llm_service.is_ready():
            servicos_status["llm"] = "online"
            llm_provider = getattr(llm_service, 'provider', 'unknown')
            llm_model = getattr(llm_service, 'model', 'unknown')
        else:
            llm_provider = None
            llm_model = None
    except Exception as e:
        logger.error(f"LLM health check falhou: {e}")
        llm_provider = None
        llm_model = None
    
    # Verifica TTS
    try:
        if tts_service and tts_service.is_ready():
            servicos_status["tts"] = "online"
    except Exception as e:
        logger.error(f"TTS health check falhou: {e}")
    
    # Verifica Context Manager
    if context_manager:
        servicos_status["context"] = "online"
        active_sessions = len(getattr(context_manager, 'sessions', {}))
    else:
        active_sessions = 0
    
    # Verifica Plugins
    plugins_info = {}
    if plugin_manager:
        plugins_info = {
            "total": plugin_manager.get_plugin_count(),
            "plugins": plugin_manager.list_plugins(),
            "tools": len(plugin_manager.get_tool_definitions())
        }
    
    # Verifica Memory Service
    memory_info = {}
    if memory_service:
        try:
            # Tenta obter estatísticas de memória
            memory_info = {
                "enabled": True,
                "stats": getattr(memory_service, 'get_stats', lambda: {})()
            }
        except:
            memory_info = {"enabled": True}
    
    # Verifica Response Cache
    cache_info = {}
    if response_cache:
        try:
            cache_size = len(getattr(response_cache, 'cache', {}))
            cache_info = {
                "enabled": True,
                "size": cache_size,
                "max_size": getattr(response_cache, 'max_size', 0)
            }
        except:
            cache_info = {"enabled": True}
    
    # Determina status geral (crítico se STT ou LLM offline)
    critical_services_online = (
        servicos_status.get("stt") == "online" and
        servicos_status.get("llm") == "online"
    )
    
    if critical_services_online and servicos_status.get("tts") == "online":
        status_geral = "healthy"
    elif critical_services_online:
        status_geral = "degraded"  # TTS offline mas críticos online
    else:
        status_geral = "unhealthy"  # STT ou LLM offline
    
    return {
        "status": status_geral,
        "versao": "1.0.0",
        "servicos": servicos_status,
        "timestamp": datetime.now().isoformat(),
        "configuracao": {
            "llm_provider": settings.llm_provider,
            "llm_model": llm_model or settings.ollama_model or "unknown",
            "whisper_model": settings.whisper_model,
            "tts_engine": settings.tts_engine,
            "piper_voice": settings.piper_voice
        },
        "plugins": plugins_info,
        "memoria": memory_info,
        "cache": cache_info,
        "sessoes_ativas": active_sessions
    }

