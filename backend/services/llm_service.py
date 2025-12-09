"""
Wrapper de compatibilidade para llm_service.py
DEPRECATED: Use backend.services.llm em vez disso
"""
import warnings

warnings.warn(
    "backend.services.llm_service está deprecated. Use backend.services.llm",
    DeprecationWarning,
    stacklevel=2
)

# Re-exporta tudo do novo módulo
from backend.services.llm import (
    BaseLLMService,
    OllamaLLMService,
    GroqLLMService,
    create_llm_service
)

__all__ = [
    "BaseLLMService",
    "OllamaLLMService",
    "GroqLLMService",
    "create_llm_service"
]
