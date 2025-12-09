"""
Testes para Fase 1: Infraestrutura de Coleta de Dados e Feedback
"""
import asyncio
import httpx
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


async def test_health_check():
    """Testa se o servidor está rodando"""
    print("🔍 Testando health check...")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Servidor está rodando")
                return True
            else:
                print(f"❌ Servidor retornou status {response.status_code}")
                return False
        except httpx.ConnectError:
            print("❌ Não foi possível conectar ao servidor")
            print("   Certifique-se de que o servidor está rodando:")
            print("   uvicorn backend.api.main:app --reload")
            return False


async def test_collect_conversation():
    """Testa coleta automática de conversas"""
    print("\n🔍 Testando coleta automática de conversas...")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # Envia uma mensagem de teste
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Olá, como você está?"}
            )
            
            if response.status_code == 200:
                # Verifica se a conversa foi coletada
                conv_response = await client.get(f"{BASE_URL}/api/feedback/conversations?limit=1")
                if conv_response.status_code == 200:
                    data = conv_response.json()
                    if data.get("count", 0) > 0:
                        print("✅ Conversa coletada automaticamente")
                        print(f"   Total de conversas: {data['count']}")
                        return True
                    else:
                        print("⚠️  Conversa não encontrada (pode levar alguns segundos)")
                        return False
                else:
                    print(f"❌ Erro ao listar conversas: {conv_response.status_code}")
                    return False
            else:
                print(f"❌ Erro ao processar texto: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


async def test_submit_feedback():
    """Testa envio de feedback"""
    print("\n🔍 Testando envio de feedback...")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # Primeiro, obtém uma conversa
            conv_response = await client.get(f"{BASE_URL}/api/feedback/conversations?limit=1")
            if conv_response.status_code != 200:
                print("⚠️  Nenhuma conversa disponível para testar feedback")
                return False
            
            conversations = conv_response.json().get("conversations", [])
            if not conversations:
                print("⚠️  Nenhuma conversa disponível para testar feedback")
                return False
            
            conversation_id = conversations[0]["id"]
            
            # Envia feedback positivo
            feedback_data = {
                "conversation_id": conversation_id,
                "rating": 5,
                "comment": "Resposta muito útil!"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/feedback",
                json=feedback_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Feedback enviado com sucesso")
                print(f"   Feedback ID: {data.get('feedback_id')}")
                return True
            else:
                print(f"❌ Erro ao enviar feedback: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


async def test_feedback_stats():
    """Testa estatísticas de feedback"""
    print("\n🔍 Testando estatísticas de feedback...")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/feedback/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print("✅ Estatísticas obtidas:")
                print(f"   Total de feedback: {stats.get('total', 0)}")
                print(f"   Média de rating: {stats.get('avg_rating', 0):.2f}")
                print(f"   Positivos: {stats.get('positive', 0)}")
                print(f"   Negativos: {stats.get('negative', 0)}")
                print(f"   Total de conversas: {stats.get('total_conversations', 0)}")
                return True
            else:
                print(f"❌ Erro ao obter estatísticas: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


async def test_export_dataset():
    """Testa exportação de dataset"""
    print("\n🔍 Testando exportação de dataset...")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/feedback/export",
                params={"format": "alpaca", "min_quality": 0.5, "limit": 10}
            )
            
            if response.status_code == 200:
                # Salva o arquivo
                output_path = Path("data/training/test_dataset.json")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(response.content)
                
                # Verifica se o arquivo é válido JSON
                try:
                    with open(output_path, "r", encoding="utf-8") as f:
                        dataset = json.load(f)
                    print("✅ Dataset exportado com sucesso")
                    print(f"   Arquivo: {output_path}")
                    print(f"   Exemplos: {len(dataset)}")
                    if dataset:
                        print(f"   Primeiro exemplo:")
                        print(f"     Input: {dataset[0].get('input', 'N/A')[:50]}...")
                        print(f"     Output: {dataset[0].get('output', 'N/A')[:50]}...")
                    return True
                except json.JSONDecodeError:
                    print("❌ Arquivo exportado não é JSON válido")
                    return False
            else:
                print(f"❌ Erro ao exportar dataset: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTES - FASE 1: Infraestrutura de Coleta de Dados")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Health check
    results.append(("Health Check", await test_health_check()))
    
    # Teste 2: Coleta de conversas
    results.append(("Coleta de Conversas", await test_collect_conversation()))
    
    # Teste 3: Envio de feedback
    results.append(("Envio de Feedback", await test_submit_feedback()))
    
    # Teste 4: Estatísticas
    results.append(("Estatísticas", await test_feedback_stats()))
    
    # Teste 5: Exportação
    results.append(("Exportação de Dataset", await test_export_dataset()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! Fase 1 está funcionando corretamente.")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Verifique os erros acima.")


if __name__ == "__main__":
    asyncio.run(main())

