"""
Rotas REST para processamento de áudio
"""
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import Response
from typing import Optional
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.api.middleware.rate_limit import get_rate_limit
from backend.api.validators.audio_validator import validate_audio

from backend.services import (
    WhisperSTTService,
    BaseLLMService,
    PiperTTSService,
    ContextManager
)
from backend.services.intent_detector import IntentDetector
from backend.config.settings import settings
from backend.api.utils.headers import sanitize_header_value
from backend.api.handlers.audio_processor import process_audio_complete
from backend.api.handlers.text_processor import process_text_complete


router = APIRouter(prefix="/api", tags=["process"])

# Rate limiter (será inicializado no main.py)
limiter: Optional[Limiter] = None


def init_rate_limiter(app_limiter: Limiter):
    """Inicializa o rate limiter"""
    global limiter
    limiter = app_limiter

# Instâncias dos serviços (serão inicializadas no startup)
stt_service: Optional[WhisperSTTService] = None
llm_service: Optional[BaseLLMService] = None
tts_service: Optional[PiperTTSService] = None
context_manager: Optional[ContextManager] = None
memory_service = None
plugin_manager = None  # Novo: PluginManager
web_search_tool = None  # Mantido para compatibilidade
intent_detector = None  # Detector de intenção para Architecture Advisor
feedback_service = None  # Serviço de feedback para coleta de dados
reward_model_service = None  # Modelo de recompensa para RLHF (opcional)
rlhf_service = None  # Serviço RLHF (opcional)
response_cache = None  # Cache de respostas (opcional)
privacy_mode_service = None  # Serviço de modo privacidade


def init_services(stt, llm, tts, ctx, memory=None, web_search=None, intent_detector_instance=None, feedback_service_instance=None, response_cache_instance=None, privacy_mode_service_instance=None):
    """
    Inicializa os serviços
    
    Args:
        stt: Serviço de STT
        llm: Serviço de LLM
        tts: Serviço de TTS
        ctx: Gerenciador de contexto
        memory: Serviço de memória
        web_search: PluginManager ou web_search_tool (compatibilidade)
        intent_detector_instance: Instância do IntentDetector
        feedback_service_instance: Instância do FeedbackService
    """
    global stt_service, llm_service, tts_service, context_manager, memory_service, plugin_manager, web_search_tool, intent_detector, feedback_service, reward_model_service, rlhf_service, response_cache, privacy_mode_service
    stt_service = stt
    llm_service = llm
    tts_service = tts
    context_manager = ctx
    memory_service = memory
    feedback_service = feedback_service_instance
    intent_detector = intent_detector_instance
    response_cache = response_cache_instance
    privacy_mode_service = privacy_mode_service_instance
    
    # Aceita PluginManager ou web_search_tool antigo (compatibilidade)
    from backend.core.plugin_manager import PluginManager
    if isinstance(web_search, PluginManager):
        plugin_manager = web_search
        # Tenta obter web_search_tool do plugin para compatibilidade
        web_search_plugin = plugin_manager.get_plugin("web_search")
        if web_search_plugin:
            web_search_tool = web_search_plugin
    else:
        # Modo antigo (compatibilidade)
        plugin_manager = None
        web_search_tool = web_search
    
    # Inicializa modelo de recompensa e RLHF (opcional)
    if settings.rlhf_enabled:
        try:
            from backend.services.reward_model_service import RewardModelService
            from backend.services.rlhf_service import RLHFService
            from pathlib import Path
            
            reward_model_path = settings.reward_model_path
            if reward_model_path and Path(reward_model_path).exists():
                logger.info(f"Carregando modelo de recompensa de: {reward_model_path}")
                reward_model_service = RewardModelService()
                reward_model_service.load_model(reward_model_path)
                rlhf_service = RLHFService(reward_model_path=reward_model_path)
                logger.info("✅ Modelo de recompensa e RLHF inicializados")
            else:
                logger.info("Modelo de recompensa não encontrado - RLHF desabilitado até treinamento")
                reward_model_service = None
                rlhf_service = None
        except Exception as e:
            logger.warning(f"Erro ao inicializar RLHF: {e} - continuando sem RLHF")
            reward_model_service = None
            rlhf_service = None
    else:
        reward_model_service = None
        rlhf_service = None


@router.post("/process_audio")
async def process_audio(
    request: Request,
    audio: UploadFile = File(..., description="Arquivo de áudio"),
    session_id: Optional[str] = Form(None, description="ID da sessão")
):
    """
    Processa áudio completo: STT -> LLM -> TTS
    
    Args:
        audio: Arquivo de áudio (WAV, MP3, etc)
        session_id: ID da sessão para manter contexto
        
    Returns:
        Áudio da resposta + metadados
    """
    try:
        logger.info(f"Processando áudio: {audio.filename}")
        
        # Lê dados do áudio
        audio_data = await audio.read()
        
        # Valida áudio
        validate_audio(audio_data, audio.filename)
        
        # Processa usando handler
        response, session_id, tempo_total = await process_audio_complete(
            stt_service=stt_service,
            llm_service=llm_service,
            tts_service=tts_service,
            context_manager=context_manager,
            memory_service=memory_service,
            plugin_manager=plugin_manager,
            web_search_tool=web_search_tool,
            reward_model_service=reward_model_service,
            rlhf_service=rlhf_service,
            feedback_service=feedback_service,
            audio_data=audio_data,
            session_id=session_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe")
async def transcribe_only(
    audio: UploadFile = File(..., description="Arquivo de áudio")
):
    """
    Apenas transcreve áudio (sem LLM ou TTS)
    
    Args:
        audio: Arquivo de áudio
        
    Returns:
        JSON com transcrição
    """
    try:
        logger.info(f"Transcrevendo áudio: {audio.filename}")
        
        audio_data = await audio.read()
        texto, confianca, duracao = stt_service.transcribe_audio(audio_data)
        
        return {
            "texto": texto,
            "confianca": confianca,
            "duracao": duracao,
            "idioma": "pt"
        }
        
    except Exception as e:
        logger.error(f"Erro na transcrição: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_text(texto: str = Form(..., description="Texto para sintetizar")):
    """
    Apenas sintetiza texto em áudio (sem STT ou LLM)
    
    Args:
        texto: Texto para converter em voz
        
    Returns:
        Áudio WAV
    """
    try:
        logger.info(f"Sintetizando texto: '{texto[:50]}...'")
        
        audio_data = await tts_service.synthesize(texto)
        
        return Response(
            content=audio_data,
            media_type="audio/wav"
        )
        
    except Exception as e:
        logger.error(f"Erro na síntese: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Obtém informações sobre uma sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Informações da sessão
    """
    info = await context_manager.get_session_info(session_id)
    
    if not info:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    return info


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Remove uma sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Confirmação
    """
    await context_manager.delete_session(session_id)
    return {"message": "Sessão removida com sucesso"}


@router.post("/process_text")
async def process_text(
    request: Request,
    texto: str = Form(..., description="Texto para processar (simula STT)"),
    session_id: Optional[str] = Form(None, description="ID da sessão"),
    system_prompt: Optional[str] = Form(None, description="System prompt customizado (para evolução)")
):
    """
    Processa texto diretamente (sem STT): LLM -> TTS
    Rate limit: 30 requisições por minuto por IP
    """
    """
    Processa texto diretamente (sem STT): LLM -> TTS
    Útil para testes sem precisar de áudio real
    Rate limit: 30 requisições por minuto por IP
    
    Args:
        texto: Texto para processar
        session_id: ID da sessão para manter contexto
        
    Returns:
        Áudio da resposta + metadados
    """
    try:
        logger.info(f"Processando texto: '{texto}'")
        
        # Processa usando handler
        response, session_id, tempo_total = await process_text_complete(
            llm_service=llm_service,
            tts_service=tts_service,
            context_manager=context_manager,
            memory_service=memory_service,
            intent_detector=intent_detector,
            plugin_manager=plugin_manager,
            web_search_tool=web_search_tool,
            reward_model_service=reward_model_service,
            rlhf_service=rlhf_service,
            feedback_service=feedback_service,
            texto=texto,
            session_id=session_id,
            system_prompt=system_prompt,
            response_cache=response_cache,
            privacy_mode_service=privacy_mode_service
        )
        
        return response
        
    except RuntimeError as e:
        # Erro de rate limit ou similar - retorna mensagem mais amigável
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            logger.warning(f"Rate limit atingido: {error_msg}")
            raise HTTPException(
                status_code=429,
                detail="Limite de requisições atingido. Por favor, tente novamente em alguns minutos. "
                       "O sistema está tentando usar fallback automático."
            )
        else:
            raise HTTPException(status_code=500, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# Funções _format_architecture_response e _create_natural_response 
# movidas para backend/api/utils/architecture_formatter.py

