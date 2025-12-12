"""
Plugin de Calculadora para o Jonh Assistant
Permite realizar cálculos matemáticos básicos
"""
from typing import Dict, Any
from loguru import logger
import math
import re

from backend.core.plugin_manager import BasePlugin


class CalculatorPlugin(BasePlugin):
    """
    Plugin de calculadora matemática
    """
    
    @property
    def name(self) -> str:
        """Nome único do plugin"""
        return "calculator"
    
    @property
    def description(self) -> str:
        """Descrição do plugin"""
        return "Realiza cálculos matemáticos básicos e avançados"
    
    def is_enabled(self) -> bool:
        """Sempre habilitado"""
        return True
    
    def can_handle(self, query: str) -> bool:
        """
        Verifica se a query é um cálculo matemático
        """
        # Palavras-chave que indicam cálculos
        calc_keywords = [
            'calcular', 'calcule', 'quanto é', 'quanto dá', 'somar', 'subtrair',
            'multiplicar', 'dividir', 'raiz', 'potência', 'elevado', 'percentual',
            '+', '-', '*', '/', 'x', '÷'
        ]
        
        # Verifica se contém palavras-chave ou operadores matemáticos
        query_lower = query.lower()
        has_keyword = any(keyword in query_lower for keyword in calc_keywords)
        has_operator = bool(re.search(r'[\+\-\*\/x÷\^]', query))
        has_numbers = bool(re.search(r'\d+', query))
        
        return (has_keyword or has_operator) and has_numbers
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna definição da ferramenta no formato OpenAI Function Calling
        """
        return {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Realiza cálculos matemáticos. Suporta operações básicas (+, -, *, /), potências (^), raiz quadrada (sqrt), porcentagem, e funções matemáticas (sin, cos, tan, log, etc). Use quando o usuário pedir para calcular, somar, subtrair, multiplicar, dividir, ou fazer qualquer operação matemática.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Expressão matemática para calcular. Exemplos: '2 + 2', '10 * 5', 'raiz quadrada de 16', '5 ao quadrado', '20% de 100', 'seno de 30', etc."
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa cálculo matemático
        """
        if function_name != "calculate":
            raise ValueError(f"Função '{function_name}' não suportada por este plugin")
        
        expression = arguments.get("expression", "")
        if not expression:
            raise ValueError("Expressão matemática não fornecida")
        
        try:
            # Normaliza a expressão
            normalized = self._normalize_expression(expression)
            
            # Avalia a expressão de forma segura
            result = self._safe_eval(normalized)
            
            logger.info(f"🧮 Calculadora: {expression} = {result}")
            
            return {
                "result": result,
                "expression": expression,
                "formatted_result": self._format_result(result)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo: {e}")
            raise ValueError(f"Erro ao calcular '{expression}': {str(e)}")
    
    def _normalize_expression(self, expression: str) -> str:
        """
        Normaliza expressão matemática para formato avaliável
        """
        expr = expression.lower().strip()
        
        # Substitui palavras por operadores
        replacements = {
            'quanto é': '',
            'quanto dá': '',
            'calcule': '',
            'calcular': '',
            ' ': '',  # Remove espaços
            'x': '*',
            '×': '*',
            '÷': '/',
            'ao quadrado': '**2',
            'ao cubo': '**3',
            'elevado a': '**',
            'elevado': '**',
            '^': '**',
            'raiz quadrada de': 'sqrt(',
            'raiz de': 'sqrt(',
            'por cento': '/100',
            '%': '/100*',
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        # Adiciona parêntese de fechamento para raiz quadrada se necessário
        expr = re.sub(r'sqrt\(([^)]+)\)', r'sqrt(\1)', expr)
        if expr.count('sqrt(') > expr.count(')'):
            expr += ')' * (expr.count('sqrt(') - expr.count(')'))
        
        # Normaliza porcentagem (ex: "20% de 100" → "100 * 20/100")
        expr = re.sub(r'(\d+)%?\s*de\s*(\d+)', r'\2 * \1/100', expr)
        
        # Substitui funções matemáticas
        math_functions = {
            'seno de': 'sin(',
            'sin de': 'sin(',
            'cosseno de': 'cos(',
            'cos de': 'cos(',
            'tangente de': 'tan(',
            'tan de': 'tan(',
            'logaritmo de': 'log10(',
            'log de': 'log10(',
            'ln de': 'log(',
        }
        
        for old, new in math_functions.items():
            if old in expr:
                expr = expr.replace(old, new)
                # Adiciona parêntese de fechamento
                if expr.count('(') > expr.count(')'):
                    expr += ')'
        
        return expr
    
    def _safe_eval(self, expression: str) -> float:
        """
        Avalia expressão matemática de forma segura
        """
        # Lista permitida de funções e constantes
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "pow": pow,
            "__builtins__": {},
        }
        
        # Remove caracteres perigosos
        if re.search(r'[^0-9+\-*/().\sabcdefghijklmnopqrstuvwxyz_]', expression):
            raise ValueError("Caracteres inválidos na expressão")
        
        try:
            result = eval(expression, allowed_names, {})
            
            # Converte para float se for número
            if isinstance(result, (int, float)):
                return float(result)
            else:
                raise ValueError("Resultado não é um número")
                
        except Exception as e:
            raise ValueError(f"Erro ao avaliar expressão: {str(e)}")
    
    def _format_result(self, result: float) -> str:
        """
        Formata resultado de forma legível
        """
        # Remove zeros desnecessários para números inteiros
        if result == int(result):
            return str(int(result))
        
        # Formata com 2 casas decimais
        return f"{result:.2f}".rstrip('0').rstrip('.')

