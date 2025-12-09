"""
Serviço de embeddings para busca semântica de memórias
"""
from typing import List, Optional, Dict
from loguru import logger
import numpy as np
import hashlib

# Tenta importar sentence-transformers, mas não falha se não estiver instalado
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers não disponível. Busca semântica será desabilitada.")


class EmbeddingService:
    """Serviço para gerar embeddings de texto"""
    
    _instance: Optional['EmbeddingService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.model = None
        self._embedding_cache: Dict[str, List[float]] = {}
        self._cache_max_size = 1000
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Modelo leve e rápido, funciona bem em PT-BR
                logger.info("Carregando modelo de embeddings: all-MiniLM-L6-v2")
                self.model = SentenceTransformer(
                    'all-MiniLM-L6-v2',
                    device='cpu',
                    cache_folder='./models'
                )
                logger.info("✅ Modelo de embeddings carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo de embeddings: {e}")
                self.model = None
        else:
            logger.warning("sentence-transformers não disponível. Usando busca por palavras-chave.")
    
    def is_available(self) -> bool:
        """Verifica se o serviço de embeddings está disponível"""
        return self.model is not None
    
    def _get_cache_key(self, text: str) -> str:
        """Gera chave de cache para um texto"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _clean_cache(self):
        """Limpa cache se exceder tamanho máximo"""
        if len(self._embedding_cache) > self._cache_max_size:
            items_to_remove = int(self._cache_max_size * 0.2)
            keys_to_remove = list(self._embedding_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self._embedding_cache[key]
            logger.debug(f"Cache limpo: {items_to_remove} itens removidos")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos (com cache)
        
        Args:
            texts: Lista de textos para embeddar
            
        Returns:
            Lista de vetores de embeddings
        """
        if not self.is_available():
            raise RuntimeError("Serviço de embeddings não está disponível")
        
        try:
            # Verifica cache primeiro
            cached_embeddings = []
            texts_to_embed = []
            indices_to_embed = []
            
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self._embedding_cache:
                    cached_embeddings.append((i, self._embedding_cache[cache_key]))
                else:
                    texts_to_embed.append(text)
                    indices_to_embed.append(i)
            
            # Gera embeddings apenas para textos não em cache
            new_embeddings = []
            if texts_to_embed:
                embeddings = self.model.encode(texts_to_embed, normalize_embeddings=True)
                embeddings_list = embeddings.tolist()
                
                # Armazena no cache
                for text, embedding in zip(texts_to_embed, embeddings_list):
                    cache_key = self._get_cache_key(text)
                    self._embedding_cache[cache_key] = embedding
                    new_embeddings.append(embedding)
                
                self._clean_cache()
            
            # Combina embeddings do cache e novos
            result = [None] * len(texts)
            for i, emb in cached_embeddings:
                result[i] = emb
            for i, emb in zip(indices_to_embed, new_embeddings):
                result[i] = emb
            
            cache_hits = len(cached_embeddings)
            if cache_hits > 0:
                logger.debug(f"Cache hit: {cache_hits}/{len(texts)} embeddings")
            
            return result
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Gera embedding para uma query (texto único) com cache
        
        Args:
            text: Texto para embeddar
            
        Returns:
            Vetor de embedding
        """
        # Verifica cache
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            logger.debug("Query embedding encontrado no cache")
            return self._embedding_cache[cache_key]
        
        # Gera novo embedding
        embedding = self.embed([text])[0]
        
        # Armazena no cache
        self._embedding_cache[cache_key] = embedding
        self._clean_cache()
        
        return embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula similaridade de cosseno entre dois vetores
        
        Args:
            vec1: Primeiro vetor
            vec2: Segundo vetor
            
        Returns:
            Similaridade (0.0 a 1.0)
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade: {e}")
            return 0.0

