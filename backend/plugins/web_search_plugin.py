"""
Plugin de busca web para o Jonh Assistant
Migrado de backend/services/tool_service.py
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import time
import hashlib

from backend.core.plugin_manager import BasePlugin

try:
    from cachetools import TTLCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("cachetools não disponível - cache de buscas desabilitado")

try:
    from ddgs import DDGS  # ✅ Mudança aqui
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    logger.warning("ddgs não disponível - instale com: pip install ddgs")  # ✅ E aqui
    DUCKDUCKGO_AVAILABLE = False
    DDGS = None

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    logger.warning("tavily não disponível - instale com: pip install tavily-python")
    TAVILY_AVAILABLE = False
    TavilyClient = None


class WebSearchPlugin(BasePlugin):
    """
    Plugin de busca web usando DuckDuckGo e Tavily
    """
    
    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        prefer_tavily: bool = False,
        enable_cache: bool = True,
        cache_size: int = 100,
        cache_ttl: int = 3600  # 1 hora
    ):
        """
        Inicializa o plugin de busca web
        
        Args:
            tavily_api_key: API key do Tavily (opcional)
            prefer_tavily: Se True, usa Tavily como primeira opção
            enable_cache: Habilita cache de buscas recentes
            cache_size: Tamanho máximo do cache
            cache_ttl: Time-to-live do cache em segundos
        """
        self.tavily_api_key = tavily_api_key
        self.prefer_tavily = prefer_tavily
        self.tavily_client = None
        self.enable_cache = enable_cache
        
        # Inicializa cache de buscas
        self.search_cache = None
        if enable_cache and CACHE_AVAILABLE:
            self.search_cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
            logger.info(f"✅ Cache de buscas inicializado: max_size={cache_size}, ttl={cache_ttl}s")
        elif enable_cache:
            logger.warning("⚠️ Cache de buscas desabilitado (cachetools não disponível)")
        
        # Inicializa Tavily se API key fornecida
        if tavily_api_key and TAVILY_AVAILABLE:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
                logger.info("✅ Tavily inicializado com sucesso")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar Tavily: {e}")
                self.tavily_client = None
        
        # Verifica disponibilidade
        if not DUCKDUCKGO_AVAILABLE and not self.tavily_client:
            logger.error("❌ Nenhum serviço de busca disponível (DuckDuckGo ou Tavily)")
    
    @property
    def name(self) -> str:
        """Nome único do plugin"""
        return "web_search"
    
    @property
    def description(self) -> str:
        """Descrição do plugin"""
        return "Busca informações atualizadas na web usando DuckDuckGo e Tavily"
    
    def is_enabled(self) -> bool:
        """Verifica se pelo menos um serviço está disponível"""
        return DUCKDUCKGO_AVAILABLE or self.tavily_client is not None
    
    def requires_network(self) -> bool:
        """Este plugin requer conexão com internet"""
        return True
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna definição da ferramenta no formato OpenAI Function Calling
        
        Returns:
            Dicionário com definição da tool
        """
        return {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Busca informações atualizadas na web. Use quando precisar de informações sobre eventos recentes, notícias, dados atualizados, ou qualquer informação que pode ter mudado recentemente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Termo de busca em português. Seja específico e direto."
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa a busca web
        
        Args:
            function_name: Nome da função (deve ser "search_web")
            arguments: Argumentos da função (deve conter "query")
            
        Returns:
            Lista de resultados com 'title', 'url', 'snippet'
        """
        if function_name != "search_web":
            raise ValueError(f"Função '{function_name}' não suportada por este plugin")
        
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 5)
        
        return self.search(query, max_results)
    
    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Gera chave para cache baseada na query"""
        normalized_query = " ".join(query.lower().strip().split())
        key_string = f"{normalized_query}:{max_results}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Busca informações na web (com cache)
        
        Args:
            query: Termo de busca
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados com 'title', 'url', 'snippet'
        """
        if not query or not query.strip():
            logger.warning("⚠️ Query de busca vazia")
            return []
        
        # Verifica cache primeiro
        if self.search_cache is not None:
            cache_key = self._get_cache_key(query, max_results)
            cached_result = self.search_cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"✅ Busca do cache: '{query}' ({len(cached_result)} resultados)")
                return cached_result
        
        start_time = time.time()
        logger.info(f"🔍 Buscando na web: '{query}'")
        
        results = []
        
        # Tenta Tavily primeiro se preferido e disponível
        if self.prefer_tavily and self.tavily_client:
            results = self._search_tavily(query, max_results)
            if results:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Busca Tavily concluída em {elapsed:.0f}ms: {len(results)} resultados")
        
        # Tenta DuckDuckGo se Tavily não retornou resultados
        if not results and DUCKDUCKGO_AVAILABLE:
            results = self._search_duckduckgo(query, max_results)
            if results:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Busca DuckDuckGo concluída em {elapsed:.0f}ms: {len(results)} resultados")
        
        # Fallback para Tavily se DuckDuckGo falhou
        if not results and self.tavily_client:
            results = self._search_tavily(query, max_results)
            if results:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Busca Tavily (fallback) concluída em {elapsed:.0f}ms: {len(results)} resultados")
        
        if not results:
            logger.error(f"❌ Falha em todas as tentativas de busca para: '{query}'")
            return []
        
        # Armazena no cache se habilitado
        if self.search_cache is not None:
            cache_key = self._get_cache_key(query, max_results)
            self.search_cache[cache_key] = results
            logger.debug(f"💾 Resultados armazenados no cache: '{query}'")
        
        return results
    
    def _search_duckduckgo(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, str]]:
        """Busca usando DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
                return results
        except Exception as e:
            logger.error(f"❌ Erro na busca DuckDuckGo: {e}")
            return []
    
    def _search_tavily(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, str]]:
        """Busca usando Tavily"""
        try:
            if not self.tavily_client:
                return []
            
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"  # "basic" ou "advanced"
            )
            
            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")
                })
            return results
        except Exception as e:
            logger.error(f"❌ Erro na busca Tavily: {e}")
            return []

