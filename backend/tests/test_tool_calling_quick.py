#!/usr/bin/env python3
"""
Teste rápido de tool calling nos modelos Mistral
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import ollama
except ImportError:
    print("❌ Erro: biblioteca 'ollama' não instalada")
    sys.exit(1)

MODELS = [
    "mistral-small:latest",
    "mistral:7b-instruct",
    "mistral:latest",
]

TEST_TOOL = {
    "type": "function",
    "function": {
        "name": "test_tool",
        "description": "Ferramenta de teste",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    }
}

print("🔧 Testando suporte a Tool Calling nos modelos Mistral\n")
print("=" * 60)

client = ollama.Client()

for model_name in MODELS:
    print(f"\n🧪 Testando: {model_name}")
    print("-" * 60)
    
    try:
        # Teste simples primeiro
        start = time.time()
        response = client.chat(
            model=model_name,
            messages=[{"role": "user", "content": "Olá"}],
            tools=[TEST_TOOL]
        )
        elapsed = time.time() - start
        
        message = response.get('message', {})
        tool_calls = message.get('tool_calls', [])
        
        if tool_calls and len(tool_calls) > 0:
            print(f"✅ Tool calling SUPORTADO")
            print(f"⏱️  Tempo: {elapsed:.2f}s")
        else:
            # Verifica se retornou resposta normal (pode não ter usado tool)
            content = message.get('content', '')
            if content:
                print(f"⚠️  Tool calling pode não estar funcionando")
                print(f"   Resposta recebida: {content[:50]}...")
                print(f"⏱️  Tempo: {elapsed:.2f}s")
            else:
                print(f"❌ Erro na resposta")
                
    except Exception as e:
        error_msg = str(e).lower()
        if 'tool' in error_msg or 'function' in error_msg or '400' in error_msg:
            print(f"❌ Tool calling NÃO SUPORTADO")
            print(f"   Erro: {str(e)[:100]}")
        else:
            print(f"⚠️  Erro ao testar: {str(e)[:100]}")

print("\n" + "=" * 60)
print("✅ Teste concluído!")
print("\n💡 Recomendação:")
print("   Use o modelo que suporta tool calling para melhor integração")

