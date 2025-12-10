"""
Inicialização de todos os serviços da aplicação
"""
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger

from backend.config import settings
from backend.services import (
    WhisperSTTService,
    create_llm_service,
    PiperTTSService,
    OpenWakeWordService
)
from backend.database.database import Database
from backend.services.context_manager_db import ContextManagerDB
from backend.services.memory_service import MemoryService
from backend.services.feedback_service import FeedbackService
from backend.services.cleanup_service import CleanupService
from backend.core.plugin_manager import PluginManager
from backend.plugins.web_search_plugin import WebSearchPlugin
from backend.plugins.architecture_advisor_plugin import ArchitectureAdvisorPlugin
from backend.services.intent_detector import IntentDetector
from backend.services.embedding_service import EmbeddingService
from backend.services.intent_clustering_service import IntentClusteringService
from backend.api.handlers.response_cache_handler import create_response_cache


async def initialize_all_services(
    base_path: Path
) -> Tuple[
    WhisperSTTService,
    any,  # LLM Service (BaseLLMService)
    PiperTTSService,
    OpenWakeWordService,
    ContextManagerDB,
    MemoryService,
    FeedbackService,
    CleanupService,
    PluginManager,
    IntentDetector,
    Database,
    EmbeddingService,
    any,  # IntentClusteringService (opcional)
    any  # ResponseCache (opcional)
]:
    """
    Inicializa todos os serviços da aplicação
    
    Args:
        base_path: Caminho base do projeto
        
    Returns:
        Tupla com todos os serviços inicializados
    """
    logger.info("Inicializando serviços de IA...")
    
    # 1. STT Service
    stt_service = WhisperSTTService(
        model_size=settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type
    )
    
    # 2. LLM Service
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
        finetuned_model = None
        if settings.sft_enabled and settings.finetuned_model_name:
            finetuned_model = settings.finetuned_model_name
        
        llm_service = create_llm_service(
            provider="ollama",
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            finetuned_model=finetuned_model
        )
    
    # 3. TTS Service (Fase 2 - com processadores profissionais)
    tts_service = PiperTTSService(
        enable_cache=True,
        cache_size=100,
        cache_ttl=3600
    )
    
    # Pré-aquece TTS (carrega modelo e cacheia respostas comuns)
    logger.info("Pré-aquecendo TTS...")
    try:
        from backend.services.tts_cache_analyzer import TTSCacheAnalyzer
        analyzer = TTSCacheAnalyzer()
        prewarm_phrases = analyzer.get_prewarm_phrases(limit=15)
        
        for phrase in prewarm_phrases:
            try:
                await tts_service.synthesize(phrase)
            except Exception as e:
                logger.debug(f"Erro ao pré-aquecer frase '{phrase[:30]}...': {e}")
        
        logger.info(f"✅ TTS pré-aquecido com {len(prewarm_phrases)} frases")
    except Exception as e:
        logger.warning(f"Erro ao pré-aquecer TTS: {e}")
    
    # 4. Wake Word Service
    logger.info("Inicializando OpenWakeWord...")
    wake_word_service = OpenWakeWordService(
        models=settings.wake_word_models,
        custom_model_paths=settings.wake_word_custom_models,
        inference_framework=settings.wake_word_inference_framework,
        threshold=settings.wake_word_threshold
    )
    
    if wake_word_service.is_ready():
        loaded_models = wake_word_service.get_loaded_models()
        logger.info(f"✅ OpenWakeWord inicializado: modelos {loaded_models}")
    else:
        logger.warning("⚠️ OpenWakeWord não está pronto (modelo será carregado sob demanda)")
    
    # 5. Database
    logger.info("Inicializando banco de dados...")
    db_path = str(base_path / "data" / "jonh_assistant.db")
    database = Database(db_path=db_path)
    await database.connect()
    logger.info("✅ Banco de dados conectado")
    
    # 6. Context Manager
    context_manager = ContextManagerDB(
        database=database,
        max_history=10,
        session_timeout=3600
    )
    
    # 7. Memory Service
    memory_service = MemoryService(database)
    logger.info("✅ Serviço de memória inicializado")
    
    # 8. Feedback Service
    feedback_service = FeedbackService(database)
    logger.info("✅ Serviço de feedback inicializado")
    
    # 9. Cleanup Service
    cleanup_service = CleanupService(database)
    logger.info("✅ Serviço de limpeza inicializado")
    
    # 10. Plugin Manager
    plugin_manager = _initialize_plugins(llm_service)
    
    # 11. Embedding Service (para clustering - Fase 4)
    logger.info("Inicializando serviço de embeddings...")
    embedding_service = EmbeddingService()
    logger.info("✅ Serviço de embeddings inicializado")
    
    # 12. Intent Clustering Service (Fase 4)
    clustering_service = None
    if settings.clustering_enabled:
        logger.info("Inicializando serviço de clustering...")
        clustering_service = IntentClusteringService(database, embedding_service)
        logger.info("✅ Serviço de clustering inicializado")
    
    # 13. Intent Detector
    logger.info("Inicializando detector de intenção...")
    intent_detector = IntentDetector(
        llm_service=llm_service,
        embedding_service=embedding_service,
        clustering_service=clustering_service
    )
    
    # Carrega cache de clusters se disponível
    if clustering_service:
        try:
            await intent_detector.refresh_clusters_cache()
        except Exception as e:
            logger.warning(f"Erro ao carregar cache de clusters: {e}")
    
    logger.info("✅ Detector de intenção inicializado")
    
    # 14. Cache de respostas (com embedding service para busca semântica)
    response_cache = create_response_cache(embedding_service)
    
    return (
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
        response_cache
    )


def _initialize_plugins(llm_service) -> PluginManager:
    """
    Inicializa e registra plugins
    
    Args:
        llm_service: Serviço LLM para plugins que precisam
        
    Returns:
        PluginManager configurado
    """
    logger.info("Inicializando sistema de plugins...")
    
    plugin_manager = PluginManager()
    
    # Registra plugin de busca web se habilitado
    if settings.web_search_enabled:
        logger.info("Registrando plugin de busca web...")
        web_search_plugin = WebSearchPlugin(
            tavily_api_key=settings.tavily_api_key,
            prefer_tavily=settings.web_search_prefer_tavily
        )
        if plugin_manager.register(web_search_plugin):
            logger.info("✅ Plugin de busca web registrado")
        else:
            logger.warning("⚠️ Plugin de busca web não pôde ser registrado")
    
    # Registra plugin de arquitetura se habilitado
    if settings.architecture_advisor_enabled:
        logger.info("Registrando plugin de arquitetura...")
        advisor_plugin = ArchitectureAdvisorPlugin()
        if plugin_manager.register(advisor_plugin):
            logger.info("✅ Plugin de arquitetura registrado")
        else:
            logger.warning("⚠️ Plugin de arquitetura não pôde ser registrado")
    
    logger.info(f"✅ Sistema de plugins inicializado: {plugin_manager.get_plugin_count()} plugin(s) registrado(s)")
    
    return plugin_manager

