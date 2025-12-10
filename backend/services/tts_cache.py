"""
Cache para sínteses TTS frequentes
Reduz latência para respostas comuns
"""
import hashlib
from typing import Optional, Dict, List
from pathlib import Path
import json
from loguru import logger

try:
    from cachetools import TTLCache
    CACHE_TOOLS_AVAILABLE = True
except ImportError:
    CACHE_TOOLS_AVAILABLE = False
    logger.warning("cachetools não disponível - cache TTS desabilitado")


class TTSCache:
    """Cache de sínteses TTS"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        Inicializa cache TTS
        
        Args:
            max_size: Tamanho máximo do cache (número de itens)
            ttl: Time-to-live em segundos (1 hora padrão)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Optional[Dict[str, bytes]] = None
        
        if CACHE_TOOLS_AVAILABLE:
            self.cache = TTLCache(maxsize=max_size, ttl=ttl)
            logger.info(f"Cache TTS inicializado: max_size={max_size}, ttl={ttl}s")
        else:
            logger.warning("Cache TTS desabilitado (cachetools não disponível)")
    
    def _get_key(self, texto: str) -> str:
        """Gera chave do cache baseada no texto"""
        return hashlib.md5(texto.encode('utf-8')).hexdigest()
    
    def get(self, texto: str) -> Optional[bytes]:
        """
        Obtém síntese do cache
        
        Args:
            texto: Texto original
            
        Returns:
            Bytes do áudio ou None se não encontrado
        """
        if not self.cache:
            return None
        
        key = self._get_key(texto)
        audio = self.cache.get(key)
        
        if audio:
            logger.debug(f"✅ Cache hit TTS: '{texto[:50]}...'")
            return audio
        
        return None
    
    def set(self, texto: str, audio: bytes):
        """
        Armazena síntese no cache
        
        Args:
            texto: Texto original
            audio: Bytes do áudio gerado
        """
        if not self.cache:
            return
        
        key = self._get_key(texto)
        self.cache[key] = audio
        logger.debug(f"💾 Cache set TTS: '{texto[:50]}...'")
    
    def clear(self):
        """Limpa o cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache TTS limpo")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        if not self.cache:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "max_size": self.max_size,
            "ttl": self.ttl,
            "current_size": len(self.cache)
        }
    
    def prewarm(self, phrases: List[str]):
        """
        Pré-aquece cache com lista de frases
        
        Args:
            phrases: Lista de frases para pré-cache
        """
        if not self.cache:
            logger.warning("Cache não disponível para pré-aquecimento")
            return
        
        logger.info(f"Pré-aquecendo cache com {len(phrases)} frases...")
        # Nota: Pré-aquecimento real requer síntese, então isso é apenas preparação
        # O pré-aquecimento real deve ser feito chamando synthesize() para cada frase

