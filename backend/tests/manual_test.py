"""
Script de teste manual da API
"""
import sys
from pathlib import Path
import requests
import wave
import numpy as np

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_test_audio(filename: str = "test_audio.wav", duration: float = 2.0):
    """
    Cria arquivo de áudio de teste
    
    Args:
        filename: Nome do arquivo
        duration: Duração em segundos
    """
    sample_rate = 16000
    samples = int(sample_rate * duration)
    
    # Gera tom de 440 Hz (Lá)
    t = np.linspace(0, duration, samples)
    audio_data = np.sin(2 * np.pi * 440 * t)
    
    # Converte para int16
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Salva como WAV
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"Arquivo de teste criado: {filename}")
    return filename


def test_health_check(base_url: str = "http://localhost:8000"):
    """Testa health check"""
    print("\n" + "=" * 60)
    print("TESTE 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False


def test_root(base_url: str = "http://localhost:8000"):
    """Testa endpoint raiz"""
    print("\n" + "=" * 60)
    print("TESTE 2: Endpoint Raiz")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False


def test_synthesize(base_url: str = "http://localhost:8000"):
    """Testa síntese de voz"""
    print("\n" + "=" * 60)
    print("TESTE 3: Síntese de Voz (TTS)")
    print("=" * 60)
    
    try:
        texto = "Olá, este é um teste do assistente Jonh."
        
        response = requests.post(
            f"{base_url}/api/synthesize",
            data={"texto": texto}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Tamanho do áudio: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Salva áudio
            output_file = "output_tts.wav"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Áudio salvo em: {output_file}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Erro: {e}")
        return False


def test_process_audio(base_url: str = "http://localhost:8000"):
    """Testa processamento completo de áudio"""
    print("\n" + "=" * 60)
    print("TESTE 4: Processamento Completo (STT -> LLM -> TTS)")
    print("=" * 60)
    
    try:
        # Cria áudio de teste
        audio_file = create_test_audio("test_input.wav", duration=1.0)
        
        # Envia para processamento
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            response = requests.post(
                f"{base_url}/api/process_audio",
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Mostra headers informativos
            print(f"Transcrição: {response.headers.get('X-Transcription', 'N/A')}")
            print(f"Resposta: {response.headers.get('X-Response-Text', 'N/A')}")
            print(f"Session ID: {response.headers.get('X-Session-ID', 'N/A')}")
            print(f"Tempo: {response.headers.get('X-Processing-Time', 'N/A')}s")
            print(f"Tokens: {response.headers.get('X-Tokens-Used', 'N/A')}")
            
            # Salva áudio de resposta
            output_file = "output_response.wav"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Áudio de resposta salvo em: {output_file}")
            
            return True
        else:
            print(f"Erro: {response.text}")
            return False
        
    except Exception as e:
        print(f"Erro: {e}")
        return False
    finally:
        # Limpa arquivo de teste
        if Path("test_input.wav").exists():
            Path("test_input.wav").unlink()


def test_sessions(base_url: str = "http://localhost:8000"):
    """Testa gerenciamento de sessões"""
    print("\n" + "=" * 60)
    print("TESTE 5: Gerenciamento de Sessões")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/sessions")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Sessões ativas: {data['total']}")
            for session in data['sessions']:
                print(f"  - {session['session_id']}: {session['message_count']} mensagens")
            return True
        
        return False
        
    except Exception as e:
        print(f"Erro: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("SCRIPT DE TESTE MANUAL - JONH ASSISTANT API")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print(f"\nTestando API em: {base_url}")
    print("Certifique-se de que o servidor está rodando!")
    
    input("\nPressione ENTER para continuar...")
    
    # Executa testes
    resultados = {
        "Health Check": test_health_check(base_url),
        "Endpoint Raiz": test_root(base_url),
        "Síntese de Voz": test_synthesize(base_url),
        "Processamento Completo": test_process_audio(base_url),
        "Gerenciamento de Sessões": test_sessions(base_url)
    }
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for teste, resultado in resultados.items():
        status = "✓ PASSOU" if resultado else "✗ FALHOU"
        print(f"{teste}: {status}")
    
    total = len(resultados)
    passou = sum(resultados.values())
    print(f"\nTotal: {passou}/{total} testes passaram")
    
    return passou == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

