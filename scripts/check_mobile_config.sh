#!/bin/bash
# Script profissional para verificar e atualizar configuração do mobile
# Versão simplificada e focada

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/mobile_app/lib/config/env.dart"
DEFAULT_PORT=8000

# Cores
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Função para exibir mensagens
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Detecta IP do Windows na rede WiFi (para WSL)
detect_windows_ip() {
    local ip=""
    
    # Tenta obter do env.dart primeiro (apenas do defaultValue)
    if [ -f "$ENV_FILE" ]; then
        local url=$(get_current_config)
        if [ -n "$url" ]; then
            ip=$(echo "$url" | grep -oP "http://\K[0-9.]+(?=:[0-9]+)")
            if [ -n "$ip" ] && [[ $ip =~ ^192\.168\. ]]; then
                echo "$ip"
                return 0
            fi
        fi
    fi
    
    # Fallback: IP padrão comum do Windows na rede WiFi
    echo "192.168.1.5"
}

# Verifica se servidor está rodando
check_server() {
    local ip=$1
    local port=$2
    
    if curl -s --connect-timeout 2 "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Obtém IP atual do env.dart (apenas do defaultValue, ignora comentários)
get_current_config() {
    if [ -f "$ENV_FILE" ]; then
        # Procura a URL que está na linha após "defaultValue:" (pode estar na mesma linha ou próxima)
        # Procura por padrão: 'http://IP:PORT' ou "http://IP:PORT"
        local url=$(awk '/defaultValue:/{found=1; next} found && /http:\/\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+/{gsub(/["'\'']/, ""); print; exit}' "$ENV_FILE" 2>/dev/null | grep -oP "http://[0-9.]+:[0-9]+" | head -1 || echo "")
        if [ -z "$url" ]; then
            # Fallback: procura qualquer URL após defaultValue
            url=$(sed -n '/defaultValue:/,/);/p' "$ENV_FILE" 2>/dev/null | grep -oP "['\"]http://[0-9.]+:[0-9]+['\"]" | head -1 | tr -d "'\"")
        fi
        if [ -n "$url" ]; then
            echo "$url"
            return 0
        fi
    fi
    echo ""
}

# Atualiza IP no env.dart (se necessário)
update_env_file() {
    local new_ip=$1
    local new_port=$2
    local current_url=$(get_current_config)
    
    if [ -z "$current_url" ]; then
        error "Não foi possível ler configuração atual do env.dart"
        return 1
    fi
    
    local current_ip=$(echo "$current_url" | grep -oP "http://\K[0-9.]+")
    local current_port=$(echo "$current_url" | grep -oP ":\K[0-9]+")
    
    if [ "$current_ip" = "$new_ip" ] && [ "$current_port" = "$new_port" ]; then
        success "Configuração já está correta: $current_url"
        return 0
    fi
    
    info "Atualizando configuração: $current_url → http://$new_ip:$new_port"
    
    # Backup
    cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
    
    # Atualiza apenas a URL dentro do defaultValue (preserva formatação)
    # Procura pela linha que contém a URL após defaultValue:
    sed -i "s|'http://[0-9.]\+:[0-9]\+'|'http://${new_ip}:${new_port}'|g" "$ENV_FILE"
    
    success "Configuração atualizada com sucesso!"
    return 0
}

# Main
main() {
    echo "═══════════════════════════════════════════════════════════════"
    echo "  📱 VERIFICAÇÃO DE CONFIGURAÇÃO MOBILE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Detecta IP
    local detected_ip=$(detect_windows_ip)
    info "IP detectado do Windows: $detected_ip"
    
    # Lê configuração atual
    local current_url=$(get_current_config)
    if [ -n "$current_url" ]; then
        local current_ip=$(echo "$current_url" | grep -oP "http://\K[0-9.]+")
        local current_port=$(echo "$current_url" | grep -oP ":\K[0-9]+")
        info "Configuração atual: $current_url"
    else
        error "Não foi possível ler configuração do env.dart"
        exit 1
    fi
    
    echo ""
    
    # Verifica servidor
    info "Verificando servidor..."
    if check_server "$current_ip" "${current_port:-$DEFAULT_PORT}"; then
        success "Servidor está rodando na porta ${current_port:-$DEFAULT_PORT}"
    else
        warning "Servidor não está acessível na porta ${current_port:-$DEFAULT_PORT}"
        warning "Certifique-se de que o servidor está rodando:"
        echo "   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port ${current_port:-$DEFAULT_PORT}"
    fi
    
    echo ""
    
    # Atualiza se necessário
    if [ "$detected_ip" != "$current_ip" ]; then
        warning "IP detectado ($detected_ip) difere do configurado ($current_ip)"
        read -p "Deseja atualizar para $detected_ip? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            update_env_file "$detected_ip" "${current_port:-$DEFAULT_PORT}"
        else
            info "Mantendo configuração atual"
        fi
    else
        success "IP está correto: $current_ip"
    fi
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${GREEN}✅ Verificação concluída${NC}"
    echo ""
    echo "📊 Resumo:"
    echo "   IP configurado: $current_url"
    echo "   IP detectado: $detected_ip"
    echo "   Servidor: $(check_server "$current_ip" "${current_port:-$DEFAULT_PORT}" && echo 'Rodando' || echo 'Parado')"
    echo ""
    echo "🚀 Próximo passo:"
    echo "   cd mobile_app && flutter build apk --release"
    echo "═══════════════════════════════════════════════════════════════"
}

main "$@"

