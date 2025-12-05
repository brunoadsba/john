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

# Verifica Ollama
if ! pgrep -x "ollama" > /dev/null; then
    warn "Ollama não está rodando. Iniciando..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Verifica modelo
if ! ollama list | grep -q "llama3"; then
    error "Modelo Llama3 não encontrado. Execute: ollama pull llama3:8b-instruct-q4_0"
    exit 1
fi

echo ""
echo "=========================================="
echo "Iniciando Jonh Assistant API"
echo "=========================================="
echo ""

# Ativa ambiente virtual e inicia servidor
cd backend/api
../../backend/.venv/bin/python main.py

