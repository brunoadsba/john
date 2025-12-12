"""
Testes unitários para CurrencyConverterPlugin
"""
import pytest
from backend.plugins.currency_converter_plugin import CurrencyConverterPlugin


def test_currency_converter_initialization():
    """Testa inicialização do plugin"""
    plugin = CurrencyConverterPlugin()
    assert plugin is not None
    assert plugin.name == "currency_converter"
    assert plugin.is_enabled() is True


def test_currency_converter_tool_definition():
    """Testa definição da tool"""
    plugin = CurrencyConverterPlugin()
    tool_def = plugin.get_tool_definition()
    
    assert tool_def is not None
    assert tool_def["type"] == "function"
    assert tool_def["function"]["name"] == "convert_currency"
    assert "parameters" in tool_def["function"]


def test_currency_converter_basic_conversion():
    """Testa conversão básica"""
    plugin = CurrencyConverterPlugin()
    
    # Conversão simples
    result = plugin.execute("convert_currency", {
        "amount": 100,
        "from_currency": "BRL",
        "to_currency": "USD"
    })
    
    assert result is not None
    assert "converted_amount" in result
    assert "rate" in result
    assert result["from_currency"] == "BRL"
    assert result["to_currency"] == "USD"


def test_currency_converter_same_currency():
    """Testa conversão para mesma moeda"""
    plugin = CurrencyConverterPlugin()
    
    result = plugin.execute("convert_currency", {
        "amount": 100,
        "from_currency": "BRL",
        "to_currency": "BRL"
    })
    
    assert result["converted_amount"] == 100
    assert result["rate"] == 1.0


def test_currency_converter_can_handle():
    """Testa detecção de queries de conversão"""
    plugin = CurrencyConverterPlugin()
    
    assert plugin.can_handle("converter 100 reais para dólar") is True
    assert plugin.can_handle("quanto é 50 USD em BRL") is True
    assert plugin.can_handle("câmbio") is True
    assert plugin.can_handle("Olá, como vai?") is False


def test_currency_converter_error_handling():
    """Testa tratamento de erros"""
    plugin = CurrencyConverterPlugin()
    
    with pytest.raises(ValueError):
        plugin.execute("convert_currency", {})  # Sem parâmetros
    
    with pytest.raises(ValueError):
        plugin.execute("invalid_function", {"amount": 100, "from_currency": "BRL", "to_currency": "USD"})


def test_currency_normalization():
    """Testa normalização de códigos de moeda"""
    plugin = CurrencyConverterPlugin()
    
    # Testa normalização de variações
    assert plugin._normalize_currency_code("real") == "BRL"
    assert plugin._normalize_currency_code("dólar") == "USD"
    assert plugin._normalize_currency_code("EUR") == "EUR"

