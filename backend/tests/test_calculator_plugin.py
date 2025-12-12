"""
Testes unitários para CalculatorPlugin
"""
import pytest
from backend.plugins.calculator_plugin import CalculatorPlugin


def test_calculator_plugin_initialization():
    """Testa inicialização do plugin"""
    plugin = CalculatorPlugin()
    assert plugin is not None
    assert plugin.name == "calculator"
    assert plugin.is_enabled() is True


def test_calculator_tool_definition():
    """Testa definição da tool"""
    plugin = CalculatorPlugin()
    tool_def = plugin.get_tool_definition()
    
    assert tool_def is not None
    assert tool_def["type"] == "function"
    assert tool_def["function"]["name"] == "calculate"
    assert "parameters" in tool_def["function"]


def test_calculator_basic_operations():
    """Testa operações básicas"""
    plugin = CalculatorPlugin()
    
    # Soma
    result = plugin.execute("calculate", {"expression": "2 + 2"})
    assert result["result"] == 4.0
    
    # Subtração
    result = plugin.execute("calculate", {"expression": "10 - 5"})
    assert result["result"] == 5.0
    
    # Multiplicação
    result = plugin.execute("calculate", {"expression": "3 * 4"})
    assert result["result"] == 12.0
    
    # Divisão
    result = plugin.execute("calculate", {"expression": "15 / 3"})
    assert result["result"] == 5.0


def test_calculator_can_handle():
    """Testa detecção de queries matemáticas"""
    plugin = CalculatorPlugin()
    
    assert plugin.can_handle("calcule 2 + 2") is True
    assert plugin.can_handle("quanto é 10 * 5") is True
    assert plugin.can_handle("2 + 2") is True
    assert plugin.can_handle("Olá, como vai?") is False


def test_calculator_error_handling():
    """Testa tratamento de erros"""
    plugin = CalculatorPlugin()
    
    with pytest.raises(ValueError):
        plugin.execute("calculate", {})  # Sem expressão
    
    with pytest.raises(ValueError):
        plugin.execute("invalid_function", {"expression": "2 + 2"})


def test_calculator_advanced_operations():
    """Testa operações avançadas"""
    plugin = CalculatorPlugin()
    
    # Potência
    result = plugin.execute("calculate", {"expression": "2 ** 3"})
    assert result["result"] == 8.0
    
    # Raiz quadrada
    result = plugin.execute("calculate", {"expression": "sqrt(16)"})
    assert result["result"] == 4.0

