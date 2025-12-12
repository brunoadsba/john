"""
Gerenciador de plugins modular para o Jonh Assistant
"""
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from loguru import logger


class BasePlugin(ABC):
    """
    Interface base para plugins do Jonh Assistant
    
    Todos os plugins devem herdar desta classe e implementar os métodos obrigatórios.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único do plugin"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição do que o plugin faz"""
        pass
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna definição da ferramenta no formato OpenAI Function Calling
        
        Returns:
            Dicionário com definição da tool (formato OpenAI)
        """
        pass
    
    @abstractmethod
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa a função do plugin
        
        Args:
            function_name: Nome da função a executar
            arguments: Argumentos da função (dict)
            
        Returns:
            Resultado da execução (pode ser str, dict, list, etc.)
        """
        pass
    
    def is_enabled(self) -> bool:
        """
        Verifica se o plugin está habilitado
        
        Returns:
            True se habilitado, False caso contrário
        """
        return True
    
    def can_handle(self, query: str) -> bool:
        """
        Verifica se o plugin pode lidar com uma query específica
        
        Args:
            query: Query do usuário
            
        Returns:
            True se pode lidar, False caso contrário
            
        Nota: Implementação padrão retorna True. Plugins podem sobrescrever
        para fazer detecção mais inteligente.
        """
        return True
    
    def requires_network(self) -> bool:
        """
        Indica se o plugin requer conexão com internet
        
        Returns:
            True se requer internet, False caso contrário
        """
        return False
    
    def is_available_in_privacy_mode(self) -> bool:
        """
        Verifica se plugin está disponível em modo privacidade
        
        Returns:
            True se disponível, False se requer internet
        """
        if self.requires_network():
            return False
        return self.is_enabled()


class PluginManager:
    """
    Gerenciador central de plugins
    
    Responsável por:
    - Registrar plugins
    - Fornecer lista de tools para o LLM
    - Executar plugins quando solicitado pelo LLM
    """
    
    def __init__(self):
        """Inicializa o gerenciador de plugins"""
        self._plugins: Dict[str, BasePlugin] = {}
        logger.info("PluginManager inicializado")
    
    def register(self, plugin: BasePlugin) -> bool:
        """
        Registra um plugin
        
        Args:
            plugin: Instância do plugin a registrar
            
        Returns:
            True se registrado com sucesso, False caso contrário
        """
        if not isinstance(plugin, BasePlugin):
            logger.error(f"❌ Plugin inválido: {plugin} não é uma instância de BasePlugin")
            return False
        
        if not plugin.is_enabled():
            logger.warning(f"⚠️ Plugin '{plugin.name}' está desabilitado, não será registrado")
            return False
        
        if plugin.name in self._plugins:
            logger.warning(f"⚠️ Plugin '{plugin.name}' já está registrado, substituindo...")
        
        self._plugins[plugin.name] = plugin
        logger.info(f"✅ Plugin registrado: {plugin.name} - {plugin.description}")
        return True
    
    def unregister(self, plugin_name: str) -> bool:
        """
        Remove um plugin
        
        Args:
            plugin_name: Nome do plugin a remover
            
        Returns:
            True se removido, False se não encontrado
        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            logger.info(f"✅ Plugin removido: {plugin_name}")
            return True
        
        logger.warning(f"⚠️ Plugin '{plugin_name}' não encontrado")
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Obtém um plugin pelo nome
        
        Args:
            plugin_name: Nome do plugin
            
        Returns:
            Instância do plugin ou None se não encontrado
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[BasePlugin]:
        """
        Retorna lista de todos os plugins registrados
        
        Returns:
            Lista de plugins
        """
        return list(self._plugins.values())
    
    def get_tool_definitions(self, privacy_mode: bool = False) -> List[Dict[str, Any]]:
        """
        Retorna definições de todas as tools dos plugins (formato OpenAI)
        
        Args:
            privacy_mode: Se True, filtra plugins que requerem internet
        
        Returns:
            Lista de definições de tools
        """
        tools = []
        for plugin in self._plugins.values():
            try:
                # Filtra plugins de rede em modo privacidade
                if privacy_mode and not plugin.is_available_in_privacy_mode():
                    logger.debug(f"🔒 Plugin '{plugin.name}' filtrado (requer internet)")
                    continue
                    
                tool_def = plugin.get_tool_definition()
                if tool_def:
                    tools.append(tool_def)
            except Exception as e:
                logger.error(f"❌ Erro ao obter tool definition do plugin '{plugin.name}': {e}")
        
        mode_text = "privacidade" if privacy_mode else "normal"
        logger.debug(f"📋 {len(tools)} tool definitions disponíveis (modo {mode_text})")
        return tools
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa uma tool de um plugin
        
        Args:
            tool_name: Nome da tool (ex: "search_web")
            arguments: Argumentos da tool (dict)
            
        Returns:
            Resultado da execução
            
        Raises:
            ValueError: Se tool não encontrada
            Exception: Se erro na execução do plugin
        """
        # Procura plugin que possui esta tool
        for plugin in self._plugins.values():
            try:
                tool_def = plugin.get_tool_definition()
                if not tool_def:
                    continue
                
                # Verifica se é a tool correta
                function_def = tool_def.get("function", {})
                if function_def.get("name") == tool_name:
                    logger.info(f"🔧 Executando tool '{tool_name}' do plugin '{plugin.name}'")
                    result = plugin.execute(tool_name, arguments)
                    logger.info(f"✅ Tool '{tool_name}' executada com sucesso")
                    return result
            except Exception as e:
                logger.error(f"❌ Erro ao verificar plugin '{plugin.name}': {e}")
                continue
        
        # Tool não encontrada
        error_msg = f"Tool '{tool_name}' não encontrada em nenhum plugin"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    def get_plugin_count(self) -> int:
        """
        Retorna número de plugins registrados
        
        Returns:
            Número de plugins
        """
        return len(self._plugins)
    
    def list_plugins(self) -> List[str]:
        """
        Lista nomes de todos os plugins registrados
        
        Returns:
            Lista de nomes de plugins
        """
        return list(self._plugins.keys())

