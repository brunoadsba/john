"""
Serviços de LLM - Factory e exports
"""
from backend.services.llm.base import BaseLLMService
from backend.services.llm.ollama_service import OllamaLLMService
from backend.services.llm.groq_service import GroqLLMService


def create_llm_service(
    provider: str,
    **kwargs
) -> BaseLLMService:
    """
    Factory para criar serviço de LLM apropriado
    
    Args:
        provider: "ollama" ou "groq"
        **kwargs: Argumentos específicos do provider
        
    Returns:
        Instância do serviço de LLM
    """
    if provider.lower() == "ollama":
        return OllamaLLMService(**kwargs)
    elif provider.lower() == "groq":
        return GroqLLMService(**kwargs)
    else:
        raise ValueError(f"Provider desconhecido: {provider}. Use 'ollama' ou 'groq'")


__all__ = [
    "BaseLLMService",
    "OllamaLLMService",
    "GroqLLMService",
    "create_llm_service"
]

