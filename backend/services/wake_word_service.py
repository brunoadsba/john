"""
Serviço de detecção de wake word usando OpenWakeWord
"""
import time
import numpy as np
from typing import Dict, Optional, List, Tuple
from loguru import logger
import threading

try:
    from openwakeword import Model as OWWModel
    OWW_AVAILABLE = True
except ImportError:
    logger.warning("openwakeword não disponível, usando fallback")
    OWWModel = None
    OWW_AVAILABLE = False


class OpenWakeWordService:
    """
    Serviço de detecção de wake word usando OpenWakeWord
    
    Características:
    - Processamento em tempo real
    - Suporte a múltiplas palavras
    - Thread-safe
    - Baixa latência (<100ms)
    - 100% Open Source (Apache 2.0)
    """
    
    def __init__(
        self,
        models: Optional[List[str]] = None,
        custom_model_paths: Optional[Dict[str, str]] = None,
        inference_framework: str = "onnx",
        threshold: float = 0.5
    ):
        """
        Inicializa o serviço OpenWakeWord
        
        Args:
            models: Lista de modelos pré-treinados (ex: ["alexa", "hey_jarvis"])
            custom_model_paths: Dict com caminhos para modelos customizados
            inference_framework: Framework de inferência ("onnx" ou "tf")
            threshold: Threshold de detecção (0.0 a 1.0)
        """
        self.models = models or ["alexa"]  # Padrão: alexa
        self.custom_model_paths = custom_model_paths or {}
        self.inference_framework = inference_framework
        self.threshold = threshold
        self.oww_model = None
        self._lock = threading.Lock()
        
        logger.info(
            f"Inicializando OpenWakeWord: models={self.models}, "
            f"framework={inference_framework}, threshold={threshold}"
        )
    
    def _load_model(self):
        """Carrega o modelo OpenWakeWord (lazy loading)"""
        if self.oww_model is None:
            if not OWW_AVAILABLE or OWWModel is None:
                raise RuntimeError("openwakeword não está instalado. Execute: pip install openwakeword")
            
            with self._lock:
                if self.oww_model is None:  # Double-check locking
                    logger.info("Carregando modelo OpenWakeWord...")
                    
                    try:
                        # OpenWakeWord espera uma LISTA de strings (nomes) ou caminhos
                        # Não um dicionário!
                        wakeword_models_list = []
                        
                        # Adiciona modelos pré-treinados (nomes como strings)
                        if self.models:
                            wakeword_models_list.extend(self.models)
                        
                        # Adiciona modelos customizados (caminhos de arquivos)
                        if self.custom_model_paths:
                            # custom_model_paths é um dict {nome: caminho}
                            # Adiciona apenas os caminhos (valores do dict)
                            wakeword_models_list.extend(self.custom_model_paths.values())
                        
                        # Inicializa modelo
                        # Se lista vazia, passa None para carregar todos os modelos pré-treinados
                        self.oww_model = OWWModel(
                            wakeword_models=wakeword_models_list if wakeword_models_list else None,
                            inference_framework=self.inference_framework
                        )
                        
                        loaded_models = list(self.oww_model.models.keys())
                        logger.info(
                            f"✅ Modelo OpenWakeWord carregado com sucesso: {loaded_models}"
                        )
                    except Exception as e:
                        logger.error(f"❌ Erro ao carregar modelo OpenWakeWord: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        raise
    
    def detect(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> Dict[str, Tuple[bool, float]]:
        """
        Detecta wake words em áudio
        
        Args:
            audio_data: Bytes do áudio (WAV, 16-bit PCM) ou numpy array
            sample_rate: Taxa de amostragem (default: 16000 Hz)
            
        Returns:
            Dict com {wake_word: (detectado, confianca)}
        """
        if not OWW_AVAILABLE or OWWModel is None:
            raise RuntimeError("openwakeword não está instalado")
        
        self._load_model()
        
        try:
            # Converte bytes para numpy array se necessário
            if isinstance(audio_data, bytes):
                # Assumindo 16-bit PCM (2 bytes por amostra)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Normaliza para int16 (OpenWakeWord espera int16 ou float32 normalizado)
                # Mantém como int16 que é o formato padrão
                audio_array = audio_array.astype(np.int16)
            elif isinstance(audio_data, np.ndarray):
                audio_array = audio_data.astype(np.int16)
            else:
                raise ValueError(f"Tipo de áudio não suportado: {type(audio_data)}")
            
            # Processa com OpenWakeWord (espera numpy array)
            prediction = self.oww_model.predict(audio_array)
            
            # Extrai resultados
            results = {}
            for wake_word, confidence in prediction.items():
                detected = confidence >= self.threshold
                results[wake_word] = (detected, float(confidence))
                
                # Log apenas quando detecta
                if detected:
                    logger.info(
                        f"🎯 Wake word '{wake_word}' detectado! "
                        f"Confiança: {confidence:.3f} (threshold: {self.threshold})"
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar wake word: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def is_ready(self) -> bool:
        """Verifica se o serviço está pronto"""
        try:
            if not OWW_AVAILABLE:
                return False
            self._load_model()
            return self.oww_model is not None
        except Exception as e:
            logger.debug(f"Serviço não está pronto: {e}")
            return False
    
    def get_loaded_models(self) -> List[str]:
        """Retorna lista de modelos carregados"""
        # Carrega modelo se ainda não foi carregado
        if self.oww_model is None:
            try:
                self._load_model()
            except Exception:
                pass  # Se falhar, retorna lista vazia
        
        if self.oww_model is None:
            return []
        return list(self.oww_model.models.keys())
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do serviço"""
        return {
            "available": OWW_AVAILABLE,
            "ready": self.is_ready(),
            "models": self.get_loaded_models(),
            "threshold": self.threshold,
            "framework": self.inference_framework
        }

