"""
Handler para preparação de contexto e memórias
"""
from typing import Optional, Tuple
from loguru import logger


async def prepare_context_and_memories(
    context_manager,
    memory_service,
    session_id: Optional[str],
    user_input: str
) -> Tuple[str, list, str]:
    """
    Prepara contexto e memórias para processamento
    
    Args:
        context_manager: Gerenciador de contexto
        memory_service: Serviço de memória
        session_id: ID da sessão (None para criar nova)
        user_input: Entrada do usuário
        
    Returns:
        Tupla (session_id, contexto, memoria_contexto)
    """
    # Gerencia contexto
    if not session_id:
        session_id = await context_manager.create_session()
    
    await context_manager.add_message(session_id, "user", user_input)
    contexto = await context_manager.get_context(session_id)
    
    # Busca memórias relevantes
    memoria_contexto = ""
    if memory_service:
        memoria_contexto = await memory_service.get_memories_for_context(user_input)
        # Extrai e salva memórias da conversa
        await memory_service.extract_and_save_memory(user_input, "")
    
    return session_id, contexto, memoria_contexto


async def save_memories_from_response(
    memory_service,
    user_input: str,
    assistant_response: str
):
    """
    Extrai e salva memórias da resposta
    
    Args:
        memory_service: Serviço de memória
        user_input: Entrada do usuário
        assistant_response: Resposta do assistente
    """
    if memory_service:
        await memory_service.extract_and_save_memory(user_input, assistant_response)

