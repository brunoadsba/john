"""
Cache inteligente de respostas usando embeddings
Cacheia respostas para perguntas similares
"""
import hashlib
from typing import Optional, Dict, Tuple, Any
from loguru import logger

try:
    from cachetools import TTLCache
    CACHE_TOOLS_AVAILABLE = True
except ImportError:
    CACHE_TOOLS_AVAILABLE = False
    logger.warning("cachetools não disponível - cache de respostas desabilitado")


class ResponseCache:
    """Cache inteligente de respostas do LLM"""
    
    def __init__(
        self,
        max_size: int = 500,
        ttl: int = 7200,
        embedding_service: Optional[Any] = None
    ):
        """
        Inicializa cache de respostas
        
        Args:
            max_size: Tamanho máximo do cache
            ttl: Time-to-live em segundos (2 horas padrão)
            embedding_service: Serviço de embeddings para busca semântica (opcional)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.embedding_service = embedding_service
        self.cache: Optional[Dict[str, Dict[str, Any]]] = None
        
        if CACHE_TOOLS_AVAILABLE:
            self.cache = TTLCache(maxsize=max_size, ttl=ttl)
            logger.info(f"Cache de respostas inicializado: max_size={max_size}, ttl={ttl}s")
        else:
            logger.warning("Cache de respostas desabilitado (cachetools não disponível)")
    
    def _get_key(self, texto: str) -> str:
        """Gera chave do cache baseada no texto"""
        # Normaliza texto (lowercase, remove espaços extras)
        texto_normalizado = " ".join(texto.lower().split())
        return hashlib.md5(texto_normalizado.encode('utf-8')).hexdigest()
    
    def get(self, texto: str) -> Optional[Tuple[str, int]]:
        """
        Obtém resposta do cache
        
        Args:
            texto: Texto da pergunta
            
        Returns:
            Tupla (resposta, tokens) ou None se não encontrado
        """
        if not self.cache:
            return None
        
        # Busca exata primeiro
        key = self._get_key(texto)
        cached = self.cache.get(key)
        
        if cached:
            logger.debug(f"✅ Cache hit (exato): '{texto[:50]}...'")
            return cached.get("response"), cached.get("tokens", 0)
        
        # Busca semântica (se embedding_service disponível)
        if self.embedding_service:
            try:
                # Gera embedding da pergunta
                embedding = self.embedding_service.generate_embedding(texto)
                
                # Busca no cache por similaridade
                best_match = None
                best_similarity = 0.85  # Threshold mínimo de similaridade
                
                for cached_key, cached_data in self.cache.items():
                    cached_embedding = cached_data.get("embedding")
                    if cached_embedding:
                        # Calcula similaridade (cosine similarity)
                        similarity = self._cosine_similarity(embedding, cached_embedding)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = cached_data
                
                if best_match:
                    logger.debug(
                        f"✅ Cache hit (semântico, sim={best_similarity:.2f}): "
                        f"'{texto[:50]}...'"
                    )
                    return best_match.get("response"), best_match.get("tokens", 0)
            except Exception as e:
                logger.debug(f"Erro em busca semântica: {e}")
        
        return None
    
    def set(
        self,
        texto: str,
        resposta: str,
        tokens: int = 0,
        embedding: Optional[list] = None
    ):
        """
        Armazena resposta no cache
        
        Args:
            texto: Texto da pergunta
            resposta: Resposta do LLM
            tokens: Número de tokens usados
            embedding: Embedding da pergunta (opcional, gerado automaticamente se embedding_service disponível)
        """
        if not self.cache:
            return
        
        key = self._get_key(texto)
        
        # Gera embedding se necessário
        if embedding is None and self.embedding_service:
            try:
                embedding = self.embedding_service.generate_embedding(texto)
            except Exception as e:
                logger.debug(f"Erro ao gerar embedding: {e}")
                embedding = None
        
        self.cache[key] = {
            "response": resposta,
            "tokens": tokens,
            "embedding": embedding,
            "text": texto  # Armazena texto original para debug
        }
        
        logger.debug(f"💾 Cache set: '{texto[:50]}...'")
    
    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calcula similaridade de cosseno entre dois vetores"""
        try:
            import numpy as np
            
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.debug(f"Erro ao calcular similaridade: {e}")
            return 0.0
    
    def clear(self):
        """Limpa o cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache de respostas limpo")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        if not self.cache:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "max_size": self.max_size,
            "ttl": self.ttl,
            "current_size": len(self.cache),
            "semantic_search": self.embedding_service is not None
        }

