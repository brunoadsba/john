"""
Testes para Feature 021: Tool Calling (Busca Web)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock de dependências antes de importar
import unittest.mock as mock
sys.modules['backend.database'] = mock.MagicMock()
sys.modules['backend.database.database'] = mock.MagicMock()
sys.modules['backend.services.memory_service'] = mock.MagicMock()

from backend.services.tool_service import WebSearchTool, create_web_search_tool


class TestWebSearchTool:
    """Testes do serviço de busca web"""
    
    def test_create_tool_without_services(self):
        """Testa criação quando nenhum serviço está disponível"""
        with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', False):
            with patch('backend.services.tool_service.TAVILY_AVAILABLE', False):
                tool = create_web_search_tool()
                assert tool is None
    
    @patch('backend.services.tool_service.DDGS')
    def test_search_duckduckgo_success(self, mock_ddgs_class):
        """Testa busca bem-sucedida com DuckDuckGo"""
        # Mock do DuckDuckGo
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = Mock(return_value=None)
        mock_ddgs.text.return_value = [
            {
                "title": "Teste Resultado 1",
                "href": "https://example.com/1",
                "body": "Descrição do resultado 1"
            },
            {
                "title": "Teste Resultado 2",
                "href": "https://example.com/2",
                "body": "Descrição do resultado 2"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', True):
            tool = WebSearchTool()
            results = tool.search("teste", max_results=2)
            
            assert len(results) == 2
            assert results[0]["title"] == "Teste Resultado 1"
            assert results[0]["url"] == "https://example.com/1"
            assert results[0]["snippet"] == "Descrição do resultado 1"
            assert results[1]["title"] == "Teste Resultado 2"
    
    @patch('backend.services.tool_service.DDGS')
    def test_search_duckduckgo_empty_query(self, mock_ddgs_class):
        """Testa busca com query vazia"""
        with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', True):
            tool = WebSearchTool()
            results = tool.search("")
            
            assert results == []
            mock_ddgs_class.assert_not_called()
    
    @patch('backend.services.tool_service.DDGS')
    def test_search_duckduckgo_error(self, mock_ddgs_class):
        """Testa tratamento de erro na busca DuckDuckGo"""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = Mock(return_value=None)
        mock_ddgs.text.side_effect = Exception("Erro de conexão")
        mock_ddgs_class.return_value = mock_ddgs
        
        with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', True):
            tool = WebSearchTool()
            results = tool.search("teste")
            
            assert results == []
    
    def test_get_tool_definition(self):
        """Testa definição da tool no formato OpenAI"""
        with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', True):
            tool = WebSearchTool()
            definition = tool.get_tool_definition()
            
            assert definition["type"] == "function"
            assert definition["function"]["name"] == "search_web"
            assert "description" in definition["function"]
            assert "parameters" in definition["function"]
            assert "query" in definition["function"]["parameters"]["properties"]
    
    @patch('backend.services.tool_service.TavilyClient')
    def test_search_tavily_success(self, mock_tavily_class):
        """Testa busca bem-sucedida com Tavily"""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Tavily Result 1",
                    "url": "https://tavily.com/1",
                    "content": "Conteúdo do resultado 1"
                }
            ]
        }
        mock_tavily_class.return_value = mock_client
        
        with patch('backend.services.tool_service.TAVILY_AVAILABLE', True):
            tool = WebSearchTool(tavily_api_key="test_key")
            results = tool.search("teste", max_results=1)
            
            assert len(results) == 1
            assert results[0]["title"] == "Tavily Result 1"
            assert results[0]["url"] == "https://tavily.com/1"
            assert results[0]["snippet"] == "Conteúdo do resultado 1"
    
    @patch('backend.services.tool_service.DDGS')
    def test_search_fallback_tavily_to_duckduckgo(self, mock_ddgs_class):
        """Testa fallback de Tavily para DuckDuckGo"""
        # Tavily falha
        with patch('backend.services.tool_service.TAVILY_AVAILABLE', False):
            # DuckDuckGo funciona
            mock_ddgs = MagicMock()
            mock_ddgs.__enter__ = Mock(return_value=mock_ddgs)
            mock_ddgs.__exit__ = Mock(return_value=None)
            mock_ddgs.text.return_value = [
                {"title": "DDG Result", "href": "https://ddg.com", "body": "Content"}
            ]
            mock_ddgs_class.return_value = mock_ddgs
            
            with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', True):
                tool = WebSearchTool(tavily_api_key="test_key", prefer_tavily=True)
                results = tool.search("teste")
                
                assert len(results) == 1
                assert results[0]["title"] == "DDG Result"


class TestToolIntegration:
    """Testes de integração do tool calling"""
    
    @pytest.mark.asyncio
    async def test_tool_executor_format(self):
        """Testa formato de resultado do tool executor"""
        with patch('backend.services.tool_service.DUCKDUCKGO_AVAILABLE', True):
            with patch('backend.services.tool_service.DDGS') as mock_ddgs:
                mock_ddgs_instance = MagicMock()
                mock_ddgs_instance.__enter__ = Mock(return_value=mock_ddgs_instance)
                mock_ddgs_instance.__exit__ = Mock(return_value=None)
                mock_ddgs_instance.text.return_value = [
                    {
                        "title": "Resultado Teste",
                        "href": "https://test.com",
                        "body": "Este é um resultado de teste para verificar formatação"
                    }
                ]
                mock_ddgs.return_value = mock_ddgs_instance
                
                tool = WebSearchTool()
                results = tool.search("teste", max_results=1)
                
                # Verifica formatação esperada pelo LLM
                assert len(results) > 0
                assert "title" in results[0]
                assert "url" in results[0]
                assert "snippet" in results[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

