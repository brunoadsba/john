"""
Testes de tool calling no LLM service (Feature 021)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.llm_service import OllamaLLMService, GroqLLMService


class TestOllamaToolCalling:
    """Testes de tool calling no Ollama"""
    
    @pytest.fixture
    def ollama_service(self):
        """Fixture do serviço Ollama"""
        with patch('backend.services.llm_service.ollama') as mock_ollama:
            mock_client = MagicMock()
            mock_ollama.Client.return_value = mock_client
            service = OllamaLLMService(
                model="llama3:8b-instruct-q4_0",
                host="http://localhost:11434"
            )
            service.client = mock_client
            return service
    
    def test_generate_response_without_tools(self, ollama_service):
        """Testa geração de resposta sem tools"""
        mock_response = {
            'message': {
                'content': 'Resposta normal sem tool calling'
            },
            'eval_count': 100
        }
        ollama_service.client.chat.return_value = mock_response
        
        resposta, tokens = ollama_service.generate_response(
            "Olá",
            contexto=None
        )
        
        assert resposta == "Resposta normal sem tool calling"
        assert tokens == 100
        ollama_service.client.chat.assert_called_once()
    
    def test_generate_response_with_tool_calling(self, ollama_service):
        """Testa geração de resposta com tool calling"""
        # Primeira chamada: LLM decide usar tool
        mock_response_1 = {
            'message': {
                'content': '',
                'tool_calls': [
                    {
                        'function': {
                            'name': 'search_web',
                            'arguments': '{"query": "temperatura hoje"}'
                        }
                    }
                ]
            },
            'eval_count': 50
        }
        
        # Segunda chamada: LLM gera resposta final com resultados
        mock_response_2 = {
            'message': {
                'content': 'A temperatura hoje é 25°C'
            },
            'eval_count': 80
        }
        
        ollama_service.client.chat.side_effect = [mock_response_1, mock_response_2]
        
        # Tool executor mock
        def mock_tool_executor(tool_name, args):
            if tool_name == "search_web":
                return "Resultados: Temperatura 25°C"
            return "Erro"
        
        tools = [{
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Busca na web"
            }
        }]
        
        resposta, tokens = ollama_service.generate_response(
            "Qual a temperatura hoje?",
            contexto=None,
            tools=tools,
            tool_executor=mock_tool_executor
        )
        
        assert "25°C" in resposta
        assert tokens == 130  # 50 + 80
        assert ollama_service.client.chat.call_count == 2
    
    def test_generate_response_tool_error(self, ollama_service):
        """Testa tratamento de erro em tool calling"""
        mock_response_1 = {
            'message': {
                'content': '',
                'tool_calls': [
                    {
                        'function': {
                            'name': 'search_web',
                            'arguments': '{"query": "teste"}'
                        }
                    }
                ]
            },
            'eval_count': 50
        }
        
        mock_response_2 = {
            'message': {
                'content': 'Não consegui buscar informações'
            },
            'eval_count': 60
        }
        
        ollama_service.client.chat.side_effect = [mock_response_1, mock_response_2]
        
        def mock_tool_executor(tool_name, args):
            raise Exception("Erro na busca")
        
        tools = [{"type": "function", "function": {"name": "search_web"}}]
        
        resposta, tokens = ollama_service.generate_response(
            "Teste",
            tools=tools,
            tool_executor=mock_tool_executor
        )
        
        assert "Não consegui" in resposta or "erro" in resposta.lower()
        assert ollama_service.client.chat.call_count == 2


class TestGroqToolCalling:
    """Testes de tool calling no Groq"""
    
    @pytest.fixture
    def groq_service(self):
        """Fixture do serviço Groq"""
        with patch('backend.services.llm_service.Groq') as mock_groq_class:
            mock_client = MagicMock()
            mock_groq_class.return_value = mock_client
            service = GroqLLMService(
                api_key="test_key",
                model="llama-3.1-8b-instant"
            )
            service.client = mock_client
            return service
    
    def test_generate_response_with_tool_calling(self, groq_service):
        """Testa tool calling no Groq"""
        # Mock da primeira resposta com tool call
        mock_message_1 = MagicMock()
        mock_message_1.content = None
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "search_web"
        mock_tool_call.function.arguments = '{"query": "teste"}'
        mock_message_1.tool_calls = [mock_tool_call]
        
        mock_choice_1 = MagicMock()
        mock_choice_1.message = mock_message_1
        mock_usage_1 = MagicMock()
        mock_usage_1.total_tokens = 50
        
        mock_response_1 = MagicMock()
        mock_response_1.choices = [mock_choice_1]
        mock_response_1.usage = mock_usage_1
        
        # Mock da segunda resposta final
        mock_message_2 = MagicMock()
        mock_message_2.content = "Resposta final com resultados"
        mock_message_2.tool_calls = None
        
        mock_choice_2 = MagicMock()
        mock_choice_2.message = mock_message_2
        mock_usage_2 = MagicMock()
        mock_usage_2.total_tokens = 80
        
        mock_response_2 = MagicMock()
        mock_response_2.choices = [mock_choice_2]
        mock_response_2.usage = mock_usage_2
        
        groq_service.client.chat.completions.create.side_effect = [
            mock_response_1,
            mock_response_2
        ]
        
        def mock_tool_executor(tool_name, args):
            return "Resultados da busca"
        
        tools = [{"type": "function", "function": {"name": "search_web"}}]
        
        resposta, tokens = groq_service.generate_response(
            "Teste",
            tools=tools,
            tool_executor=mock_tool_executor
        )
        
        assert "Resposta final" in resposta
        assert tokens == 130  # 50 + 80
        assert groq_service.client.chat.completions.create.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

