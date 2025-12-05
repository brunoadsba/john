#!/bin/bash
# Script para atualizar automaticamente o IP do servidor no app mobile
# Detecta o IP atual da máquina e atualiza o código Flutter se necessário

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_SERVICE_FILE="$PROJECT_ROOT/mobile_app/lib/services/api_service.dart"
PORT=8000

echo "═══════════════════════════════════════════════════════════════"
echo "  ATUALIZAÇÃO AUTOMÁTICA DE IP - JONH ASSISTANT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Detecta IP atual da máquina
detect_ip() {
    local ip=""
    
    if command -v hostname &> /dev/null; then
        # Linux/WSL - pega primeiro IP não localhost
        ip=$(hostname -I 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i !~ /^127\./) {print $i; exit}}')
    fi
    
    # Se não encontrou, tenta ip route
    if [ -z "$ip" ]; then
        if command -v ip &> /dev/null; then
            ip=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $7; exit}' | head -1)
        fi
    fi
    
    # Fallback: interface de rede ativa
    if [ -z "$ip" ]; then
        if [ -f /proc/net/route ]; then
            # Pega IP da primeira interface que não é loopback
            while IFS= read -r line; do
                if [[ $line =~ ^[a-z0-9]+ ]] && [[ ! $line =~ lo ]]; then
                    interface=$(echo "$line" | awk '{print $1}')
                    ip=$(ip addr show "$interface" 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1 | head -1)
                    if [ -n "$ip" ] && [[ ! $ip =~ ^127\. ]]; then
                        break
                    fi
                fi
            done < <(ip route 2>/dev/null | head -5)
        fi
    fi
    
    if [ -z "$ip" ] || [[ $ip =~ ^127\. ]]; then
        echo "❌ Erro: Não foi possível detectar o IP da rede local" >&2
        echo "   Tente configurar manualmente em $API_SERVICE_FILE" >&2
        exit 1
    fi
    
    echo "$ip"
}

# Extrai IP atual do arquivo Dart
get_current_ip() {
    if [ -f "$API_SERVICE_FILE" ]; then
        # Procura por padrão http://IP:8000
        grep -oP "http://\K[0-9.]+(?=:${PORT})" "$API_SERVICE_FILE" 2>/dev/null | head -1 || echo ""
    else
        echo ""
    fi
}

# Atualiza IP no arquivo Dart
update_ip() {
    local new_ip=$1
    local old_ip=$2
    
    if [ "$new_ip" = "$old_ip" ]; then
        echo "✅ IP não mudou: $new_ip"
        return 0
    fi
    
    echo "🔄 IP mudou: ${old_ip:-'não configurado'} → $new_ip"
    echo "   Atualizando arquivo..."
    
    # Verifica se arquivo existe
    if [ ! -f "$API_SERVICE_FILE" ]; then
        echo "❌ Erro: Arquivo não encontrado: $API_SERVICE_FILE" >&2
        exit 1
    fi
    
    # Backup
    cp "$API_SERVICE_FILE" "${API_SERVICE_FILE}.bak"
    echo "   Backup criado: ${API_SERVICE_FILE}.bak"
    
    # Atualiza baseUrl
    if [ -n "$old_ip" ]; then
        sed -i "s|http://${old_ip}:${PORT}|http://${new_ip}:${PORT}|g" "$API_SERVICE_FILE"
    else
        # Se não tinha IP, substitui o padrão
        sed -i "s|http://[0-9.]\+:${PORT}|http://${new_ip}:${PORT}|g" "$API_SERVICE_FILE"
    fi
    
    # Atualiza wsUrl
    if [ -n "$old_ip" ]; then
        sed -i "s|ws://${old_ip}:${PORT}|ws://${new_ip}:${PORT}|g" "$API_SERVICE_FILE"
    else
        sed -i "s|ws://[0-9.]\+:${PORT}|ws://${new_ip}:${PORT}|g" "$API_SERVICE_FILE"
    fi
    
    echo "✅ IP atualizado com sucesso!"
    echo ""
    echo "📝 Mudanças:"
    echo "   baseUrl: http://${new_ip}:${PORT}"
    echo "   wsUrl: ws://${new_ip}:${PORT}/ws/listen"
    
    return 1
}

# Verifica se servidor está acessível
test_connection() {
    local ip=$1
    echo ""
    echo "🔍 Testando conexão com servidor..."
    
    if curl -s --connect-timeout 2 "http://${ip}:${PORT}/health" > /dev/null 2>&1; then
        echo "✅ Servidor acessível em http://${ip}:${PORT}"
        return 0
    else
        echo "⚠️  Servidor não está acessível em http://${ip}:${PORT}"
        echo "   Verifique se o servidor está rodando:"
        echo "   python3 backend/api/main.py"
        return 1
    fi
}

# Main
CURRENT_IP=$(get_current_ip)
NEW_IP=$(detect_ip)

echo "IP atual no código: ${CURRENT_IP:-'não encontrado'}"
echo "IP detectado: $NEW_IP"
echo ""

UPDATED=false
if update_ip "$NEW_IP" "$CURRENT_IP"; then
    UPDATED=true
fi

test_connection "$NEW_IP"

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ "$UPDATED" = false ]; then
    echo "✅ Tudo pronto! IP atualizado e servidor acessível."
    echo ""
    echo "🚀 Próximo passo:"
    echo "   cd mobile_app && flutter run"
else
    echo "✅ IP já está correto!"
    echo ""
    echo "💡 Dica: Execute este script sempre que mudar de rede WiFi"
fi

echo "═══════════════════════════════════════════════════════════════"

