# Jonh - Assistente de Voz Inteligente

Assistente de voz profissional, similar à Alexa, com processamento local e opção de cloud para máxima performance.

## Características

- **Híbrido Local/Cloud**: STT e TTS 100% local (Whisper + Piper), LLM configurável (Groq cloud padrão ou Ollama local)
- **Streaming LLM (SSE)**: resposta começa a aparecer em tempo real
- **Baixa latência**: pipeline otimizado com paralelismo e cache (< 3s alvo)
- **Cache inteligente**: respostas e TTS com pré-aquecimento
- **Português nativo**: parâmetros ajustados para pt-BR (STT/TTS)
- **Tool calling**: busca web automática (DuckDuckGo/Tavily) quando necessário
- **Monitoramento de performance**: métricas end-to-end e script de análise
- **Estrutura profissional**: código organizado, documentação completa, testes automatizados

## Arquitetura

### Backend (Python/FastAPI)
- **STT**: faster-whisper (large-v3) - **100% local**, roda offline
- **LLM**: Groq (cloud, padrão) ou Ollama (local, opcional) com streaming SSE
  - **Padrão**: Groq para máxima velocidade e confiabilidade
  - **Offline**: Configure `LLM_PROVIDER=ollama` para rodar 100% local
  - **Tool calling**: busca web via plugin (DuckDuckGo/Tavily) - requer internet
- **TTS**: Piper TTS + cache/pre-warm - **100% local**, roda offline
- **API**: FastAPI com REST + WebSocket + SSE (`/api/stream_text`)
- **Performance**: paralelismo (contexto/memória), caches (resposta/TTS), métricas

### Mobile App (Flutter)
- **Arquitetura feature-based**: domínios de voz, wake word, chat
- **Interface de chat**: texto + áudio com resposta em streaming
- **Streaming SSE**: `StreamingService` consome `/api/stream_text`
- **Wake word**: background service com reconexão
- **Métricas**: performance end-to-end no app e no backend

## Requisitos

### Hardware
- CPU: Intel i5/i7 12ª geração ou superior
- RAM: 16 GB (recomendado 32 GB)
- Armazenamento: 20 GB livres para modelos
- GPU: Opcional (NVIDIA com CUDA para melhor performance)

**Testado em:** Galaxy Book 2 (32GB RAM, 1TB NVMe, i5/i7 12ª gen) ✅

### Software
- Windows 11 com WSL2 (Ubuntu 22.04 ou 24.04)
- Python 3.10+
- Flutter 3.35+
- Android Studio (para desenvolvimento mobile)
- **Groq API Key** (padrão) ou **Ollama instalado** (para modo offline)

## Instalação

### 1) Backend
```bash
# Clone
git clone https://github.com/brunoadsba/john.git
cd john

# Ambiente virtual
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Dependências
pip install -r backend/requirements.txt

# Variáveis de ambiente
cp .env.example .env
nano .env   # Configure:
            # LLM_PROVIDER=groq (padrão, requer GROQ_API_KEY)
            # ou LLM_PROVIDER=ollama (offline, requer Ollama instalado)
```

Iniciar servidor (expondo para o mobile):
```bash
cd backend
source .venv/bin/activate
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2) Mobile (opcional)
```bash
# Verifique/ajuste URL do backend em env.dart
./scripts/check_mobile_config.sh

cd mobile_app
flutter pub get
flutter run        # ou: flutter run -d chrome
```

Build de APK:
```bash
cd mobile_app
flutter build apk --release
# Saída: build/app/outputs/flutter-apk/app-release.apk
```

### 3) Testes rápidos
```bash
# Health
curl http://127.0.0.1:8000/health

# Streaming LLM (SSE)
curl -N "http://127.0.0.1:8000/api/stream_text?texto=oi%20jonh"

# Script de métricas
python3 backend/scripts/analyze_performance.py
```

Documentação complementar:
- [docs/STATUS_PROJETO.md](docs/STATUS_PROJETO.md) - Status atual e features implementadas
- [docs/ARQUITETURA.md](docs/ARQUITETURA.md) - Arquitetura técnica completa
- [docs/MOBILE_APP.md](docs/MOBILE_APP.md) - Guia do app mobile
- [docs/API.md](docs/API.md) - Documentação da API
- [docs/INSTALACAO.md](docs/INSTALACAO.md) - Guia de instalação detalhado
- [QUICKSTART.md](QUICKSTART.md) - Guia rápido de início

## Uso

### API REST

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Síntese de Voz (TTS)
```bash
curl -X POST http://localhost:8000/api/synthesize \
  -F "texto=Olá, este é o assistente Jonh" \
  -o resposta.wav
```

#### Processamento Completo
```bash
curl -X POST http://localhost:8000/api/process_audio \
  -F "audio=@seu_audio.wav" \
  -o resposta.wav
```

### WebSocket

Conecte-se ao endpoint `ws://localhost:8000/ws/listen` para comunicação em tempo real.

Exemplo de protocolo:
```json
// Cliente envia
{"type": "start_session"}

// Servidor responde
{"type": "session_started", "session_id": "uuid-123"}

// Cliente envia áudio (bytes)
<audio_bytes>

// Servidor processa e retorna
{"type": "transcription", "text": "olá jonh"}
{"type": "response", "text": "Olá! Como posso ajudar?"}
<audio_bytes_resposta>
```

## Testes

### Testes Automatizados
```bash
cd backend
source .venv/bin/activate
pytest -v

# Web E2E (Playwright)
cd ..
./scripts/test_playwright.sh
```

### Teste Manual
```bash
# Execute o script de teste manual
python tests/manual_test.py
```

## Estrutura do Projeto

```
john/
├── backend/                     # Backend Python/FastAPI
│   ├── api/
│   │   ├── main.py              # Aplicação FastAPI principal
│   │   └── routes/
│   │       ├── process.py       # Endpoints REST
│   │       ├── websocket.py     # Endpoints WebSocket
│   │       └── streaming.py     # SSE /api/stream_text
│   ├── services/
│   │   ├── stt_service.py       # Speech-to-Text (Whisper)
│   │   ├── llm/                 # Serviços LLM (Groq/Ollama)
│   │   ├── tts_service.py       # Text-to-Speech (Piper)
│   │   └── ...                   # Outros serviços
│   ├── config/
│   │   └── settings.py          # Configurações
│   └── requirements.txt         # Dependências Python
├── mobile_app/                  # App Flutter
│   ├── lib/
│   │   ├── main.dart            # Entry point
│   │   ├── features/            # Arquitetura feature-based
│   │   ├── services/            # Lógica de negócio
│   │   └── widgets/             # Componentes reutilizáveis
│   └── pubspec.yaml             # Dependências Flutter
├── docs/                        # Documentação oficial
│   ├── STATUS_PROJETO.md        # Status e features
│   ├── ARQUITETURA.md           # Arquitetura técnica
│   ├── API.md                   # Documentação da API
│   └── ...                      # Outros documentos
├── scripts/                     # Scripts de automação
├── models/                      # Modelos de IA (Whisper, Piper)
├── data/                        # Dados do projeto
├── _local/                      # Arquivos locais (não versionados)
│   ├── docs/                    # Documentação interna
│   ├── scripts/                 # Scripts de teste local
│   └── temp/                    # Arquivos temporários
├── README.md                    # Este arquivo
├── CONTRIBUTING.md              # Guia de contribuição
├── LICENSE.txt                  # Licença
├── SECURITY.md                  # Política de segurança
└── QUICKSTART.md                # Guia rápido
```

## Endpoints da API

### REST

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações básicas da API |
| GET | `/health` | Status dos serviços |
| GET | `/sessions` | Lista sessões ativas |
| POST | `/api/process_audio` | Pipeline completo (STT→LLM→TTS) |
| POST | `/api/transcribe` | Apenas transcrição |
| POST | `/api/synthesize` | Apenas síntese de voz |
| GET | `/api/stream_text` | Streaming LLM via SSE |
| GET | `/api/errors/stats` | Estatísticas de erros |
| GET | `/api/errors/list` | Listagem de erros |
| GET | `/api/session/{id}` | Informações da sessão |
| DELETE | `/api/session/{id}` | Remove sessão |

### WebSocket

| Endpoint | Descrição |
|----------|-----------|
| `/ws/listen` | Comunicação em tempo real |
| `/ws/stream` | Streaming contínuo de áudio |

## Documentação da API

Acesse a documentação interativa em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Desenvolvimento

### Adicionar Novo Serviço

1. Crie o arquivo em `backend/services/`
2. Implemente a classe do serviço
3. Adicione ao `__init__.py` do módulo
4. Inicialize no `main.py`
5. Use nas rotas conforme necessário

### Adicionar Nova Rota

1. Crie/edite arquivo em `backend/api/routes/`
2. Defina o router e endpoints
3. Registre no `main.py` com `app.include_router()`

## Troubleshooting

### Modo Offline (100% Local)

Para rodar completamente offline:

1. **Instalar Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3:8b-instruct-q4_0
```

2. **Configurar .env:**
```bash
LLM_PROVIDER=ollama
WEB_SEARCH_ENABLED=false
```

3. **Verificar Ollama:**
```bash
systemctl --user status ollama
# Se não estiver rodando:
systemctl --user start ollama
```

### Groq não conecta
- Verifique se `GROQ_API_KEY` está configurada no `.env`
- Teste a chave: `curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"`

### Erro de memória
- Reduza o tamanho do modelo Whisper (use 'tiny' ou 'base')
- Use modelo Llama menor (llama3:8b-instruct-q2_K)
- Feche outros aplicativos

### Áudio não funciona
- Verifique formato do áudio (WAV, 16kHz mono recomendado)
- Instale dependências de áudio: `sudo apt install libsndfile1`

### Interface Web para Testes

**Acesse a interface web:**
```bash
# 1. Inicie o servidor
./scripts/start_server.sh

# 2. Acesse no navegador
http://localhost:8000/web/

# Ou use o script
./scripts/test_web_interface.sh
```

**Funcionalidades:**
- ✅ Enviar mensagens de texto
- ✅ Receber respostas do LLM
- ✅ Ouvir áudio TTS
- ✅ Testar memória (salvar/recuperar)
- ✅ Ver status dos serviços
- ✅ Logs em tempo real

**Testes Automatizados:**
```bash
# Executa 10 testes E2E (100% passando)
./scripts/test_playwright.sh
```

### Problemas Conhecidos
Para lista completa de problemas e soluções, veja:
- [ERROS_E_PROBLEMAS.md](docs/ERROS_E_PROBLEMAS.md)
- [CORRECAO_ERROS_WEB.md](docs/CORRECAO_ERROS_WEB.md)

## Funcionalidades Implementadas

### ✅ Backend
- [x] API REST com FastAPI
- [x] WebSocket para comunicação em tempo real
- [x] Speech-to-Text (Whisper/Faster-Whisper)
- [x] Text-to-Speech (Piper TTS + Edge-TTS fallback)
- [x] LLM (Groq cloud padrão + Ollama local opcional)
- [x] **Tool Calling** (Feature 021): Busca web automática
- [x] Wake Word Detection (OpenWakeWord)
- [x] Gerenciamento de contexto de conversação
- [x] Banco de dados SQLite para persistência
- [x] Sistema de memória (anotações e lembranças)
- [x] **Métricas de Performance** (Feature 020): Tracking end-to-end
- [x] Testes automatizados (12 testes Feature 021)

### ✅ Mobile App (Flutter)
- [x] **Arquitetura Feature-Based** (Fase 3): Organização por domínios
- [x] **Design System** (Fase 1): Tema centralizado e consistente
- [x] **Separação de Responsabilidades** (Fase 2): Controllers e Widgets
- [x] **Testes Automatizados** (Fase 4): 33 testes (Unit, Widget, Integration)
- [x] Interface de chat
- [x] Gravação de áudio otimizada
- [x] **Qualidade de Áudio** (Feature 019): Reprodução completa sem interrupções
- [x] **Métricas de Performance** (Feature 020): Tracking end-to-end
- [x] Reprodução de áudio
- [x] WebSocket para comunicação em tempo real
- [x] Background service para wake word (Android/iOS)
- [x] Notificações persistentes
- [x] Tela de configurações
- [x] Suporte web (com limitações)
- [x] Detecção de plataforma

### ✅ Interface Web para Testes
- [x] Interface web completa (`/web/`)
- [x] Testes automatizados (Playwright)
- [x] Envio de mensagens de texto
- [x] Recebimento de respostas LLM
- [x] Reprodução de áudio TTS
- [x] Teste de memória (salvar/recuperar)
- [x] Logs em tempo real
- [x] Status dos serviços

### ✅ Ambiente de Desenvolvimento
- [x] Flutter 3.38.4 (atualizado)
- [x] Android Studio configurado
- [x] VS Code com extensões profissionais
- [x] Playwright para testes E2E
- [x] Scripts de automação
- [x] Aliases úteis configurados

## Roadmap

### ✅ Concluído
- [x] Backend com API REST
- [x] WebSocket para tempo real
- [x] Gerenciamento de contexto
- [x] Persistência de histórico (SQLite)
- [x] Sistema de memória com busca semântica
- [x] Testes automatizados (Backend + Playwright)
- [x] App mobile Flutter
- [x] Dual LLM (Ollama + Groq)
- [x] Wake word detection (OpenWakeWord)
- [x] Background service
- [x] Interface web para testes
- [x] Ambiente de desenvolvimento profissional
- [x] Documentação completa

### ✅ Recém Implementado (Dezembro 2025)
- [x] **Feature 019**: Melhorar Qualidade de Áudio
  - Timeout dinâmico baseado na duração
  - Limpeza automática de arquivos temporários
  - Retry automático em caso de falha
- [x] **Feature 020**: Otimizar Latência End-to-End
  - Sistema completo de métricas de performance
  - Logging de tempos por etapa (STT, LLM, TTS)
  - Validação de objetivos (< 3s total)
- [x] **Feature 021**: Tool Calling (Busca Web)
  - Busca web automática (DuckDuckGo/Tavily)
  - LLM decide quando buscar informações atualizadas
  - Integração completa no WebSocket
- [x] **Feature 022**: Sistema de Plugins Modular
  - PluginManager com registro dinâmico
  - Plugin de busca web integrado
  - Arquitetura extensível para novos plugins
- [x] **Fase 1 - Otimização de Performance** (Concluída)
  - Streaming LLM via SSE (`/api/stream_text`)
  - Processamento paralelo (STT/contexto/memória)
  - Cache inteligente de respostas (semantic search)
  - Cache e pré-aquecimento de TTS
  - Script de análise de performance

### 🚧 Em Desenvolvimento
- [ ] **Fase 2 - Melhoria de Qualidade TTS**: Avaliar vozes, pós-processamento, dicionário de pronúncia
- [ ] **Fase 4 - Modernização da Interface**: Design system, chat moderno, animações, temas
- [ ] Testes físicos em dispositivo Android (Features 015-020)
- [ ] Validação de tool calling em produção

### 📋 Planejado
- [x] Feature 022: Sistema de Plugins Modular ✅ (implementado)
- [ ] Mais tools (calculadora, conversão de moedas, etc.)
- [ ] Cache de buscas recentes
- [ ] Interface web melhorada
- [ ] Docker compose completo
- [ ] CI/CD pipeline
- [ ] Suporte iOS
- [ ] Suporte a múltiplos idiomas
- [ ] Integração smart home

**Nota:** Documentos de planejamento interno estão em `_local/docs/` (não versionados)

## Modo Offline vs Cloud

### Configuração Padrão (Cloud)
- **LLM**: Groq (requer internet e API key)
- **STT**: Whisper local (offline)
- **TTS**: Piper local (offline)
- **Busca Web**: Habilitada (requer internet)

### Modo 100% Offline
- **LLM**: Ollama local (sem internet)
- **STT**: Whisper local (offline)
- **TTS**: Piper local (offline)
- **Busca Web**: Desabilitada

**Para ativar modo offline:** Configure `LLM_PROVIDER=ollama` e `WEB_SEARCH_ENABLED=false` no `.env`

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## Licença

MIT License - veja LICENSE para detalhes

## Contato

Para dúvidas e sugestões, abra uma issue no GitHub:
- **Repositório**: https://github.com/brunoadsba/john
- **Issues**: https://github.com/brunoadsba/john/issues

---

**Jonh Assistant** - Seu assistente de voz local, privado e profissional.

