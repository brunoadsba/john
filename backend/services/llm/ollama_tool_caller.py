"""
Lógica de tool calling para Ollama
"""
from typing import List, Dict, Optional, Tuple
from loguru import logger


def process_ollama_tool_calls(
    message: Dict,
    tool_executor: Optional[callable],
    mensagens: List[Dict[str, str]],
    iteration: int,
    max_iterations: int
) -> Tuple[bool, str, int]:
    """
    Processa tool calls retornados pelo Ollama
    
    Args:
        message: Mensagem da resposta do Ollama
        tool_executor: Função para executar tools
        mensagens: Lista de mensagens atual
        iteration: Iteração atual
        max_iterations: Número máximo de iterações
        
    Returns:
        Tupla (continuar_loop, resposta, tokens_usados)
    """
    # Verifica se há tool calls
    tool_calls = message.get('tool_calls', [])
    
    if not tool_calls or not tool_executor or iteration >= max_iterations - 1:
        # Sem tool calls ou última iteração - retorna resposta
        resposta = message.get('content', '')
        return False, resposta, 0
    
    # Processa tool calls
    logger.info(f"🔧 Tool calls detectados: {len(tool_calls)}")
    
    resposta = message.get('content', '')
    
    # Executa cada tool call
    for tool_call in tool_calls:
        tool_name = tool_call.get('function', {}).get('name', '')
        tool_args = tool_call.get('function', {}).get('arguments', '{}')
        
        logger.info(f"🔧 Executando tool: {tool_name} com args: {tool_args}")
        
        try:
            import json
            args_dict = json.loads(tool_args) if isinstance(tool_args, str) else tool_args
            tool_result = tool_executor(tool_name, args_dict)
            
            # Adiciona mensagem do assistente com tool call
            mensagens.append({
                "role": "assistant",
                "content": resposta,
                "tool_calls": [tool_call]
            })
            
            # Adiciona resultado do tool às mensagens
            mensagens.append({
                "role": "tool",
                "name": tool_name,
                "content": str(tool_result)
            })
            
            logger.info(f"✅ Tool '{tool_name}' executado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao executar tool '{tool_name}': {e}")
            mensagens.append({
                "role": "tool",
                "name": tool_name,
                "content": f"Erro: {str(e)}"
            })
    
    # Continua loop para gerar resposta final
    return True, "", 0

