#!/bin/bash
# Script para iniciar o servidor Jonh Assistant

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica diretório
if [ ! -f "backend/api/main.py" ]; then
    error "Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verifica ambiente virtual
if [ ! -d "backend/.venv" ]; then
    error "Ambiente virtual não encontrado. Execute: ./scripts/install_dependencies.sh"
    exit 1
fi

# Verifica se a porta 8000 está em uso
if lsof -ti:8000 > /dev/null 2>&1; then
    warn "Porta 8000 já está em uso. Encerrando processos..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Verifica Ollama (opcional - apenas se usar Ollama)
if ! pgrep -x "ollama" > /dev/null; then
    warn "Ollama não está rodando. (Pode ignorar se estiver usando Groq)"
fi

# Verifica modelo Ollama (opcional)
if pgrep -x "ollama" > /dev/null && ! ollama list 2>/dev/null | grep -q "llama3"; then
    warn "Modelo Llama3 não encontrado. (Pode ignorar se estiver usando Groq)"
fi

echo ""
echo "=========================================="
echo "Iniciando Jonh Assistant API"
echo "=========================================="
echo ""

# Ativa ambiente virtual e inicia servidor
cd backend/api
../../backend/.venv/bin/python main.py

