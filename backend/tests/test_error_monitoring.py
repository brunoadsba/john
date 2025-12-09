"""
Teste do sistema de monitoramento de erros
Simula erros do mobile e valida o funcionamento completo
"""
import asyncio
import httpx
import json
from typing import Dict, Any
from datetime import datetime

# Configuração
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 30.0


async def test_report_error(
    client: httpx.AsyncClient,
    level: str,
    error_type: str,
    message: str,
    stack_trace: str = None,
    device_info: Dict[str, Any] = None,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Testa reporte de erro"""
    print(f"\n📋 Testando reporte: [{level}/{error_type}] {message[:50]}...")
    
    payload = {
        "level": level,
        "type": error_type,
        "message": message,
    }
    
    if stack_trace:
        payload["stack_trace"] = stack_trace
    if device_info:
        payload["device_info"] = device_info
    if context:
        payload["context"] = context
    
    try:
        response = await client.post(
            f"{BASE_URL}/api/errors/report",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Erro reportado com sucesso!")
            print(f"   Error ID: {data.get('error_id')}")
            print(f"   Severity: {data.get('severity')}")
            print(f"   Soluções sugeridas: {len(data.get('suggested_solutions', []))}")
            if data.get('suggested_solutions'):
                for i, solution in enumerate(data.get('suggested_solutions', [])[:3], 1):
                    print(f"      {i}. {solution}")
            return data
        else:
            print(f"❌ Erro ao reportar: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return {}
    
    except Exception as e:
        print(f"❌ Exceção ao reportar erro: {e}")
        return {}


async def test_get_analytics(
    client: httpx.AsyncClient,
    error_type: str = None,
    level: str = None,
    resolved: bool = None
) -> Dict[str, Any]:
    """Testa obtenção de analytics"""
    print(f"\n📊 Testando analytics...")
    
    params = {}
    if error_type:
        params["error_type"] = error_type
    if level:
        params["level"] = level
    if resolved is not None:
        params["resolved"] = resolved
    
    try:
        response = await client.get(
            f"{BASE_URL}/api/errors/analytics",
            params=params,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics obtidos com sucesso!")
            print(f"   Total de erros: {data.get('total', 0)}")
            
            stats = data.get('stats', {})
            print(f"   Estatísticas:")
            print(f"      Total: {stats.get('total', 0)}")
            print(f"      Por nível: {stats.get('by_level', {})}")
            print(f"      Por tipo: {stats.get('by_type', {})}")
            print(f"      Resolvidos: {stats.get('by_resolution', {}).get('resolved', 0)}")
            print(f"      Não resolvidos: {stats.get('by_resolution', {}).get('unresolved', 0)}")
            print(f"      Últimas 24h: {stats.get('recent_24h', 0)}")
            
            trends = data.get('trends', {})
            print(f"   Tendências:")
            print(f"      Tipo mais comum: {trends.get('most_common_type', 'N/A')}")
            print(f"      Mensagem mais comum: {trends.get('most_common_message', 'N/A')[:50]}")
            
            return data
        else:
            print(f"❌ Erro ao obter analytics: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return {}
    
    except Exception as e:
        print(f"❌ Exceção ao obter analytics: {e}")
        return {}


async def test_get_error(
    client: httpx.AsyncClient,
    error_id: str
) -> Dict[str, Any]:
    """Testa obtenção de erro específico"""
    print(f"\n🔍 Testando obtenção de erro: {error_id[:8]}...")
    
    try:
        response = await client.get(
            f"{BASE_URL}/api/errors/{error_id}",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            error = data.get('error', {})
            print(f"✅ Erro obtido com sucesso!")
            print(f"   Tipo: {error.get('type')}")
            print(f"   Nível: {error.get('level')}")
            print(f"   Mensagem: {error.get('message', '')[:60]}...")
            print(f"   Resolvido: {error.get('resolved', False)}")
            return data
        else:
            print(f"❌ Erro ao obter erro: {response.status_code}")
            return {}
    
    except Exception as e:
        print(f"❌ Exceção ao obter erro: {e}")
        return {}


async def test_resolve_error(
    client: httpx.AsyncClient,
    error_id: str,
    resolution_notes: str = None
) -> bool:
    """Testa marcação de erro como resolvido"""
    print(f"\n✅ Testando resolução de erro: {error_id[:8]}...")
    
    payload = {}
    if resolution_notes:
        payload["resolution_notes"] = resolution_notes
    
    try:
        response = await client.post(
            f"{BASE_URL}/api/errors/{error_id}/resolve",
            json=payload if payload else None,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Erro marcado como resolvido!")
            return True
        else:
            print(f"❌ Erro ao resolver: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Exceção ao resolver erro: {e}")
        return False


async def test_validation_errors(client: httpx.AsyncClient):
    """Testa validação de erros (deve falhar)"""
    print(f"\n🔒 Testando validações...")
    
    # Teste 1: Level inválido
    print("   Teste 1: Level inválido")
    try:
        response = await client.post(
            f"{BASE_URL}/api/errors/report",
            json={
                "level": "invalid",
                "type": "network",
                "message": "Test"
            },
            timeout=TIMEOUT
        )
        if response.status_code == 400:
            print("   ✅ Validação funcionou (level inválido rejeitado)")
        else:
            print(f"   ❌ Validação falhou: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 2: Type inválido
    print("   Teste 2: Type inválido")
    try:
        response = await client.post(
            f"{BASE_URL}/api/errors/report",
            json={
                "level": "error",
                "type": "invalid_type",
                "message": "Test"
            },
            timeout=TIMEOUT
        )
        if response.status_code == 400:
            print("   ✅ Validação funcionou (type inválido rejeitado)")
        else:
            print(f"   ❌ Validação falhou: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")


async def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA DE MONITORAMENTO DE ERROS")
    print("=" * 60)
    
    # Verifica se servidor está rodando
    print("\n🔍 Verificando se servidor está rodando...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            if response.status_code == 200:
                print("✅ Servidor está rodando!")
            else:
                print(f"⚠️ Servidor respondeu com {response.status_code}")
    except httpx.ConnectError as e:
        print(f"❌ Não foi possível conectar ao servidor em {BASE_URL}")
        print("   Verifique se o servidor está rodando e acessível")
        print(f"   Erro: {e}")
        return
    except Exception as e:
        print(f"❌ Erro ao verificar servidor: {e}")
        print("   Certifique-se de que o servidor está rodando em http://127.0.0.1:8000")
        return
    
    async with httpx.AsyncClient() as client:
        # Teste 1: Erro de rede
        error1 = await test_report_error(
            client,
            level="error",
            error_type="network",
            message="Failed to connect to server: Connection refused",
            stack_trace="SocketException: Connection refused\n  at WebSocketClient.connect()",
            device_info={
                "platform": "android",
                "os_version": "13",
                "device_model": "Galaxy Book 2",
                "app_version": "1.0.0"
            },
            context={
                "session_id": "test_session_001",
                "screen": "HomeScreen",
                "user_action": "pressed_connect_button"
            }
        )
        
        await asyncio.sleep(0.5)
        
        # Teste 2: Erro de áudio
        error2 = await test_report_error(
            client,
            level="error",
            error_type="audio",
            message="Microphone permission denied",
            stack_trace="PermissionException: Microphone access denied\n  at AudioService.startRecording()",
            device_info={
                "platform": "android",
                "os_version": "13",
                "device_model": "Galaxy Book 2"
            },
            context={
                "session_id": "test_session_001",
                "screen": "HomeScreen",
                "user_action": "pressed_record_button"
            }
        )
        
        await asyncio.sleep(0.5)
        
        # Teste 3: Erro crítico (crash)
        error3 = await test_report_error(
            client,
            level="critical",
            error_type="crash",
            message="Unhandled exception: NullPointerException",
            stack_trace="NullPointerException: Attempted to read from null pointer\n  at MessageHandler.processMessage()\n  at ApiService.onMessage()",
            device_info={
                "platform": "android",
                "os_version": "13",
                "device_model": "Galaxy Book 2"
            },
            context={
                "session_id": "test_session_001",
                "screen": "ChatScreen"
            }
        )
        
        await asyncio.sleep(0.5)
        
        # Teste 4: Warning
        error4 = await test_report_error(
            client,
            level="warning",
            error_type="network",
            message="Slow network connection detected",
            device_info={
                "platform": "android",
                "os_version": "13"
            }
        )
        
        await asyncio.sleep(0.5)
        
        # Teste 5: Erro de permissão
        error5 = await test_report_error(
            client,
            level="error",
            error_type="permission",
            message="Storage permission denied",
            device_info={
                "platform": "android",
                "os_version": "13"
            }
        )
        
        await asyncio.sleep(1.0)
        
        # Teste 6: Analytics geral
        analytics = await test_get_analytics(client)
        
        # Teste 7: Analytics filtrado
        await test_get_analytics(client, error_type="network")
        await test_get_analytics(client, level="error")
        await test_get_analytics(client, resolved=False)
        
        # Teste 8: Obter erro específico
        if error1 and error1.get('error_id'):
            await test_get_error(client, error1['error_id'])
        
        # Teste 9: Resolver erro
        if error2 and error2.get('error_id'):
            await test_resolve_error(
                client,
                error2['error_id'],
                resolution_notes="Usuário concedeu permissão de microfone"
            )
        
        # Teste 10: Validações
        await test_validation_errors(client)
        
        # Teste 11: Analytics após resolução
        print("\n📊 Analytics após resolução:")
        await test_get_analytics(client)
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

