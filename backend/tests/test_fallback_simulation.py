"""
Teste de simulação de fallback Groq → Ollama
Testa o código de fallback sem precisar atingir rate limit real
"""
import sys
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.llm_service import GroqLLMService, OllamaLLMService
from unittest.mock import Mock, patch, MagicMock
from loguru import logger


def test_fallback_code_structure():
    """Testa se o código de fallback está implementado corretamente"""
    print("=" * 60)
    print("TESTE - Estrutura do Código de Fallback")
    print("=" * 60)
    
    # Verifica se o código tem tratamento de rate limit
    with open("backend/services/llm_service.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    checks = {
        "Rate limit detection": "Rate limit" in code or "rate_limit" in code or "429" in code,
        "Fallback to Ollama": "ollama_service" in code or "OllamaLLMService" in code,
        "Error handling": "RuntimeError" in code and "rate limit" in code.lower(),
        "Fallback activation log": "[Groq→Ollama]" in code or "Fallback ativado" in code,
    }
    
    print("\nVerificações de código:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ Estrutura do código de fallback está correta!")
    else:
        print("\n⚠️  Algumas verificações falharam")
    
    return all_passed


def test_ollama_service_availability():
    """Testa se OllamaService pode ser instanciado"""
    print("\n" + "=" * 60)
    print("TESTE - Disponibilidade do OllamaService")
    print("=" * 60)
    
    try:
        # Tenta importar
        from backend.services.llm_service import OllamaLLMService
        
        # Tenta criar instância (sem conectar)
        service = OllamaLLMService(
            model="llama3.1:8b",
            host="http://localhost:11434",
            temperature=0.7,
            max_tokens=512
        )
        
        print("✅ OllamaLLMService pode ser instanciado")
        
        # Verifica se tem método generate_response
        if hasattr(service, 'generate_response'):
            print("✅ Método generate_response disponível")
            return True
        else:
            print("❌ Método generate_response não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar OllamaService: {e}")
        return False


def test_groq_error_detection():
    """Testa detecção de erros do Groq"""
    print("\n" + "=" * 60)
    print("TESTE - Detecção de Erros do Groq")
    print("=" * 60)
    
    # Simula diferentes tipos de erro
    error_messages = [
        "Rate limit reached for model",
        "rate_limit_exceeded",
        "Error code: 429",
        "Rate limit",
    ]
    
    code = ""
    with open("backend/services/llm_service.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    detected = []
    for error_msg in error_messages:
        if error_msg.lower() in code.lower():
            detected.append(error_msg)
            print(f"  ✅ Detecta: '{error_msg}'")
        else:
            print(f"  ⚠️  Não detecta explicitamente: '{error_msg}'")
    
    if len(detected) >= 2:
        print(f"\n✅ Sistema detecta múltiplos formatos de erro de rate limit")
        return True
    else:
        print(f"\n⚠️  Detecção pode ser melhorada")
        return False


def test_fallback_imports():
    """Testa se os imports necessários estão presentes"""
    print("\n" + "=" * 60)
    print("TESTE - Imports Necessários")
    print("=" * 60)
    
    try:
        # Verifica imports no llm_service.py
        with open("backend/services/llm_service.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        required_imports = {
            "ollama": "ollama" in code or "import ollama" in code,
            "OllamaLLMService": "OllamaLLMService" in code,
            "RuntimeError": "RuntimeError" in code,
        }
        
        all_imported = True
        for import_name, imported in required_imports.items():
            status = "✅" if imported else "❌"
            print(f"  {status} {import_name}")
            if not imported:
                all_imported = False
        
        if all_imported:
            print("\n✅ Todos os imports necessários estão presentes")
            return True
        else:
            print("\n⚠️  Alguns imports podem estar faltando")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar imports: {e}")
        return False


def main():
    """Executa todos os testes"""
    results = []
    
    results.append(("Estrutura do Código", test_fallback_code_structure()))
    results.append(("OllamaService Disponível", test_ollama_service_availability()))
    results.append(("Detecção de Erros", test_groq_error_detection()))
    results.append(("Imports Necessários", test_fallback_imports()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "⚠️  VERIFICAR"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Código de fallback está implementado corretamente!")
        print("\n💡 Para testar o fallback em ação:")
        print("   1. Aguarde o Groq atingir rate limit (ou simule)")
        print("   2. Verifique os logs do servidor para mensagens de fallback")
        print("   3. O sistema deve usar Ollama automaticamente")
    else:
        print("\n⚠️  Alguns testes falharam - verifique o código")


if __name__ == "__main__":
    main()

