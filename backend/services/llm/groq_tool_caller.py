"""
Lógica de tool calling para Groq
"""
from typing import List, Dict, Optional, Tuple
from loguru import logger


def process_tool_calls(
    message,
    tool_executor: Optional[callable],
    mensagens: List[Dict[str, str]],
    iteration: int,
    max_iterations: int
) -> Tuple[bool, str, int]:
    """
    Processa tool calls retornados pelo Groq
    
    Args:
        message: Mensagem da resposta do Groq
        tool_executor: Função para executar tools
        mensagens: Lista de mensagens atual
        iteration: Iteração atual
        max_iterations: Número máximo de iterações
        
    Returns:
        Tupla (continuar_loop, resposta, tokens_usados)
    """
    tool_calls = message.tool_calls
    
    if not tool_calls or iteration >= max_iterations - 1:
        # Sem tool calls ou última iteração - retorna resposta
        resposta = message.content or ""
        tokens_usados = 0  # Será calculado depois
        return False, resposta, tokens_usados
    
    # Processa tool calls
    logger.info(f"[Groq] Tool calls detectados ({len(tool_calls)}): {[tc.function.name for tc in tool_calls]}")
    
    # Adiciona resposta do assistente com tool calls
    mensagens.append({
        "role": "assistant",
        "content": message.content or "",
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in tool_calls
        ]
    })
    
    # Executa cada tool call
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args_str = tool_call.function.arguments
        
        try:
            import json
            tool_args = json.loads(tool_args_str)
        except json.JSONDecodeError:
            logger.error(f"⚠️ Erro ao parsear argumentos da tool '{tool_name}': {tool_args_str}")
            tool_args = {}
        
        if tool_executor:
            try:
                tool_result = tool_executor(tool_name, tool_args)
                logger.info(f"✅ Tool '{tool_name}' executada com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao executar tool '{tool_name}': {e}")
                tool_result = f"Erro: {str(e)}"
        else:
            logger.warning(f"⚠️ Tool '{tool_name}' chamada mas tool_executor não disponível")
            tool_result = "Tool executor não disponível"
        
        # Adiciona resultado da tool
        # IMPORTANTE: Groq exige tool_call_id para mensagens com role:tool
        mensagens.append({
            "role": "tool",
            "content": str(tool_result),
            "tool_call_id": tool_call.id  # ID do tool call original
        })
    
    # Continua loop para gerar resposta final
    return True, "", 0

