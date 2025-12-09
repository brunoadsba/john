"""
Testes do banco de dados e memória
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.database import Database
from backend.services.context_manager_db import ContextManagerDB
from backend.services.memory_service import MemoryService


@pytest.mark.asyncio
async def test_database_connection():
    """Testa conexão com banco de dados"""
    db = Database(":memory:")  # Banco em memória para testes
    await db.connect()
    assert db._connection is not None
    await db.close()


@pytest.mark.asyncio
async def test_database_sessions():
    """Testa criação e gerenciamento de sessões"""
    db = Database(":memory:")
    await db.connect()
    
    # Cria sessão
    session_id = "test-session-123"
    await db.create_session(session_id)
    
    # Verifica sessão
    session = await db.get_session(session_id)
    assert session is not None
    assert session["session_id"] == session_id
    
    # Adiciona mensagem
    await db.add_message(session_id, "user", "Olá")
    await db.add_message(session_id, "assistant", "Olá! Como posso ajudar?")
    
    # Verifica mensagens
    messages = await db.get_messages(session_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    
    await db.close()


@pytest.mark.asyncio
async def test_database_memories():
    """Testa salvamento e recuperação de memórias"""
    db = Database(":memory:")
    await db.connect()
    
    # Salva memória
    await db.save_memory("nome_usuario", "Bruno", "pessoal")
    
    # Recupera memória
    memory = await db.get_memory("nome_usuario")
    assert memory is not None
    assert memory["value"] == "Bruno"
    assert memory["category"] == "pessoal"
    
    # Busca memórias
    memories = await db.search_memories(query="Bruno")
    assert len(memories) > 0
    
    await db.close()


@pytest.mark.asyncio
async def test_context_manager_db():
    """Testa ContextManagerDB"""
    db = Database(":memory:")
    await db.connect()
    
    ctx = ContextManagerDB(db)
    
    # Cria sessão
    session_id = await ctx.create_session()
    assert session_id is not None
    
    # Adiciona mensagens
    await ctx.add_message(session_id, "user", "Olá")
    await ctx.add_message(session_id, "assistant", "Olá!")
    
    # Obtém contexto
    contexto = await ctx.get_context(session_id)
    assert len(contexto) == 2
    
    await db.close()


@pytest.mark.asyncio
async def test_memory_service():
    """Testa MemoryService"""
    db = Database(":memory:")
    await db.connect()
    
    mem = MemoryService(db)
    
    # Salva memória usando método do MemoryService
    await mem.save_explicit_memory("test_key", "test_value", "test")
    
    # Recupera memória
    result = await mem.get_memory("test_key")
    assert result is not None
    assert result["value"] == "test_value"
    
    # Busca memórias
    memories = await mem.search_memories(query="test")
    assert len(memories) > 0
    
    await db.close()

