"""
Rotas REST para processamento de áudio
"""
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from typing import Optional
from loguru import logger

from backend.services import (
    WhisperSTTService,
    BaseLLMService,
    PiperTTSService,
    ContextManager
)


router = APIRouter(prefix="/api", tags=["process"])

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


@router.post("/process_audio")
async def process_audio(
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
        start_time = time.time()
        
        logger.info(f"Processando áudio: {audio.filename}")
        
        # Lê dados do áudio
        audio_data = await audio.read()
        
        # 1. Speech-to-Text
        logger.info("Etapa 1: Transcrição (STT)")
        texto_transcrito, confianca, duracao = stt_service.transcribe_audio(audio_data)
        
        if not texto_transcrito or not texto_transcrito.strip():
            raise HTTPException(
                status_code=400, 
                detail="Não foi possível transcrever o áudio. Verifique se o arquivo contém fala real e está em formato suportado (WAV, 16kHz mono recomendado)."
            )
        
        logger.info(f"Transcrito: '{texto_transcrito}'")
        
        # 2. Gerencia contexto
        if not session_id:
            session_id = context_manager.create_session()
        
        context_manager.add_message(session_id, "user", texto_transcrito)
        contexto = context_manager.get_context(session_id)
        
        # 3. LLM - Gera resposta
        logger.info("Etapa 2: Geração de resposta (LLM)")
        resposta_texto, tokens = llm_service.generate_response(
            texto_transcrito,
            contexto
        )
        
        context_manager.add_message(session_id, "assistant", resposta_texto)
        
        logger.info(f"Resposta: '{resposta_texto}'")
        
        # 4. Text-to-Speech
        logger.info("Etapa 3: Síntese de voz (TTS)")
        audio_resposta = tts_service.synthesize(resposta_texto)
        
        tempo_total = time.time() - start_time
        
        logger.info(
            f"Processamento completo em {tempo_total:.2f}s: "
            f"STT -> '{texto_transcrito}' -> LLM -> '{resposta_texto}' -> TTS"
        )
        
        # Retorna áudio com headers informativos
        return Response(
            content=audio_resposta,
            media_type="audio/wav",
            headers={
                "X-Transcription": texto_transcrito,
                "X-Response-Text": resposta_texto,
                "X-Session-ID": session_id,
                "X-Processing-Time": str(tempo_total),
                "X-Tokens-Used": str(tokens)
            }
        )
        
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
        
        audio_data = tts_service.synthesize(texto)
        
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
    info = context_manager.get_session_info(session_id)
    
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
    context_manager.delete_session(session_id)
    return {"message": "Sessão removida com sucesso"}

