"""
Validador de áudio
Validações de tamanho, formato e qualidade de áudio
"""
from fastapi import HTTPException
from loguru import logger

# Limites configuráveis
MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_AUDIO_SIZE = 100  # 100 bytes (mínimo para WAV válido)
SUPPORTED_FORMATS = ["wav", "mp3", "ogg", "flac"]
MAX_DURATION_SECONDS = 300  # 5 minutos


def validate_audio_size(audio_data: bytes) -> None:
    """
    Valida tamanho do áudio
    
    Args:
        audio_data: Bytes do áudio
    
    Raises:
        HTTPException: Se tamanho inválido
    """
    size = len(audio_data)
    
    if size < MIN_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Áudio muito pequeno ({size} bytes). Mínimo: {MIN_AUDIO_SIZE} bytes"
        )
    
    if size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Áudio muito grande ({size / 1024 / 1024:.2f} MB). Máximo: {MAX_AUDIO_SIZE / 1024 / 1024} MB"
        )


def validate_audio_format(filename: str) -> None:
    """
    Valida formato do arquivo de áudio
    
    Args:
        filename: Nome do arquivo
    
    Raises:
        HTTPException: Se formato não suportado
    """
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Nome do arquivo não fornecido"
        )
    
    extension = filename.split(".")[-1].lower() if "." in filename else ""
    
    if extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{extension}' não suportado. Formatos suportados: {', '.join(SUPPORTED_FORMATS)}"
        )


def validate_wav_header(audio_data: bytes) -> bool:
    """
    Valida header básico de arquivo WAV
    
    Args:
        audio_data: Bytes do áudio
    
    Returns:
        True se parece ser WAV válido
    """
    if len(audio_data) < 12:
        return False
    
    # Verifica assinatura "RIFF" no início
    if audio_data[:4] != b"RIFF":
        return False
    
    # Verifica "WAVE" após RIFF
    if audio_data[8:12] != b"WAVE":
        return False
    
    return True


def validate_audio(audio_data: bytes, filename: str = None) -> None:
    """
    Validação completa de áudio
    
    Args:
        audio_data: Bytes do áudio
        filename: Nome do arquivo (opcional)
    
    Raises:
        HTTPException: Se validação falhar
    """
    # Valida tamanho
    validate_audio_size(audio_data)
    
    # Valida formato se filename fornecido
    if filename:
        validate_audio_format(filename)
    
    # Valida header WAV se parece ser WAV
    if filename and filename.lower().endswith(".wav"):
        if not validate_wav_header(audio_data):
            logger.warning(f"Header WAV inválido para arquivo {filename}, mas continuando processamento")

