"""
Handler para execução de tools/plugins
"""
from typing import Dict, Optional, List, Any, Callable
from loguru import logger


def create_tool_executor(plugin_manager: Any, web_search_tool: Any = None) -> Optional[Callable]:
    """
    Cria função executor de tools baseado no PluginManager ou modo antigo
    
    Args:
        plugin_manager: Instância do PluginManager
        web_search_tool: Tool de busca web antiga (compatibilidade)
        
    Returns:
        Função executor ou None se não houver tools disponíveis
    """
    if plugin_manager:
        def execute_tool(tool_name: str, args: dict) -> str:
            """Executa uma tool via PluginManager e retorna resultado formatado"""
            try:
                result = plugin_manager.execute_tool(tool_name, args)
                
                # Formata resultado para o LLM
                if isinstance(result, dict):
                    # Resultado estruturado (ex: Architecture Advisor)
                    if result.get("success"):
                        data = result.get("data", {})
                        if isinstance(data, dict):
                            # Formata dados estruturados
                            formatted = ""
                            for key, value in data.items():
                                if isinstance(value, list):
                                    formatted += f"{key}:\n"
                                    for item in value:
                                        formatted += f"  - {item}\n"
                                elif isinstance(value, dict):
                                    formatted += f"{key}:\n"
                                    for k, v in value.items():
                                        formatted += f"  - {k}: {v}\n"
                                else:
                                    formatted += f"{key}: {value}\n"
                            return formatted if formatted else str(data)
                        return str(data)
                    else:
                        return f"Erro: {result.get('message', 'Erro desconhecido')}"
                elif isinstance(result, list):
                    # Lista de resultados (ex: busca web)
                    if not result:
                        return "Nenhum resultado encontrado."
                    
                    formatted = "Resultados:\n\n"
                    for i, r in enumerate(result, 1):
                        if isinstance(r, dict):
                            formatted += f"{i}. {r.get('title', 'Sem título')}\n"
                            if r.get('url'):
                                formatted += f"   URL: {r.get('url', '')}\n"
                            if r.get('snippet'):
                                formatted += f"   {r.get('snippet', '')[:200]}...\n\n"
                        else:
                            formatted += f"{i}. {str(r)}\n\n"
                    return formatted
                else:
                    # Resultado simples
                    return str(result)
            except Exception as e:
                logger.error(f"❌ Erro ao executar tool '{tool_name}': {e}")
                import traceback
                logger.error(traceback.format_exc())
                return f"Erro ao executar {tool_name}: {str(e)}"
        
        return execute_tool
    
    elif web_search_tool:
        # Modo antigo: compatibilidade
        def execute_tool(tool_name: str, args: dict) -> str:
            """Executa uma tool e retorna resultado formatado"""
            if tool_name == "search_web":
                query = args.get("query", "")
                if not query:
                    return "Erro: query de busca vazia"
                
                results = web_search_tool.search(query, max_results=5)
                if not results:
                    return "Nenhum resultado encontrado na busca."
                
                # Formata resultados para o LLM
                formatted = "Resultados da busca:\n\n"
                for i, r in enumerate(results, 1):
                    formatted += f"{i}. {r.get('title', 'Sem título')}\n"
                    formatted += f"   URL: {r.get('url', '')}\n"
                    formatted += f"   {r.get('snippet', '')[:200]}...\n\n"
                
                return formatted
            else:
                return f"Tool desconhecida: {tool_name}"
        
        return execute_tool
    
    return None

