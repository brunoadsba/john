# Guia de Instalação Detalhado - Jonh Assistant

## Pré-requisitos

### Hardware Mínimo
- CPU: Intel i5 8ª geração ou AMD Ryzen 5 3600
- RAM: 16 GB
- Armazenamento: 20 GB livres
- GPU: Opcional (NVIDIA com CUDA para melhor performance)

### Hardware Recomendado
- CPU: Intel i7 12ª geração ou AMD Ryzen 7 5800X
- RAM: 32 GB
- Armazenamento: 50 GB SSD
- GPU: NVIDIA RTX 3060 ou superior

### Software
- Windows 11 (ou Linux Ubuntu 22.04+)
- WSL2 (se Windows)
- Python 3.10 ou superior
- Git

## Instalação no Windows (WSL2)

### Passo 1: Instalar WSL2

Abra PowerShell como Administrador:

```powershell
# Instala WSL2 com Ubuntu
wsl --install -d Ubuntu

# Atualiza WSL
wsl --update

# Reinicie o computador se solicitado
```

Após reiniciar, abra Ubuntu e configure usuário/senha.

### Passo 2: Atualizar Sistema

No terminal Ubuntu (WSL):

```bash
sudo apt update && sudo apt upgrade -y
```

### Passo 3: Instalar Dependências do Sistema

```bash
# Ferramentas essenciais
sudo apt install -y build-essential git curl wget

# Dependências de áudio
sudo apt install -y libsndfile1 ffmpeg

# Python e pip
sudo apt install -y python3 python3-pip python3-venv
```

### Passo 4: Instalar Ollama

```bash
# Baixa e instala Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verifica instalação
ollama --version

# Inicia serviço Ollama
ollama serve &

# Aguarde alguns segundos e teste
ollama list
```

### Passo 5: Baixar Modelo LLM

```bash
# Modelo recomendado (4.7 GB)
ollama pull llama3:8b-instruct-q4_0

# Alternativa menor (3.2 GB)
ollama pull llama3:8b-instruct-q2_K

# Alternativa maior e melhor (8.9 GB)
ollama pull llama3:8b-instruct-q6_K

# Verifica modelos instalados
ollama list
```

### Passo 6: Clonar Repositório

```bash
# Navegue até seu diretório home
cd ~

# Clone o projeto
git clone <url-do-repositorio> john
cd john
```

### Passo 7: Configurar Ambiente Python

```bash
# Cria ambiente virtual
cd backend
python3 -m venv .venv

# Ativa ambiente virtual
source .venv/bin/activate

# Atualiza pip
pip install --upgrade pip

# Instala dependências
pip install -r requirements.txt
```

**Nota**: A instalação das dependências pode levar 5-10 minutos.

### Passo 8: Configurar Variáveis de Ambiente

```bash
# Volta para raiz do projeto
cd ..

# Cria arquivo .env (se não existir)
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
```

### Passo 9: Criar Diretórios Necessários

```bash
mkdir -p models/piper temp
```

### Passo 10: Testar Instalação

```bash
# Ativa ambiente virtual (se não estiver ativo)
source backend/.venv/bin/activate

# Inicia servidor
cd backend/api
python main.py
```

Você deve ver:

```
============================================================
Iniciando Jonh Assistant API
============================================================
Inicializando serviços de IA...
Inicializando Whisper STT: model=base, device=cpu
Inicializando Ollama LLM: model=llama3:8b-instruct-q4_0, host=http://localhost:11434
Inicializando Piper TTS: voice=pt_BR-faber-medium
Serviços inicializados com sucesso
Servidor rodando em 0.0.0.0:8000
============================================================
```

### Passo 11: Verificar Health Check

Em outro terminal:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{
  "status": "healthy",
  "versao": "1.0.0",
  "servicos": {
    "stt": "online",
    "llm": "online",
    "tts": "online",
    "context": "online"
  }
}
```

## Instalação no Linux Nativo

### Ubuntu 22.04 / 24.04

Siga os passos 2-11 acima, pulando o Passo 1 (WSL2).

### Outras Distribuições

Adapte os comandos de instalação de pacotes para seu gerenciador:

- **Fedora/RHEL**: `dnf install` ao invés de `apt install`
- **Arch**: `pacman -S` ao invés de `apt install`

## Otimizações

### Usar GPU NVIDIA (CUDA)

Se você tem GPU NVIDIA:

```bash
# Instala CUDA Toolkit no WSL2
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda-repo-wsl-ubuntu-12-3-local_12.3.0-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-12-3-local_12.3.0-1_amd64.deb
sudo cp /var/cuda-repo-wsl-ubuntu-12-3-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# Atualiza .env
nano .env
# Mude: WHISPER_DEVICE=cuda
# Mude: WHISPER_COMPUTE_TYPE=float16
```

### Modelo Whisper Maior

Para melhor qualidade de transcrição:

```bash
# No .env, mude:
WHISPER_MODEL=medium  # ou large-v3
```

**Atenção**: Modelos maiores consomem mais RAM e são mais lentos.

## Troubleshooting

### Erro: "Ollama connection refused"

```bash
# Verifique se Ollama está rodando
ps aux | grep ollama

# Se não estiver, inicie
ollama serve &

# Aguarde 5 segundos e teste
ollama list
```

### Erro: "No module named 'faster_whisper'"

```bash
# Ative o ambiente virtual
source backend/.venv/bin/activate

# Reinstale dependências
pip install -r backend/requirements.txt
```

### Erro: "Out of memory"

Reduza o tamanho dos modelos:

```bash
# Use modelo Whisper menor
# No .env: WHISPER_MODEL=tiny

# Use modelo Llama menor
ollama pull llama3:8b-instruct-q2_K
# No .env: OLLAMA_MODEL=llama3:8b-instruct-q2_K
```

### Servidor não inicia

```bash
# Verifique porta em uso
sudo lsof -i :8000

# Se houver processo, mate-o ou mude a porta no .env
```

### Áudio não funciona

```bash
# Reinstale dependências de áudio
sudo apt install --reinstall libsndfile1 ffmpeg

# Teste com arquivo WAV simples
```

## Próximos Passos

1. **Teste a API**: Use o script `backend/tests/manual_test.py`
2. **Explore a documentação**: Acesse `http://localhost:8000/docs`
3. **Configure o app mobile**: Veja documentação do Flutter (futuro)

## Desinstalação

```bash
# Remove ambiente virtual
rm -rf backend/.venv

# Remove modelos (opcional)
rm -rf models/

# Remove Ollama (opcional)
sudo rm /usr/local/bin/ollama
rm -rf ~/.ollama
```

## Suporte

Para problemas não listados aqui:

1. Verifique logs do servidor
2. Consulte documentação da API
3. Abra issue no GitHub com:
   - Versão do sistema operacional
   - Saída do comando `python --version`
   - Saída do comando `ollama list`
   - Logs de erro completos

