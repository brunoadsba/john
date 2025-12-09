"""
Fallback do Groq para Ollama quando rate limit é atingido
"""
from typing import List, Dict, Optional
from loguru import logger

try:
    import ollama
except ImportError:
    ollama = None


def try_ollama_fallback(
    prompt: str,
    contexto: Optional[List[Dict[str, str]]],
    memorias_contexto: str,
    tools: Optional[List[Dict]],
    tool_executor: Optional[callable],
    system_prompt_override: Optional[str],
    temperature: float,
    max_tokens: int
) -> Optional[tuple[str, int]]:
    """
    Tenta usar Ollama como fallback quando Groq atinge rate limit
    
    Args:
        prompt: Prompt original
        contexto: Contexto da conversa
        memorias_contexto: Memórias relevantes
        tools: Tools disponíveis
        tool_executor: Executor de tools
        system_prompt_override: System prompt customizado
        temperature: Temperatura para geração
        max_tokens: Número máximo de tokens
        
    Returns:
        Tupla (resposta, tokens) ou None se fallback falhar
    """
    if not ollama:
        logger.warning("[Groq→Ollama] Ollama não está disponível")
        return None
    
    try:
        logger.info("[Groq] Tentando fallback automático para Ollama...")
        
        # Importa aqui para evitar dependência circular
        from backend.services.llm.ollama_service import OllamaLLMService
        
        # Tenta usar modelo disponível (llama3:8b-instruct-q4_0 ou llama3.1:8b)
        fallback_model = "llama3:8b-instruct-q4_0"  # Modelo mais comum
        ollama_service = OllamaLLMService(
            model=fallback_model,
            host="http://localhost:11434",
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if ollama_service.is_ready():
            logger.info("[Groq→Ollama] ✅ Fallback ativado, usando Ollama")
            return ollama_service.generate_response(
                prompt=prompt,
                contexto=contexto,
                memorias_contexto=memorias_contexto,
                tools=tools,
                tool_executor=tool_executor,
                system_prompt_override=system_prompt_override
            )
        else:
            logger.warning("[Groq→Ollama] Ollama não está disponível")
    except Exception as fallback_error:
        logger.error(f"[Groq→Ollama] ❌ Fallback falhou: {fallback_error}")
    
    return None

