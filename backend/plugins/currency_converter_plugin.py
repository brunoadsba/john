"""
Plugin de Conversão de Moedas para o Jonh Assistant
Converte valores entre diferentes moedas usando taxa de câmbio atualizada
"""
from typing import Dict, Any, Optional
from loguru import logger
import time

from backend.core.plugin_manager import BasePlugin

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("requests não disponível - instale com: pip install requests")
    REQUESTS_AVAILABLE = False


class CurrencyConverterPlugin(BasePlugin):
    """
    Plugin de conversão de moedas usando API pública
    """
    
    # Taxas de câmbio base (BRL = 1.0)
    # Estas são aproximadas e devem ser atualizadas via API
    DEFAULT_RATES = {
        "BRL": 1.0,
        "USD": 0.20,  # ~1 USD = 5 BRL
        "EUR": 0.18,  # ~1 EUR = 5.5 BRL
        "GBP": 0.16,  # ~1 GBP = 6.2 BRL
        "JPY": 29.0,  # ~1 JPY = 0.034 BRL
        "CNY": 1.4,   # ~1 CNY = 0.71 BRL
        "ARS": 180.0,  # ~1 ARS = 0.0055 BRL
        "CLP": 180.0,  # ~1 CLP = 0.0055 BRL
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o plugin de conversão de moedas
        
        Args:
            api_key: API key para serviço de câmbio (opcional, usa cache se não fornecido)
        """
        self.api_key = api_key
        self.rates_cache = {}
        self.cache_timestamp = 0
        self.cache_ttl = 3600  # 1 hora
        
        # Popula cache inicial com taxas padrão
        self.rates_cache = self.DEFAULT_RATES.copy()
    
    @property
    def name(self) -> str:
        """Nome único do plugin"""
        return "currency_converter"
    
    @property
    def description(self) -> str:
        """Descrição do plugin"""
        return "Converte valores entre diferentes moedas (BRL, USD, EUR, GBP, JPY, etc.)"
    
    def is_enabled(self) -> bool:
        """Sempre habilitado (usa taxas padrão se API não disponível)"""
        return True
    
    def requires_network(self) -> bool:
        """Este plugin requer conexão com internet para taxas atualizadas"""
        return True
    
    def can_handle(self, query: str) -> bool:
        """
        Verifica se a query é sobre conversão de moedas
        """
        query_lower = query.lower()
        
        # Palavras-chave
        keywords = [
            'converter', 'conversão', 'câmbio', 'cambio', 'moeda',
            'dólar', 'dolar', 'euro', 'libra', 'iene', 'yen',
            'real', 'peso', 'convert', 'currency'
        ]
        
        # Códigos de moedas comuns
        currencies = ['usd', 'eur', 'gbp', 'jpy', 'brl', 'cny', 'ars', 'clp']
        
        has_keyword = any(keyword in query_lower for keyword in keywords)
        has_currency = any(f" {curr} " in f" {query_lower} " or query_lower.startswith(curr) or query_lower.endswith(curr) for curr in currencies)
        
        return has_keyword or has_currency
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna definição da ferramenta no formato OpenAI Function Calling
        """
        return {
            "type": "function",
            "function": {
                "name": "convert_currency",
                "description": "Converte valores entre diferentes moedas. Use quando o usuário pedir para converter valores monetários, saber quanto vale em outra moeda, ou calcular câmbio. Suporta: BRL (Real), USD (Dólar), EUR (Euro), GBP (Libra), JPY (Iene), CNY (Yuan), ARS (Peso Argentino), CLP (Peso Chileno).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Valor a ser convertido (número)"
                        },
                        "from_currency": {
                            "type": "string",
                            "description": "Moeda de origem (código de 3 letras: BRL, USD, EUR, GBP, JPY, CNY, ARS, CLP)"
                        },
                        "to_currency": {
                            "type": "string",
                            "description": "Moeda de destino (código de 3 letras: BRL, USD, EUR, GBP, JPY, CNY, ARS, CLP)"
                        }
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa conversão de moeda
        """
        if function_name != "convert_currency":
            raise ValueError(f"Função '{function_name}' não suportada por este plugin")
        
        amount = arguments.get("amount")
        from_currency = arguments.get("from_currency", "").upper()
        to_currency = arguments.get("to_currency", "").upper()
        
        if amount is None:
            raise ValueError("Valor não fornecido")
        
        if not from_currency or not to_currency:
            raise ValueError("Moedas de origem e destino devem ser especificadas")
        
        # Normaliza códigos de moeda
        from_currency = self._normalize_currency_code(from_currency)
        to_currency = self._normalize_currency_code(to_currency)
        
        if from_currency == to_currency:
            return {
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "converted_amount": amount,
                "rate": 1.0,
                "message": f"{amount} {from_currency} = {amount} {to_currency} (mesma moeda)"
            }
        
        # Obtém taxas atualizadas
        rates = self._get_exchange_rates()
        
        if from_currency not in rates:
            raise ValueError(f"Moeda '{from_currency}' não suportada")
        if to_currency not in rates:
            raise ValueError(f"Moeda '{to_currency}' não suportada")
        
        # Converte via BRL como intermediário
        # Ex: USD -> EUR: USD -> BRL -> EUR
        usd_to_brl = 1.0 / rates.get("USD", 5.0)
        from_to_brl = 1.0 / rates.get(from_currency, 1.0)
        brl_to_to = rates.get(to_currency, 1.0)
        
        # Taxa de conversão
        rate = from_to_brl * brl_to_to
        
        # Valor convertido
        converted = amount * rate
        
        logger.info(f"💱 Conversão: {amount} {from_currency} → {converted:.2f} {to_currency} (taxa: {rate:.4f})")
        
        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": round(converted, 2),
            "rate": round(rate, 4),
            "formatted": f"{amount} {from_currency} = {converted:.2f} {to_currency}"
        }
    
    def _normalize_currency_code(self, code: str) -> str:
        """
        Normaliza código de moeda
        """
        code = code.upper().strip()
        
        # Mapeamento de variações comuns
        mappings = {
            "R$": "BRL",
            "REAL": "BRL",
            "REAIS": "BRL",
            "$": "USD",
            "DOLAR": "USD",
            "DÓLAR": "USD",
            "DOLLAR": "USD",
            "EURO": "EUR",
            "LIBRA": "GBP",
            "IENE": "JPY",
            "YEN": "JPY",
            "YUAN": "CNY",
            "PESO": "ARS",  # Assumindo peso argentino por padrão
            "PESOS": "ARS",
        }
        
        return mappings.get(code, code[:3]) if len(code) > 3 else code
    
    def _get_exchange_rates(self) -> Dict[str, float]:
        """
        Obtém taxas de câmbio (com cache)
        """
        current_time = time.time()
        
        # Verifica se cache é válido
        if current_time - self.cache_timestamp < self.cache_ttl:
            return self.rates_cache
        
        # Tenta atualizar via API se disponível
        if REQUESTS_AVAILABLE and self.api_key:
            try:
                # Exemplo com exchangerate-api.com (requer API key)
                # Você pode usar outra API pública gratuita
                response = requests.get(
                    f"https://api.exchangerate-api.com/v4/latest/BRL",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get("rates", {})
                    
                    # Converte para base BRL = 1.0
                    brl_rates = {}
                    for currency, rate in rates.items():
                        brl_rates[currency] = 1.0 / rate if rate > 0 else 1.0
                    
                    self.rates_cache.update(brl_rates)
                    self.cache_timestamp = current_time
                    logger.info("✅ Taxas de câmbio atualizadas via API")
                    return self.rates_cache
            except Exception as e:
                logger.warning(f"⚠️ Erro ao atualizar taxas via API: {e}, usando cache")
        
        # Retorna cache existente (taxas padrão)
        return self.rates_cache

