"""Serviços de IA do assistente Jonh"""
from .stt_service import WhisperSTTService
from .llm import (
    BaseLLMService,
    OllamaLLMService,
    GroqLLMService,
    create_llm_service
)
from .tts_service import PiperTTSService
from .wake_word_service import OpenWakeWordService
from .context_manager import ContextManager
from .memory_service import MemoryService
from .embedding_service import EmbeddingService
from .intent_detector import IntentDetector

__all__ = [
    "WhisperSTTService",
    "BaseLLMService",
    "OllamaLLMService",
    "GroqLLMService",
    "create_llm_service",
    "PiperTTSService",
    "OpenWakeWordService",
    "ContextManager",
    "MemoryService",
    "EmbeddingService",
    "IntentDetector",
]

