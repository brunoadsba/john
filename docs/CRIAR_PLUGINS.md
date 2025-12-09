# 📦 Guia: Como Criar Plugins para o Jonh Assistant

**Data:** 07/12/2025  
**Versão:** 1.0

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura de um Plugin](#estrutura-de-um-plugin)
3. [Exemplo Completo](#exemplo-completo)
4. [Registrando um Plugin](#registrando-um-plugin)
5. [Boas Práticas](#boas-práticas)
6. [Exemplos de Plugins](#exemplos-de-plugins)

---

## Visão Geral

O sistema de plugins permite adicionar novas funcionalidades ao Jonh Assistant sem modificar o código principal. Cada plugin:

- ✅ É autocontido (código isolado)
- ✅ Pode ser ativado/desativado facilmente
- ✅ Expõe tools que o LLM pode usar automaticamente
- ✅ Segue uma interface padrão (`BasePlugin`)

---

## Estrutura de um Plugin

Todo plugin deve herdar de `BasePlugin` e implementar os seguintes métodos:

### Métodos Obrigatórios

1. **`name`** (property): Nome único do plugin
2. **`description`** (property): Descrição do que o plugin faz
3. **`get_tool_definition()`**: Retorna definição da tool no formato OpenAI
4. **`execute(function_name, arguments)`**: Executa a função do plugin

### Métodos Opcionais

- **`is_enabled()`**: Verifica se plugin está habilitado (padrão: `True`)
- **`can_handle(query)`**: Verifica se plugin pode lidar com uma query (padrão: `True`)

---

## Exemplo Completo

Vamos criar um plugin simples de calculadora:

```python
"""
Plugin de calculadora para o Jonh Assistant
"""
from typing import Dict, Any
from loguru import logger

from backend.core.plugin_manager import BasePlugin


class CalculatorPlugin(BasePlugin):
    """Plugin que realiza cálculos matemáticos"""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "Realiza cálculos matemáticos básicos"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Retorna definição da tool no formato OpenAI"""
        return {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Calcula expressões matemáticas. Use para operações como soma, subtração, multiplicação, divisão, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Expressão matemática a calcular (ex: '50 + 30', '100 * 2')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Executa o cálculo"""
        if function_name != "calculate":
            raise ValueError(f"Função '{function_name}' não suportada")
        
        expression = arguments.get("expression", "")
        if not expression:
            raise ValueError("Expressão vazia")
        
        try:
            # AVISO: eval() é perigoso em produção!
            # Use uma biblioteca segura como 'simpleeval' em produção
            result = eval(expression)
            logger.info(f"✅ Cálculo executado: {expression} = {result}")
            return str(result)
        except Exception as e:
            logger.error(f"❌ Erro ao calcular '{expression}': {e}")
            return f"Erro ao calcular: {str(e)}"
```

**Salve em:** `backend/plugins/calculator_plugin.py`

---

## Registrando um Plugin

### Opção 1: No `main.py` (Recomendado)

Adicione o registro no `startup_event`:

```python
# Em backend/api/main.py

from backend.plugins.calculator_plugin import CalculatorPlugin

# No startup_event, após criar plugin_manager:
calculator_plugin = CalculatorPlugin()
plugin_manager.register(calculator_plugin)
```

### Opção 2: Via `__init__.py`

Adicione ao `backend/plugins/__init__.py`:

```python
from backend.plugins.calculator_plugin import CalculatorPlugin

__all__ = ["WebSearchPlugin", "CalculatorPlugin"]
```

E registre no `main.py`:

```python
from backend.plugins import CalculatorPlugin

calculator_plugin = CalculatorPlugin()
plugin_manager.register(calculator_plugin)
```

---

## Boas Práticas

### 1. Nomes Únicos

Use nomes descritivos e únicos:

```python
# ✅ Bom
name = "calculator"
name = "weather_forecast"
name = "currency_converter"

# ❌ Ruim
name = "calc"  # Muito genérico
name = "plugin1"  # Não descritivo
```

### 2. Descrições Claras

Descreva o que o plugin faz de forma clara:

```python
# ✅ Bom
description = "Fornece previsão do tempo para qualquer cidade"

# ❌ Ruim
description = "Plugin de tempo"
```

### 3. Tool Definitions Detalhadas

A descrição da tool deve ser clara para o LLM:

```python
"description": "Busca informações atualizadas na web. Use quando precisar de informações sobre eventos recentes, notícias, dados atualizados, ou qualquer informação que pode ter mudado recentemente."
```

### 4. Tratamento de Erros

Sempre trate erros adequadamente:

```python
def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
    try:
        # Lógica do plugin
        return result
    except Exception as e:
        logger.error(f"❌ Erro no plugin '{self.name}': {e}")
        return f"Erro: {str(e)}"
```

### 5. Validação de Argumentos

Valide os argumentos recebidos:

```python
def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
    required_arg = arguments.get("required_arg")
    if not required_arg:
        raise ValueError("Argumento 'required_arg' é obrigatório")
    
    # Continua processamento...
```

### 6. Logging

Use logging para debug e monitoramento:

```python
from loguru import logger

logger.info(f"✅ Plugin '{self.name}' executado com sucesso")
logger.error(f"❌ Erro no plugin '{self.name}': {e}")
```

---

## Exemplos de Plugins

### Plugin de Conversão de Moedas

```python
class CurrencyConverterPlugin(BasePlugin):
    """Converte valores entre moedas"""
    
    @property
    def name(self) -> str:
        return "currency_converter"
    
    @property
    def description(self) -> str:
        return "Converte valores entre diferentes moedas"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "convert_currency",
                "description": "Converte valores entre moedas (ex: USD para BRL)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "Valor a converter"},
                        "from_currency": {"type": "string", "description": "Moeda origem (ex: USD)"},
                        "to_currency": {"type": "string", "description": "Moeda destino (ex: BRL)"}
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        if function_name != "convert_currency":
            raise ValueError(f"Função '{function_name}' não suportada")
        
        # Implementação da conversão (usar API real em produção)
        amount = arguments.get("amount", 0)
        from_curr = arguments.get("from_currency", "")
        to_curr = arguments.get("to_currency", "")
        
        # Exemplo simplificado (usar API real)
        rate = 5.0  # USD -> BRL (exemplo)
        result = amount * rate
        
        return f"{amount} {from_curr} = {result} {to_curr}"
```

### Plugin de Previsão do Tempo

```python
class WeatherPlugin(BasePlugin):
    """Fornece previsão do tempo"""
    
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return "Fornece previsão do tempo para qualquer cidade"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Obtém previsão do tempo para uma cidade",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Nome da cidade (ex: São Paulo)"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        if function_name != "get_weather":
            raise ValueError(f"Função '{function_name}' não suportada")
        
        city = arguments.get("city", "")
        # Implementação real usaria uma API de clima
        return f"Tempo em {city}: 25°C, parcialmente nublado"
```

---

## Testando um Plugin

Crie testes unitários para seu plugin:

```python
# backend/tests/test_calculator_plugin.py

def test_calculator_plugin():
    plugin = CalculatorPlugin()
    
    assert plugin.name == "calculator"
    assert plugin.is_enabled() is True
    
    tool_def = plugin.get_tool_definition()
    assert tool_def["function"]["name"] == "calculate"
    
    result = plugin.execute("calculate", {"expression": "50 + 30"})
    assert result == "80"
```

---

## Checklist de Criação

- [ ] Plugin herda de `BasePlugin`
- [ ] Implementa todos os métodos obrigatórios
- [ ] Nome único e descritivo
- [ ] Tool definition clara e detalhada
- [ ] Tratamento de erros adequado
- [ ] Validação de argumentos
- [ ] Logging implementado
- [ ] Testes unitários criados
- [ ] Plugin registrado no `main.py`
- [ ] Documentação atualizada

---

## Próximos Passos

1. Crie seu plugin seguindo o exemplo acima
2. Adicione testes unitários
3. Registre o plugin no `main.py`
4. Teste manualmente fazendo perguntas ao Jonh
5. Documente funcionalidades específicas do seu plugin

---

**Última atualização:** 07/12/2025

