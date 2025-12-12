"""
Testes de integração para funcionalidades de localização
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.context_manager_db import ContextManagerDB
from backend.database.database import Database


@pytest.fixture
async def db():
    """Cria instância temporária do banco de dados"""
    db_path = ":memory:"  # Banco em memória para testes
    database = Database(db_path=db_path)
    await database.connect()
    yield database
    await database.close()


@pytest.fixture
async def context_manager(db):
    """Cria instância do ContextManagerDB"""
    return ContextManagerDB(database=db, max_history=10, session_timeout=3600)


@pytest.mark.asyncio
async def test_context_manager_db_set_location(context_manager):
    """Testa armazenamento de localização no ContextManagerDB"""
    # Cria sessão
    session_id = await context_manager.create_session()
    
    # Define localização
    lat = -23.5505
    lon = -46.6333
    address_info = {
        "city": "São Paulo",
        "state": "São Paulo",
        "country": "Brasil",
        "address": "São Paulo, São Paulo, Brasil"
    }
    
    await context_manager.set_location(session_id, lat, lon, address_info)
    
    # Recupera localização
    location = await context_manager.get_location(session_id)
    
    assert location is not None
    assert location["latitude"] == lat
    assert location["longitude"] == lon
    assert location["address_info"]["city"] == "São Paulo"


@pytest.mark.asyncio
async def test_context_manager_db_get_location_nonexistent(context_manager):
    """Testa recuperação de localização inexistente"""
    location = await context_manager.get_location("nonexistent-session-id")
    assert location is None


@pytest.mark.asyncio
async def test_context_manager_db_location_update(context_manager):
    """Testa atualização de localização"""
    session_id = await context_manager.create_session()
    
    # Primeira localização
    await context_manager.set_location(
        session_id, -23.5505, -46.6333, {"city": "São Paulo"}
    )
    
    # Atualiza para nova localização
    await context_manager.set_location(
        session_id, -22.9068, -43.1729, {"city": "Rio de Janeiro"}
    )
    
    location = await context_manager.get_location(session_id)
    
    assert location["latitude"] == -22.9068
    assert location["longitude"] == -43.1729
    assert location["address_info"]["city"] == "Rio de Janeiro"

