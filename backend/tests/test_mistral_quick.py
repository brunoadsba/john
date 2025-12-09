#!/usr/bin/env python3
"""
Teste rápido de modelos Mistral - apenas verifica disponibilidade e tool calling
"""

import sys
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
    "mistral-medium:latest",
    "mistral:8x7b",
]

print("🔍 Verificando modelos Mistral disponíveis...\n")

client = ollama.Client()
models_list = client.list()

# Extrai nomes dos modelos
available_models = []
if hasattr(models_list, 'models'):
    available_models = [m.model if hasattr(m, 'model') else str(m) for m in models_list.models]
elif isinstance(models_list, dict):
    available_models = models_list.get('models', [])
elif isinstance(models_list, list):
    available_models = [str(m) for m in models_list]

print("✅ Modelos Mistral encontrados:\n")

mistral_found = []
for model_name in MODELS:
    for available in available_models:
        if model_name in str(available) or str(available) in model_name:
            mistral_found.append(model_name)
            print(f"  ✅ {model_name}")
            break

if not mistral_found:
    print("  ❌ Nenhum modelo Mistral encontrado")
    print("\n💡 Baixe com: ollama pull mistral-small:latest")
else:
    print(f"\n📊 Total: {len(mistral_found)} modelo(s) disponível(is)")
    print("\n💡 Para testar tool calling completo, execute:")
    print("   python3 backend/tests/test_mistral_models.py")

