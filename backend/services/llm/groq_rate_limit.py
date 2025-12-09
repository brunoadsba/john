"""
Detecção e tratamento de rate limit do Groq
"""
from typing import Optional
from loguru import logger


def is_rate_limit_error(error: Exception) -> bool:
    """
    Detecta se um erro é relacionado a rate limit do Groq
    
    Args:
        error: Exceção capturada
        
    Returns:
        True se for rate limit, False caso contrário
    """
    error_str = str(error)
    error_type = type(error).__name__
    
    is_rate_limit = (
        "Rate limit" in error_str or 
        "rate_limit" in error_str or 
        "429" in error_str or
        "RateLimitError" in error_type or
        "Rate limit reached" in error_str or
        "rate_limit_exceeded" in error_str or
        "Error code: 429" in error_str or
        "tokens per day" in error_str.lower() or
        "TPD" in error_str
    )
    
    return is_rate_limit


def handle_rate_limit_error(
    error: Exception,
    prompt: str,
    contexto: Optional[list],
    memorias_contexto: str,
    tools: Optional[list],
    tool_executor: Optional[callable],
    system_prompt_override: Optional[str],
    fallback_callback: callable
) -> Optional[tuple]:
    """
    Trata erro de rate limit tentando fallback
    
    Args:
        error: Exceção de rate limit
        prompt: Prompt original
        contexto: Contexto da conversa
        memorias_contexto: Memórias relevantes
        tools: Tools disponíveis
        tool_executor: Executor de tools
        system_prompt_override: System prompt customizado
        fallback_callback: Função para tentar fallback
        
    Returns:
        Resultado do fallback ou None
    """
    logger.warning(f"[Groq] Rate limit detectado: {error}")
    
    # Tenta fallback
    fallback_result = fallback_callback(
        prompt, contexto, memorias_contexto, tools, tool_executor, system_prompt_override
    )
    
    if fallback_result:
        return fallback_result
    
    # Se não conseguiu fallback, levanta erro
    raise RuntimeError(
        f"Groq rate limit atingido. Limite diário de tokens excedido. "
        f"Configure Ollama como fallback ou tente novamente mais tarde. "
        f"Erro: {error}"
    )

