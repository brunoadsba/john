"""
Handler para preparação de tools e tool executor
"""
from typing import Optional, List, Dict, Callable, Any
from loguru import logger

from backend.api.handlers.tool_executor import create_tool_executor


def prepare_tools_for_llm(
    plugin_manager: Any,
    web_search_tool: Any,
    llm_service: Any,
    privacy_mode_service: Optional[Any] = None
) -> tuple[Optional[List[Dict]], Optional[Callable]]:
    """
    Prepara tools e tool executor para o LLM
    
    Args:
        plugin_manager: Instância do PluginManager
        web_search_tool: Tool de busca web antiga (compatibilidade)
        llm_service: Serviço de LLM
        privacy_mode_service: Serviço de modo privacidade (opcional)
        
    Returns:
        Tupla (tools, tool_executor) ou (None, None) se não houver tools
    """
    tools = None
    tool_executor = None
    
    # Verifica modo privacidade
    privacy_mode = False
    if privacy_mode_service:
        privacy_mode = privacy_mode_service.get_privacy_mode()
        logger.debug(f"🔒 Modo privacidade: {'ATIVO' if privacy_mode else 'INATIVO'}")
    
    # Verifica se modelo suporta tools antes de passar
    if plugin_manager and hasattr(llm_service, 'model'):
        model_name = llm_service.model.lower()
        # Ollama llama3:8b não suporta tools, mas Mistral sim
        if 'llama3:8b' not in model_name or 'mistral' in model_name:
            # Filtra plugins baseado em modo privacidade
            tools = plugin_manager.get_tool_definitions(privacy_mode=privacy_mode)
            tool_executor = create_tool_executor(plugin_manager, web_search_tool)
            
            if privacy_mode and tools:
                logger.info(f"🔒 Modo privacidade: {len(tools)} tools locais disponíveis")
        else:
            logger.info("Modelo Ollama llama3:8b não suporta tools, pulando tool calling")
    elif web_search_tool:
        # Modo antigo: compatibilidade
        # Em modo privacidade, não usa web_search
        if not privacy_mode:
            tools = [web_search_tool.get_tool_definition()]
            tool_executor = create_tool_executor(None, web_search_tool)
        else:
            logger.info("🔒 Modo privacidade: web_search_tool desabilitado")
    
    return tools, tool_executor
