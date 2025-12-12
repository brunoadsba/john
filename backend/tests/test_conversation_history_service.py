"""
Testes para ConversationHistoryService
"""
import pytest
import json
from pathlib import Path
import tempfile
import os

from backend.database.database import Database
from backend.services.conversation_history_service import ConversationHistoryService


@pytest.fixture
def temp_db():
    """Cria banco de dados temporário para testes"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db = Database(db_path=db_path)
    yield db
    
    # Cleanup
    db_path_obj = Path(db_path)
    if db_path_obj.exists():
        os.unlink(db_path)
    if db._connection:
        import asyncio
        asyncio.run(db.close())


@pytest.fixture
def history_service(temp_db):
    """Cria instância do serviço para testes"""
    return ConversationHistoryService(temp_db)


@pytest.mark.asyncio
async def test_save_conversation(history_service, temp_db):
    """Testa salvamento de conversa"""
    await temp_db.connect()
    
    conversation_id = await history_service.save_conversation(
        session_id="test-session-1",
        title="Teste de Conversa",
        messages=[
            {"role": "user", "content": "Olá"},
            {"role": "assistant", "content": "Oi! Como posso ajudar?"}
        ]
    )
    
    assert conversation_id > 0


@pytest.mark.asyncio
async def test_save_conversation_duplicate(history_service, temp_db):
    """Testa atualização de conversa existente"""
    await temp_db.connect()
    
    # Salva primeira vez
    id1 = await history_service.save_conversation(
        session_id="test-session-2",
        title="Título Original",
        messages=[{"role": "user", "content": "Mensagem 1"}]
    )
    
    # Atualiza com mesmo session_id
    id2 = await history_service.save_conversation(
        session_id="test-session-2",
        title="Título Atualizado",
        messages=[
            {"role": "user", "content": "Mensagem 1"},
            {"role": "assistant", "content": "Resposta 1"}
        ]
    )
    
    # Deve retornar o mesmo ID
    assert id1 == id2


@pytest.mark.asyncio
async def test_get_saved_conversations(history_service, temp_db):
    """Testa listagem de conversas salvas"""
    await temp_db.connect()
    
    # Salva algumas conversas
    await history_service.save_conversation(
        session_id="session-1",
        title="Conversa 1",
        messages=[{"role": "user", "content": "Teste 1"}]
    )
    
    await history_service.save_conversation(
        session_id="session-2",
        title="Conversa 2",
        messages=[{"role": "user", "content": "Teste 2"}]
    )
    
    # Lista conversas
    conversations = await history_service.get_saved_conversations(limit=10)
    
    assert len(conversations) >= 2
    assert all("id" in conv for conv in conversations)
    assert all("title" in conv for conv in conversations)


@pytest.mark.asyncio
async def test_get_conversation_by_id(history_service, temp_db):
    """Testa recuperação de conversa por ID"""
    await temp_db.connect()
    
    # Salva conversa
    conversation_id = await history_service.save_conversation(
        session_id="session-3",
        title="Conversa de Teste",
        messages=[
            {"role": "user", "content": "Pergunta"},
            {"role": "assistant", "content": "Resposta"}
        ]
    )
    
    # Recupera conversa
    conversation = await history_service.get_conversation_by_id(conversation_id)
    
    assert conversation is not None
    assert conversation["id"] == conversation_id
    assert conversation["title"] == "Conversa de Teste"
    assert len(conversation["messages"]) == 2
    assert conversation["messages"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_delete_conversation(history_service, temp_db):
    """Testa deleção de conversa"""
    await temp_db.connect()
    
    # Salva conversa
    conversation_id = await history_service.save_conversation(
        session_id="session-4",
        title="Conversa para Deletar",
        messages=[{"role": "user", "content": "Teste"}]
    )
    
    # Deleta
    deleted = await history_service.delete_conversation(conversation_id)
    assert deleted is True
    
    # Verifica que foi deletada
    conversation = await history_service.get_conversation_by_id(conversation_id)
    assert conversation is None


@pytest.mark.asyncio
async def test_update_conversation_title(history_service, temp_db):
    """Testa atualização de título"""
    await temp_db.connect()
    
    # Salva conversa
    conversation_id = await history_service.save_conversation(
        session_id="session-5",
        title="Título Antigo",
        messages=[{"role": "user", "content": "Teste"}]
    )
    
    # Atualiza título
    updated = await history_service.update_conversation_title(
        conversation_id,
        "Título Novo"
    )
    assert updated is True
    
    # Verifica atualização
    conversation = await history_service.get_conversation_by_id(conversation_id)
    assert conversation["title"] == "Título Novo"


@pytest.mark.asyncio
async def test_save_conversation_validation(history_service, temp_db):
    """Testa validações de salvamento"""
    await temp_db.connect()
    
    # Testa session_id vazio
    with pytest.raises(ValueError):
        await history_service.save_conversation(
            session_id="",
            title="Título",
            messages=[{"role": "user", "content": "Teste"}]
        )
    
    # Testa title vazio
    with pytest.raises(ValueError):
        await history_service.save_conversation(
            session_id="session",
            title="",
            messages=[{"role": "user", "content": "Teste"}]
        )
    
    # Testa messages vazio
    with pytest.raises(ValueError):
        await history_service.save_conversation(
            session_id="session",
            title="Título",
            messages=[]
        )


@pytest.mark.asyncio
async def test_get_conversations_pagination(history_service, temp_db):
    """Testa paginação na listagem"""
    await temp_db.connect()
    
    # Salva várias conversas
    for i in range(5):
        await history_service.save_conversation(
            session_id=f"session-pag-{i}",
            title=f"Conversa {i}",
            messages=[{"role": "user", "content": f"Mensagem {i}"}]
        )
    
    # Primeira página
    page1 = await history_service.get_saved_conversations(limit=2, offset=0)
    assert len(page1) == 2
    
    # Segunda página
    page2 = await history_service.get_saved_conversations(limit=2, offset=2)
    assert len(page2) == 2
    
    # Verifica que são diferentes
    assert page1[0]["id"] != page2[0]["id"]

