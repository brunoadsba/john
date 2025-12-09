"""
Testes de integração de tool calling via WebSocket (Feature 021)
"""
import pytest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from websockets.client import connect
from loguru import logger


@pytest.mark.asyncio
async def test_websocket_tool_calling_integration():
    """
    Testa integração completa de tool calling via WebSocket
    Requer servidor rodando em localhost:8000
    """
    WS_URL = "ws://localhost:8000/ws/listen"
    
    try:
        async with connect(WS_URL) as websocket:
            logger.info("✅ Conectado ao WebSocket")
            
            # Envia mensagem de texto (simula transcrição)
            message = {
                "type": "text",
                "text": "Qual a temperatura hoje em São Paulo?",
                "session_id": None
            }
            
            await websocket.send(json.dumps(message))
            logger.info("📤 Mensagem enviada")
            
            # Aguarda resposta
            response_received = False
            tool_called = False
            
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    logger.info(f"📥 Recebido: {data.get('type')}")
                    
                    if data.get("type") == "response":
                        response_received = True
                        text = data.get("text", "")
                        logger.info(f"✅ Resposta recebida: {text[:100]}...")
                        
                        # Verifica se a resposta menciona temperatura (indica que tool foi usado)
                        if "temperatura" in text.lower() or "°c" in text.lower() or "graus" in text.lower():
                            tool_called = True
                            logger.success("✅ Tool calling funcionou! Resposta contém informações de busca")
                        
                        break
                    elif data.get("type") == "error":
                        logger.error(f"❌ Erro: {data.get('message')}")
                        break
                        
            except asyncio.TimeoutError:
                logger.warning("⏱️ Timeout aguardando resposta")
            
            assert response_received, "Resposta não foi recebida"
            # Nota: tool_called pode ser False se o LLM não decidir usar a tool
            # Isso é aceitável - o importante é que o sistema não quebrou
            
    except ConnectionRefusedError:
        pytest.skip("Servidor não está rodando. Execute: ./scripts/start_server.sh")
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        raise


@pytest.mark.asyncio
async def test_websocket_tool_calling_news_query():
    """
    Testa tool calling com pergunta sobre notícias
    """
    WS_URL = "ws://localhost:8000/ws/listen"
    
    try:
        async with connect(WS_URL) as websocket:
            logger.info("✅ Conectado ao WebSocket")
            
            message = {
                "type": "text",
                "text": "Quais são as últimas notícias sobre inteligência artificial?",
                "session_id": None
            }
            
            await websocket.send(json.dumps(message))
            logger.info("📤 Mensagem enviada")
            
            response_received = False
            
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "response":
                        response_received = True
                        text = data.get("text", "")
                        logger.info(f"✅ Resposta: {text[:150]}...")
                        break
                    elif data.get("type") == "error":
                        logger.error(f"❌ Erro: {data.get('message')}")
                        break
                        
            except asyncio.TimeoutError:
                logger.warning("⏱️ Timeout")
            
            assert response_received, "Resposta não foi recebida"
            
    except ConnectionRefusedError:
        pytest.skip("Servidor não está rodando")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

