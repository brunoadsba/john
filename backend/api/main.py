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
from backend.api.routes import process, websocket, web_interface, feedback, health, analytics, streaming, conversations, location, privacy
from backend.api.routes.errors import router as errors_router, init_error_services
from backend.api.middleware.rate_limit import setup_rate_limiting
from backend.api.startup.services_initializer import initialize_all_services


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

# Configuração de Rate Limiting
app_limiter = setup_rate_limiting(app)

# Instâncias globais dos serviços
stt_service = None
llm_service = None
tts_service = None
wake_word_service = None
context_manager = None
cleanup_service = None
feedback_service = None
conversation_history_service = None


@app.on_event("startup")
async def startup_event():
    """Inicializa serviços no startup da aplicação"""
    global stt_service, llm_service, tts_service, wake_word_service, context_manager
    global database, memory_service, cleanup_service, feedback_service
    global conversation_history_service, geocoding_service, privacy_mode_service
    global privacy_mode_service
    
    logger.info("=" * 60)
    logger.info("Iniciando Jonh Assistant API")
    logger.info("=" * 60)
    
    try:
        # Inicializa todos os serviços
        base_path = Path(__file__).parent.parent.parent
        (
            stt_service,
            llm_service,
            tts_service,
            wake_word_service,
            context_manager,
            memory_service,
            feedback_service,
            cleanup_service,
            plugin_manager,
            intent_detector,
            database,
            embedding_service,
            clustering_service,
            response_cache,
            conversation_history_service,
            geocoding_service,
            privacy_mode_service
        ) = await initialize_all_services(base_path)
        
        # Inicializa serviços nas rotas
        process.init_services(stt_service, llm_service, tts_service, context_manager, memory_service, plugin_manager, intent_detector, feedback_service, response_cache, privacy_mode_service)
        process.init_rate_limiter(app_limiter)
        websocket.init_services(stt_service, llm_service, tts_service, wake_word_service, context_manager, memory_service, plugin_manager, feedback_service, privacy_mode_service)
        web_interface.init_services(stt_service, llm_service, tts_service, context_manager, memory_service)
        feedback.init_feedback_service(feedback_service)
        health.init_health_services(stt_service, llm_service, tts_service, context_manager, plugin_manager, memory_service, response_cache)
        analytics.init_analytics_services(database, embedding_service)
        init_error_services(database)
        streaming.init_services(llm_service, context_manager, memory_service, plugin_manager, intent_detector, response_cache, privacy_mode_service)
        conversations.init_services(conversation_history_service, context_manager)
        location.init_services(context_manager, geocoding_service)
        privacy.init_privacy_service(privacy_mode_service)
        
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
    
    # Limpa sessões expiradas
    if context_manager:
        await context_manager.cleanup_expired_sessions()
    
    # Executa limpeza automática
    if cleanup_service:
        try:
            await cleanup_service.cleanup_all()
        except Exception as e:
            logger.warning(f"Erro na limpeza automática: {e}")
    
    # Fecha banco de dados
    if database:
        await database.close()
        logger.info("Banco de dados fechado")
    
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
app.include_router(web_interface.router)
app.include_router(feedback.router)
app.include_router(health.router)
app.include_router(analytics.router)
app.include_router(streaming.router)
app.include_router(conversations.router)
app.include_router(location.router)
app.include_router(privacy.router)
app.include_router(errors_router)


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

