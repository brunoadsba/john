"""
Serviço de ferramentas (tools) para o LLM
Implementa busca web usando DuckDuckGo (padrão) e Tavily (fallback)
"""
from typing import Dict, List, Optional
from loguru import logger
import time

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    logger.warning("duckduckgo_search não disponível - instale com: pip install duckduckgo-search")
    DUCKDUCKGO_AVAILABLE = False
    DDGS = None

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    logger.warning("tavily não disponível - instale com: pip install tavily-python")
    TAVILY_AVAILABLE = False
    TavilyClient = None


class WebSearchTool:
    """Ferramenta de busca web para o LLM"""
    
    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        prefer_tavily: bool = False
    ):
        """
        Inicializa a ferramenta de busca web
        
        Args:
            tavily_api_key: API key do Tavily (opcional)
            prefer_tavily: Se True, usa Tavily como primeira opção
        """
        self.tavily_api_key = tavily_api_key
        self.prefer_tavily = prefer_tavily
        self.tavily_client = None
        
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
    
    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Busca informações na web
        
        Args:
            query: Termo de busca
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados com 'title', 'url', 'snippet'
        """
        if not query or not query.strip():
            logger.warning("⚠️ Query de busca vazia")
            return []
        
        start_time = time.time()
        logger.info(f"🔍 Buscando na web: '{query}'")
        
        # Tenta Tavily primeiro se preferido e disponível
        if self.prefer_tavily and self.tavily_client:
            results = self._search_tavily(query, max_results)
            if results:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Busca Tavily concluída em {elapsed:.0f}ms: {len(results)} resultados")
                return results
        
        # Tenta DuckDuckGo
        if DUCKDUCKGO_AVAILABLE:
            results = self._search_duckduckgo(query, max_results)
            if results:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Busca DuckDuckGo concluída em {elapsed:.0f}ms: {len(results)} resultados")
                return results
        
        # Fallback para Tavily se DuckDuckGo falhou
        if self.tavily_client:
            results = self._search_tavily(query, max_results)
            if results:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Busca Tavily (fallback) concluída em {elapsed:.0f}ms: {len(results)} resultados")
                return results
        
        logger.error(f"❌ Falha em todas as tentativas de busca para: '{query}'")
        return []
    
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
    
    def get_tool_definition(self) -> Dict:
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


def create_web_search_tool(
    tavily_api_key: Optional[str] = None,
    prefer_tavily: bool = False
) -> Optional[WebSearchTool]:
    """
    Factory para criar ferramenta de busca web
    
    Args:
        tavily_api_key: API key do Tavily (opcional)
        prefer_tavily: Se True, usa Tavily como primeira opção
        
    Returns:
        Instância de WebSearchTool ou None se nenhum serviço disponível
    """
    tool = WebSearchTool(tavily_api_key=tavily_api_key, prefer_tavily=prefer_tavily)
    
    # Verifica se pelo menos um serviço está disponível
    if not DUCKDUCKGO_AVAILABLE and not tool.tavily_client:
        logger.warning("⚠️ Nenhum serviço de busca disponível")
        return None
    
    return tool

