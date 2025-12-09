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
            model_size: Tamanho do modelo (tiny, base, small, medium, large, large-v2, large-v3)
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
            
            # Configurações de transcrição
            # Desabilita VAD filter para áudios curtos (pode estar cortando fala)
            use_vad = duracao > 1.0
            
            # Otimização: reduz beam_size de 5 para 3 (mais rápido, qualidade similar)
            # Desabilita VAD para áudios < 2s (melhor para comandos curtos)
            beam_size = 3  # Reduzido de 5 para melhor performance
            use_vad_optimized = duracao > 2.0  # Aumentado threshold de 1.0s para 2.0s
            
            segments, info = self.model.transcribe(
                audio_array,
                language=language,
                beam_size=beam_size,
                vad_filter=use_vad_optimized,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    threshold=0.5
                ) if use_vad_optimized else None
            )
            
            # Extrai texto dos segmentos
            segmentos_lista = list(segments)
            logger.debug(f"📊 Segmentos detectados: {len(segmentos_lista)}")
            
            if len(segmentos_lista) > 0:
                for i, seg in enumerate(segmentos_lista):
                    logger.debug(f"  Segmento {i+1}: '{seg.text}' (confiança: {seg.no_speech_prob:.2f}, tempo: {seg.start:.2f}-{seg.end:.2f}s)")
            
            texto_completo = " ".join([segment.text for segment in segmentos_lista])
            
            # Calcula confiança média
            confianca = info.language_probability
            
            tempo_processamento = time.time() - start_time
            
            # Log detalhado
            if texto_completo.strip():
                logger.info(
                    f"✅ Transcrição concluída em {tempo_processamento:.2f}s: '{texto_completo[:100]}' "
                    f"(confiança: {confianca:.2f}, segmentos: {len(segmentos_lista)})"
                )
            else:
                logger.warning(
                    f"⚠️ Transcrição vazia em {tempo_processamento:.2f}s "
                    f"(confiança: {confianca:.2f}, segmentos: {len(segmentos_lista)}, duração: {duracao:.2f}s)"
                )
                # Log informações adicionais para debug
                if len(segmentos_lista) > 0:
                    logger.debug(f"   Primeiro segmento: no_speech_prob={segmentos_lista[0].no_speech_prob:.2f}")
            
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
            # Log detalhado do áudio recebido
            logger.debug(f"📊 Áudio recebido: {len(audio_data)} bytes")
            
            # Tenta ler como arquivo de áudio
            audio_io = io.BytesIO(audio_data)
            audio_array, sample_rate = sf.read(audio_io)
            
            # Log informações do áudio
            logger.info(f"📊 Áudio decodificado: shape={audio_array.shape}, sample_rate={sample_rate}Hz, dtype={audio_array.dtype}")
            
            # Converte para mono se necessário
            if len(audio_array.shape) > 1:
                logger.debug(f"📊 Convertendo de {audio_array.shape[1]} canais para mono")
                audio_array = audio_array.mean(axis=1)
            
            # Converte para float32
            audio_array = audio_array.astype(np.float32)
            
            # Calcula estatísticas do áudio
            duration = len(audio_array) / sample_rate
            max_amplitude = np.abs(audio_array).max()
            mean_amplitude = np.abs(audio_array).mean()
            rms = np.sqrt(np.mean(audio_array**2))
            
            logger.info(
                f"📊 Estatísticas do áudio: "
                f"duração={duration:.2f}s, "
                f"max_amp={max_amplitude:.4f}, "
                f"mean_amp={mean_amplitude:.4f}, "
                f"rms={rms:.4f}"
            )
            
            # Verifica se o áudio tem conteúdo suficiente
            if duration < 0.5:
                logger.warning(f"⚠️ Áudio muito curto: {duration:.2f}s (mínimo recomendado: 0.5s)")
            
            if max_amplitude < 0.01:
                logger.warning(f"⚠️ Áudio muito baixo: max_amplitude={max_amplitude:.4f} (pode estar silencioso)")
            
            if rms < 0.001:
                logger.warning(f"⚠️ RMS muito baixo: {rms:.4f} (áudio pode estar sem fala)")
            
            return audio_array, sample_rate
            
        except Exception as e:
            logger.error(f"Erro ao converter áudio: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            raise ValueError(f"Formato de áudio inválido: {e}")
    
    def is_ready(self) -> bool:
        """Verifica se o serviço está pronto"""
        try:
            if WhisperModel is None:
                logger.warning("faster-whisper não está instalado")
                return False
            self._load_model()
            return self.model is not None
        except Exception as e:
            logger.error(f"Serviço STT não está pronto: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

