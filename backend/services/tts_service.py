"""
Serviço de Text-to-Speech usando Piper TTS com fallback para edge-tts
Fase 2: Integração com processadores de texto profissionais
"""
import io
import time
from typing import Optional
from loguru import logger

from backend.config.settings import settings

# Tenta importar módulos novos (Fase 2)
try:
    from backend.services.tts import (
        PiperTTSService as NewPiperTTSService,
        TTSTextProcessor,
        TTSPronunciationDict,
        TTSSSMLProcessor,
    )
    TTS_MODULES_AVAILABLE = True
except ImportError:
    TTS_MODULES_AVAILABLE = False
    logger.warning("Módulos TTS Fase 2 não disponíveis, usando implementação legada")

# Tenta importar edge-tts como fallback
EdgeTTSAvailable = False
try:
    import edge_tts
    EdgeTTSAvailable = True
except ImportError:
    logger.warning("edge-tts não disponível")


class PiperTTSService:
    """
    Serviço de síntese de voz usando Piper TTS (Fase 2).
    
    Integra processadores de texto profissionais:
    - Normalização (nf-tts-normalizer)
    - Dicionário de pronúncia
    - SSML básico
    """
    
    def __init__(
        self,
        voice: Optional[str] = None,
        model_path: Optional[str] = None,
        enable_cache: bool = True,
        cache_size: int = 100,
        cache_ttl: int = 3600
    ):
        """
        Inicializa o serviço TTS
        
        Args:
            voice: Nome da voz (legado, não usado na Fase 2)
            model_path: Caminho para modelo (legado)
            enable_cache: Habilita cache de sínteses
            cache_size: Tamanho do cache
            cache_ttl: TTL do cache em segundos
        """
        # Inicializa cache TTS
        self.cache = None
        if enable_cache:
            try:
                from backend.services.tts_cache import TTSCache
                self.cache = TTSCache(max_size=cache_size, ttl=cache_ttl)
            except Exception as e:
                logger.warning(f"Cache TTS não disponível: {e}")
        
        # Inicializa processadores (Fase 2)
        self.text_processor = None
        self.pronunciation_dict = None
        self.ssml_processor = None
        self.piper_service = None
        
        if TTS_MODULES_AVAILABLE:
            try:
                self.text_processor = TTSTextProcessor(
                    enable_numbers=settings.tts_enable_numbers,
                    enable_dates=settings.tts_enable_dates
                )
                self.pronunciation_dict = TTSPronunciationDict(
                    dict_path=settings.tts_pronunciation_dict_path
                )
                self.ssml_processor = TTSSSMLProcessor(
                    enable_pauses=settings.tts_enable_ssml
                )
                
                # Inicializar Piper TTS se engine configurado
                if settings.tts_engine == "piper":
                    try:
                        self.piper_service = NewPiperTTSService(
                            model_path=settings.tts_model_path,
                            config_path=settings.tts_config_path,
                            use_cuda=settings.tts_use_cuda
                        )
                        logger.info("✅ Piper TTS Fase 2 inicializado")
                    except Exception as e:
                        logger.warning(f"Piper TTS não disponível: {e}, usando edge-tts como fallback")
                        self.piper_service = None
                
                logger.info("Processadores TTS Fase 2 inicializados")
            except Exception as e:
                logger.warning(f"Erro ao inicializar processadores Fase 2: {e}")
        
        logger.info(f"TTS Service inicializado (engine: {settings.tts_engine})")
    
    async def synthesize(self, texto: str) -> bytes:
        """
        Sintetiza texto em áudio (método assíncrono)
        
        Args:
            texto: Texto para converter em voz
            
        Returns:
            Bytes do áudio WAV gerado
        """
        try:
            start_time = time.time()
            
            # Processar texto (Fase 2)
            texto_processado = texto
            if self.text_processor:
                texto_processado = self.text_processor.process(texto_processado)
            
            if self.pronunciation_dict:
                texto_processado = self.pronunciation_dict.apply(texto_processado)
            
            if self.ssml_processor:
                texto_processado = self.ssml_processor.process(texto_processado)
            
            # Verifica cache com texto processado
            if self.cache:
                cached_audio = self.cache.get(texto_processado)
                if cached_audio:
                    tempo_cache = time.time() - start_time
                    logger.info(f"✅ TTS do cache em {tempo_cache:.3f}s")
                    return cached_audio
            
            logger.info(f"Sintetizando texto: '{texto[:50]}...'")
            
            # Usar Piper TTS se disponível
            if self.piper_service and self.piper_service.is_ready():
                audio_bytes = await self.piper_service.synthesize(texto_processado)
            elif EdgeTTSAvailable:
                # Fallback para edge-tts
                audio_bytes = await self._synthesize_edge_tts(texto_processado)
            else:
                # Fallback para mock
                audio_bytes = self._synthesize_mock(texto_processado)
            
            tempo_processamento = time.time() - start_time
            logger.info(f"Síntese concluída em {tempo_processamento:.2f}s ({len(audio_bytes)} bytes)")
            
            # Armazena no cache
            if self.cache:
                self.cache.set(texto_processado, audio_bytes)
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Erro na síntese de voz: {e}")
            # Fallback gracioso
            if EdgeTTSAvailable:
                try:
                    return await self._synthesize_edge_tts(texto)
                except Exception as e2:
                    logger.error(f"Erro no edge-tts: {e2}")
            return self._synthesize_mock(texto)
    
    async def _synthesize_edge_tts(self, texto: str) -> bytes:
        """Síntese usando edge-tts (fallback)"""
        import edge_tts
        
        voice = "pt-BR-AntonioNeural"
        
        try:
            communicate = edge_tts.Communicate(texto, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            # Converte MP3 para WAV
            try:
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
                audio_segment = audio_segment.set_frame_rate(22050).set_channels(1)
                buffer = io.BytesIO()
                audio_segment.export(buffer, format="wav")
                buffer.seek(0)
                return buffer.read()
            except ImportError:
                logger.warning("pydub não disponível, retornando MP3")
                return audio_data
        except Exception as e:
            logger.error(f"Erro no edge-tts: {e}")
            return self._synthesize_mock(texto)
    
    def _synthesize_mock(self, texto: str) -> bytes:
        """Síntese mock (silêncio)"""
        import wave
        import numpy as np
        
        sample_rate = 22050
        duration = 2.0
        samples = int(sample_rate * duration)
        audio_data = np.zeros(samples, dtype=np.int16)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        buffer.seek(0)
        return buffer.read()
    
    def is_ready(self) -> bool:
        """Verifica se o serviço está pronto"""
        return self.piper_service is not None or EdgeTTSAvailable
