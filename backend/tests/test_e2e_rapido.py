#!/usr/bin/env python3
"""
Teste E2E Rápido - Versão resumida
"""

import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:8000"
TIMEOUT = 15

def test(name: str, func):
    """Executa um teste"""
    print(f"\n🧪 {name}")
    print("-" * 60)
    start = time.time()
    try:
        result = func()
        duration = time.time() - start
        if result:
            print(f"✅ PASSOU ({duration:.2f}s)")
            return True, duration
        else:
            print(f"❌ FALHOU ({duration:.2f}s)")
            return False, duration
    except Exception as e:
        duration = time.time() - start
        print(f"❌ ERRO: {e} ({duration:.2f}s)")
        return False, duration

def main():
    print("=" * 60)
    print("🧪 TESTE E2E RÁPIDO - Jonh Assistant")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Saúde do servidor
    passed, duration = test("1. Saúde do Servidor", lambda: 
        requests.get(f"{BASE_URL}/docs", timeout=5).status_code == 200
    )
    results.append(("Saúde do Servidor", passed, duration))
    
    # Teste 2: Processamento de texto
    def test_text():
        r = requests.post(f"{BASE_URL}/api/process_text", 
                         data={"texto": "Olá"}, timeout=TIMEOUT)
        if r.status_code == 200:
            print(f"   Resposta: {r.headers.get('X-Response-Text', '')[:50]}...")
            return True
        return False
    passed, duration = test("2. Processamento de Texto", test_text)
    results.append(("Processamento de Texto", passed, duration))
    
    # Teste 3: Architecture Advisor
    def test_advisor():
        r = requests.post(f"{BASE_URL}/api/process_text",
                         data={"texto": "Analise os requisitos de um sistema de chat"},
                         timeout=TIMEOUT)
        if r.status_code == 200:
            intent = r.headers.get("X-Architecture-Intent", "")
            if intent:
                print(f"   Intent: {intent}")
                return True
        return False
    passed, duration = test("3. Architecture Advisor", test_advisor)
    results.append(("Architecture Advisor", passed, duration))
    
    # Teste 4: Contexto
    def test_context():
        r1 = requests.post(f"{BASE_URL}/api/process_text",
                          data={"texto": "Meu nome é Teste"}, timeout=TIMEOUT)
        if r1.status_code != 200:
            return False
        session_id = r1.headers.get("X-Session-ID")
        if not session_id:
            return False
        
        r2 = requests.post(f"{BASE_URL}/api/process_text",
                          data={"texto": "Qual é meu nome?", "session_id": session_id},
                          timeout=TIMEOUT)
        if r2.status_code == 200:
            response = r2.headers.get("X-Response-Text", "")
            if "teste" in response.lower():
                print(f"   Contexto mantido: ✅")
                return True
        return False
    passed, duration = test("4. Gerenciamento de Contexto", test_context)
    results.append(("Gerenciamento de Contexto", passed, duration))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    
    passed_count = sum(1 for _, p, _ in results if p)
    total_time = sum(d for _, _, d in results)
    
    for name, passed, duration in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name:<35} {duration:>6.2f}s")
    
    print("-" * 60)
    print(f"Total: {passed_count}/{len(results)} testes passaram")
    print(f"Tempo total: {total_time:.2f}s")
    print("=" * 60)
    
    if passed_count == len(results):
        print("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"⚠️  {len(results) - passed_count} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())

