"""
Serviço de Text-to-Speech usando Piper TTS com fallback para edge-tts
"""
import io
import time
from typing import Optional
from loguru import logger

# Tenta importar piper-tts (pode não estar totalmente configurado ainda)
PiperVoice = None
PiperVoiceAvailable = False

# Tenta importar edge-tts como fallback
EdgeTTSAvailable = False
try:
    import edge_tts
    EdgeTTSAvailable = True
    logger.info("edge-tts importado com sucesso (fallback TTS)")
except ImportError:
    logger.warning("edge-tts não disponível - será usado mock se Piper também não estiver disponível")

try:
    # Tenta diferentes formas de importar piper-tts
    try:
        from piper_tts import PiperVoice
        PiperVoiceAvailable = True
        logger.info("piper-tts importado com sucesso (piper_tts)")
    except ImportError:
        try:
            from piper import PiperVoice
            PiperVoiceAvailable = True
            logger.info("piper-tts importado com sucesso (piper)")
        except ImportError:
            try:
                import piper_tts
                PiperVoice = getattr(piper_tts, 'PiperVoice', None)
                if PiperVoice:
                    PiperVoiceAvailable = True
                    logger.info("piper-tts importado com sucesso (getattr)")
            except ImportError:
                pass
    
    if not PiperVoiceAvailable:
        if EdgeTTSAvailable:
            logger.info("piper-tts não disponível, usando edge-tts como fallback")
        else:
            logger.warning("piper-tts não disponível, usando mock")
except Exception as e:
    logger.warning(f"piper-tts não disponível: {e}")
    if EdgeTTSAvailable:
        logger.info("Usando edge-tts como fallback")


class PiperTTSService:
    """Serviço de síntese de voz usando Piper TTS"""
    
    def __init__(
        self,
        voice: str = "pt_BR-faber-medium",
        model_path: Optional[str] = None,
        enable_cache: bool = True,
        cache_size: int = 100,
        cache_ttl: int = 3600
    ):
        """
        Inicializa o serviço Piper TTS
        
        Args:
            voice: Nome da voz (ex: pt_BR-faber-medium)
            model_path: Caminho para os modelos (opcional)
            enable_cache: Habilita cache de sínteses
            cache_size: Tamanho do cache
            cache_ttl: TTL do cache em segundos
        """
        self.voice_name = voice
        self.model_path = model_path
        self.voice = None
        
        # Inicializa cache TTS
        self.cache = None
        if enable_cache:
            try:
                from backend.services.tts_cache import TTSCache
                self.cache = TTSCache(max_size=cache_size, ttl=cache_ttl)
            except Exception as e:
                logger.warning(f"Cache TTS não disponível: {e}")
        
        logger.info(f"Inicializando Piper TTS: voice={voice}, cache={'enabled' if self.cache else 'disabled'}")
    
    def _load_voice(self):
        """Carrega a voz Piper (lazy loading) ou edge-tts como fallback"""
        if self.voice is None:
            if not PiperVoiceAvailable or PiperVoice is None:
                # Piper não está instalado, tenta edge-tts
                if EdgeTTSAvailable:
                    logger.info("Usando edge-tts como fallback (vozes naturais pt-BR)")
                    self.voice = "edge-tts"  # Marca como edge-tts
                    return
                else:
                    logger.warning("Nenhum TTS disponível, usando mock")
                    self.voice = "mock"  # Marca como mock
                    return
            
            logger.info(f"Carregando voz Piper: {self.voice_name}...")
            
            try:
                # Tenta carregar a voz
                # Nota: A implementação real depende de como você instalou o Piper
                # Este é um exemplo simplificado
                self.voice = self._create_voice_instance()
                logger.info("Voz Piper carregada com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao carregar voz: {e}")
                # Em caso de erro, tenta edge-tts
                if EdgeTTSAvailable:
                    logger.warning("Usando edge-tts como fallback devido ao erro")
                    self.voice = "edge-tts"
                else:
                    logger.warning("Usando síntese mock devido ao erro")
                    self.voice = "mock"
    
    def _create_voice_instance(self):
        """
        Cria instância da voz Piper
        
        Returns:
            Instância da voz ou None se não disponível
        """
        # Implementação simplificada para MVP
        # Na versão completa, você carregaria o modelo ONNX da voz
        logger.warning("Usando implementação simplificada do Piper TTS")
        return "mock_voice"  # Placeholder para MVP
    
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
            
            # Verifica cache primeiro
            if self.cache:
                cached_audio = self.cache.get(texto)
                if cached_audio:
                    tempo_cache = time.time() - start_time
                    logger.info(
                        f"✅ TTS do cache em {tempo_cache:.3f}s: '{texto[:50]}...'"
                    )
                    return cached_audio
            
            # Carrega voz se necessário (não levanta erro se usar mock)
            self._load_voice()
            
            logger.info(f"Sintetizando texto: '{texto[:50]}...'")
            
            # Verifica qual TTS usar
            if self.voice == "edge-tts" or (not PiperVoiceAvailable and EdgeTTSAvailable):
                # Usa edge-tts (vozes naturais) - método assíncrono
                audio_bytes = await self._synthesize_edge_tts(texto)
            elif self.voice == "mock" or not EdgeTTSAvailable:
                # Usa síntese mock (silêncio)
                audio_bytes = self._synthesize_mock(texto)
            else:
                # Usa Piper real (implementação futura)
                # audio_bytes = self.voice.synthesize(texto)
                audio_bytes = await self._synthesize_edge_tts(texto) if EdgeTTSAvailable else self._synthesize_mock(texto)
            
            tempo_processamento = time.time() - start_time
            logger.info(
                f"Síntese concluída em {tempo_processamento:.2f}s "
                f"({len(audio_bytes)} bytes)"
            )
            
            # Armazena no cache
            if self.cache:
                self.cache.set(texto, audio_bytes)
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Erro na síntese de voz: {e}")
            # Em caso de erro, tenta edge-tts, senão mock
            if EdgeTTSAvailable:
                logger.warning("Tentando edge-tts como fallback devido ao erro")
                try:
                    return await self._synthesize_edge_tts(texto)
                except Exception as e2:
                    logger.error(f"Erro no edge-tts: {e2}")
            logger.warning("Retornando áudio mock devido ao erro")
            return self._synthesize_mock(texto)
    
    async def _synthesize_edge_tts(self, texto: str) -> bytes:
        """
        Síntese usando edge-tts (vozes naturais Microsoft) - método assíncrono
        
        Args:
            texto: Texto a sintetizar
            
        Returns:
            Bytes de áudio WAV (convertido de MP3)
        """
        import edge_tts
        import tempfile
        import os
        
        # Vozes pt-BR disponíveis no edge-tts
        # pt-BR-FranciscaNeural (feminina) ou pt-BR-AntonioNeural (masculina)
        voice = "pt-BR-AntonioNeural"  # Voz masculina brasileira
        
        try:
            # Gera áudio usando edge-tts (já estamos em contexto async)
            communicate = edge_tts.Communicate(texto, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            # edge-tts retorna MP3, precisa converter para WAV
            mp3_data = audio_data
            
            # Converte MP3 para WAV usando pydub (se disponível) ou ffmpeg
            try:
                from pydub import AudioSegment
                from pydub.utils import which
                
                # Carrega MP3 do buffer
                audio_segment = AudioSegment.from_mp3(io.BytesIO(mp3_data))
                
                # Converte para WAV (16kHz mono para compatibilidade)
                audio_segment = audio_segment.set_frame_rate(22050).set_channels(1)
                
                # Exporta para WAV
                buffer = io.BytesIO()
                audio_segment.export(buffer, format="wav")
                buffer.seek(0)
                wav_data = buffer.read()
                
                logger.info(f"Áudio convertido de MP3 para WAV: {len(mp3_data)} → {len(wav_data)} bytes")
                return wav_data
                
            except ImportError:
                # Se pydub não estiver disponível, tenta usar ffmpeg diretamente
                logger.warning("pydub não disponível, tentando converter com ffmpeg")
                return self._convert_mp3_to_wav_ffmpeg(mp3_data)
            
        except Exception as e:
            logger.error(f"Erro no edge-tts: {e}")
            # Fallback para mock em caso de erro
            return self._synthesize_mock(texto)
    
    def _convert_mp3_to_wav_ffmpeg(self, mp3_data: bytes) -> bytes:
        """
        Converte MP3 para WAV usando ffmpeg via subprocess
        
        Args:
            mp3_data: Bytes do MP3
            
        Returns:
            Bytes do WAV
        """
        import subprocess
        import tempfile
        
        try:
            # Salva MP3 temporário
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                mp3_file.write(mp3_data)
                mp3_path = mp3_file.name
            
            # Converte para WAV usando ffmpeg
            wav_path = mp3_path.replace('.mp3', '.wav')
            subprocess.run(
                [
                    'ffmpeg', '-i', mp3_path,
                    '-ar', '22050',  # Sample rate
                    '-ac', '1',      # Mono
                    '-f', 'wav',
                    '-y',            # Sobrescrever
                    wav_path
                ],
                check=True,
                capture_output=True
            )
            
            # Lê WAV gerado
            with open(wav_path, 'rb') as wav_file:
                wav_data = wav_file.read()
            
            # Limpa arquivos temporários
            try:
                os.unlink(mp3_path)
                os.unlink(wav_path)
            except:
                pass
            
            return wav_data
            
        except Exception as e:
            logger.error(f"Erro ao converter MP3 para WAV: {e}")
            # Se falhar, retorna MP3 mesmo (just_audio pode suportar)
            return mp3_data
    
    def _synthesize_mock(self, texto: str) -> bytes:
        """
        Síntese mock para MVP (retorna silêncio)
        
        Args:
            texto: Texto a sintetizar
            
        Returns:
            Bytes de áudio WAV com silêncio
        """
        import wave
        import numpy as np
        
        # Gera 2 segundos de silêncio como placeholder
        sample_rate = 22050
        duration = 2.0
        samples = int(sample_rate * duration)
        
        # Cria array de silêncio
        audio_data = np.zeros(samples, dtype=np.int16)
        
        # Converte para WAV
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        buffer.seek(0)
        return buffer.read()
    
    def is_ready(self) -> bool:
        """Verifica se o serviço está pronto"""
        try:
            # Para MVP, sempre retorna True (usando mock)
            return True
            
        except Exception as e:
            logger.error(f"Serviço TTS não está pronto: {e}")
            return False


class PiperTTSServiceReal(PiperTTSService):
    """
    Implementação real do Piper TTS
    
    Esta classe será usada quando os modelos estiverem instalados.
    Para o MVP, usamos a versão mock acima.
    """
    
    def _create_voice_instance(self):
        """Carrega modelo ONNX real do Piper"""
        # Implementação completa virá quando instalarmos os modelos
        pass

