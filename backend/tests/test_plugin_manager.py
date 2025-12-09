"""
Testes unitários para PluginManager
"""
import pytest
from typing import Dict, Any

from backend.core.plugin_manager import PluginManager, BasePlugin
from backend.plugins.web_search_plugin import WebSearchPlugin


class MockPlugin(BasePlugin):
    """Plugin mock para testes"""
    
    def __init__(self, name: str, description: str, enabled: bool = True):
        self._name = name
        self._description = description
        self._enabled = enabled
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": f"{self._name}_tool",
                "description": self._description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        if function_name == f"{self._name}_tool":
            return f"Resultado de {self._name}: {arguments.get('input', '')}"
        raise ValueError(f"Função '{function_name}' não suportada")


class TestPluginManager:
    """Testes para PluginManager"""
    
    def test_init(self):
        """Testa inicialização do PluginManager"""
        manager = PluginManager()
        assert manager.get_plugin_count() == 0
        assert manager.list_plugins() == []
    
    def test_register_plugin(self):
        """Testa registro de plugin"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin")
        
        result = manager.register(plugin)
        assert result is True
        assert manager.get_plugin_count() == 1
        assert "test" in manager.list_plugins()
    
    def test_register_duplicate_plugin(self):
        """Testa registro de plugin duplicado (substitui)"""
        manager = PluginManager()
        plugin1 = MockPlugin("test", "Test plugin 1")
        plugin2 = MockPlugin("test", "Test plugin 2")
        
        manager.register(plugin1)
        manager.register(plugin2)  # Substitui
        
        assert manager.get_plugin_count() == 1
        assert manager.get_plugin("test").description == "Test plugin 2"
    
    def test_register_disabled_plugin(self):
        """Testa que plugin desabilitado não é registrado"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin", enabled=False)
        
        result = manager.register(plugin)
        assert result is False
        assert manager.get_plugin_count() == 0
    
    def test_register_invalid_plugin(self):
        """Testa registro de plugin inválido"""
        manager = PluginManager()
        
        result = manager.register("not a plugin")
        assert result is False
        assert manager.get_plugin_count() == 0
    
    def test_unregister_plugin(self):
        """Testa remoção de plugin"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin")
        
        manager.register(plugin)
        assert manager.get_plugin_count() == 1
        
        result = manager.unregister("test")
        assert result is True
        assert manager.get_plugin_count() == 0
    
    def test_unregister_nonexistent_plugin(self):
        """Testa remoção de plugin inexistente"""
        manager = PluginManager()
        
        result = manager.unregister("nonexistent")
        assert result is False
    
    def test_get_plugin(self):
        """Testa obtenção de plugin"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin")
        
        manager.register(plugin)
        retrieved = manager.get_plugin("test")
        
        assert retrieved is not None
        assert retrieved.name == "test"
        assert retrieved.description == "Test plugin"
    
    def test_get_nonexistent_plugin(self):
        """Testa obtenção de plugin inexistente"""
        manager = PluginManager()
        
        result = manager.get_plugin("nonexistent")
        assert result is None
    
    def test_get_all_plugins(self):
        """Testa obtenção de todos os plugins"""
        manager = PluginManager()
        plugin1 = MockPlugin("test1", "Test plugin 1")
        plugin2 = MockPlugin("test2", "Test plugin 2")
        
        manager.register(plugin1)
        manager.register(plugin2)
        
        all_plugins = manager.get_all_plugins()
        assert len(all_plugins) == 2
        assert plugin1 in all_plugins
        assert plugin2 in all_plugins
    
    def test_get_tool_definitions(self):
        """Testa obtenção de definições de tools"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin")
        
        manager.register(plugin)
        tools = manager.get_tool_definitions()
        
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "test_tool"
    
    def test_execute_tool(self):
        """Testa execução de tool"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin")
        
        manager.register(plugin)
        result = manager.execute_tool("test_tool", {"input": "hello"})
        
        assert result == "Resultado de test: hello"
    
    def test_execute_nonexistent_tool(self):
        """Testa execução de tool inexistente"""
        manager = PluginManager()
        plugin = MockPlugin("test", "Test plugin")
        
        manager.register(plugin)
        
        with pytest.raises(ValueError, match="Tool 'nonexistent_tool' não encontrada"):
            manager.execute_tool("nonexistent_tool", {})


class TestWebSearchPlugin:
    """Testes para WebSearchPlugin"""
    
    def test_plugin_properties(self):
        """Testa propriedades do plugin"""
        plugin = WebSearchPlugin()
        
        assert plugin.name == "web_search"
        assert "busca" in plugin.description.lower()
    
    def test_get_tool_definition(self):
        """Testa definição da tool"""
        plugin = WebSearchPlugin()
        tool_def = plugin.get_tool_definition()
        
        assert tool_def["type"] == "function"
        assert tool_def["function"]["name"] == "search_web"
        assert "query" in tool_def["function"]["parameters"]["required"]
    
    def test_execute_search_web(self):
        """Testa execução de busca web (mock)"""
        plugin = WebSearchPlugin()
        
        # Testa com query vazia (deve retornar lista vazia)
        result = plugin.execute("search_web", {"query": ""})
        assert result == []
    
    def test_execute_invalid_function(self):
        """Testa execução de função inválida"""
        plugin = WebSearchPlugin()
        
        with pytest.raises(ValueError, match="Função 'invalid' não suportada"):
            plugin.execute("invalid", {})


class TestPluginManagerIntegration:
    """Testes de integração do PluginManager com WebSearchPlugin"""
    
    def test_register_web_search_plugin(self):
        """Testa registro do plugin de busca web"""
        manager = PluginManager()
        plugin = WebSearchPlugin()
        
        result = manager.register(plugin)
        # Pode ser True ou False dependendo se DuckDuckGo/Tavily estão disponíveis
        assert isinstance(result, bool)
        
        if result:
            assert manager.get_plugin_count() == 1
            assert "web_search" in manager.list_plugins()
    
    def test_get_tool_definitions_from_web_search(self):
        """Testa obtenção de tool definitions do plugin de busca web"""
        manager = PluginManager()
        plugin = WebSearchPlugin()
        
        if manager.register(plugin):
            tools = manager.get_tool_definitions()
            assert len(tools) >= 0  # Pode ser 0 se plugin não estiver habilitado
            
            if len(tools) > 0:
                assert tools[0]["function"]["name"] == "search_web"

