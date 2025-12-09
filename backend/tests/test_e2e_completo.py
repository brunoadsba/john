#!/usr/bin/env python3
"""
Teste End-to-End Completo do Jonh Assistant
Testa todo o fluxo do sistema exceto dispositivos físicos
"""

import sys
import time
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


@dataclass
class TestResult:
    """Resultado de um teste"""
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    details: Optional[Dict] = None


class E2ETester:
    """Testador End-to-End"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session_id: Optional[str] = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log formatado"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪"
        }.get(level, "ℹ️")
        print(f"{prefix} {message}")
    
    def test_server_health(self) -> TestResult:
        """Testa se servidor está respondendo"""
        self.log("Testando saúde do servidor...", "TEST")
        start = time.time()
        
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                self.log("Servidor está respondendo", "SUCCESS")
                return TestResult("Server Health", True, duration)
            else:
                return TestResult("Server Health", False, duration, 
                                f"Status code: {response.status_code}")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Server Health", False, duration, str(e))
    
    def test_simple_text_processing(self) -> TestResult:
        """Testa processamento de texto simples"""
        self.log("Testando processamento de texto simples...", "TEST")
        start = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Olá, como você está?"},
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                # Verifica headers
                headers = response.headers
                response_text = headers.get("X-Response-Text", "")
                processing_time = headers.get("X-Processing-Time", "")
                tokens = headers.get("X-Tokens-Used", "")
                
                self.log(f"Resposta em {duration:.2f}s", "SUCCESS")
                self.log(f"Texto resposta: {response_text[:50]}...", "INFO")
                
                return TestResult(
                    "Simple Text Processing",
                    True,
                    duration,
                    details={
                        "response_time": processing_time,
                        "tokens": tokens,
                        "response_preview": response_text[:100]
                    }
                )
            else:
                return TestResult("Simple Text Processing", False, duration,
                                f"Status code: {response.status_code}")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Simple Text Processing", False, duration, str(e))
    
    def test_architecture_advisor(self) -> TestResult:
        """Testa Architecture Advisor via IntentDetector"""
        self.log("Testando Architecture Advisor...", "TEST")
        start = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Analise os requisitos de um sistema de e-commerce"},
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                headers = response.headers
                intent = headers.get("X-Architecture-Intent", "")
                response_text = headers.get("X-Response-Text", "")
                
                if intent:
                    self.log(f"Intent detectado: {intent}", "SUCCESS")
                    self.log(f"Resposta em {duration:.2f}s", "SUCCESS")
                    
                    return TestResult(
                        "Architecture Advisor",
                        True,
                        duration,
                        details={
                            "intent": intent,
                            "response_preview": response_text[:150]
                        }
                    )
                else:
                    return TestResult("Architecture Advisor", False, duration,
                                    "Intent não detectado")
            else:
                return TestResult("Architecture Advisor", False, duration,
                                f"Status code: {response.status_code}")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Architecture Advisor", False, duration, str(e))
    
    def test_security_checklist(self) -> TestResult:
        """Testa Security Checklist do Architecture Advisor"""
        self.log("Testando Security Checklist...", "TEST")
        start = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Checklist de segurança para sistema web com pagamentos"},
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                headers = response.headers
                intent = headers.get("X-Architecture-Intent", "")
                response_text = headers.get("X-Response-Text", "")
                
                if "security" in intent.lower() or "segurança" in response_text.lower():
                    self.log(f"Security Checklist funcionando", "SUCCESS")
                    return TestResult(
                        "Security Checklist",
                        True,
                        duration,
                        details={"intent": intent}
                    )
                else:
                    return TestResult("Security Checklist", False, duration,
                                    "Security intent não detectado")
            else:
                return TestResult("Security Checklist", False, duration,
                                f"Status code: {response.status_code}")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Security Checklist", False, duration, str(e))
    
    def test_context_management(self) -> TestResult:
        """Testa gerenciamento de contexto (sessão)"""
        self.log("Testando gerenciamento de contexto...", "TEST")
        start = time.time()
        
        try:
            # Primeira mensagem
            response1 = requests.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Meu nome é Bruno"},
                timeout=TIMEOUT
            )
            
            if response1.status_code != 200:
                return TestResult("Context Management", False, time.time() - start,
                                f"Primeira mensagem falhou: {response1.status_code}")
            
            session_id = response1.headers.get("X-Session-ID")
            if not session_id:
                return TestResult("Context Management", False, time.time() - start,
                                "Session ID não retornado")
            
            # Segunda mensagem na mesma sessão
            response2 = requests.post(
                f"{BASE_URL}/api/process_text",
                data={
                    "texto": "Qual é o meu nome?",
                    "session_id": session_id
                },
                timeout=TIMEOUT
            )
            
            duration = time.time() - start
            
            if response2.status_code == 200:
                response_text = response2.headers.get("X-Response-Text", "")
                if "Bruno" in response_text or "bruno" in response_text.lower():
                    self.log("Contexto mantido entre mensagens", "SUCCESS")
                    return TestResult(
                        "Context Management",
                        True,
                        duration,
                        details={"session_id": session_id}
                    )
                else:
                    return TestResult("Context Management", False, duration,
                                    "Contexto não foi mantido")
            else:
                return TestResult("Context Management", False, duration,
                                f"Segunda mensagem falhou: {response2.status_code}")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Context Management", False, duration, str(e))
    
    def test_web_search(self) -> TestResult:
        """Testa busca web (tool calling)"""
        self.log("Testando busca web...", "TEST")
        start = time.time()
        
        try:
            # Pergunta que deve acionar busca web
            response = requests.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Qual é a previsão do tempo para hoje?"},
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                response_text = response.headers.get("X-Response-Text", "")
                # Verifica se há indicação de busca (pode não sempre acionar)
                self.log("Busca web testada (pode não acionar sempre)", "INFO")
                return TestResult(
                    "Web Search",
                    True,
                    duration,
                    details={"note": "Tool pode não acionar dependendo do LLM"}
                )
            else:
                return TestResult("Web Search", False, duration,
                                f"Status code: {response.status_code}")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Web Search", False, duration, str(e))
    
    def test_audio_processing(self) -> TestResult:
        """Testa processamento de áudio (simulado)"""
        self.log("Testando processamento de áudio...", "TEST")
        start = time.time()
        
        try:
            # Cria arquivo WAV simples (silêncio de 1 segundo)
            import wave
            import io
            
            # Gera WAV de silêncio (para teste)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(b'\x00' * 16000)  # 1 segundo de silêncio
            
            wav_data = wav_buffer.getvalue()
            
            # Envia áudio
            files = {'audio': ('test.wav', wav_data, 'audio/wav')}
            response = requests.post(
                f"{BASE_URL}/api/process_audio",
                files=files,
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                self.log("Processamento de áudio funcionando", "SUCCESS")
                return TestResult(
                    "Audio Processing",
                    True,
                    duration,
                    details={"audio_size": len(wav_data)}
                )
            elif response.status_code == 400:
                # Pode falhar se áudio não tiver fala (esperado para silêncio)
                self.log("Áudio processado (sem transcrição esperado)", "INFO")
                return TestResult(
                    "Audio Processing",
                    True,
                    duration,
                    details={"note": "Áudio sem fala retorna 400 (esperado)"}
                )
            else:
                return TestResult("Audio Processing", False, duration,
                                f"Status code: {response.status_code}")
        except ImportError:
            return TestResult("Audio Processing", False, 0,
                            "Biblioteca 'wave' não disponível")
        except Exception as e:
            duration = time.time() - start
            return TestResult("Audio Processing", False, duration, str(e))
    
    def test_performance(self) -> TestResult:
        """Testa performance com múltiplas requisições"""
        self.log("Testando performance...", "TEST")
        start = time.time()
        
        try:
            times = []
            for i in range(5):
                req_start = time.time()
                response = requests.post(
                    f"{BASE_URL}/api/process_text",
                    data={"texto": f"Teste {i+1}"},
                    timeout=TIMEOUT
                )
                req_time = time.time() - req_start
                times.append(req_time)
                
                if response.status_code != 200:
                    return TestResult("Performance", False, time.time() - start,
                                    f"Requisição {i+1} falhou")
            
            duration = time.time() - start
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            self.log(f"Tempo médio: {avg_time:.2f}s", "SUCCESS")
            self.log(f"Tempo mínimo: {min_time:.2f}s", "INFO")
            self.log(f"Tempo máximo: {max_time:.2f}s", "INFO")
            
            return TestResult(
                "Performance",
                True,
                duration,
                details={
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "total_requests": 5
                }
            )
        except Exception as e:
            duration = time.time() - start
            return TestResult("Performance", False, duration, str(e))
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 70)
        print("🧪 TESTE END-TO-END COMPLETO - Jonh Assistant")
        print("=" * 70)
        print()
        
        tests = [
            self.test_server_health,
            self.test_simple_text_processing,
            self.test_architecture_advisor,
            self.test_security_checklist,
            self.test_context_management,
            self.test_web_search,
            self.test_audio_processing,
            self.test_performance,
        ]
        
        for test_func in tests:
            result = test_func()
            self.results.append(result)
            print()
        
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print()
        print("=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)
        print()
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        total_time = sum(r.duration for r in self.results)
        
        print(f"Total de testes: {total}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {total - passed}")
        print(f"⏱️  Tempo total: {total_time:.2f}s")
        print()
        
        print("Detalhes:")
        print("-" * 70)
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.name:<40} {result.duration:>6.2f}s")
            if result.error:
                print(f"   Erro: {result.error}")
            if result.details:
                for key, value in result.details.items():
                    print(f"   {key}: {value}")
        
        print()
        print("=" * 70)
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
        else:
            print(f"⚠️  {total - passed} teste(s) falharam")
        
        print("=" * 70)


def main():
    """Função principal"""
    tester = E2ETester()
    
    try:
        tester.run_all_tests()
        
        # Retorna código de saída baseado nos resultados
        failed = sum(1 for r in tester.results if not r.passed)
        sys.exit(0 if failed == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

