# Jonh Assistant - Assistente de Voz Inteligente

Assistente de voz profissional com processamento local e opção de cloud para máxima performance. Similar à Alexa, mas com controle total sobre seus dados e processamento.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Características Principais](#características-principais)
- [Requisitos](#requisitos)
- [Instalação Completa](#instalação-completa)
- [Configuração](#configuração)
- [Como Executar](#como-executar)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API e Endpoints](#api-e-endpoints)
- [Troubleshooting](#troubleshooting)
- [Desenvolvimento](#desenvolvimento)

---

## 🎯 Visão Geral

O **Jonh Assistant** é um assistente de voz completo que combina:

- **Processamento Local**: STT (Speech-to-Text) 100% offline
- **Respostas em Texto**: LLM retorna respostas textuais (TTS disponível via endpoint `/api/synthesize`)
- **Flexibilidade Cloud/Local**: LLM configurável entre Groq (cloud, rápido) ou Ollama (local, privado)
- **Inteligência Contextual**: Sistema de memória, histórico de conversas e ferramentas inteligentes
- **Interface Moderna**: App mobile Flutter com design profissional
- **Extensível**: Sistema de plugins modular para adicionar novas funcionalidades

---

## ✨ Características Principais

### Backend
- ✅ **Speech-to-Text**: Whisper Large-v3 (100% local, offline)
- ⚠️ **Text-to-Speech**: Piper TTS implementado mas **desabilitado no fluxo principal** (disponível via `/api/synthesize`)
- ✅ **LLM Dual**: Groq (cloud, padrão) ou Ollama (local, opcional)
- ✅ **Streaming**: Respostas em tempo real via SSE
- ✅ **Tool Calling**: Busca web, calculadora, conversão de moedas, **especialista em vagas**
- ✅ **Sistema de Memória**: Armazenamento e recuperação de lembranças
- ✅ **Histórico de Conversas**: Persistência de conversas com SQLite
- ✅ **Geolocalização**: Suporte a GPS para contexto local
- ✅ **Wake Word**: Detecção por voz com OpenWakeWord
- ✅ **Performance**: Pipeline otimizado com cache e paralelismo

### Mobile App (Flutter)
- ✅ **Interface Moderna**: Design profissional com tema claro/escuro
- ✅ **Chat em Tempo Real**: Streaming de respostas em texto
- ✅ **Gravação de Áudio**: Captura otimizada (16kHz mono) para entrada do usuário
- ✅ **Respostas em Texto**: Assistente responde via texto (TTS desabilitado no fluxo principal)
- ✅ **Offline**: App funciona mesmo com servidor desconectado
- ⚠️ **Wake Word**: Implementado mas requer configuração (Access Key do Picovoice)
- ✅ **Histórico**: Visualização e gerenciamento de conversas salvas
- ✅ **Multiplataforma**: Android, iOS (parcial) e Web

---

## 📦 Requisitos

### Hardware Mínimo
- **CPU**: Intel i5/i7 12ª geração ou superior (ou equivalente AMD)
- **RAM**: 16 GB (recomendado 32 GB para melhor performance)
- **Armazenamento**: 20 GB livres (para modelos de IA)
- **GPU**: Opcional (NVIDIA com CUDA melhora performance)

**Testado e otimizado em**: Galaxy Book 2 (32GB RAM, 1TB NVMe, i5/i7 12ª gen)

### Software
- **OS**: Windows 11 com WSL2 (Ubuntu 22.04/24.04) ou Linux nativo
- **Python**: 3.10 ou superior
- **Flutter**: 3.35+ (para desenvolvimento mobile)
- **FFmpeg**: Instalado no sistema (para processamento de áudio)
- **Groq API Key** (padrão) ou **Ollama instalado** (modo offline)

### Dependências do Sistema
```bash
# Ubuntu/WSL2
sudo apt update
sudo apt install -y python3-pip python3-venv ffmpeg libsndfile1 build-essential

# Para Flutter (se desenvolver mobile)
# Siga: https://docs.flutter.dev/get-started/install/linux
```

---

## 🚀 Instalação Completa

### 1. Clonar Repositório

```bash
git clone https://github.com/brunoadsba/john.git
cd john
```

### 2. Configurar Backend

```bash
# Criar ambiente virtual
python3 -m venv backend/.venv
source backend/.venv/bin/activate  # No Windows: backend\.venv\Scripts\activate

# Instalar dependências
pip install -r backend/requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env  # Se não existir, crie manualmente
nano .env  # Ou use seu editor preferido
```

**Configure o `.env` com:**

```bash
# LLM Provider (groq ou ollama)
LLM_PROVIDER=groq

# Se usar Groq (padrão - requer internet)
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=llama-3.1-8b-instant

# Se usar Ollama (local - offline)
# LLM_PROVIDER=ollama
# OLLAMA_HOST=http://localhost:11434
# OLLAMA_MODEL=llama3:8b-instruct-q4_0

# Busca Web (opcional - requer Tavily API key)
WEB_SEARCH_ENABLED=true
TAVILY_API_KEY=sua_chave_aqui  # Opcional - usa DuckDuckGo se não fornecido

# Outras configurações
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### 3. Baixar Modelos

Os modelos são baixados automaticamente na primeira execução. Para baixar manualmente:

```bash
# Whisper (STT)
# Baixado automaticamente na primeira execução

# Piper TTS
# Baixe modelo pt-BR de: https://github.com/rhasspy/piper/releases
# Coloque em: models/tts/pt_BR-jeff-medium.onnx

# Ollama (se usar modo offline)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3:8b-instruct-q4_0
```

### 4. Configurar Mobile App (Opcional)

```bash
cd mobile_app

# Instalar dependências Flutter
flutter pub get

# Configurar URL do backend
# Edite: lib/config/env.dart
# Ou use script automático:
cd ..
./scripts/check_mobile_config.sh

# Gerar ícones (se tiver logo)
flutter pub run flutter_launcher_icons
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

Principais variáveis configuráveis:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `LLM_PROVIDER` | `groq` ou `ollama` | `groq` |
| `GROQ_API_KEY` | Chave API do Groq | - |
| `GROQ_MODEL` | Modelo Groq | `llama-3.1-8b-instant` |
| `OLLAMA_HOST` | URL do Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo Ollama | `llama3:8b-instruct-q4_0` |
| `WEB_SEARCH_ENABLED` | Habilitar busca web | `true` |
| `TAVILY_API_KEY` | Chave Tavily (opcional) | - |
| `HOST` | Host do servidor | `0.0.0.0` |
| `PORT` | Porta do servidor | `8000` |
| `LOG_LEVEL` | Nível de log | `INFO` |

### Configurações Avançadas

Edite `backend/config/settings.py` para ajustes finos:
- Modelos de TTS/STT
- Thresholds de wake word
- Cache e performance
- Configurações de plugins

---

## 🏃 Como Executar

### Backend

```bash
# Ativar ambiente virtual
cd backend
source .venv/bin/activate

# Iniciar servidor
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

# Ou usar script
cd ..
./scripts/start_server.sh
```

Servidor estará disponível em:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

### Mobile App

```bash
cd mobile_app

# Executar em dispositivo/emulador
flutter run

# Executar no navegador (para testes)
flutter run -d chrome

# Build APK para Android
flutter build apk --release
# APK gerado em: build/app/outputs/flutter-apk/app-release.apk

# Build com IP customizado
flutter build apk --release \
  --dart-define=BACKEND_URL=http://SEU_IP:8000
```

### Testes Rápidos

```bash
# Health check
curl http://localhost:8000/health

# Streaming LLM
curl -N "http://localhost:8000/api/stream_text?texto=oi%20Jonh"

# Interface web para testes
# Acesse: http://localhost:8000/web/
```

---

## 🎨 Funcionalidades

### Conversação Inteligente

- **Processamento de Áudio**: Grave áudio e receba respostas em texto
- **Streaming**: Respostas aparecem em tempo real (apenas texto)
- **Contexto**: O assistente lembra da conversa atual
- **Memória Persistente**: Salve e recupere informações importantes
- **⚠️ Nota**: TTS está desabilitado - respostas são apenas textuais

### Ferramentas e Plugins

#### 🔍 Busca Web
Busca informações atualizadas na internet usando DuckDuckGo ou Tavily.

```
Usuário: "Qual é a previsão do tempo para hoje?"
Assistente: [Busca na web e retorna informações atualizadas]
```

#### 🧮 Calculadora
Resolve cálculos matemáticos complexos.

```
Usuário: "Quanto é 25 * 47 + 132?"
Assistente: [Calcula e retorna: 1307]
```

#### 💱 Conversão de Moedas
Converte valores entre diferentes moedas usando taxas atualizadas.

```
Usuário: "Quanto é 100 dólares em reais?"
Assistente: [Busca taxa atual e converte]
```

#### 💼 Especialista em Vagas
Busca inteligente de vagas de emprego com:
- **9+ sites principais**: LinkedIn, Indeed, Vagas.com, Gupy, Catho, etc.
- **Detecção de nicho**: Estágios, tecnologia, criação, freelance
- **Filtros robustos**: Remove vagas encerradas automaticamente
- **Informações detalhadas**: Site de origem, datas de publicação/encerramento

```
Usuário: "Busque vagas de estágio em tecnologia"
Assistente: [Busca em sites especializados e retorna resultados formatados]
```

#### 📍 Geolocalização
Fornece contexto local quando necessário (requer permissão GPS no mobile).

---

## ⚠️ Notas Importantes

### Status do TTS (Text-to-Speech)

**TTS está DESABILITADO no fluxo principal de respostas do assistente.**

- ✅ TTS está **implementado** e funcional (Piper TTS)
- ❌ TTS **não é usado** nas respostas automáticas
- ✅ Endpoint `/api/synthesize` disponível para síntese manual
- 📖 Ver [docs/STATUS_ATUAL_TTS.md](docs/STATUS_ATUAL_TTS.md) para detalhes

O assistente atualmente responde **apenas via texto** para:
- Respostas mais rápidas
- Melhor UX em mobile
- Redução de uso de recursos

Para reabilitar TTS, veja instruções em `docs/STATUS_ATUAL_TTS.md`.

### Wake Word

**Wake Word requer configuração manual:**

- Backend: OpenWakeWord funcional (modelo "alexa")
- Mobile: Porcupine implementado mas requer:
  - Access Key do Picovoice (obter em https://console.picovoice.ai/)
  - Configuração em SharedPreferences
  - Modelo customizado "jonh" ou usar "alexa"

---

### Histórico de Conversas

- Salve conversas importantes
- Visualize e gerencie histórico
- Edite títulos de conversas
- Delete conversas antigas

---

## 📁 Estrutura do Projeto

```
john/
├── backend/                    # Backend Python/FastAPI
│   ├── api/
│   │   ├── main.py             # Aplicação FastAPI principal
│   │   ├── routes/             # Endpoints REST e WebSocket
│   │   │   ├── process.py      # Processamento de áudio/texto
│   │   │   ├── websocket.py    # WebSocket em tempo real
│   │   │   ├── streaming.py    # SSE streaming
│   │   │   ├── health.py       # Health check
│   │   │   └── ...
│   │   ├── handlers/           # Handlers de processamento
│   │   └── middleware/         # Middlewares (rate limiting, etc.)
│   ├── services/               # Serviços principais
│   │   ├── stt_service.py      # Speech-to-Text (Whisper)
│   │   ├── llm/                # LLM (Groq/Ollama)
│   │   ├── tts/                # Text-to-Speech (Piper)
│   │   ├── context_manager.py  # Gerenciamento de contexto
│   │   ├── memory_service.py   # Sistema de memória
│   │   └── ...
│   ├── plugins/                # Plugins e ferramentas
│   │   ├── web_search_plugin.py
│   │   ├── job_search_plugin.py  # Especialista em vagas
│   │   ├── calculator_plugin.py
│   │   └── ...
│   ├── config/
│   │   └── settings.py         # Configurações
│   ├── data/                   # Dados e dicionários
│   └── requirements.txt        # Dependências Python
│
├── mobile_app/                 # App Flutter
│   ├── lib/
│   │   ├── main.dart           # Entry point
│   │   ├── features/           # Arquitetura feature-based
│   │   │   ├── home/           # Tela principal
│   │   │   ├── voice/          # Funcionalidades de voz
│   │   │   └── wake_word/      # Wake word
│   │   ├── services/           # Serviços e lógica
│   │   │   ├── api_service.dart
│   │   │   ├── audio_service.dart
│   │   │   └── ...
│   │   ├── widgets/            # Componentes reutilizáveis
│   │   ├── models/             # Modelos de dados
│   │   ├── theme/              # Design system
│   │   └── config/             # Configurações
│   ├── android/                # Configurações Android
│   └── pubspec.yaml            # Dependências Flutter
│
├── models/                     # Modelos de IA
│   ├── whisper/                # Modelos Whisper (STT)
│   └── tts/                    # Modelos Piper TTS
│
├── scripts/                    # Scripts de automação
│   ├── start_server.sh         # Iniciar servidor
│   ├── check_mobile_config.sh  # Verificar config mobile
│   └── ...
│
├── docs/                       # Documentação detalhada
│   ├── API.md                  # Documentação da API
│   ├── ARQUITETURA.md          # Arquitetura técnica
│   └── ...
│
├── .env                        # Variáveis de ambiente (criar)
├── .env.example                # Exemplo de configuração
├── README.md                   # Este arquivo
├── QUICKSTART.md               # Guia rápido
└── LICENSE.txt                 # Licença
```

---

## 🔌 API e Endpoints

### REST Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Informações da API |
| `GET` | `/health` | Status dos serviços |
| `POST` | `/api/process_audio` | Pipeline completo (STT→LLM→texto) |
| `POST` | `/api/process_text` | Processamento de texto (LLM) |
| `POST` | `/api/transcribe` | Apenas transcrição de áudio |
| `POST` | `/api/synthesize` | Apenas síntese de voz (TTS manual) |
| `GET` | `/api/stream_text` | Streaming LLM via SSE |
| `GET` | `/api/sessions` | Lista sessões ativas |
| `GET` | `/api/session/{id}` | Informações da sessão |
| `DELETE` | `/api/session/{id}` | Remove sessão |
| `POST` | `/api/conversations/save` | Salvar conversa |
| `GET` | `/api/conversations` | Listar conversas |
| `GET` | `/api/conversations/{id}` | Recuperar conversa |
| `DELETE` | `/api/conversations/{id}` | Deletar conversa |
| `PATCH` | `/api/conversations/{id}/title` | Atualizar título |

### WebSocket

| Endpoint | Descrição |
|----------|-----------|
| `/ws/listen` | Comunicação em tempo real |

**Protocolo WebSocket:**
```json
// Cliente → Servidor
{"type": "start_session"}
<audio_bytes>

// Servidor → Cliente
{"type": "session_started", "session_id": "uuid-123"}
{"type": "transcription", "text": "olá Jonh"}
{"type": "response", "text": "Olá! Como posso ajudar?", "metrics": {...}}
{"type": "complete", "metrics": {...}}
```

**Nota**: Respostas são apenas em texto. TTS está desabilitado no fluxo principal.

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Servidor não inicia

**Erro**: `ModuleNotFoundError` ou `ImportError`
```bash
# Solução: Ative o ambiente virtual
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

#### 2. Groq não conecta

**Erro**: `401 Unauthorized` ou `API key invalid`
```bash
# Verifique a chave no .env
cat .env | grep GROQ_API_KEY

# Teste a chave
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer SUA_CHAVE_AQUI"
```

#### 3. Ollama não encontrado

**Erro**: `Connection refused` ou `Ollama not running`
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo
ollama pull llama3:8b-instruct-q4_0

# Verificar se está rodando
systemctl --user status ollama
# Se não estiver:
systemctl --user start ollama
```

#### 4. Áudio não funciona

**Erro**: `FFmpeg not found` ou áudio não processa
```bash
# Instalar FFmpeg
sudo apt install ffmpeg libsndfile1

# Verificar formato do áudio
# Deve ser: WAV, 16kHz, mono, 16-bit
```

#### 5. Mobile não conecta ao servidor

**Problema**: App não encontra o backend

**Solução WSL2 (Windows):**
```powershell
# 1. Descobrir IP do WSL2
wsl hostname -I

# 2. Configurar port forwarding (PowerShell como Admin)
netsh interface portproxy add v4tov4 \
  listenport=8000 listenaddress=0.0.0.0 \
  connectport=8000 connectaddress=WSL2_IP

# 3. Permitir no firewall
New-NetFirewallRule -DisplayName "Jonh Assistant API" \
  -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 4. Atualizar URL no mobile app
# Edite: mobile_app/lib/config/env.dart
# Use: http://SEU_IP_WINDOWS:8000
```

**Solução Linux/Mac:**
```bash
# 1. Descobrir IP local
hostname -I

# 2. Atualizar URL no mobile app
# Edite: mobile_app/lib/config/env.dart
# Use: http://SEU_IP:8000
```

#### 6. Erro de memória

**Sintoma**: Aplicação trava ou erro `Out of Memory`

**Soluções:**
```bash
# 1. Usar modelo Whisper menor
# Edite .env:
WHISPER_MODEL=base  # ao invés de large-v3

# 2. Usar modelo Ollama menor
ollama pull llama3:8b-instruct-q2_K

# 3. Fechar outros aplicativos
# 4. Reduzir max_tokens no settings.py
```

#### 7. Mobile app não compila

**Erro**: Compilação Flutter falha

```bash
# Limpar build
cd mobile_app
flutter clean
flutter pub get

# Verificar versão Flutter
flutter --version  # Deve ser 3.35+

# Verificar erros
flutter doctor
```

### Modo Offline (100% Local)

Para rodar completamente offline:

1. **Instalar Ollama**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3:8b-instruct-q4_0
```

2. **Configurar .env**
```bash
LLM_PROVIDER=ollama
WEB_SEARCH_ENABLED=false
```

3. **Verificar**
```bash
# Ollama deve estar rodando
systemctl --user status ollama

# Teste
curl http://localhost:11434/api/generate -d '{
  "model": "llama3:8b-instruct-q4_0",
  "prompt": "teste",
  "stream": false
}'
```

**Nota**: STT (Whisper) é 100% local e não requer internet. TTS (Piper) está implementado mas desabilitado no fluxo principal de respostas do assistente - use `/api/synthesize` para síntese manual se necessário.

---

## 💻 Desenvolvimento

### Adicionar Novo Plugin

1. Crie arquivo em `backend/plugins/`
```python
from backend.core.plugin_manager import BasePlugin

class MeuPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "meu_plugin"
    
    def get_tool_definition(self) -> Dict:
        return {...}  # Definição OpenAI Function Calling
    
    def execute(self, function_name: str, arguments: Dict) -> Any:
        # Sua lógica aqui
        return resultado
```

2. Registre no `PluginManager` (já feito automaticamente se estiver em `backend/plugins/`)

### Adicionar Nova Rota

1. Crie arquivo em `backend/api/routes/`
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/minha_rota")

@router.get("/teste")
async def teste():
    return {"status": "ok"}
```

2. Registre em `backend/api/main.py`
```python
from backend.api.routes import minha_rota
app.include_router(minha_rota.router)
```

### Testes

```bash
# Backend
cd backend
pytest -v

# Mobile (Flutter)
cd mobile_app
flutter test

# E2E Web (Playwright)
./scripts/test_playwright.sh
```

---

## 📚 Documentação Adicional

- **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido de início
- **[docs/API.md](docs/API.md)** - Documentação completa da API
- **[docs/ARQUITETURA.md](docs/ARQUITETURA.md)** - Arquitetura técnica
- **[docs/STATUS_PROJETO.md](docs/STATUS_PROJETO.md)** - Status e features
- **[docs/ANALISE_CRITICA_PROJETO.md](docs/ANALISE_CRITICA_PROJETO.md)** - Análise crítica promises vs reality
- **[docs/STATUS_ATUAL_TTS.md](docs/STATUS_ATUAL_TTS.md)** - Status detalhado do TTS
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guia de contribuição

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE.txt](LICENSE.txt) para detalhes.

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/brunoadsba/john/issues)
- **Documentação**: [docs/](docs/)

---

**Jonh Assistant** - Seu assistente de voz local, privado e profissional. 🎙️✨
