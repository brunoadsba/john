"""
Serviço de Speech-to-Text usando Faster Whisper
"""
import io
import time
from typing import Tuple
from loguru import logger
import soundfile as sf
import numpy as np

try:
    from faster_whisper import WhisperModel
except ImportError:
    logger.warning("faster-whisper não disponível, usando fallback")
    WhisperModel = None


class WhisperSTTService:
    """Serviço de transcrição de áudio usando Whisper"""
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Inicializa o serviço Whisper
        
        Args:
            model_size: Tamanho do modelo (tiny, base, small, medium, large)
            device: Dispositivo (cpu, cuda)
            compute_type: Tipo de computação (int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
        logger.info(f"Inicializando Whisper STT: model={model_size}, device={device}")
        
    def _load_model(self):
        """Carrega o modelo Whisper (lazy loading)"""
        if self.model is None:
            if WhisperModel is None:
                raise RuntimeError("faster-whisper não está instalado")
            
            logger.info("Carregando modelo Whisper...")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Modelo Whisper carregado com sucesso")
    
    def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "pt"
    ) -> Tuple[str, float, float]:
        """
        Transcreve áudio para texto
        
        Args:
            audio_data: Dados do áudio em bytes
            language: Código do idioma (pt, en, etc)
            
        Returns:
            Tupla (texto, confiança, duração)
        """
        try:
            start_time = time.time()
            
            # Carrega modelo se necessário
            self._load_model()
            
            # Converte bytes para array numpy
            audio_array, sample_rate = self._bytes_to_audio(audio_data)
            
            # Calcula duração
            duracao = len(audio_array) / sample_rate
            
            # Transcreve
            logger.info(f"Transcrevendo áudio ({duracao:.2f}s)...")
            segments, info = self.model.transcribe(
                audio_array,
                language=language,
                beam_size=5,
                vad_filter=True
            )
            
            # Extrai texto dos segmentos
            texto_completo = " ".join([segment.text for segment in segments])
            
            # Calcula confiança média
            confianca = info.language_probability
            
            tempo_processamento = time.time() - start_time
            logger.info(
                f"Transcrição concluída em {tempo_processamento:.2f}s: '{texto_completo[:50]}...'"
            )
            
            return texto_completo.strip(), confianca, duracao
            
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            raise
    
    def _bytes_to_audio(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """
        Converte bytes de áudio para array numpy
        
        Args:
            audio_data: Dados do áudio em bytes
            
        Returns:
            Tupla (array numpy, sample rate)
        """
        try:
            # Tenta ler como arquivo de áudio
            audio_io = io.BytesIO(audio_data)
            audio_array, sample_rate = sf.read(audio_io)
            
            # Converte para mono se necessário
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)
            
            # Converte para float32
            audio_array = audio_array.astype(np.float32)
            
            return audio_array, sample_rate
            
        except Exception as e:
            logger.error(f"Erro ao converter áudio: {e}")
            raise ValueError(f"Formato de áudio inválido: {e}")
    
    def is_ready(self) -> bool:
        """Verifica se o serviço está pronto"""
        try:
            self._load_model()
            return self.model is not None
        except Exception as e:
            logger.error(f"Serviço STT não está pronto: {e}")
            return False

