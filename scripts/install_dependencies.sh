#!/bin/bash
# Script de instalação de dependências do Jonh Assistant

set -e  # Para em caso de erro

echo "=========================================="
echo "Instalação de Dependências - Jonh Assistant"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para mensagens
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se está no diretório correto
if [ ! -f "backend/requirements.txt" ]; then
    error "Execute este script do diretório raiz do projeto"
    exit 1
fi

# 1. Instala dependências do sistema
info "Instalando dependências do sistema..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv build-essential \
    libsndfile1 ffmpeg curl wget git

# 2. Cria ambiente virtual
info "Criando ambiente virtual Python..."
if [ -d "backend/.venv" ]; then
    warn "Ambiente virtual já existe, recriando..."
    rm -rf backend/.venv
fi
python3 -m venv backend/.venv

# 3. Instala dependências Python
info "Instalando dependências Python..."
backend/.venv/bin/pip install --upgrade pip
backend/.venv/bin/pip install -r backend/requirements.txt

# 4. Verifica Ollama
info "Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    warn "Ollama não encontrado. Instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    info "Ollama já instalado: $(ollama --version)"
fi

# 5. Inicia Ollama se não estiver rodando
if ! pgrep -x "ollama" > /dev/null; then
    info "Iniciando Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# 6. Baixa modelo LLM
info "Verificando modelo LLM..."
if ollama list | grep -q "llama3:8b-instruct"; then
    info "Modelo Llama3 já instalado"
else
    warn "Baixando modelo Llama3 (isso pode demorar)..."
    ollama pull llama3:8b-instruct-q4_0
fi

# 7. Cria diretórios necessários
info "Criando diretórios..."
mkdir -p models/piper models/whisper temp

# 8. Cria arquivo .env se não existir
if [ ! -f ".env" ]; then
    info "Criando arquivo .env..."
    cat > .env << 'EOF'
# Configurações do Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:8b-instruct-q4_0

# Whisper
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8

# Piper TTS
PIPER_VOICE=pt_BR-faber-medium
PIPER_MODEL_PATH=./models/piper

# Caminhos
MODELS_DIR=./models
TEMP_DIR=./temp

# Logging
LOG_LEVEL=INFO
EOF
else
    info "Arquivo .env já existe"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Instalação concluída com sucesso!${NC}"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Ative o ambiente virtual:"
echo "   source backend/.venv/bin/activate"
echo ""
echo "2. Inicie o servidor:"
echo "   cd backend/api && python main.py"
echo ""
echo "3. Acesse a documentação:"
echo "   http://localhost:8000/docs"
echo ""

