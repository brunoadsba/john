"""
Handler para coleta de feedback e conversas
"""
from typing import Optional, Any
from loguru import logger


async def collect_conversation_feedback(
    feedback_service: Optional[Any],
    session_id: str,
    user_input: str,
    assistant_response: str,
    tokens_used: int,
    processing_time: float,
    used_tool: Optional[str] = None
) -> Optional[int]:
    """
    Coleta conversa automaticamente para feedback
    
    Args:
        feedback_service: Serviço de feedback
        session_id: ID da sessão
        user_input: Entrada do usuário
        assistant_response: Resposta do assistente
        tokens_used: Tokens utilizados
        processing_time: Tempo de processamento
        used_tool: Ferramenta usada (opcional)
        
    Returns:
        ID da conversa coletada (None se erro ou serviço não disponível)
    """
    if not feedback_service:
        return None
    
    try:
        conversation_id = await feedback_service.collect_conversation(
            session_id=session_id,
            user_input=user_input,
            assistant_response=assistant_response,
            tokens_used=tokens_used,
            processing_time=processing_time,
            used_tool=used_tool
        )
        return conversation_id
    except Exception as e:
        logger.warning(f"Erro ao coletar conversa: {e}")
        return None

