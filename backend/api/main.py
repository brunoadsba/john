"""
Aplicação principal FastAPI do assistente Jonh
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from datetime import datetime

from backend.config import settings
from backend.services import (
    WhisperSTTService,
    create_llm_service,
    PiperTTSService,
    ContextManager
)
from backend.api.routes import process, websocket


# Configuração do logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

# Cria aplicação FastAPI
app = FastAPI(
    title="Jonh Assistant API",
    description="API do assistente de voz local Jonh",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias globais dos serviços
stt_service = None
llm_service = None
tts_service = None
context_manager = None


@app.on_event("startup")
async def startup_event():
    """Inicializa serviços no startup da aplicação"""
    global stt_service, llm_service, tts_service, context_manager
    
    logger.info("=" * 60)
    logger.info("Iniciando Jonh Assistant API")
    logger.info("=" * 60)
    
    try:
        # Inicializa serviços
        logger.info("Inicializando serviços de IA...")
        
        stt_service = WhisperSTTService(
            model_size=settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type
        )
        
        # Cria serviço LLM baseado no provider configurado
        logger.info(f"Usando LLM provider: {settings.llm_provider}")
        
        if settings.llm_provider.lower() == "groq":
            llm_service = create_llm_service(
                provider="groq",
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
        else:  # ollama
            llm_service = create_llm_service(
                provider="ollama",
                model=settings.ollama_model,
                host=settings.ollama_host,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
        
        tts_service = PiperTTSService(
            voice=settings.piper_voice,
            model_path=settings.piper_model_path
        )
        
        context_manager = ContextManager(
            max_history=10,
            session_timeout=3600
        )
        
        # Inicializa serviços nas rotas
        process.init_services(stt_service, llm_service, tts_service, context_manager)
        websocket.init_services(stt_service, llm_service, tts_service, context_manager)
        
        logger.info("Serviços inicializados com sucesso")
        logger.info(f"Servidor rodando em {settings.host}:{settings.port}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup ao desligar a aplicação"""
    logger.info("Encerrando Jonh Assistant API...")
    
    # Limpa sessões
    if context_manager:
        for session_id in context_manager.get_all_sessions():
            context_manager.delete_session(session_id)
    
    logger.info("API encerrada")


@app.get("/", tags=["root"])
async def root():
    """Endpoint raiz"""
    return {
        "nome": "Jonh Assistant API",
        "versao": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["health"])
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


@app.get("/sessions", tags=["sessions"])
async def list_sessions():
    """Lista todas as sessões ativas"""
    if not context_manager:
        return {"sessions": []}
    
    sessions = []
    for session_id in context_manager.get_all_sessions():
        info = context_manager.get_session_info(session_id)
        if info:
            sessions.append(info)
    
    return {"sessions": sessions, "total": len(sessions)}


# Registra rotas
app.include_router(process.router)
app.include_router(websocket.router)


# Handler de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc) if settings.debug else "Erro ao processar requisição"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

