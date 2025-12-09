#!/usr/bin/env python3
"""
Teste End-to-End Profissional - Jonh Assistant
Teste equilibrado com validações inteligentes, métricas detalhadas e relatórios estruturados
"""

import sys
import time
import requests
import json
import wave
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import statistics

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:8000"
TIMEOUT = 60
REPORT_FILE = Path(__file__).parent / "e2e_report.json"


class TestStatus(Enum):
    """Status do teste"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class ResponseMetrics:
    """Métricas de uma resposta"""
    status_code: int
    response_time: float
    audio_size: int
    tokens_used: int = 0
    response_length: int = 0
    has_session_id: bool = False
    has_intent: bool = False
    processing_time: Optional[float] = None


@dataclass
class QualityScore:
    """Score de qualidade de uma resposta"""
    relevance: float = 0.0  # 0-1: Relevância da resposta
    completeness: float = 0.0  # 0-1: Completude da resposta
    structure: float = 0.0  # 0-1: Estrutura correta
    performance: float = 0.0  # 0-1: Performance (baseado em tempo)
    
    @property
    def overall(self) -> float:
        """Score geral (média ponderada)"""
        return (self.relevance * 0.4 + 
                self.completeness * 0.3 + 
                self.structure * 0.2 + 
                self.performance * 0.1)


@dataclass
class TestResult:
    """Resultado de um teste com métricas detalhadas"""
    name: str
    status: TestStatus
    duration: float
    error: Optional[str] = None
    metrics: Optional[ResponseMetrics] = None
    quality: Optional[QualityScore] = None
    details: Dict[str, Any] = field(default_factory=dict)
    assertions: List[Tuple[str, bool, Optional[str]]] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Compatibilidade com código antigo"""
        return self.status == TestStatus.PASSED


class ProfessionalE2ETester:
    """Testador E2E Profissional com validações inteligentes"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o testador
        
        Args:
            config: Configuração opcional (num_conversation_messages, etc)
        """
        self.config = {
            "num_conversation_messages": 5,  # Reduzido para equilíbrio
            "num_stress_requests": 3,  # Reduzido para não sobrecarregar
            "num_performance_tests": 5,  # Equilibrado
            "enable_audio_test": True,
            "enable_stress_test": True,
            "strict_validation": True,  # Validações mais rigorosas
            **{**(config or {})}
        }
        self.results: List[TestResult] = []
        self.session_ids: List[str] = []
        self.baseline_metrics: Dict[str, float] = {}  # Para detectar regressões
        
    def log(self, message: str, level: str = "INFO", indent: int = 0):
        """Log formatado com indentação"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪",
            "PERF": "⚡",
            "QUALITY": "📊"
        }.get(level, "ℹ️")
        indent_str = "  " * indent
        print(f"{indent_str}{prefix} {message}")
    
    def make_request(self, texto: str, session_id: Optional[str] = None) -> Tuple[bool, Dict, ResponseMetrics]:
        """
        Faz requisição e retorna resultado com métricas detalhadas
        
        Returns:
            (success, data, metrics)
        """
        start = time.time()
        metrics = ResponseMetrics(status_code=0, response_time=0.0, audio_size=0)
        
        try:
            data = {"texto": texto}
            if session_id:
                data["session_id"] = session_id
            
            response = requests.post(
                f"{BASE_URL}/api/process_text",
                data=data,
                timeout=TIMEOUT
            )
            
            metrics.response_time = time.time() - start
            metrics.status_code = response.status_code
            metrics.audio_size = len(response.content)
            
            if response.status_code == 200:
                headers = response.headers
                metrics.tokens_used = int(headers.get("X-Tokens-Used", 0) or 0)
                response_text = headers.get("X-Response-Text", "")
                metrics.response_length = len(response_text)
                metrics.has_session_id = bool(headers.get("X-Session-ID"))
                metrics.has_intent = bool(headers.get("X-Architecture-Intent"))
                
                proc_time = headers.get("X-Processing-Time", "")
                if proc_time:
                    try:
                        metrics.processing_time = float(proc_time)
                    except ValueError:
                        pass
                
                return True, {
                    "status": 200,
                    "session_id": headers.get("X-Session-ID"),
                    "response_text": response_text,
                    "processing_time": proc_time,
                    "tokens": metrics.tokens_used,
                    "intent": headers.get("X-Architecture-Intent", ""),
                    "audio_size": metrics.audio_size
                }, metrics
            else:
                return False, {
                    "status": response.status_code,
                    "error": response.text[:500] if hasattr(response, 'text') else "Unknown error"
                }, metrics
        except Exception as e:
            metrics.response_time = time.time() - start
            return False, {"error": str(e)}, metrics
    
    def validate_response_structure(self, data: Dict, metrics: ResponseMetrics) -> Tuple[bool, List[str]]:
        """
        Valida estrutura da resposta
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        is_valid = True
        
        # Validações básicas
        if metrics.status_code != 200:
            issues.append(f"Status code inválido: {metrics.status_code}")
            is_valid = False
        
        if not metrics.has_session_id:
            issues.append("Session ID ausente nos headers")
            is_valid = False
        
        if metrics.audio_size == 0:
            issues.append("Áudio de resposta vazio")
            is_valid = False
        
        if metrics.response_time > 30.0:  # Timeout prático
            issues.append(f"Tempo de resposta muito alto: {metrics.response_time:.2f}s")
            is_valid = False
        
        # Validações de qualidade (se strict_validation)
        if self.config["strict_validation"]:
            if metrics.response_length < 10:
                issues.append(f"Resposta muito curta: {metrics.response_length} caracteres")
                is_valid = False
            
            if metrics.tokens_used == 0:
                issues.append("Tokens usados = 0 (pode indicar problema)")
        
        return is_valid, issues
    
    def calculate_quality_score(self, data: Dict, metrics: ResponseMetrics, expected_intent: bool = False) -> QualityScore:
        """Calcula score de qualidade da resposta"""
        score = QualityScore()
        
        # Relevance: Resposta não vazia e tem conteúdo
        if metrics.response_length > 0:
            score.relevance = min(1.0, metrics.response_length / 100.0)  # Normaliza
        
        # Completeness: Tem todos os elementos esperados
        completeness_items = 0
        total_items = 3
        
        if metrics.has_session_id:
            completeness_items += 1
        if metrics.audio_size > 0:
            completeness_items += 1
        if metrics.tokens_used > 0:
            completeness_items += 1
        
        score.completeness = completeness_items / total_items
        
        # Structure: Estrutura correta
        structure_items = 0
        total_structure = 2
        
        if metrics.status_code == 200:
            structure_items += 1
        if "response_text" in data:
            structure_items += 1
        
        score.structure = structure_items / total_structure
        
        # Performance: Baseado em tempo de resposta
        # Ideal: < 2s, Aceitável: < 5s, Ruim: > 10s
        if metrics.response_time < 2.0:
            score.performance = 1.0
        elif metrics.response_time < 5.0:
            score.performance = 0.8
        elif metrics.response_time < 10.0:
            score.performance = 0.5
        else:
            score.performance = 0.2
        
        return score
    
    def test_conversation_flow(self) -> TestResult:
        """Testa fluxo de conversação com validações inteligentes"""
        self.log("Testando fluxo de conversação", "TEST")
        start = time.time()
        
        num_messages = self.config["num_conversation_messages"]
        conversation = [
            "Olá, meu nome é Bruno e sou desenvolvedor",
            "Estou trabalhando em um projeto de e-commerce",
            "Preciso de ajuda com arquitetura do sistema",
            "O sistema precisa processar pagamentos e notificações",
            "Qual stack você recomenda?"
        ][:num_messages]
        
        session_id = None
        all_metrics: List[ResponseMetrics] = []
        assertions = []
        errors = []
        
        for i, msg in enumerate(conversation, 1):
            self.log(f"Mensagem {i}/{num_messages}: {msg[:40]}...", "INFO", indent=1)
            success, data, metrics = self.make_request(msg, session_id)
            
            all_metrics.append(metrics)
            
            # Validações por mensagem
            is_valid, issues = self.validate_response_structure(data, metrics)
            assertions.append((f"Mensagem {i} válida", is_valid, "; ".join(issues) if issues else None))
            
            if not success:
                errors.append(f"Mensagem {i} falhou: {data.get('error', 'Unknown')}")
                break
            
            session_id = data.get("session_id")
            time.sleep(0.3)  # Pausa entre mensagens
        
        total_duration = time.time() - start
        
        # Calcula métricas agregadas
        avg_response_time = statistics.mean([m.response_time for m in all_metrics]) if all_metrics else 0
        total_tokens = sum([m.tokens_used for m in all_metrics])
        
        # Determina status
        if not errors and all(a[1] for a in assertions):
            status = TestStatus.PASSED
        elif not errors:
            status = TestStatus.WARNING
        else:
            status = TestStatus.FAILED
        
        # Calcula qualidade média
        avg_quality = QualityScore()
        if all_metrics:
            qualities = [self.calculate_quality_score({}, m) for m in all_metrics]
            avg_quality.relevance = statistics.mean([q.relevance for q in qualities])
            avg_quality.completeness = statistics.mean([q.completeness for q in qualities])
            avg_quality.structure = statistics.mean([q.structure for q in qualities])
            avg_quality.performance = statistics.mean([q.performance for q in qualities])
        
        return TestResult(
            name="Conversation Flow",
            status=status,
            duration=total_duration,
            error="; ".join(errors) if errors else None,
            metrics=ResponseMetrics(
                status_code=200 if not errors else 0,
                response_time=avg_response_time,
                audio_size=0,
                tokens_used=total_tokens
            ),
            quality=avg_quality,
            details={
                "messages_processed": len([m for m in all_metrics if m.status_code == 200]),
                "total_messages": num_messages,
                "avg_response_time": avg_response_time,
                "total_tokens": total_tokens,
                "session_id": session_id
            },
            assertions=assertions
        )
    
    def test_architecture_advisor(self) -> TestResult:
        """Testa Architecture Advisor com validações de qualidade"""
        self.log("Testando Architecture Advisor", "TEST")
        start = time.time()
        
        scenarios = [
            {
                "name": "Análise de Requisitos",
                "text": "Analise os requisitos de um sistema de marketplace com pagamentos, estoque e notificações",
                "expect_intent": True
            },
            {
                "name": "Security Checklist",
                "text": "Checklist de segurança para sistema web com pagamentos e autenticação OAuth",
                "expect_intent": True
            },
            {
                "name": "Design de Arquitetura",
                "text": "Como estruturar arquitetura de microserviços para processamento de vídeo?",
                "expect_intent": True
            }
        ]
        
        passed = 0
        all_metrics: List[ResponseMetrics] = []
        assertions = []
        errors = []
        
        for scenario in scenarios:
            self.log(f"  Cenário: {scenario['name']}", "INFO", indent=1)
            success, data, metrics = self.make_request(scenario["text"])
            
            all_metrics.append(metrics)
            
            if success:
                intent_detected = metrics.has_intent
                expected = scenario.get("expect_intent", False)
                
                if expected and intent_detected:
                    passed += 1
                    assertions.append((f"Intent detectado em {scenario['name']}", True, None))
                elif expected:
                    errors.append(f"{scenario['name']}: Intent não detectado")
                    assertions.append((f"Intent detectado em {scenario['name']}", False, "Intent esperado mas não detectado"))
                else:
                    passed += 1  # Não esperava intent, então está OK
            else:
                errors.append(f"{scenario['name']}: {data.get('error', 'Unknown')}")
                assertions.append((f"{scenario['name']} processado", False, data.get('error')))
            
            time.sleep(0.5)
        
        total_duration = time.time() - start
        
        # Calcula qualidade média
        avg_quality = QualityScore()
        if all_metrics:
            qualities = [self.calculate_quality_score({}, m, expected_intent=True) for m in all_metrics]
            avg_quality.relevance = statistics.mean([q.relevance for q in qualities])
            avg_quality.completeness = statistics.mean([q.completeness for q in qualities])
            avg_quality.structure = statistics.mean([q.structure for q in qualities])
            avg_quality.performance = statistics.mean([q.performance for q in qualities])
        
        status = TestStatus.PASSED if passed == len(scenarios) and not errors else TestStatus.FAILED
        
        return TestResult(
            name="Architecture Advisor",
            status=status,
            duration=total_duration,
            error="; ".join(errors) if errors else None,
            metrics=ResponseMetrics(
                status_code=200 if passed == len(scenarios) else 0,
                response_time=statistics.mean([m.response_time for m in all_metrics]) if all_metrics else 0,
                audio_size=0,
                tokens_used=sum([m.tokens_used for m in all_metrics])
            ),
            quality=avg_quality,
            details={
                "scenarios_passed": passed,
                "total_scenarios": len(scenarios),
                "intent_detection_rate": passed / len(scenarios) if scenarios else 0
            },
            assertions=assertions
        )
    
    def test_performance_benchmark(self) -> TestResult:
        """Benchmark de performance com análise estatística"""
        self.log("Benchmark de performance", "TEST")
        start = time.time()
        
        num_tests = self.config["num_performance_tests"]
        test_messages = [
            "Olá",
            "Como você está?",
            "Explique o que é Python",
            "Qual é a melhor linguagem de programação?",
            "Obrigado pela ajuda!"
        ][:num_tests]
        
        times = []
        tokens_list = []
        all_metrics: List[ResponseMetrics] = []
        errors = []
        
        for i, msg in enumerate(test_messages, 1):
            self.log(f"  Requisição {i}/{num_tests}...", "INFO", indent=1)
            success, data, metrics = self.make_request(msg)
            
            all_metrics.append(metrics)
            
            if success:
                times.append(metrics.response_time)
                tokens_list.append(metrics.tokens_used)
            else:
                errors.append(f"Requisição {i}: {data.get('error', 'Unknown')}")
        
        total_duration = time.time() - start
        
        if len(times) == num_tests:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            total_tokens = sum(tokens_list)
            
            self.log(f"Tempo médio: {avg_time:.2f}s", "PERF", indent=1)
            self.log(f"Mediana: {median_time:.2f}s", "PERF", indent=1)
            self.log(f"Desvio padrão: {std_dev:.2f}s", "PERF", indent=1)
            
            # Valida performance
            assertions = [
                ("Tempo médio < 10s", avg_time < 10.0, f"Tempo médio: {avg_time:.2f}s"),
                ("Tempo máximo < 30s", max_time < 30.0, f"Tempo máximo: {max_time:.2f}s"),
                ("Throughput > 0.1 req/s", (num_tests / total_duration) > 0.1, None)
            ]
            
            # Calcula qualidade
            avg_quality = QualityScore()
            if all_metrics:
                qualities = [self.calculate_quality_score({}, m) for m in all_metrics]
                avg_quality.relevance = statistics.mean([q.relevance for q in qualities])
                avg_quality.completeness = statistics.mean([q.completeness for q in qualities])
                avg_quality.structure = statistics.mean([q.structure for q in qualities])
                avg_quality.performance = statistics.mean([q.performance for q in qualities])
            
            return TestResult(
                name="Performance Benchmark",
                status=TestStatus.PASSED,
                duration=total_duration,
                metrics=ResponseMetrics(
                    status_code=200,
                    response_time=avg_time,
                    audio_size=0,
                    tokens_used=total_tokens
                ),
                quality=avg_quality,
                details={
                    "requests": num_tests,
                    "avg_time": avg_time,
                    "median_time": median_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "std_dev": std_dev,
                    "total_tokens": total_tokens,
                    "throughput": num_tests / total_duration
                },
                assertions=assertions
            )
        else:
            return TestResult(
                name="Performance Benchmark",
                status=TestStatus.FAILED,
                duration=total_duration,
                error=f"{len(times)}/{num_tests} requisições passaram",
                details={"errors": errors}
            )
    
    def test_error_handling(self) -> TestResult:
        """Testa tratamento de erros com validações inteligentes"""
        self.log("Testando tratamento de erros", "TEST")
        start = time.time()
        
        error_cases = [
            {"name": "Texto vazio", "text": "", "expected_status": [400, 422]},
            {"name": "Emoji", "text": "Olá 😀 como está? 🚀", "expected_status": [200]},  # Deve funcionar agora
            {"name": "Unicode", "text": "Olá 你好 مرحبا", "expected_status": [200]},  # Deve funcionar
            {"name": "Texto muito longo", "text": "A" * 5000, "expected_status": [200, 400, 422]},
        ]
        
        handled = 0
        assertions = []
        errors = []
        
        for case in error_cases:
            success, data, metrics = self.make_request(case["text"])
            expected = case["expected_status"]
            actual_status = metrics.status_code
            
            # Verifica se status está nos esperados
            is_handled = actual_status in expected or success
            assertions.append((
                f"{case['name']} tratado corretamente",
                is_handled,
                f"Status {actual_status} não está em {expected}" if not is_handled else None
            ))
            
            if is_handled:
                handled += 1
            else:
                errors.append(f"{case['name']}: Status {actual_status} inesperado")
        
        total_duration = time.time() - start
        
        status = TestStatus.PASSED if handled == len(error_cases) else TestStatus.FAILED
        
        return TestResult(
            name="Error Handling",
            status=status,
            duration=total_duration,
            error="; ".join(errors) if errors else None,
            details={"cases_handled": handled, "total_cases": len(error_cases)},
            assertions=assertions
        )
    
    def test_stress_concurrent(self) -> TestResult:
        """Teste de stress com requisições concorrentes (equilibrado)"""
        if not self.config["enable_stress_test"]:
            return TestResult(
                name="Stress Test",
                status=TestStatus.SKIPPED,
                duration=0,
                details={"reason": "Desabilitado na configuração"}
            )
        
        self.log("Teste de stress (concorrência)", "TEST")
        start = time.time()
        
        num_requests = self.config["num_stress_requests"]
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
        
        messages = [f"Teste de stress {i+1}" for i in range(num_requests)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(make_request_async, msg, i+1)
                for i, msg in enumerate(messages)
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        total_duration = time.time() - start
        passed = sum(1 for _, success, _ in results if success)
        avg_time = statistics.mean([time for _, _, time in results]) if results else 0
        
        status = TestStatus.PASSED if passed == num_requests else TestStatus.FAILED
        
        return TestResult(
            name="Stress Test (Concorrência)",
            status=status,
            duration=total_duration,
            error=None if passed == num_requests else f"{passed}/{num_requests} passaram",
            details={
                "concurrent_requests": num_requests,
                "passed": passed,
                "avg_response_time": avg_time
            }
        )
    
    def run_all_tests(self):
        """Executa todos os testes e gera relatório"""
        print("=" * 80)
        print("🧪 TESTE END-TO-END PROFISSIONAL - Jonh Assistant")
        print("=" * 80)
        print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Configuração: {json.dumps(self.config, indent=2)}")
        print()
        
        tests = [
            ("Fluxo de Conversação", self.test_conversation_flow),
            ("Architecture Advisor", self.test_architecture_advisor),
            ("Benchmark de Performance", self.test_performance_benchmark),
            ("Tratamento de Erros", self.test_error_handling),
            ("Teste de Stress", self.test_stress_concurrent),
        ]
        
        for name, test_func in tests:
            print(f"\n{'='*80}")
            print(f"🧪 {name}")
            print('='*80)
            try:
                result = test_func()
                self.results.append(result)
                self._print_test_result(result)
            except Exception as e:
                error_result = TestResult(
                    name,
                    TestStatus.FAILED,
                    0,
                    error=f"Exceção: {str(e)}"
                )
                self.results.append(error_result)
                import traceback
                self.log(f"Erro: {e}", "ERROR")
                traceback.print_exc()
        
        self._generate_report()
        self._print_summary()
    
    def _print_test_result(self, result: TestResult):
        """Imprime resultado de um teste"""
        status_icon = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌",
            TestStatus.WARNING: "⚠️",
            TestStatus.SKIPPED: "⏭️"
        }.get(result.status, "❓")
        
        print(f"{status_icon} Status: {result.status.value}")
        print(f"   Duração: {result.duration:.2f}s")
        
        if result.error:
            print(f"   Erro: {result.error}")
        
        if result.quality:
            print(f"   Qualidade: {result.quality.overall:.2%} (R:{result.quality.relevance:.2%}, "
                  f"C:{result.quality.completeness:.2%}, S:{result.quality.structure:.2%}, "
                  f"P:{result.quality.performance:.2%})")
        
        if result.metrics:
            print(f"   Tempo médio: {result.metrics.response_time:.2f}s")
            if result.metrics.tokens_used > 0:
                print(f"   Tokens: {result.metrics.tokens_used}")
        
        if result.assertions:
            for assertion_name, passed, error in result.assertions:
                icon = "✅" if passed else "❌"
                print(f"   {icon} {assertion_name}" + (f": {error}" if error else ""))
    
    def _generate_report(self):
        """Gera relatório JSON para CI/CD"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.status == TestStatus.PASSED),
                "failed": sum(1 for r in self.results if r.status == TestStatus.FAILED),
                "warnings": sum(1 for r in self.results if r.status == TestStatus.WARNING),
                "skipped": sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
                "total_duration": sum(r.duration for r in self.results)
            },
            "results": []
        }
        
        # Converte resultados para dict (manualmente para lidar com enums)
        for r in self.results:
            result_dict = {
                "name": r.name,
                "status": r.status.value,
                "duration": r.duration,
                "error": r.error,
                "metrics": asdict(r.metrics) if r.metrics else None,
                "quality": asdict(r.quality) if r.quality else None,
                "details": r.details,
                "assertions": r.assertions
            }
            report["results"].append(result_dict)
        
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"Relatório JSON salvo em: {REPORT_FILE}", "INFO")
    
    def _print_summary(self):
        """Imprime resumo completo"""
        print("\n" + "=" * 80)
        print("📊 RESUMO COMPLETO")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        total = len(self.results)
        total_time = sum(r.duration for r in self.results)
        
        print(f"Total de testes: {total}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⚠️  Avisos: {warnings}")
        print(f"⏭️  Pulado: {skipped}")
        print(f"⏱️  Tempo total: {total_time:.2f}s")
        print()
        
        print("Detalhes dos Testes:")
        print("-" * 80)
        for result in self.results:
            status_icon = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌",
                TestStatus.WARNING: "⚠️",
                TestStatus.SKIPPED: "⏭️"
            }.get(result.status, "❓")
            
            quality_str = f" | Qualidade: {result.quality.overall:.1%}" if result.quality else ""
            print(f"{status_icon} {result.name:<40} {result.duration:>8.2f}s{quality_str}")
            
            if result.error:
                print(f"   ❌ Erro: {result.error}")
        
        print("=" * 80)
        
        if failed == 0 and warnings == 0:
            print("🎉 TODOS OS TESTES PASSARAM!")
        elif failed == 0:
            print("✅ Todos os testes passaram (com avisos)")
        else:
            print(f"⚠️  {failed} teste(s) falharam")
        
        print(f"📄 Relatório JSON: {REPORT_FILE}")
        print("=" * 80)
        print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste E2E Profissional - Jonh Assistant")
    parser.add_argument("--quick", action="store_true", help="Modo rápido (menos testes)")
    parser.add_argument("--full", action="store_true", help="Modo completo (mais testes)")
    parser.add_argument("--no-stress", action="store_true", help="Desabilitar teste de stress")
    parser.add_argument("--config", type=str, help="Arquivo JSON com configuração customizada")
    
    args = parser.parse_args()
    
    # Configuração base
    config = {}
    
    if args.quick:
        config = {
            "num_conversation_messages": 3,
            "num_stress_requests": 2,
            "num_performance_tests": 3,
            "enable_stress_test": not args.no_stress
        }
    elif args.full:
        config = {
            "num_conversation_messages": 10,
            "num_stress_requests": 5,
            "num_performance_tests": 10,
            "enable_stress_test": not args.no_stress
        }
    else:
        # Modo equilibrado (padrão)
        config = {
            "num_conversation_messages": 5,
            "num_stress_requests": 3,
            "num_performance_tests": 5,
            "enable_stress_test": not args.no_stress
        }
    
    if args.config:
        with open(args.config, "r") as f:
            custom_config = json.load(f)
            config.update(custom_config)
    
    tester = ProfessionalE2ETester(config)
    
    try:
        tester.run_all_tests()
        
        # Retorna código de saída
        failed = sum(1 for r in tester.results if r.status == TestStatus.FAILED)
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

