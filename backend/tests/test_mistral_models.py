#!/usr/bin/env python3
"""
Script de teste para comparar modelos Mistral disponíveis no Ollama

Testa:
- Disponibilidade dos modelos
- Suporte a tool calling
- Performance (tempo de resposta)
- Qualidade das respostas
- Uso de memória (estimado)
"""

import time
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import ollama
except ImportError:
    print("❌ Erro: biblioteca 'ollama' não instalada")
    print("Instale com: pip install ollama")
    sys.exit(1)

import psutil
import os


@dataclass
class ModelTestResult:
    """Resultado do teste de um modelo"""
    model_name: str
    available: bool
    supports_tools: bool
    response_time: float
    tokens_per_second: float
    response_quality: str
    error: Optional[str] = None
    ram_usage_mb: Optional[float] = None


class MistralModelTester:
    """Testador de modelos Mistral"""
    
    # Modelos para testar (em ordem de preferência)
    MODELS_TO_TEST = [
        "mistral-small:latest",
        "mistral:7b-instruct",
        "mistral:latest",
        "mistral-medium:latest",
        "mistral:8x7b",
    ]
    
    # Prompt de teste simples
    SIMPLE_PROMPT = "Olá! Como você está? Responda em português brasileiro."
    
    # Prompt para testar tool calling
    TOOL_TEST_PROMPT = """Você tem acesso a uma ferramenta chamada 'test_tool' que recebe um parâmetro 'message'.
Use essa ferramenta para enviar a mensagem 'teste de tool calling'."""
    
    # Tool definition para teste
    TEST_TOOL = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Ferramenta de teste para verificar tool calling",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Mensagem de teste"
                    }
                },
                "required": ["message"]
            }
        }
    }
    
    def __init__(self):
        self.results: List[ModelTestResult] = []
        self.client = ollama.Client()
    
    def get_ram_usage(self) -> float:
        """Retorna uso de RAM em MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def check_model_available(self, model_name: str) -> bool:
        """Verifica se o modelo está disponível localmente"""
        try:
            models = self.client.list()
            model_list = []
            
            if hasattr(models, 'models'):
                model_list = [m.model if hasattr(m, 'model') else str(m) for m in models.models]
            elif isinstance(models, dict):
                model_list = models.get('models', [])
            elif isinstance(models, list):
                model_list = [str(m) for m in models]
            
            # Verifica se o modelo está na lista
            for m in model_list:
                if model_name in str(m) or str(m) in model_name:
                    return True
            
            return False
        except Exception as e:
            print(f"⚠️  Erro ao verificar disponibilidade: {e}")
            return False
    
    def test_simple_response(self, model_name: str) -> Tuple[bool, float, str]:
        """
        Testa resposta simples do modelo
        
        Returns:
            (sucesso, tempo_resposta, resposta_texto)
        """
        try:
            start_time = time.time()
            ram_before = self.get_ram_usage()
            
            response = self.client.chat(
                model=model_name,
                messages=[
                    {"role": "user", "content": self.SIMPLE_PROMPT}
                ]
            )
            
            elapsed_time = time.time() - start_time
            ram_after = self.get_ram_usage()
            
            resposta = response.get('message', {}).get('content', '')
            
            # Calcula tokens/segundo (estimado)
            tokens_used = response.get('eval_count', 0) or len(resposta.split())
            tokens_per_sec = tokens_used / elapsed_time if elapsed_time > 0 else 0
            
            return True, elapsed_time, resposta, tokens_per_sec, ram_after - ram_before
            
        except Exception as e:
            return False, 0, f"Erro: {str(e)}", 0, 0
    
    def test_tool_calling(self, model_name: str) -> bool:
        """Testa se o modelo suporta tool calling"""
        try:
            response = self.client.chat(
                model=model_name,
                messages=[
                    {"role": "user", "content": self.TOOL_TEST_PROMPT}
                ],
                tools=[self.TEST_TOOL]
            )
            
            message = response.get('message', {})
            tool_calls = message.get('tool_calls', [])
            
            # Se retornou tool_calls, suporta
            if tool_calls and len(tool_calls) > 0:
                return True
            
            # Verifica se a resposta menciona a ferramenta (fallback)
            content = message.get('content', '').lower()
            if 'test_tool' in content or 'ferramenta' in content:
                return True
            
            return False
            
        except Exception as e:
            # Se der erro específico de "não suporta tools", retorna False
            error_msg = str(e).lower()
            if 'tool' in error_msg or 'function' in error_msg:
                return False
            # Outros erros podem ser temporários
            return False
    
    def evaluate_response_quality(self, resposta: str) -> str:
        """Avalia qualidade da resposta (simples)"""
        resposta_lower = resposta.lower()
        
        # Verifica se respondeu em português
        portuguese_words = ['olá', 'oi', 'estou', 'bem', 'tudo', 'como']
        has_portuguese = any(word in resposta_lower for word in portuguese_words)
        
        # Verifica se a resposta não está vazia
        if not resposta or len(resposta.strip()) < 5:
            return "❌ Resposta muito curta ou vazia"
        
        # Verifica se respondeu de forma adequada
        if has_portuguese and len(resposta) > 10:
            return "✅ Boa qualidade"
        elif len(resposta) > 10:
            return "⚠️  Resposta OK mas não em português"
        else:
            return "⚠️  Resposta curta"
    
    def test_model(self, model_name: str) -> ModelTestResult:
        """Testa um modelo completo"""
        print(f"\n{'='*60}")
        print(f"🧪 Testando modelo: {model_name}")
        print(f"{'='*60}")
        
        # 1. Verifica disponibilidade
        print(f"📦 Verificando disponibilidade...")
        available = self.check_model_available(model_name)
        
        if not available:
            print(f"⚠️  Modelo não encontrado localmente")
            print(f"💡 Baixe com: ollama pull {model_name}")
            return ModelTestResult(
                model_name=model_name,
                available=False,
                supports_tools=False,
                response_time=0,
                tokens_per_second=0,
                response_quality="Modelo não disponível",
                error="Modelo não encontrado localmente"
            )
        
        print(f"✅ Modelo disponível")
        
        # 2. Testa resposta simples
        print(f"💬 Testando resposta simples...")
        success, elapsed_time, resposta, tokens_per_sec, ram_usage = self.test_simple_response(model_name)
        
        if not success:
            return ModelTestResult(
                model_name=model_name,
                available=True,
                supports_tools=False,
                response_time=0,
                tokens_per_second=0,
                response_quality="Erro ao gerar resposta",
                error=resposta
            )
        
        print(f"⏱️  Tempo de resposta: {elapsed_time:.2f}s")
        print(f"🚀 Tokens/segundo: {tokens_per_sec:.1f}")
        print(f"💾 Uso de RAM: {ram_usage:.1f} MB")
        print(f"📝 Resposta: {resposta[:100]}...")
        
        # 3. Avalia qualidade
        quality = self.evaluate_response_quality(resposta)
        print(f"⭐ Qualidade: {quality}")
        
        # 4. Testa tool calling
        print(f"🔧 Testando suporte a tool calling...")
        supports_tools = self.test_tool_calling(model_name)
        
        if supports_tools:
            print(f"✅ Tool calling suportado!")
        else:
            print(f"❌ Tool calling não suportado")
        
        return ModelTestResult(
            model_name=model_name,
            available=True,
            supports_tools=supports_tools,
            response_time=elapsed_time,
            tokens_per_second=tokens_per_sec,
            response_quality=quality,
            ram_usage_mb=ram_usage
        )
    
    def run_all_tests(self) -> List[ModelTestResult]:
        """Executa testes em todos os modelos"""
        print("🚀 Iniciando testes de modelos Mistral")
        print(f"📋 Modelos a testar: {len(self.MODELS_TO_TEST)}")
        
        for model_name in self.MODELS_TO_TEST:
            result = self.test_model(model_name)
            self.results.append(result)
            
            # Pequena pausa entre testes
            time.sleep(2)
        
        return self.results
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        print(f"\n{'='*60}")
        print("📊 RESUMO DOS TESTES")
        print(f"{'='*60}\n")
        
        # Filtra apenas modelos disponíveis
        available_results = [r for r in self.results if r.available]
        
        if not available_results:
            print("❌ Nenhum modelo disponível para teste")
            print("\n💡 Baixe modelos com:")
            for model in self.MODELS_TO_TEST:
                print(f"   ollama pull {model}")
            return
        
        # Ordena por tempo de resposta (mais rápido primeiro)
        available_results.sort(key=lambda x: x.response_time if x.response_time > 0 else float('inf'))
        
        print(f"{'Modelo':<30} {'Tool Calling':<15} {'Tempo (s)':<12} {'Tokens/s':<12} {'Qualidade':<20}")
        print("-" * 90)
        
        for result in available_results:
            tool_status = "✅ Sim" if result.supports_tools else "❌ Não"
            tempo = f"{result.response_time:.2f}" if result.response_time > 0 else "N/A"
            tokens = f"{result.tokens_per_second:.1f}" if result.tokens_per_second > 0 else "N/A"
            
            print(f"{result.model_name:<30} {tool_status:<15} {tempo:<12} {tokens:<12} {result.response_quality:<20}")
        
        # Recomendação
        print(f"\n{'='*60}")
        print("💡 RECOMENDAÇÕES")
        print(f"{'='*60}\n")
        
        # Melhor modelo com tool calling
        models_with_tools = [r for r in available_results if r.supports_tools]
        if models_with_tools:
            best_with_tools = min(models_with_tools, key=lambda x: x.response_time)
            print(f"✅ MELHOR MODELO COM TOOL CALLING:")
            print(f"   {best_with_tools.model_name}")
            print(f"   Tempo: {best_with_tools.response_time:.2f}s")
            print(f"   Tokens/s: {best_with_tools.tokens_per_second:.1f}\n")
        
        # Modelo mais rápido
        fastest = min(available_results, key=lambda x: x.response_time if x.response_time > 0 else float('inf'))
        print(f"⚡ MODELO MAIS RÁPIDO:")
        print(f"   {fastest.model_name}")
        print(f"   Tempo: {fastest.response_time:.2f}s\n")
        
        # Modelo com melhor qualidade
        best_quality = [r for r in available_results if "✅" in r.response_quality]
        if best_quality:
            best = min(best_quality, key=lambda x: x.response_time)
            print(f"⭐ MELHOR QUALIDADE:")
            print(f"   {best.model_name}")
            print(f"   {best.response_quality}\n")
    
    def save_results_json(self, filename: str = "mistral_test_results.json"):
        """Salva resultados em JSON"""
        results_dict = [asdict(r) for r in self.results]
        output_path = Path(__file__).parent / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos em: {output_path}")


def main():
    """Função principal"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     TESTE DE MODELOS MISTRAL - Galaxy Book 2 (32GB RAM)   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    tester = MistralModelTester()
    
    try:
        # Executa testes
        results = tester.run_all_tests()
        
        # Imprime resumo
        tester.print_summary()
        
        # Salva resultados
        tester.save_results_json()
        
        print(f"\n✅ Testes concluídos!")
        print(f"📊 Total de modelos testados: {len(results)}")
        print(f"✅ Modelos disponíveis: {len([r for r in results if r.available])}")
        print(f"🔧 Modelos com tool calling: {len([r for r in results if r.supports_tools])}")
        
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

