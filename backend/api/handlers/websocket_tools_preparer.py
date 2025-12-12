"""
Preparação de tools para WebSocket handlers
"""
from typing import Optional, Tuple, List, Dict
from loguru import logger

from backend.core.plugin_manager import PluginManager


def prepare_tools_for_websocket(
    plugin_manager: Optional[PluginManager],
    web_search_tool: Optional[any],
    privacy_mode_service: Optional[any] = None
) -> Tuple[Optional[List[Dict]], Optional[callable]]:
    """
    Prepara tools e tool executor para uso no WebSocket
    
    Args:
        plugin_manager: PluginManager (modo novo)
        web_search_tool: WebSearchTool (modo antigo, compatibilidade)
        privacy_mode_service: Serviço de modo privacidade (opcional)
        
    Returns:
        Tupla (tools, tool_executor)
    """
    tools = None
    tool_executor = None
    
    # Determina modo privacidade
    privacy_mode = False
    if privacy_mode_service:
        privacy_mode = privacy_mode_service.get_privacy_mode()
    
    if plugin_manager:
        # Novo modo: usa PluginManager (filtra plugins se em modo privacidade)
        tools = plugin_manager.get_tool_definitions(privacy_mode=privacy_mode)
        
        def execute_tool(tool_name: str, args: dict) -> str:
            """Executa uma tool via PluginManager e retorna resultado formatado"""
            try:
                result = plugin_manager.execute_tool(tool_name, args)
                
                # Formata resultado para o LLM
                if isinstance(result, list):
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
                return f"Erro ao executar {tool_name}: {str(e)}"
        
        tool_executor = execute_tool
    elif web_search_tool:
        # Modo antigo: compatibilidade
        tools = [web_search_tool.get_tool_definition()]
        
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
        
        tool_executor = execute_tool
    
    return tools, tool_executor

