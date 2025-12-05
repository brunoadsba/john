"""
Testes de integração do pipeline completo
"""
import pytest
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services import (
    WhisperSTTService,
    OllamaLLMService,
    PiperTTSService,
    ContextManager
)


class TestIntegration:
    """Testes de integração do sistema"""
    
    @pytest.fixture
    def context_manager(self):
        """Fixture do gerenciador de contexto"""
        return ContextManager(max_history=5, session_timeout=300)
    
    def test_context_manager_session(self, context_manager):
        """Testa criação e gerenciamento de sessões"""
        # Cria sessão
        session_id = context_manager.create_session()
        assert session_id is not None
        
        # Adiciona mensagens
        context_manager.add_message(session_id, "user", "Olá")
        context_manager.add_message(session_id, "assistant", "Olá! Como posso ajudar?")
        
        # Verifica contexto
        contexto = context_manager.get_context(session_id)
        assert len(contexto) == 2
        assert contexto[0]["role"] == "user"
        assert contexto[1]["role"] == "assistant"
        
        # Verifica informações da sessão
        info = context_manager.get_session_info(session_id)
        assert info is not None
        assert info["message_count"] == 2
        assert info["is_active"] is True
        
        # Remove sessão
        context_manager.delete_session(session_id)
        info = context_manager.get_session_info(session_id)
        assert info is None
    
    def test_context_manager_history_limit(self, context_manager):
        """Testa limite de histórico"""
        session_id = context_manager.create_session()
        
        # Adiciona mais mensagens que o limite
        for i in range(10):
            context_manager.add_message(session_id, "user", f"Mensagem {i}")
        
        # Verifica que mantém apenas as últimas 5
        contexto = context_manager.get_context(session_id)
        assert len(contexto) == 5
        assert contexto[-1]["content"] == "Mensagem 9"
    
    @pytest.mark.skipif(
        not Path("/usr/local/bin/ollama").exists(),
        reason="Ollama não instalado"
    )
    def test_llm_service_basic(self):
        """Testa serviço LLM básico"""
        llm = OllamaLLMService(
            model="llama3:8b-instruct-q4_0",
            host="http://localhost:11434"
        )
        
        # Verifica se está pronto
        if llm.is_ready():
            # Gera resposta simples
            resposta, tokens = llm.generate_response("Olá, como você está?")
            
            assert resposta is not None
            assert len(resposta) > 0
            assert tokens > 0
            print(f"\nResposta do LLM: {resposta}")
    
    def test_tts_service_mock(self):
        """Testa serviço TTS (versão mock)"""
        tts = PiperTTSService(voice="pt_BR-faber-medium")
        
        # Verifica se está pronto
        assert tts.is_ready() is True
        
        # Sintetiza texto
        audio_data = tts.synthesize("Olá, este é um teste.")
        
        assert audio_data is not None
        assert len(audio_data) > 0
        assert isinstance(audio_data, bytes)


@pytest.mark.asyncio
class TestAPIIntegration:
    """Testes de integração da API"""
    
    @pytest.fixture
    async def client(self):
        """Fixture do cliente HTTP"""
        from httpx import AsyncClient
        from backend.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    async def test_root_endpoint(self, client):
        """Testa endpoint raiz"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Jonh Assistant API"
        assert data["status"] == "online"
    
    async def test_health_endpoint(self, client):
        """Testa health check"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "servicos" in data
        assert "versao" in data
    
    async def test_sessions_endpoint(self, client):
        """Testa listagem de sessões"""
        response = await client.get("/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

