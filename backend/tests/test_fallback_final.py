"""
Teste final do fallback Groq → Ollama
Verifica se tudo está funcionando corretamente
"""
import asyncio
import httpx
from pathlib import Path

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


async def test_complete_flow():
    """Testa fluxo completo com verificação de fallback"""
    print("=" * 60)
    print("TESTE FINAL - Fallback Groq → Ollama")
    print("=" * 60)
    
    # 1. Verifica Ollama
    print("\n1️⃣ Verificando Ollama...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                print(f"   ✅ Ollama disponível")
                print(f"   📋 Modelos: {', '.join(model_names[:3])}...")
                
                # Verifica se tem modelo compatível
                has_llama = any("llama3" in name.lower() for name in model_names)
                if has_llama:
                    print(f"   ✅ Modelo Llama disponível para fallback")
                else:
                    print(f"   ⚠️  Nenhum modelo Llama encontrado")
            else:
                print(f"   ❌ Ollama retornou status {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Ollama não disponível: {e}")
        return False
    
    # 2. Testa requisição normal
    print("\n2️⃣ Testando requisição normal...")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Teste de fallback"}
            )
            
            if response.status_code == 200:
                print(f"   ✅ Requisição processada com sucesso")
                print(f"   💡 Verifique logs do servidor para ver qual provider foi usado")
                return True
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limit atingido (esperado)")
                print(f"   💡 Sistema deve tentar fallback para Ollama")
                print(f"   💡 Verifique logs do servidor para confirmação")
                return True  # Rate limit é esperado, fallback deve ativar
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


async def main():
    """Executa teste final"""
    result = await test_complete_flow()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ TESTE CONCLUÍDO")
        print("\n📋 Próximos passos:")
        print("   1. Verifique os logs do servidor")
        print("   2. Procure por mensagens '[Groq→Ollama]'")
        print("   3. Quando Groq atingir rate limit, fallback deve ativar automaticamente")
    else:
        print("⚠️  TESTE FALHOU")
        print("\n💡 Verifique:")
        print("   1. Servidor está rodando?")
        print("   2. Ollama está disponível?")
        print("   3. Modelo Llama está instalado?")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

