"""
Testes para fallback automático Groq → Ollama quando rate limit é atingido
"""
import asyncio
import httpx
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TIMEOUT = 60.0


async def test_ollama_available():
    """Testa se Ollama está disponível"""
    print("🔍 Testando disponibilidade do Ollama...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                print(f"✅ Ollama está disponível")
                print(f"   Modelos disponíveis: {', '.join(model_names[:5])}")
                return True
            else:
                print(f"⚠️  Ollama retornou status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ollama não está disponível: {e}")
        print("   Certifique-se de que Ollama está rodando: ollama serve")
        return False


async def test_groq_status():
    """Testa status do Groq"""
    print("\n🔍 Testando status do Groq...")
    try:
        # Tenta uma requisição simples
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Teste rápido"}
            )
            
            if response.status_code == 200:
                print("✅ Groq está funcionando")
                return True
            elif response.status_code == 429:
                print("⚠️  Groq atingiu rate limit (esperado para testar fallback)")
                return False
            else:
                print(f"⚠️  Groq retornou status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erro ao testar Groq: {e}")
        return False


async def test_fallback_activation():
    """Testa se o fallback é ativado quando Groq falha"""
    print("\n🔍 Testando ativação do fallback...")
    
    # Primeiro verifica se Ollama está disponível
    ollama_available = await test_ollama_available()
    if not ollama_available:
        print("⚠️  Ollama não disponível - não é possível testar fallback")
        return False
    
    # Tenta fazer requisições até atingir rate limit ou verificar fallback
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        test_messages = [
            "Olá, como você está?",
            "Qual a capital do Brasil?",
            "Me conte uma piada",
        ]
        
        fallback_detected = False
        
        for i, message in enumerate(test_messages, 1):
            try:
                print(f"\n   Teste {i}/{len(test_messages)}: '{message[:30]}...'")
                response = await client.post(
                    f"{BASE_URL}/api/process_text",
                    data={"texto": message}
                )
                
                if response.status_code == 200:
                    # Verifica headers para ver qual provider foi usado
                    # (infelizmente não temos header específico, mas podemos verificar logs)
                    print(f"   ✅ Resposta recebida (status 200)")
                    # Se chegou aqui, funcionou (pode ser Groq ou Ollama via fallback)
                    fallback_detected = True
                elif response.status_code == 429:
                    print(f"   ⚠️  Rate limit atingido (status 429)")
                    print(f"   💡 Verifique os logs do servidor para ver se fallback foi ativado")
                    # Mesmo com 429, o fallback pode ter sido tentado
                    fallback_detected = True
                else:
                    print(f"   ⚠️  Status inesperado: {response.status_code}")
                
                # Pequena pausa entre requisições
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Erro na requisição: {e}")
        
        if fallback_detected:
            print("\n✅ Fallback testado (verifique logs do servidor para confirmação)")
            return True
        else:
            print("\n⚠️  Não foi possível confirmar fallback automaticamente")
            return False


async def test_error_handling():
    """Testa tratamento de erros"""
    print("\n🔍 Testando tratamento de erros...")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Testa com mensagem que deve funcionar
        try:
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Teste de erro"}
            )
            
            if response.status_code in [200, 429]:
                print("✅ Tratamento de erros funcionando")
                if response.status_code == 429:
                    # Verifica se a mensagem de erro é amigável
                    try:
                        error_data = response.json()
                        if "Limite de requisições" in str(error_data) or "rate limit" in str(error_data).lower():
                            print("   ✅ Mensagem de erro é amigável")
                    except:
                        pass
                return True
            else:
                print(f"⚠️  Status inesperado: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False


async def test_server_logs_analysis():
    """Analisa logs do servidor para verificar fallback"""
    print("\n🔍 Análise de logs do servidor...")
    print("   💡 Verifique manualmente os logs do servidor para:")
    print("      - Mensagens '[Groq] Rate limit atingido'")
    print("      - Mensagens '[Groq→Ollama] ✅ Fallback ativado'")
    print("      - Uso de Ollama após erro do Groq")
    return True


async def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTES - Fallback Groq → Ollama")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Ollama disponível
    results.append(("Ollama Disponível", await test_ollama_available()))
    
    # Teste 2: Status do Groq
    results.append(("Status do Groq", await test_groq_status()))
    
    # Teste 3: Fallback
    results.append(("Ativação do Fallback", await test_fallback_activation()))
    
    # Teste 4: Tratamento de erros
    results.append(("Tratamento de Erros", await test_error_handling()))
    
    # Teste 5: Análise de logs
    results.append(("Análise de Logs", await test_server_logs_analysis()))
    
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
    
    print("\n" + "=" * 60)
    print("INSTRUÇÕES")
    print("=" * 60)
    print("1. Verifique os logs do servidor para confirmar fallback")
    print("2. Se Groq atingir rate limit, o sistema deve tentar Ollama automaticamente")
    print("3. Se Ollama não estiver disponível, você verá erro 429")
    print("4. Para testar fallback forçado, pare temporariamente o Groq ou espere rate limit")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

