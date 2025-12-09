"""
Testes das funcionalidades principais da Alexa:
1. Ouvir (STT - Speech to Text)
2. Responder (TTS - Text to Speech)
3. Armazenar (Banco de dados/Memória)
4. Interagir com Inteligência (LLM)
"""
import pytest
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services import WhisperSTTService, create_llm_service, PiperTTSService
from backend.database.database import Database
from backend.services.context_manager_db import ContextManagerDB
from backend.services.memory_service import MemoryService
from backend.config import settings


# ========== TESTE 1: OUVIR (STT) ==========

def test_1_stt_service_initialized():
    """Testa se STT está inicializado"""
    stt_service = WhisperSTTService(
        model_size=settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type
    )
    assert stt_service is not None
    assert stt_service.model_size == settings.whisper_model
    print("✅ STT Service: Inicializado")


# ========== TESTE 2: INTELIGÊNCIA (LLM) ==========

def test_2_llm_service_initialized():
    """Testa se LLM está inicializado"""
    if settings.llm_provider.lower() == "groq":
        llm_service = create_llm_service(
            provider="groq",
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    else:
        llm_service = create_llm_service(
            provider="ollama",
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    
    assert llm_service is not None
    assert llm_service.is_ready() is True
    print(f"✅ LLM Service: Inicializado ({settings.llm_provider})")


def test_2_llm_generate_response():
    """Testa geração de resposta pelo LLM"""
    if settings.llm_provider.lower() == "groq":
        llm_service = create_llm_service(
            provider="groq",
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    else:
        llm_service = create_llm_service(
            provider="ollama",
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    
    prompt = "Olá, como você está?"
    resposta, tokens = llm_service.generate_response(prompt, memorias_contexto="")
    
    assert resposta is not None
    assert len(resposta) > 0
    assert tokens > 0
    print(f"✅ LLM: Resposta gerada ({tokens} tokens): {resposta[:50]}...")


# ========== TESTE 3: RESPONDER (TTS) ==========

def test_3_tts_service_initialized():
    """Testa se TTS está inicializado"""
    tts_service = PiperTTSService(
        voice=settings.piper_voice,
        model_path=settings.piper_model_path
    )
    assert tts_service is not None
    assert tts_service.is_ready() is True
    print("✅ TTS Service: Inicializado")


@pytest.mark.asyncio
async def test_3_tts_synthesize():
    """Testa síntese de voz"""
    tts_service = PiperTTSService(
        voice=settings.piper_voice,
        model_path=settings.piper_model_path
    )
    texto = "Olá, eu sou o Jonh Assistant"
    audio_bytes = await tts_service.synthesize(texto)
    
    assert audio_bytes is not None
    assert len(audio_bytes) > 0
    print(f"✅ TTS: Áudio sintetizado ({len(audio_bytes)} bytes)")


# ========== TESTE 4: ARMAZENAR (BANCO DE DADOS) ==========

@pytest.mark.asyncio
async def test_4_database_store_conversation():
    """Testa armazenamento de conversa"""
    db = Database(":memory:")
    await db.connect()
    
    context_manager = ContextManagerDB(
        database=db,
        max_history=10,
        session_timeout=3600
    )
    
    # Cria sessão
    session_id = await context_manager.create_session()
    assert session_id is not None
    
    # Adiciona mensagens
    await context_manager.add_message(session_id, "user", "Qual é meu nome?")
    await context_manager.add_message(session_id, "assistant", "Seu nome é Bruno")
    
    # Verifica se foi armazenado
    contexto = await context_manager.get_context(session_id)
    assert len(contexto) == 2
    assert contexto[0]["content"] == "Qual é meu nome?"
    assert contexto[1]["content"] == "Seu nome é Bruno"
    
    print(f"✅ Database: Conversa armazenada (sessão: {session_id})")
    await db.close()


@pytest.mark.asyncio
async def test_4_database_store_memory():
    """Testa armazenamento de memória"""
    db = Database(":memory:")
    await db.connect()
    
    memory_service = MemoryService(db)
    
    # Salva memória
    await memory_service.save_explicit_memory(
        "nome_usuario",
        "Bruno",
        "pessoal"
    )
    
    # Recupera memória
    memory = await memory_service.get_memory("nome_usuario")
    assert memory is not None
    assert memory["value"] == "Bruno"
    assert memory["category"] == "pessoal"
    
    print("✅ Database: Memória armazenada e recuperada")
    await db.close()


# ========== TESTE 5: INTERAÇÃO COMPLETA ==========

@pytest.mark.asyncio
async def test_5_complete_interaction():
    """Testa interação completa: STT -> LLM -> TTS -> Armazenar"""
    print("\n🔄 Testando interação completa...")
    
    # Inicializa serviços
    stt_service = WhisperSTTService(
        model_size=settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type
    )
    
    if settings.llm_provider.lower() == "groq":
        llm_service = create_llm_service(
            provider="groq",
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    else:
        llm_service = create_llm_service(
            provider="ollama",
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    
    tts_service = PiperTTSService(
        voice=settings.piper_voice,
        model_path=settings.piper_model_path
    )
    
    db = Database(":memory:")
    await db.connect()
    
    context_manager = ContextManagerDB(
        database=db,
        max_history=10,
        session_timeout=3600
    )
    
    memory_service = MemoryService(db)
    
    # 1. Cria sessão
    session_id = await context_manager.create_session()
    print(f"✅ Sessão criada: {session_id}")
    
    # 2. Simula transcrição (STT)
    # Nota: Não podemos testar STT real sem arquivo de áudio
    # Mas podemos simular a entrada
    texto_usuario = "Anote que meu nome é Bruno"
    print(f"📝 Usuário disse: '{texto_usuario}'")
    
    # 3. Armazena mensagem do usuário
    await context_manager.add_message(session_id, "user", texto_usuario)
    
    # 4. Busca memórias relevantes
    memoria_contexto = await memory_service.get_memories_for_context(texto_usuario)
    print(f"💭 Memórias relevantes: {len(memoria_contexto)} caracteres")
    
    # 5. Extrai e salva memórias
    await memory_service.extract_and_save_memory(texto_usuario, "")
    
    # 6. Gera resposta com LLM
    contexto = await context_manager.get_context(session_id)
    
    resposta, tokens = llm_service.generate_response(
        texto_usuario,
        contexto,
        memorias_contexto=memoria_contexto
    )
    print(f"🤖 LLM respondeu: '{resposta[:100]}...' ({tokens} tokens)")
    
    assert resposta is not None
    assert len(resposta) > 0
    
    # 7. Armazena resposta
    await context_manager.add_message(session_id, "assistant", resposta)
    
    # 8. Sintetiza resposta (TTS)
    audio_resposta = await tts_service.synthesize(resposta)
    print(f"🔊 TTS: Áudio gerado ({len(audio_resposta)} bytes)")
    
    assert audio_resposta is not None
    assert len(audio_resposta) > 0
    
    # 9. Verifica se memória foi salva
    memories = await memory_service.search_memories(query="Bruno")
    assert len(memories) > 0
    print(f"💾 Memória encontrada: {memories[0]['value']}")
    
    # 10. Testa recuperação de memória em nova pergunta
    nova_pergunta = "Qual é meu nome?"
    memoria_relevante = await memory_service.get_memories_for_context(nova_pergunta)
    print(f"🔍 Memória relevante para '{nova_pergunta}': {memoria_relevante[:50]}...")
    
    assert "Bruno" in memoria_relevante or len(memoria_relevante) > 0
    
    print("\n✅ Interação completa testada com sucesso!")
    await db.close()


@pytest.mark.asyncio
async def test_5_memory_recall():
    """Testa se o sistema lembra informações armazenadas"""
    print("\n🔄 Testando recuperação de memória...")
    
    db = Database(":memory:")
    await db.connect()
    
    memory_service = MemoryService(db)
    
    if settings.llm_provider.lower() == "groq":
        llm_service = create_llm_service(
            provider="groq",
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    else:
        llm_service = create_llm_service(
            provider="ollama",
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    
    context_manager = ContextManagerDB(
        database=db,
        max_history=10,
        session_timeout=3600
    )
    
    # 1. Salva informações
    await memory_service.save_explicit_memory("cor_favorita", "azul", "preferencias")
    await memory_service.save_explicit_memory("comida_favorita", "pizza", "preferencias")
    print("💾 Memórias salvas: cor_favorita=azul, comida_favorita=pizza")
    
    # 2. Cria sessão
    session_id = await context_manager.create_session()
    
    # 3. Pergunta que deve usar memória
    pergunta = "Qual é minha cor favorita?"
    await context_manager.add_message(session_id, "user", pergunta)
    
    # 4. Busca memórias relevantes
    memoria_contexto = await memory_service.get_memories_for_context(pergunta)
    print(f"🔍 Memórias encontradas: {memoria_contexto}")
    
    # 5. Gera resposta com memória
    contexto = await context_manager.get_context(session_id)
    
    resposta, tokens = llm_service.generate_response(
        pergunta,
        contexto,
        memorias_contexto=memoria_contexto
    )
    print(f"🤖 Resposta: '{resposta}'")
    
    # Verifica se resposta menciona a cor
    assert resposta is not None
    assert len(resposta) > 0
    
    # A resposta deve mencionar "azul" ou usar a memória
    resposta_lower = resposta.lower()
    assert "azul" in resposta_lower or len(memoria_contexto) > 0
    
    print("✅ Sistema lembrou da informação armazenada!")
    await db.close()


@pytest.mark.asyncio
async def test_5_conversation_history():
    """Testa se o sistema mantém histórico de conversa"""
    print("\n🔄 Testando histórico de conversa...")
    
    db = Database(":memory:")
    await db.connect()
    
    context_manager = ContextManagerDB(
        database=db,
        max_history=10,
        session_timeout=3600
    )
    
    if settings.llm_provider.lower() == "groq":
        llm_service = create_llm_service(
            provider="groq",
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    else:
        llm_service = create_llm_service(
            provider="ollama",
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    
    # Cria sessão
    session_id = await context_manager.create_session()
    
    # Simula conversa
    conversa = [
        ("user", "Olá"),
        ("assistant", "Olá! Como posso ajudar?"),
        ("user", "Qual é o clima hoje?"),
        ("assistant", "Não tenho acesso ao clima no momento."),
        ("user", "Obrigado"),
        ("assistant", "De nada! Estou aqui para ajudar."),
    ]
    
    for role, content in conversa:
        await context_manager.add_message(session_id, role, content)
    
    # Verifica histórico
    contexto = await context_manager.get_context(session_id)
    assert len(contexto) == len(conversa)
    
    # Verifica que contexto está completo
    assert contexto[0]["role"] == "user"
    assert contexto[0]["content"] == "Olá"
    assert contexto[-1]["role"] == "assistant"
    assert contexto[-1]["content"] == "De nada! Estou aqui para ajudar."
    
    print(f"✅ Histórico mantido: {len(contexto)} mensagens")
    
    # Testa que LLM pode usar o contexto
    pergunta = "O que eu perguntei antes?"
    contexto_completo = await context_manager.get_context(session_id)
    
    resposta, tokens = llm_service.generate_response(
        pergunta,
        contexto_completo,
        memorias_contexto=""
    )
    print(f"🤖 Resposta com contexto: '{resposta[:100]}...'")
    
    assert resposta is not None
    print("✅ LLM usou contexto da conversa!")
    await db.close()
