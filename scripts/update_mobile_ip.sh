#!/bin/bash
# Script inteligente: Atualiza IP, gerencia servidor e executa app
# Detecta IP, gerencia servidor automaticamente, tenta portas alternativas

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_SERVICE_FILE="$PROJECT_ROOT/mobile_app/lib/services/api_service.dart"
SERVER_SCRIPT="$PROJECT_ROOT/backend/api/main.py"
PID_FILE="/tmp/john_server.pid"
LOG_FILE="/tmp/john_server.log"
DEFAULT_PORT=8000
MAX_PORT_ATTEMPTS=10

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 JONH ASSISTANT - SCRIPT INTELIGENTE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Detecta IP atual da máquina
detect_ip() {
    local ip=""
    
    if command -v hostname &> /dev/null; then
        ip=$(hostname -I 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i !~ /^127\./) {print $i; exit}}')
    fi
    
    if [ -z "$ip" ]; then
        if command -v ip &> /dev/null; then
            ip=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $7; exit}' | head -1)
        fi
    fi
    
    if [ -z "$ip" ]; then
        if [ -f /proc/net/route ]; then
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
        echo -e "${RED}❌ Erro: Não foi possível detectar o IP da rede local${NC}" >&2
        exit 1
    fi
    
    echo "$ip"
}

# Verifica se porta está em uso
is_port_in_use() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i :$port > /dev/null 2>&1
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$port "
    elif command -v ss &> /dev/null; then
        ss -tuln | grep -q ":$port "
    else
        # Fallback: tenta conectar
        timeout 1 bash -c "echo > /dev/tcp/localhost/$port" 2>/dev/null
    fi
}

# Encontra porta disponível
find_available_port() {
    local start_port=$1
    local port=$start_port
    local attempts=0
    
    while [ $attempts -lt $MAX_PORT_ATTEMPTS ]; do
        if ! is_port_in_use $port; then
            echo $port
            return 0
        fi
        port=$((port + 1))
        attempts=$((attempts + 1))
    done
    
    echo ""
    return 1
}

# Verifica se servidor está rodando
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            # Verifica se é realmente o nosso processo
            if ps -p "$pid" -o cmd= 2>/dev/null | grep -q "backend/api/main.py"; then
                echo "$pid"
                return 0
            fi
        fi
    fi
    
    # Tenta encontrar processo manualmente
    local pid=$(pgrep -f "python3.*backend/api/main.py" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        echo "$pid" > "$PID_FILE"
        echo "$pid"
        return 0
    fi
    
    return 1
}

# Detecta porta do servidor rodando
detect_server_port() {
    local pid=$1
    
    if [ -z "$pid" ]; then
        echo ""
        return 1
    fi
    
    # Tenta detectar porta do processo
    if command -v lsof &> /dev/null; then
        local port=$(lsof -p "$pid" -a -i TCP -s TCP:LISTEN 2>/dev/null | grep -oP ':\K[0-9]+' | head -1)
        if [ -n "$port" ]; then
            echo "$port"
            return 0
        fi
    fi
    
    # Fallback: testa portas comuns
    for port in 8000 8001 8002 8003 8004; do
        if curl -s --connect-timeout 1 "http://localhost:$port/health" > /dev/null 2>&1; then
            echo "$port"
            return 0
        fi
    done
    
    echo ""
    return 1
}

# Inicia servidor
start_server() {
    local port=$1
    
    echo -e "${BLUE}🔄 Iniciando servidor na porta $port...${NC}"
    
    # Remove PID file antigo se existir
    rm -f "$PID_FILE"
    
    # Inicia servidor em background
    cd "$PROJECT_ROOT"
    nohup python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Salva PID
    echo "$pid" > "$PID_FILE"
    
    # Aguarda servidor iniciar (máximo 10 segundos)
    local max_wait=10
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if curl -s --connect-timeout 1 "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Servidor iniciado com sucesso (PID: $pid, Porta: $port)${NC}"
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "."
    done
    
    echo ""
    echo -e "${YELLOW}⚠️  Servidor pode estar iniciando ainda...${NC}"
    echo "   Verifique logs: tail -f $LOG_FILE"
    
    return 0
}

# Para servidor
stop_server() {
    local pid=$(is_server_running)
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}🛑 Parando servidor (PID: $pid)...${NC}"
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        # Force kill se ainda estiver rodando
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        rm -f "$PID_FILE"
        echo -e "${GREEN}✅ Servidor parado${NC}"
    fi
}

# Extrai IP atual do código
get_current_ip() {
    if [ -f "$API_SERVICE_FILE" ]; then
        grep -oP "http://\K[0-9.]+(?=:[0-9]+)" "$API_SERVICE_FILE" 2>/dev/null | head -1 || echo ""
    else
        echo ""
    fi
}

# Extrai porta atual do código
get_current_port() {
    if [ -f "$API_SERVICE_FILE" ]; then
        grep -oP "http://[0-9.]+:\K[0-9]+" "$API_SERVICE_FILE" 2>/dev/null | head -1 || echo "$DEFAULT_PORT"
    else
        echo "$DEFAULT_PORT"
    fi
}

# Atualiza IP e porta no código
update_config() {
    local new_ip=$1
    local new_port=$2
    local old_ip=$3
    local old_port=$4
    
    local changed=false
    
    if [ "$new_ip" != "$old_ip" ] || [ "$new_port" != "$old_port" ]; then
        echo -e "${BLUE}🔄 Atualizando configuração...${NC}"
        echo "   IP: ${old_ip:-'não configurado'} → $new_ip"
        echo "   Porta: ${old_port:-$DEFAULT_PORT} → $new_port"
        
        # Backup
        cp "$API_SERVICE_FILE" "${API_SERVICE_FILE}.bak"
        
        # Atualiza baseUrl
        if [ -n "$old_ip" ] && [ -n "$old_port" ]; then
            sed -i "s|http://${old_ip}:${old_port}|http://${new_ip}:${new_port}|g" "$API_SERVICE_FILE"
        else
            sed -i "s|http://[0-9.]\+:[0-9]\+|http://${new_ip}:${new_port}|g" "$API_SERVICE_FILE"
        fi
        
        # Atualiza wsUrl
        if [ -n "$old_ip" ] && [ -n "$old_port" ]; then
            sed -i "s|ws://${old_ip}:${old_port}|ws://${new_ip}:${new_port}|g" "$API_SERVICE_FILE"
        else
            sed -i "s|ws://[0-9.]\+:[0-9]\+|ws://${new_ip}:${new_port}|g" "$API_SERVICE_FILE"
        fi
        
        echo -e "${GREEN}✅ Configuração atualizada!${NC}"
        changed=true
    else
        echo -e "${GREEN}✅ Configuração já está correta${NC}"
    fi
    
    [ "$changed" = true ]
}

# Testa conexão
test_connection() {
    local ip=$1
    local port=$2
    
    echo ""
    echo -e "${BLUE}🔍 Testando conexão...${NC}"
    
    if curl -s --connect-timeout 2 "http://${ip}:${port}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Servidor acessível em http://${ip}:${port}${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Servidor não está acessível em http://${ip}:${port}${NC}"
        return 1
    fi
}

# Main
main() {
    # Detecta IP
    NEW_IP=$(detect_ip)
    echo -e "${BLUE}📡 IP detectado: $NEW_IP${NC}"
    
    # Lê configuração atual
    CURRENT_IP=$(get_current_ip)
    CURRENT_PORT=$(get_current_port)
    
    echo -e "${BLUE}📋 Configuração atual:${NC}"
    echo "   IP: ${CURRENT_IP:-'não configurado'}"
    echo "   Porta: $CURRENT_PORT"
    echo ""
    
    # Verifica servidor
    SERVER_PID=$(is_server_running 2>/dev/null || echo "")
    
    if [ -n "$SERVER_PID" ] && [ "$SERVER_PID" != "" ]; then
        echo -e "${GREEN}✅ Servidor já está rodando (PID: $SERVER_PID)${NC}"
        DETECTED_PORT=$(detect_server_port "$SERVER_PID")
        
        if [ -n "$DETECTED_PORT" ]; then
            SERVER_PORT=$DETECTED_PORT
            echo "   Porta detectada: $SERVER_PORT"
        else
            SERVER_PORT=${CURRENT_PORT:-$DEFAULT_PORT}
            echo -e "${YELLOW}⚠️  Não foi possível detectar porta, usando: $SERVER_PORT${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Servidor não está rodando${NC}"
        
        # Tenta porta atual primeiro
        if [ -n "$CURRENT_PORT" ] && [ "$CURRENT_PORT" != "" ] && ! is_port_in_use "$CURRENT_PORT"; then
            SERVER_PORT=$CURRENT_PORT
            echo "   Porta $CURRENT_PORT está disponível"
        else
            # Encontra porta disponível
            echo "   Procurando porta disponível..."
            START_PORT=${CURRENT_PORT:-$DEFAULT_PORT}
            SERVER_PORT=$(find_available_port $START_PORT)
            
            if [ -z "$SERVER_PORT" ] || [ "$SERVER_PORT" = "" ]; then
                echo -e "${RED}❌ Erro: Não foi possível encontrar porta disponível${NC}"
                exit 1
            fi
            
            if [ "$SERVER_PORT" != "$START_PORT" ]; then
                echo -e "${GREEN}   Porta disponível encontrada: $SERVER_PORT (porta $START_PORT estava ocupada)${NC}"
            else
                echo -e "${GREEN}   Porta disponível: $SERVER_PORT${NC}"
            fi
        fi
        
        # Atualiza porta no código se necessário
        if [ "$SERVER_PORT" != "$CURRENT_PORT" ]; then
            update_config "$NEW_IP" "$SERVER_PORT" "$CURRENT_IP" "$CURRENT_PORT" || true
            CURRENT_PORT=$SERVER_PORT
        fi
        
        # Inicia servidor
        start_server "$SERVER_PORT"
    fi
    
    # Atualiza IP se necessário
    update_config "$NEW_IP" "$SERVER_PORT" "$CURRENT_IP" "$SERVER_PORT" || true
    
    # Testa conexão
    test_connection "$NEW_IP" "$SERVER_PORT"
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${GREEN}✅ Tudo pronto!${NC}"
    echo ""
    echo "📊 Status:"
    echo "   IP: $NEW_IP"
    echo "   Porta: $SERVER_PORT"
    echo "   Servidor: $(is_server_running > /dev/null && echo 'Rodando' || echo 'Parado')"
    echo ""
    echo "🚀 Próximo passo:"
    echo "   cd mobile_app && flutter run"
    echo "═══════════════════════════════════════════════════════════════"
}

# Trap para limpar ao sair
trap 'echo ""' EXIT

main "$@"
