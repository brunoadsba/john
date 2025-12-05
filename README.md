# Jonh - Assistente de Voz Local

Assistente de voz 100% local e profissional, similar à Alexa, rodando inteiramente no seu hardware sem dependência de nuvem.

## Características

- **100% Local**: Todo processamento de IA roda no seu computador
- **Zero Custo**: Tecnologias open-source, sem mensalidades
- **Português Nativo**: Otimizado para português brasileiro
- **Baixa Latência**: Resposta em menos de 2 segundos
- **Privacidade Total**: Seus dados não saem do seu computador

## Arquitetura

### Backend (Python/FastAPI)
- **Speech-to-Text**: faster-whisper (Whisper da OpenAI otimizado)
- **LLM**: Ollama (local) ou Groq (cloud) + Llama 3.1 8B
- **Text-to-Speech**: Piper TTS (voz pt_BR natural)
- **API**: FastAPI com endpoints REST e WebSocket

### Mobile App (Flutter)
- **Interface de Chat**: Conversação fluida com o assistente
- **Gravação de Áudio**: Captura otimizada (16kHz mono)
- **WebSocket**: Comunicação em tempo real
- **Wake Word**: Detecção por voz "Jonh" (em desenvolvimento)

## Requisitos

### Hardware
- CPU: Intel i5/i7 12ª geração ou superior
- RAM: 16 GB (recomendado 32 GB)
- Armazenamento: 20 GB livres para modelos
- GPU: Opcional (NVIDIA com CUDA para melhor performance)

### Software
- Windows 11 com WSL2 (Ubuntu 22.04 ou 24.04)
- Python 3.10+
- Ollama instalado e rodando

## Instalação

### 1. Preparar Ambiente

```bash
# Clone o repositório
cd /home/seu-usuario
git clone <seu-repositorio> john
cd john

# Crie ambiente virtual
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar Dependências

```bash
# Instale as dependências Python
pip install -r requirements.txt
```

### 3. Configurar LLM (Escolha uma opção)

#### Opção A: Ollama (Local - 100% Privado)

```bash
# Verifique se Ollama está instalado
ollama --version

# Baixe o modelo Llama 3.1 8B
ollama pull llama3:8b-instruct-q4_0

# Verifique os modelos instalados
ollama list
```

#### Opção B: Groq (Cloud - Ultra Rápido)

```bash
# 1. Crie conta em https://console.groq.com/
# 2. Obtenha sua API key
# 3. Configure no .env:
nano .env
# Mude: LLM_PROVIDER=groq
# Adicione: GROQ_API_KEY=sua_chave_aqui
```

**Veja documentação completa**: [docs/GROQ_SETUP.md](docs/GROQ_SETUP.md)

### 4. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite conforme necessário
nano .env
```

### 5. Iniciar o Servidor

```bash
# No diretório raiz do projeto
cd ~/john
python3 backend/api/main.py
```

O servidor estará disponível em: `http://localhost:8000`

### 6. Executar Mobile App (Opcional)

**Método Automático (Recomendado):**
```bash
# Script atualiza IP automaticamente e executa o app
./scripts/run_mobile_app.sh
```

**Método Manual:**
```bash
# Atualizar IP automaticamente
./scripts/update_mobile_ip.sh

# Instalar dependências
cd mobile_app
flutter pub get

# Execute o app
flutter run
```

**O script detecta e atualiza o IP automaticamente quando você muda de rede WiFi!** 🎉

**Documentação completa:**
- [Backend](docs/INSTALACAO.md)
- [Mobile App](docs/MOBILE_APP.md)
- [Wake Word](docs/WAKE_WORD.md)
- [Arquitetura](docs/ARQUITETURA.md)

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
# Execute os testes
cd backend
pytest tests/ -v
```

### Teste Manual
```bash
# Execute o script de teste manual
python tests/manual_test.py
```

## Estrutura do Projeto

```
john/
├── backend/
│   ├── api/
│   │   ├── main.py              # Aplicação FastAPI principal
│   │   └── routes/
│   │       ├── process.py       # Endpoints REST
│   │       └── websocket.py     # Endpoints WebSocket
│   ├── services/
│   │   ├── stt_service.py       # Speech-to-Text (Whisper)
│   │   ├── llm_service.py       # LLM (Ollama)
│   │   ├── tts_service.py       # Text-to-Speech (Piper)
│   │   └── context_manager.py   # Gerenciamento de contexto
│   ├── models/
│   │   └── schemas.py           # Schemas Pydantic
│   ├── config/
│   │   └── settings.py          # Configurações
│   ├── tests/
│   │   ├── test_integration.py  # Testes de integração
│   │   └── manual_test.py       # Script de teste manual
│   └── requirements.txt         # Dependências Python
├── mobile_app/                  # App Flutter
│   ├── lib/
│   │   ├── main.dart            # Entry point
│   │   ├── models/              # Modelos de dados
│   │   ├── screens/             # Telas
│   │   ├── services/            # Lógica de negócio
│   │   └── widgets/             # Componentes reutilizáveis
│   ├── android/                 # Configuração Android
│   └── pubspec.yaml             # Dependências Flutter
├── docs/                        # Documentação adicional
└── README.md                    # Este arquivo
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

### Ollama não conecta
```bash
# Verifique se está rodando
systemctl --user status ollama

# Inicie se necessário
systemctl --user start ollama
```

### Erro de memória
- Reduza o tamanho do modelo Whisper (use 'tiny' ou 'base')
- Use modelo Llama menor (llama3:8b-instruct-q2_K)
- Feche outros aplicativos

### Áudio não funciona
- Verifique formato do áudio (WAV, 16kHz mono recomendado)
- Instale dependências de áudio: `sudo apt install libsndfile1`

## Roadmap

- [x] Backend com API REST
- [x] WebSocket para tempo real
- [x] Gerenciamento de contexto
- [x] Testes básicos
- [x] App mobile Flutter
- [x] Dual LLM (Ollama + Groq)
- [x] Documentação completa
- [ ] Wake word detection (Porcupine)
- [ ] Persistência de histórico (SQLite)
- [ ] Interface web de controle
- [ ] Suporte a múltiplos idiomas
- [ ] Integração smart home
- [ ] Docker compose completo
- [ ] Suporte iOS

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT License - veja LICENSE para detalhes

## Contato

Para dúvidas e sugestões, abra uma issue no GitHub.

---

**Jonh Assistant** - Seu assistente de voz local, privado e profissional.

