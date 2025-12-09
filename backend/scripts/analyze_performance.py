"""
Script para análise de performance do pipeline Jonh
Instrumenta todas as etapas e gera relatório detalhado
"""
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from loguru import logger

from backend.services.stt_service import WhisperSTTService
from backend.services.llm_service import BaseLLMService
from backend.services.tts_service import PiperTTSService
from backend.config.settings import settings


@dataclass
class PerformanceMetrics:
    """Métricas de performance de uma requisição"""
    timestamp: float
    audio_duration: float
    stt_time: float
    stt_confidence: float
    context_prep_time: float
    llm_time: float
    llm_tokens: int
    tts_time: float
    tts_text_length: int
    total_time: float
    network_time: float = 0.0
    cache_hit: bool = False


class PerformanceAnalyzer:
    """Analisador de performance do pipeline"""
    
    def __init__(self, output_dir: str = "data/performance"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: List[PerformanceMetrics] = []
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Registra métricas de uma requisição"""
        self.metrics.append(metrics)
        logger.info(
            f"📊 Métricas: STT={metrics.stt_time:.2f}s, "
            f"LLM={metrics.llm_time:.2f}s, TTS={metrics.tts_time:.2f}s, "
            f"Total={metrics.total_time:.2f}s"
        )
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        if not self.metrics:
            return {"error": "Nenhuma métrica coletada"}
        
        # Calcula estatísticas
        stt_times = [m.stt_time for m in self.metrics]
        llm_times = [m.llm_time for m in self.metrics]
        tts_times = [m.tts_time for m in self.metrics]
        total_times = [m.total_time for m in self.metrics]
        
        # Percentis
        def percentile(data: List[float], p: float) -> float:
            sorted_data = sorted(data)
            index = int(len(sorted_data) * p / 100)
            return sorted_data[min(index, len(sorted_data) - 1)]
        
        report = {
            "total_requests": len(self.metrics),
            "stt": {
                "mean": sum(stt_times) / len(stt_times),
                "median": percentile(stt_times, 50),
                "p95": percentile(stt_times, 95),
                "p99": percentile(stt_times, 99),
                "min": min(stt_times),
                "max": max(stt_times)
            },
            "llm": {
                "mean": sum(llm_times) / len(llm_times),
                "median": percentile(llm_times, 50),
                "p95": percentile(llm_times, 95),
                "p99": percentile(llm_times, 99),
                "min": min(llm_times),
                "max": max(llm_times)
            },
            "tts": {
                "mean": sum(tts_times) / len(tts_times),
                "median": percentile(tts_times, 50),
                "p95": percentile(tts_times, 95),
                "p99": percentile(tts_times, 99),
                "min": min(tts_times),
                "max": max(tts_times)
            },
            "total": {
                "mean": sum(total_times) / len(total_times),
                "median": percentile(total_times, 50),
                "p95": percentile(total_times, 95),
                "p99": percentile(total_times, 99),
                "min": min(total_times),
                "max": max(total_times)
            },
            "cache_hit_rate": sum(1 for m in self.metrics if m.cache_hit) / len(self.metrics) * 100,
            "average_audio_duration": sum(m.audio_duration for m in self.metrics) / len(self.metrics),
            "average_response_length": sum(m.tts_text_length for m in self.metrics) / len(self.metrics)
        }
        
        return report
    
    def save_report(self, filename: str = "performance_report.json"):
        """Salva relatório em arquivo"""
        report = self.generate_report()
        report_path = self.output_dir / filename
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Relatório salvo em: {report_path}")
        return report
    
    def print_summary(self):
        """Imprime resumo das métricas"""
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE PERFORMANCE - JONH ASSISTANT")
        print("=" * 60)
        print(f"\nTotal de requisições: {report['total_requests']}")
        print(f"Taxa de cache hit: {report['cache_hit_rate']:.1f}%")
        print(f"\nDuração média de áudio: {report['average_audio_duration']:.2f}s")
        print(f"Tamanho médio de resposta: {report['average_response_length']:.0f} caracteres")
        
        print("\n" + "-" * 60)
        print("STT (Speech-to-Text)")
        print("-" * 60)
        stt = report['stt']
        print(f"  Média:    {stt['mean']:.2f}s")
        print(f"  Mediana:  {stt['median']:.2f}s")
        print(f"  P95:      {stt['p95']:.2f}s")
        print(f"  P99:      {stt['p99']:.2f}s")
        print(f"  Min/Max:  {stt['min']:.2f}s / {stt['max']:.2f}s")
        
        print("\n" + "-" * 60)
        print("LLM (Large Language Model)")
        print("-" * 60)
        llm = report['llm']
        print(f"  Média:    {llm['mean']:.2f}s")
        print(f"  Mediana:  {llm['median']:.2f}s")
        print(f"  P95:      {llm['p95']:.2f}s")
        print(f"  P99:      {llm['p99']:.2f}s")
        print(f"  Min/Max:  {llm['min']:.2f}s / {llm['max']:.2f}s")
        
        print("\n" + "-" * 60)
        print("TTS (Text-to-Speech)")
        print("-" * 60)
        tts = report['tts']
        print(f"  Média:    {tts['mean']:.2f}s")
        print(f"  Mediana:  {tts['median']:.2f}s")
        print(f"  P95:      {tts['p95']:.2f}s")
        print(f"  P99:      {tts['p99']:.2f}s")
        print(f"  Min/Max:  {tts['min']:.2f}s / {tts['max']:.2f}s")
        
        print("\n" + "-" * 60)
        print("TOTAL (End-to-End)")
        print("-" * 60)
        total = report['total']
        print(f"  Média:    {total['mean']:.2f}s")
        print(f"  Mediana:  {total['median']:.2f}s")
        print(f"  P95:      {total['p95']:.2f}s")
        print(f"  P99:      {total['p99']:.2f}s")
        print(f"  Min/Max:  {total['min']:.2f}s / {total['max']:.2f}s")
        
        print("\n" + "=" * 60)
        print("🎯 RECOMENDAÇÕES")
        print("=" * 60)
        
        if stt['mean'] > 1.0:
            print(f"⚠️  STT está lento ({stt['mean']:.2f}s). Considere:")
            print("   - Reduzir beam_size de 5 para 3")
            print("   - Usar modelo 'base' ao invés de 'large-v3'")
            print("   - Desabilitar VAD para áudios < 2s")
        
        if llm['mean'] > 0.8:
            print(f"⚠️  LLM está lento ({llm['mean']:.2f}s). Considere:")
            print("   - Implementar streaming para melhor percepção")
            print("   - Cache de respostas frequentes")
        
        if tts['mean'] > 0.5:
            print(f"⚠️  TTS está lento ({tts['mean']:.2f}s). Considere:")
            print("   - Pré-aquecer modelo no startup")
            print("   - Cache de sínteses frequentes")
        
        if total['mean'] > 2.0:
            print(f"⚠️  Latência total alta ({total['mean']:.2f}s). Meta: < 2s")
            print("   - Implementar processamento paralelo")
            print("   - Otimizar etapa mais lenta primeiro")
        
        print("=" * 60 + "\n")


async def main():
    """Função principal para teste"""
    print("📊 Análise de Performance - Jonh Assistant")
    print("Execute este script após várias requisições para gerar relatório")
    print("\nPara coletar métricas em tempo real, integre PerformanceAnalyzer")
    print("nos handlers de processamento.\n")


if __name__ == "__main__":
    asyncio.run(main())

