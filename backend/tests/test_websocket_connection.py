#!/usr/bin/env python3
"""
Teste de conexão WebSocket para Feature 015
Valida comunicação mobile-backend
"""
import asyncio
import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from websockets.client import connect
from loguru import logger

# Configuração
WS_URL = "ws://localhost:8000/ws/listen"
TIMEOUT = 10


async def test_websocket_connection():
    """Testa conexão WebSocket básica"""
    logger.info("🔄 Testando conexão WebSocket...")
    
    try:
        async with connect(WS_URL) as websocket:
            logger.success("✅ WebSocket conectado com sucesso!")
            
            # Aguarda mensagem de confirmação
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"📨 Mensagem recebida: {message}")
                
                if isinstance(message, str):
                    data = json.loads(message)
                    logger.info(f"📋 Tipo: {data.get('type')}")
                    return True
                else:
                    logger.warning("⚠️ Mensagem não é JSON")
                    return False
                    
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout aguardando mensagem")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        return False


async def test_session_start():
    """Testa início de sessão"""
    logger.info("🔄 Testando início de sessão...")
    
    try:
        async with connect(WS_URL) as websocket:
            # Recebe mensagem de boas-vindas primeiro
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                if isinstance(welcome, str):
                    data = json.loads(welcome)
                    logger.info(f"📨 Mensagem de boas-vindas: {data.get('type')}")
            except asyncio.TimeoutError:
                pass  # Pode não receber imediatamente
            
            # Envia comando de início de sessão
            await websocket.send(json.dumps({"type": "start_session"}))
            logger.info("📤 Comando start_session enviado")
            
            # Aguarda resposta (pode receber múltiplas mensagens)
            for _ in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    logger.info(f"📨 Resposta: {message}")
                    
                    if isinstance(message, str):
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        if msg_type in ["session_started", "session_created"]:
                            session_id = data.get("session_id")
                            logger.success(f"✅ Sessão criada: {session_id}")
                            return True
                        elif msg_type == "connected":
                            # Continua aguardando
                            continue
                        else:
                            logger.info(f"   Tipo recebido: {msg_type}")
                            continue
                    else:
                        logger.warning("⚠️ Resposta não é JSON")
                        continue
                        
                except asyncio.TimeoutError:
                    logger.error("❌ Timeout aguardando resposta")
                    return False
            
            logger.warning("⚠️ Sessão não foi criada após múltiplas tentativas")
            return False
                
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


async def test_audio_send():
    """Testa envio de áudio (mock)"""
    logger.info("🔄 Testando envio de áudio...")
    
    try:
        async with connect(WS_URL) as websocket:
            # Inicia sessão
            await websocket.send(json.dumps({"type": "start_session"}))
            await asyncio.sleep(0.5)
            
            # Cria áudio mock válido (WAV header + dados reais)
            # WAV header = 44 bytes
            # 1 segundo de áudio a 16kHz, mono, 16-bit = 32000 bytes de dados
            sample_rate = 16000
            duration_seconds = 1
            num_channels = 1
            bits_per_sample = 16
            bytes_per_sample = bits_per_sample // 8
            data_size = sample_rate * duration_seconds * num_channels * bytes_per_sample
            
            wav_header = bytearray(44)
            wav_header[0:4] = b'RIFF'
            wav_header[4:8] = (36 + data_size).to_bytes(4, 'little')  # File size - 8
            wav_header[8:12] = b'WAVE'
            wav_header[12:16] = b'fmt '
            wav_header[16:20] = (16).to_bytes(4, 'little')  # fmt chunk size
            wav_header[20:22] = (1).to_bytes(2, 'little')  # Audio format (PCM)
            wav_header[22:24] = (num_channels).to_bytes(2, 'little')  # Channels (mono)
            wav_header[24:28] = (sample_rate).to_bytes(4, 'little')  # Sample rate
            wav_header[28:32] = (sample_rate * num_channels * bytes_per_sample).to_bytes(4, 'little')  # Byte rate
            wav_header[32:34] = (num_channels * bytes_per_sample).to_bytes(2, 'little')  # Block align
            wav_header[34:36] = (bits_per_sample).to_bytes(2, 'little')  # Bits per sample
            wav_header[36:40] = b'data'
            wav_header[40:44] = (data_size).to_bytes(4, 'little')  # Data size
            
            # Gera samples de silêncio (valores próximos de zero, não exatamente zero)
            # Isso evita o erro "zero-size array" do numpy
            import random
            audio_samples = bytearray(data_size)
            for i in range(0, data_size, 2):  # 16-bit = 2 bytes por sample
                # Gera valores muito pequenos mas não zero (-100 a +100)
                sample_value = random.randint(-100, 100)
                audio_samples[i:i+2] = sample_value.to_bytes(2, 'little', signed=True)
            
            audio_data = wav_header + audio_samples
            
            logger.info(f"📤 Enviando áudio mock: {len(audio_data)} bytes")
            await websocket.send(bytes(audio_data))
            
            # Aguarda resposta (transcription ou response)
            try:
                responses = []
                error_message = None
                
                for _ in range(10):  # Aguarda até 10 mensagens
                    message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    if isinstance(message, str):
                        data = json.loads(message)
                        responses.append(data)
                        msg_type = data.get('type')
                        logger.info(f"📨 Resposta {len(responses)}: {msg_type}")
                        
                        if msg_type == "error":
                            error_message = data.get('message', 'Erro desconhecido')
                            logger.warning(f"⚠️ Erro do servidor: {error_message}")
                            # Continua aguardando, pode haver mais mensagens
                            
                        elif msg_type == "response":
                            text = data.get('text', '')
                            logger.success(f"✅ Resposta recebida: {text[:50]}...")
                            return True
                            
                        elif msg_type == "transcription":
                            text = data.get('text', '')
                            logger.info(f"📝 Transcrição: {text[:50]}...")
                            # Continua aguardando resposta
                            
                    elif isinstance(message, bytes):
                        logger.success(f"✅ Áudio recebido: {len(message)} bytes")
                        return True
                        
                # Se chegou aqui, não recebeu resposta válida
                if error_message:
                    logger.error(f"❌ Erro durante processamento: {error_message}")
                else:
                    logger.warning("⚠️ Nenhuma resposta de texto ou áudio recebida")
                logger.info(f"📋 Respostas recebidas: {[r.get('type') for r in responses]}")
                return False
                
            except asyncio.TimeoutError:
                logger.error("❌ Timeout aguardando resposta")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


async def test_reconnection():
    """Testa reconexão após desconexão"""
    logger.info("🔄 Testando reconexão...")
    
    try:
        # Primeira conexão
        async with connect(WS_URL) as websocket:
            logger.success("✅ Primeira conexão estabelecida")
            await websocket.send(json.dumps({"type": "start_session"}))
            await asyncio.sleep(0.5)
        
        # Simula desconexão
        logger.info("⚠️ Desconectando...")
        await asyncio.sleep(1)
        
        # Segunda conexão (reconexão)
        async with connect(WS_URL) as websocket:
            logger.success("✅ Reconexão estabelecida")
            await websocket.send(json.dumps({"type": "start_session"}))
            
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.success("✅ Mensagem recebida após reconexão")
                return True
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout após reconexão")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


async def run_all_tests():
    """Executa todos os testes"""
    logger.info("🚀 Iniciando testes de WebSocket (Feature 015)")
    logger.info("=" * 60)
    
    results = {}
    
    # Teste 1: Conexão básica
    logger.info("\n📋 Teste 1: Conexão WebSocket")
    results["connection"] = await test_websocket_connection()
    
    # Teste 2: Início de sessão
    logger.info("\n📋 Teste 2: Início de Sessão")
    results["session"] = await test_session_start()
    
    # Teste 3: Envio de áudio
    logger.info("\n📋 Teste 3: Envio de Áudio")
    results["audio"] = await test_audio_send()
    
    # Teste 4: Reconexão
    logger.info("\n📋 Teste 4: Reconexão")
    results["reconnection"] = await test_reconnection()
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name.upper():20} {status}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    logger.info("=" * 60)
    logger.info(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.success("🎉 Todos os testes passaram!")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(130)

