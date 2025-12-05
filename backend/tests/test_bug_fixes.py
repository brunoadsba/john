"""
Testes para verificar correção dos bugs identificados
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.services.llm_service import OllamaLLMService


class TestBugFixes:
    """Testes para bugs corrigidos"""
    
    def test_bug2_ollama_client_initialization(self):
        """
        Bug 2: Verifica que o cliente Ollama é corretamente inicializado
        com o host customizado
        """
        custom_host = "http://192.168.1.100:11434"
        
        with patch('backend.services.llm_service.ollama') as mock_ollama:
            mock_client = Mock()
            mock_ollama.Client.return_value = mock_client
            
            service = OllamaLLMService(
                model="llama3:8b",
                host=custom_host
            )
            
            # Verifica que Client foi chamado com host correto
            mock_ollama.Client.assert_called_once_with(host=custom_host)
            
            # Verifica que o cliente foi atribuído
            assert service.client == mock_client
            assert service.host == custom_host
    
    def test_bug2_ollama_uses_custom_client(self):
        """
        Bug 2: Verifica que chamadas usam o cliente customizado
        """
        custom_host = "http://192.168.1.100:11434"
        
        with patch('backend.services.llm_service.ollama') as mock_ollama:
            mock_client = Mock()
            mock_client.chat.return_value = {
                'message': {'content': 'Resposta teste'},
                'eval_count': 10
            }
            mock_ollama.Client.return_value = mock_client
            
            service = OllamaLLMService(
                model="llama3:8b",
                host=custom_host
            )
            
            # Gera resposta
            response, tokens = service.generate_response("teste")
            
            # Verifica que usou o cliente customizado
            mock_client.chat.assert_called_once()
            assert response == 'Resposta teste'
            assert tokens == 10
    
    @pytest.mark.asyncio
    async def test_bug1_websocket_session_capture(self):
        """
        Bug 1: Verifica que session_id é capturado de handle_control_message
        """
        from backend.api.routes.websocket import handle_control_message
        from backend.services.context_manager import ContextManager
        
        # Mock websocket
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        # Mock context manager
        with patch('backend.api.routes.websocket.context_manager') as mock_ctx:
            mock_ctx.create_session.return_value = "test-session-123"
            
            # Simula start_session
            import json
            control_msg = json.dumps({"type": "start_session"})
            
            result = await handle_control_message(mock_ws, control_msg, None)
            
            # Verifica que retornou o session_id
            assert result == "test-session-123"
            
            # Verifica que enviou mensagem correta
            mock_ws.send_json.assert_called_once()
            call_args = mock_ws.send_json.call_args[0][0]
            assert call_args["type"] == "session_started"
            assert call_args["session_id"] == "test-session-123"
    
    @pytest.mark.asyncio
    async def test_bug1_websocket_end_session_returns_none(self):
        """
        Bug 1: Verifica que end_session retorna None
        """
        from backend.api.routes.websocket import handle_control_message
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        with patch('backend.api.routes.websocket.context_manager') as mock_ctx:
            mock_ctx.delete_session = Mock()
            
            import json
            control_msg = json.dumps({"type": "end_session"})
            
            result = await handle_control_message(mock_ws, control_msg, "old-session")
            
            # Verifica que retornou None
            assert result is None
            
            # Verifica que deletou sessão
            mock_ctx.delete_session.assert_called_once_with("old-session")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

