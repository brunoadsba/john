#!/bin/bash
# Teste rápido do sistema de monitoramento via curl

BASE_URL="http://127.0.0.1:8000"

echo "============================================================"
echo "🧪 TESTE RÁPIDO - SISTEMA DE MONITORAMENTO DE ERROS"
echo "============================================================"
echo ""

# Verifica se servidor está rodando
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "❌ Servidor não está rodando!"
    echo ""
    echo "📋 Inicie o servidor primeiro:"
    echo "   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi

echo "✅ Servidor está rodando!"
echo ""

# Teste 1: Reportar erro de rede
echo "📋 Teste 1: Reportando erro de rede..."
ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/errors/report" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "error",
    "type": "network",
    "message": "Failed to connect to server: Connection refused",
    "stack_trace": "SocketException: Connection refused",
    "device_info": {
      "platform": "android",
      "os_version": "13",
      "device_model": "Galaxy Book 2"
    },
    "context": {
      "session_id": "test_001",
      "screen": "HomeScreen"
    }
  }')

ERROR_ID=$(echo "$ERROR_RESPONSE" | grep -o '"error_id":"[^"]*' | cut -d'"' -f4)

if [ -n "$ERROR_ID" ]; then
    echo "✅ Erro reportado com sucesso!"
    echo "   Error ID: $ERROR_ID"
    echo "   Resposta: $(echo "$ERROR_RESPONSE" | jq -r '.suggested_solutions[0]' 2>/dev/null || echo 'N/A')"
else
    echo "❌ Falha ao reportar erro"
    echo "   Resposta: $ERROR_RESPONSE"
    exit 1
fi

echo ""

# Teste 2: Reportar erro de áudio
echo "📋 Teste 2: Reportando erro de áudio..."
ERROR_RESPONSE2=$(curl -s -X POST "$BASE_URL/api/errors/report" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "error",
    "type": "audio",
    "message": "Microphone permission denied",
    "device_info": {
      "platform": "android",
      "os_version": "13"
    }
  }')

ERROR_ID2=$(echo "$ERROR_RESPONSE2" | grep -o '"error_id":"[^"]*' | cut -d'"' -f4)

if [ -n "$ERROR_ID2" ]; then
    echo "✅ Erro reportado com sucesso!"
    echo "   Error ID: $ERROR_ID2"
else
    echo "❌ Falha ao reportar erro"
fi

echo ""

# Teste 3: Obter analytics
echo "📋 Teste 3: Obtendo analytics..."
ANALYTICS=$(curl -s "$BASE_URL/api/errors/analytics")

TOTAL=$(echo "$ANALYTICS" | grep -o '"total":[0-9]*' | cut -d':' -f2)
RESOLVED=$(echo "$ANALYTICS" | grep -o '"resolved":[0-9]*' | cut -d':' -f2)
UNRESOLVED=$(echo "$ANALYTICS" | grep -o '"unresolved":[0-9]*' | cut -d':' -f2)

if [ -n "$TOTAL" ]; then
    echo "✅ Analytics obtidos!"
    echo "   Total de erros: $TOTAL"
    echo "   Resolvidos: ${RESOLVED:-0}"
    echo "   Não resolvidos: ${UNRESOLVED:-0}"
else
    echo "❌ Falha ao obter analytics"
fi

echo ""

# Teste 4: Obter erro específico
if [ -n "$ERROR_ID" ]; then
    echo "📋 Teste 4: Obtendo erro específico..."
    ERROR_DETAILS=$(curl -s "$BASE_URL/api/errors/$ERROR_ID")
    
    ERROR_TYPE=$(echo "$ERROR_DETAILS" | grep -o '"type":"[^"]*' | cut -d'"' -f4)
    ERROR_LEVEL=$(echo "$ERROR_DETAILS" | grep -o '"level":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$ERROR_TYPE" ]; then
        echo "✅ Erro obtido com sucesso!"
        echo "   Tipo: $ERROR_TYPE"
        echo "   Nível: $ERROR_LEVEL"
    else
        echo "❌ Falha ao obter erro"
    fi
fi

echo ""

# Teste 5: Resolver erro
if [ -n "$ERROR_ID2" ]; then
    echo "📋 Teste 5: Resolvendo erro..."
    RESOLVE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/errors/$ERROR_ID2/resolve" \
      -H "Content-Type: application/json" \
      -d '{
        "resolution_notes": "Usuário concedeu permissão de microfone"
      }')
    
    if echo "$RESOLVE_RESPONSE" | grep -q "success"; then
        echo "✅ Erro marcado como resolvido!"
    else
        echo "❌ Falha ao resolver erro"
    fi
fi

echo ""
echo "============================================================"
echo "✅ TESTES CONCLUÍDOS"
echo "============================================================"

