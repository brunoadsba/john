"""
Módulo para streaming de respostas LLM
Suporta Groq e Ollama com streaming de tokens
"""
from typing import AsyncIterator, List, Dict, Optional
from loguru import logger


async def stream_groq_response(
    client,
    model: str,
    messages: List[Dict],
    temperature: float,
    max_tokens: int,
    tools: Optional[List[Dict]] = None
) -> AsyncIterator[str]:
    """
    Stream de resposta do Groq
    
    Args:
        client: Cliente Groq
        model: Nome do modelo
        messages: Lista de mensagens
        temperature: Temperatura
        max_tokens: Máximo de tokens
        tools: Tools disponíveis (opcional)
        
    Yields:
        Tokens de texto conforme são gerados
    """
    try:
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True  # Habilita streaming
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        stream = client.chat.completions.create(**params)
        
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
                    
    except Exception as e:
        logger.error(f"Erro no streaming Groq: {e}")
        raise


async def stream_ollama_response(
    client,
    model: str,
    messages: List[Dict],
    temperature: float,
    max_tokens: int,
    tools: Optional[List[Dict]] = None
) -> AsyncIterator[str]:
    """
    Stream de resposta do Ollama
    
    Args:
        client: Cliente Ollama
        model: Nome do modelo
        messages: Lista de mensagens
        temperature: Temperatura
        max_tokens: Máximo de tokens
        tools: Tools disponíveis (opcional)
        
    Yields:
        Tokens de texto conforme são gerados
    """
    try:
        options = {
            "temperature": temperature,
            "num_predict": max_tokens
        }
        
        # Ollama streaming
        stream = client.chat(
            model=model,
            messages=messages,
            options=options,
            stream=True
        )
        
        for chunk in stream:
            if chunk.get("message") and chunk["message"].get("content"):
                yield chunk["message"]["content"]
                
    except Exception as e:
        logger.error(f"Erro no streaming Ollama: {e}")
        raise

