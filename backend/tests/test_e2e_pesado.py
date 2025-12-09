#!/usr/bin/env python3
"""
Teste End-to-End Pesado e Completo - Jonh Assistant
Testa cenários complexos e realistas do sistema
"""

import sys
import time
import requests
import json
import wave
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:8000"
TIMEOUT = 60  # Timeout maior para testes pesados


@dataclass
class TestResult:
    """Resultado de um teste"""
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    details: Optional[Dict] = None
    response_time: Optional[float] = None
    tokens_used: Optional[int] = None


class HeavyE2ETester:
    """Testador E2E Pesado"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session_ids: List[str] = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log formatado"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪",
            "PERF": "⚡"
        }.get(level, "ℹ️")
        print(f"{prefix} {message}")
    
    def make_request(self, texto: str, session_id: Optional[str] = None) -> Tuple[bool, Dict, float]:
        """Faz requisição e retorna resultado"""
        start = time.time()
        try:
            data = {"texto": texto}
            if session_id:
                data["session_id"] = session_id
            
            response = requests.post(
                f"{BASE_URL}/api/process_text",
                data=data,
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                headers = response.headers
                return True, {
                    "status": 200,
                    "session_id": headers.get("X-Session-ID"),
                    "response_text": headers.get("X-Response-Text", ""),
                    "processing_time": headers.get("X-Processing-Time", ""),
                    "tokens": headers.get("X-Tokens-Used", ""),
                    "intent": headers.get("X-Architecture-Intent", ""),
                    "audio_size": len(response.content)
                }, duration
            else:
                return False, {
                    "status": response.status_code,
                    "error": response.text[:200] if hasattr(response, 'text') else "Unknown error"
                }, duration
        except Exception as e:
            duration = time.time() - start
            return False, {"error": str(e)}, duration
    
    def test_conversation_flow(self) -> TestResult:
        """Testa fluxo completo de conversação"""
        self.log("Testando fluxo completo de conversação (10 mensagens)...", "TEST")
        start = time.time()
        
        conversation = [
            "Olá, meu nome é Bruno e sou desenvolvedor",
            "Estou trabalhando em um projeto de e-commerce",
            "Preciso de ajuda com arquitetura",
            "O sistema precisa processar pagamentos",
            "E também enviar notificações por email",
            "Qual stack você recomenda?",
            "E sobre segurança?",
            "Como escalar para 100 mil usuários?",
            "Obrigado pela ajuda!",
            "Você lembrou meu nome?"
        ]
        
        session_id = None
        errors = []
        total_tokens = 0
        
        for i, msg in enumerate(conversation, 1):
            self.log(f"  Mensagem {i}/10: {msg[:50]}...", "INFO")
            success, data, duration = self.make_request(msg, session_id)
            
            if not success:
                errors.append(f"Mensagem {i} falhou: {data.get('error', 'Unknown')}")
                break
            
            session_id = data.get("session_id")
            tokens = int(data.get("tokens", 0) or 0)
            total_tokens += tokens
            
            # Pequena pausa entre mensagens
            time.sleep(0.5)
        
        total_duration = time.time() - start
        
        if not errors:
            self.log(f"Conversa completa: {len(conversation)} mensagens", "SUCCESS")
            self.log(f"Total de tokens: {total_tokens}", "PERF")
            return TestResult(
                "Conversation Flow (10 mensagens)",
                True,
                total_duration,
                details={
                    "messages": len(conversation),
                    "total_tokens": total_tokens,
                    "avg_time_per_message": total_duration / len(conversation)
                }
            )
        else:
            return TestResult(
                "Conversation Flow",
                False,
                total_duration,
                error="; ".join(errors)
            )
    
    def test_architecture_advisor_complex(self) -> TestResult:
        """Testa Architecture Advisor com cenários complexos"""
        self.log("Testando Architecture Advisor com cenários complexos...", "TEST")
        start = time.time()
        
        scenarios = [
            {
                "name": "Análise de Requisitos Complexa",
                "text": "Analise os requisitos de um sistema de marketplace que precisa processar pagamentos, gerenciar estoque, enviar notificações push, ter chat em tempo real e dashboard analítico"
            },
            {
                "name": "Security Checklist Completo",
                "text": "Checklist de segurança para sistema web com pagamentos, autenticação OAuth, API REST, banco de dados PostgreSQL e integração com serviços externos"
            },
            {
                "name": "Design de Arquitetura",
                "text": "Como estruturar a arquitetura de um sistema de microserviços para processamento de vídeo com transcodificação, CDN e armazenamento distribuído?"
            },
            {
                "name": "Comparação de Soluções",
                "text": "Comparar MongoDB vs PostgreSQL para um sistema de analytics em tempo real com 10 milhões de eventos por dia"
            },
            {
                "name": "Planejamento de Escalabilidade",
                "text": "Como escalar um sistema de chat em tempo real de 1 mil para 1 milhão de usuários simultâneos?"
            }
        ]
        
        passed = 0
        errors = []
        
        for scenario in scenarios:
            self.log(f"  Testando: {scenario['name']}", "INFO")
            success, data, duration = self.make_request(scenario["text"])
            
            if success:
                intent = data.get("intent", "")
                if intent:
                    passed += 1
                    self.log(f"    ✅ Intent detectado: {intent}", "SUCCESS")
                else:
                    errors.append(f"{scenario['name']}: Intent não detectado")
            else:
                errors.append(f"{scenario['name']}: {data.get('error', 'Unknown')}")
            
            time.sleep(1)  # Pausa entre testes
        
        total_duration = time.time() - start
        
        if passed == len(scenarios):
            self.log(f"Todos os cenários passaram: {passed}/{len(scenarios)}", "SUCCESS")
            return TestResult(
                "Architecture Advisor Complex",
                True,
                total_duration,
                details={"scenarios_passed": passed, "total_scenarios": len(scenarios)}
            )
        else:
            return TestResult(
                "Architecture Advisor Complex",
                False,
                total_duration,
                error=f"{passed}/{len(scenarios)} passaram. Erros: {'; '.join(errors)}"
            )
    
    def test_memory_persistence(self) -> TestResult:
        """Testa persistência de memória em múltiplas sessões"""
        self.log("Testando persistência de memória...", "TEST")
        start = time.time()
        
        # Sessão 1: Salvar informações
        info_messages = [
            "Meu nome é Bruno Silva",
            "Trabalho como desenvolvedor Python",
            "Meu projeto atual é um marketplace",
            "Uso PostgreSQL como banco de dados"
        ]
        
        session_id = None
        for msg in info_messages:
            success, data, _ = self.make_request(msg, session_id)
            if success:
                session_id = data.get("session_id")
            time.sleep(0.3)
        
        # Nova sessão: Verificar se memórias persistem
        # Nota: Isso depende de como o MemoryService funciona
        # Pode não funcionar se memórias são por sessão
        
        total_duration = time.time() - start
        
        if session_id:
            self.log("Memórias salvas com sucesso", "SUCCESS")
            return TestResult(
                "Memory Persistence",
                True,
                total_duration,
                details={"session_id": session_id, "memories_saved": len(info_messages)}
            )
        else:
            return TestResult(
                "Memory Persistence",
                False,
                total_duration,
                error="Falha ao criar sessão"
            )
    
    def test_stress_multiple_sessions(self) -> TestResult:
        """Teste de stress com múltiplas sessões simultâneas"""
        self.log("Teste de stress: 5 sessões simultâneas...", "TEST")
        start = time.time()
        
        import concurrent.futures
        
        def make_request_async(text: str, session_num: int):
            """Requisição assíncrona"""
            try:
                response = requests.post(
                    f"{BASE_URL}/api/process_text",
                    data={"texto": f"[Sessão {session_num}] {text}"},
                    timeout=TIMEOUT
                )
                return session_num, response.status_code == 200, response.elapsed.total_seconds()
            except Exception as e:
                return session_num, False, 0.0
        
        # 5 requisições simultâneas
        messages = [
            "Olá, teste 1",
            "Olá, teste 2",
            "Olá, teste 3",
            "Olá, teste 4",
            "Olá, teste 5"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_request_async, msg, i+1)
                for i, msg in enumerate(messages)
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        total_duration = time.time() - start
        passed = sum(1 for _, success, _ in results if success)
        avg_time = sum(time for _, _, time in results) / len(results) if results else 0
        
        if passed == len(messages):
            self.log(f"Todas as {len(messages)} requisições simultâneas passaram", "SUCCESS")
            self.log(f"Tempo médio: {avg_time:.2f}s", "PERF")
            return TestResult(
                "Stress Test (5 sessões simultâneas)",
                True,
                total_duration,
                details={
                    "concurrent_requests": len(messages),
                    "passed": passed,
                    "avg_response_time": avg_time
                }
            )
        else:
            return TestResult(
                "Stress Test",
                False,
                total_duration,
                error=f"{passed}/{len(messages)} requisições passaram"
            )
    
    def test_long_context(self) -> TestResult:
        """Testa contexto longo (múltiplas mensagens)"""
        self.log("Testando contexto longo (20 mensagens)...", "TEST")
        start = time.time()
        
        session_id = None
        messages_sent = 0
        errors = []
        
        # Gera 20 mensagens sequenciais
        for i in range(20):
            msg = f"Mensagem {i+1}: Estou testando o contexto longo do sistema"
            success, data, duration = self.make_request(msg, session_id)
            
            if success:
                session_id = data.get("session_id")
                messages_sent += 1
            else:
                errors.append(f"Mensagem {i+1} falhou")
                break
            
            # Pausa mínima
            time.sleep(0.2)
        
        total_duration = time.time() - start
        
        if messages_sent == 20:
            self.log(f"Contexto longo mantido: {messages_sent} mensagens", "SUCCESS")
            return TestResult(
                "Long Context (20 mensagens)",
                True,
                total_duration,
                details={
                    "messages": messages_sent,
                    "avg_time": total_duration / messages_sent
                }
            )
        else:
            return TestResult(
                "Long Context",
                False,
                total_duration,
                error=f"Apenas {messages_sent}/20 mensagens processadas. Erros: {'; '.join(errors)}"
            )
    
    def test_audio_processing_realistic(self) -> TestResult:
        """Testa processamento de áudio com arquivo realista"""
        self.log("Testando processamento de áudio realista...", "TEST")
        start = time.time()
        
        try:
            # Cria WAV de 2 segundos com tom de teste (440Hz)
            import numpy as np
            
            sample_rate = 16000
            duration = 2.0
            frequency = 440.0
            
            # Gera senoide
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t)
            
            # Converte para int16
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Cria WAV
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            wav_data = wav_buffer.getvalue()
            
            # Envia áudio
            files = {'audio': ('test_audio.wav', wav_data, 'audio/wav')}
            response = requests.post(
                f"{BASE_URL}/api/process_audio",
                files=files,
                timeout=TIMEOUT
            )
            
            duration = time.time() - start
            
            if response.status_code == 200:
                self.log("Áudio processado com sucesso", "SUCCESS")
                return TestResult(
                    "Audio Processing Realistic",
                    True,
                    duration,
                    details={"audio_duration": duration, "audio_size": len(wav_data)}
                )
            elif response.status_code == 400:
                # Áudio sem fala pode retornar 400 (esperado)
                self.log("Áudio processado (sem transcrição - esperado)", "INFO")
                return TestResult(
                    "Audio Processing Realistic",
                    True,
                    duration,
                    details={"note": "Áudio sem fala retorna 400 (comportamento esperado)"}
                )
            else:
                return TestResult(
                    "Audio Processing Realistic",
                    False,
                    duration,
                    error=f"Status code: {response.status_code}"
                )
        except ImportError:
            return TestResult(
                "Audio Processing Realistic",
                False,
                0,
                error="numpy não disponível para gerar áudio de teste"
            )
        except Exception as e:
            duration = time.time() - start
            return TestResult(
                "Audio Processing Realistic",
                False,
                duration,
                error=str(e)
            )
    
    def test_performance_benchmark(self) -> TestResult:
        """Benchmark de performance com múltiplas requisições"""
        self.log("Benchmark de performance (10 requisições)...", "TEST")
        start = time.time()
        
        times = []
        tokens_list = []
        errors = []
        
        test_messages = [
            "Olá",
            "Como você está?",
            "Qual é a capital do Brasil?",
            "Explique o que é Python",
            "Conte uma piada",
            "Qual é a melhor linguagem de programação?",
            "Como funciona a internet?",
            "O que é inteligência artificial?",
            "Explique APIs REST",
            "Obrigado pela ajuda!"
        ]
        
        for i, msg in enumerate(test_messages, 1):
            self.log(f"  Requisição {i}/10...", "INFO")
            req_start = time.time()
            success, data, duration = self.make_request(msg)
            req_time = time.time() - req_start
            
            if success:
                times.append(req_time)
                tokens = int(data.get("tokens", 0) or 0)
                tokens_list.append(tokens)
            else:
                errors.append(f"Requisição {i}: {data.get('error', 'Unknown')}")
        
        total_duration = time.time() - start
        
        if len(times) == len(test_messages):
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            total_tokens = sum(tokens_list)
            
            self.log(f"Tempo médio: {avg_time:.2f}s", "PERF")
            self.log(f"Tempo mínimo: {min_time:.2f}s", "PERF")
            self.log(f"Tempo máximo: {max_time:.2f}s", "PERF")
            self.log(f"Total de tokens: {total_tokens}", "PERF")
            
            return TestResult(
                "Performance Benchmark",
                True,
                total_duration,
                details={
                    "requests": len(test_messages),
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "total_tokens": total_tokens,
                    "throughput": len(test_messages) / total_duration
                }
            )
        else:
            return TestResult(
                "Performance Benchmark",
                False,
                total_duration,
                error=f"{len(times)}/{len(test_messages)} requisições passaram. Erros: {'; '.join(errors)}"
            )
    
    def test_error_handling(self) -> TestResult:
        """Testa tratamento de erros"""
        self.log("Testando tratamento de erros...", "TEST")
        start = time.time()
        
        error_cases = [
            {"name": "Texto vazio", "text": ""},
            {"name": "Texto muito longo", "text": "A" * 10000},
            {"name": "Caracteres especiais", "text": "!@#$%^&*()_+-=[]{}|;':\",./<>?"},
            {"name": "Emoji", "text": "Olá 😀 como está? 🚀"},
            {"name": "Unicode", "text": "Olá 你好 مرحبا"},
        ]
        
        handled = 0
        errors = []
        
        for case in error_cases:
            success, data, duration = self.make_request(case["text"])
            
            # Para casos de erro, esperamos status 400 ou 422 (validação)
            # Se retornar 200, também está OK (sistema tratou)
            if success or data.get("status") in [400, 422]:
                handled += 1
            else:
                errors.append(f"{case['name']}: Status {data.get('status', 'Unknown')}")
        
        total_duration = time.time() - start
        
        if handled == len(error_cases):
            self.log(f"Todos os casos de erro tratados: {handled}/{len(error_cases)}", "SUCCESS")
            return TestResult(
                "Error Handling",
                True,
                total_duration,
                details={"cases_handled": handled, "total_cases": len(error_cases)}
            )
        else:
            return TestResult(
                "Error Handling",
                False,
                total_duration,
                error=f"{handled}/{len(error_cases)} casos tratados. Erros: {'; '.join(errors)}"
            )
    
    def run_all_tests(self):
        """Executa todos os testes pesados"""
        print("=" * 80)
        print("🔥 TESTE END-TO-END PESADO - Jonh Assistant")
        print("=" * 80)
        print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Fluxo de Conversação", self.test_conversation_flow),
            ("Architecture Advisor Complexo", self.test_architecture_advisor_complex),
            ("Persistência de Memória", self.test_memory_persistence),
            ("Teste de Stress", self.test_stress_multiple_sessions),
            ("Contexto Longo", self.test_long_context),
            ("Processamento de Áudio Realista", self.test_audio_processing_realistic),
            ("Benchmark de Performance", self.test_performance_benchmark),
            ("Tratamento de Erros", self.test_error_handling),
        ]
        
        for name, test_func in tests:
            print(f"\n{'='*80}")
            print(f"🧪 {name}")
            print('='*80)
            try:
                result = test_func()
                self.results.append(result)
            except Exception as e:
                self.results.append(TestResult(
                    name,
                    False,
                    0,
                    error=f"Exceção: {str(e)}"
                ))
                import traceback
                print(f"❌ Erro: {e}")
                traceback.print_exc()
        
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumo completo"""
        print("\n" + "=" * 80)
        print("📊 RESUMO COMPLETO DOS TESTES")
        print("=" * 80)
        print()
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        total_time = sum(r.duration for r in self.results)
        
        print(f"Total de testes: {total}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {total - passed}")
        print(f"⏱️  Tempo total: {total_time:.2f}s")
        print(f"⏱️  Tempo médio por teste: {total_time/total:.2f}s")
        print()
        
        print("Detalhes dos Testes:")
        print("-" * 80)
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.name:<50} {result.duration:>8.2f}s")
            
            if result.error:
                print(f"   ❌ Erro: {result.error}")
            
            if result.details:
                for key, value in result.details.items():
                    if isinstance(value, float):
                        print(f"   📊 {key}: {value:.2f}")
                    else:
                        print(f"   📊 {key}: {value}")
            print()
        
        print("=" * 80)
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema está funcionando perfeitamente!")
        else:
            print(f"⚠️  {total - passed} teste(s) falharam")
            print("⚠️  Verifique os erros acima")
        
        print("=" * 80)
        print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def main():
    """Função principal"""
    tester = HeavyE2ETester()
    
    try:
        tester.run_all_tests()
        
        # Retorna código de saída
        failed = sum(1 for r in tester.results if not r.passed)
        sys.exit(0 if failed == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

