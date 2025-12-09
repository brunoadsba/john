"""
Handler para processamento LLM com suporte a RLHF
"""
from typing import Optional, Tuple, Any, List, Dict
from loguru import logger


async def process_with_llm(
    llm_service: Any,
    texto: str,
    contexto: List[Dict],
    memoria_contexto: str,
    tools: Optional[List[Dict]],
    tool_executor: Optional[Any],
    system_prompt_override: Optional[str] = None,
    reward_model_service: Optional[Any] = None,
    rlhf_service: Optional[Any] = None
) -> Tuple[str, int]:
    """
    Processa texto com LLM, opcionalmente usando RLHF para rankear respostas
    
    Args:
        llm_service: Serviço de LLM
        texto: Texto do usuário
        contexto: Contexto da conversa
        memoria_contexto: Memórias relevantes
        tools: Tools disponíveis
        tool_executor: Executor de tools
        system_prompt_override: System prompt customizado
        reward_model_service: Modelo de recompensa (opcional)
        rlhf_service: Serviço RLHF (opcional)
        
    Returns:
        Tupla (resposta_texto, tokens_usados)
    """
    # Gera resposta do LLM
    resposta_texto, tokens = llm_service.generate_response(
        texto,
        contexto,
        memorias_contexto=memoria_contexto,
        tools=tools,
        tool_executor=tool_executor,
        system_prompt_override=system_prompt_override
    )
    
    # RLHF: Se modelo de recompensa disponível, avalia resposta
    if reward_model_service and rlhf_service:
        try:
            # Calcula recompensa da resposta gerada (para logging/monitoramento)
            reward_score = reward_model_service.predict_reward(texto, resposta_texto)
            logger.debug(f"Recompensa prevista: {reward_score:.3f}")
            # TODO: Implementar geração de múltiplas candidatas e seleção da melhor
            # quando modelo de recompensa estiver treinado
        except Exception as e:
            logger.warning(f"Erro ao avaliar resposta com modelo de recompensa: {e}")
    
    return resposta_texto, tokens

