"""
Handler para integração de cache de respostas
"""
from typing import Optional, Tuple, Any
from loguru import logger

from backend.services.response_cache import ResponseCache


def create_response_cache(embedding_service: Optional[Any] = None) -> Optional[ResponseCache]:
    """
    Cria instância de cache de respostas
    
    Args:
        embedding_service: Serviço de embeddings (opcional)
        
    Returns:
        Instância de ResponseCache ou None se cachetools não disponível
    """
    try:
        cache = ResponseCache(
            max_size=500,
            ttl=7200,  # 2 horas
            embedding_service=embedding_service
        )
        logger.info("✅ Cache de respostas inicializado")
        return cache
    except Exception as e:
        logger.warning(f"Cache de respostas não disponível: {e}")
        return None


async def get_cached_response(
    cache: Optional[ResponseCache],
    texto: str
) -> Optional[Tuple[str, int]]:
    """
    Obtém resposta do cache
    
    Args:
        cache: Instância do cache
        texto: Texto da pergunta
        
    Returns:
        Tupla (resposta, tokens) ou None se não encontrado
    """
    if not cache:
        return None
    
    try:
        result = cache.get(texto)
        if result:
            resposta, tokens = result
            logger.info(f"✅ Resposta do cache: '{texto[:50]}...'")
            return resposta, tokens
    except Exception as e:
        logger.debug(f"Erro ao buscar no cache: {e}")
    
    return None


async def set_cached_response(
    cache: Optional[ResponseCache],
    texto: str,
    resposta: str,
    tokens: int = 0
):
    """
    Armazena resposta no cache
    
    Args:
        cache: Instância do cache
        texto: Texto da pergunta
        resposta: Resposta do LLM
        tokens: Número de tokens usados
    """
    if not cache:
        return
    
    try:
        cache.set(texto, resposta, tokens)
    except Exception as e:
        logger.debug(f"Erro ao armazenar no cache: {e}")

