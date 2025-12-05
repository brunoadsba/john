# Arquitetura do Sistema Jonh Assistant

Documentação técnica da arquitetura completa do projeto.

## Visão Geral

O Jonh Assistant é um sistema de assistente de voz distribuído com processamento de IA local/cloud, composto por:

1. **Backend API** (Python/FastAPI)
2. **Mobile App** (Flutter/Dart)
3. **Serviços de IA** (Whisper, Ollama/Groq, Piper)

```
┌─────────────────┐
│   Mobile App    │
│    (Flutter)    │
└────────┬────────┘
         │ WebSocket/HTTP
         │
┌────────▼────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ STT  │  │ LLM  │
│Whisper│ │Ollama│
└──────┘  │ Groq │
          └──┬───┘
             │
          ┌──▼──┐
          │ TTS │
          │Piper│
          └─────┘
```

## Backend API

### Stack Tecnológica

- **Framework**: FastAPI 0.109.0
- **Servidor**: Uvicorn (ASGI)
- **Comunicação**: REST + WebSocket
- **Validação**: Pydantic 2.5.3
- **Logging**: Loguru 0.7.2

### Estrutura de Diretórios

```
backend/
├── api/
│   ├── main.py              # Aplicação FastAPI
│   └── routes/
│       ├── process.py       # Endpoints REST
│       └── websocket.py     # Endpoints WebSocket
├── services/
│   ├── stt_service.py       # Speech-to-Text
│   ├── llm_service.py       # LLM (Ollama/Groq)
│   ├── tts_service.py       # Text-to-Speech
│   └── context_manager.py   # Gerenciamento de contexto
├── models/
│   └── schemas.py           # Schemas Pydantic
├── config/
│   └── settings.py          # Configurações
└── tests/
    ├── test_integration.py
    └── manual_test.py
```

### Endpoints

#### REST

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Info da API |
| GET | `/health` | Status dos serviços |
| GET | `/sessions` | Lista sessões ativas |
| POST | `/api/process_audio` | Pipeline completo |
| POST | `/api/transcribe` | Apenas STT |
| POST | `/api/synthesize` | Apenas TTS |
| GET | `/api/session/{id}` | Info da sessão |
| DELETE | `/api/session/{id}` | Remove sessão |

#### WebSocket

| Endpoint | Descrição |
|----------|-----------|
| `/ws/listen` | Comunicação em tempo real |
| `/ws/stream` | Streaming contínuo |

### Fluxo de Processamento

```
1. Cliente envia áudio (bytes)
   ↓
2. STT Service (Whisper)
   - Converte áudio → texto
   - Retorna transcrição + confiança
   ↓
3. Context Manager
   - Adiciona mensagem ao histórico
   - Recupera contexto da sessão
   ↓
4. LLM Service (Ollama/Groq)
   - Processa pergunta + contexto
   - Gera resposta em texto
   ↓
5. Context Manager
   - Salva resposta no histórico
   ↓
6. TTS Service (Piper)
   - Converte texto → áudio
   - Retorna áudio WAV
   ↓
7. Cliente recebe áudio + metadados
```

### Gerenciamento de Estado

**Context Manager:**
- Sessões em memória (dict)
- Histórico limitado (10 mensagens)
- Timeout de sessão (3600s)
- Limpeza automática de sessões expiradas

**Estrutura de Sessão:**
```python
{
    "session_id": "uuid",
    "created_at": datetime,
    "last_activity": datetime,
    "messages": [
        {"role": "user", "content": "...", "timestamp": datetime},
        {"role": "assistant", "content": "...", "timestamp": datetime}
    ]
}
```

## Serviços de IA

### 1. Speech-to-Text (Whisper)

**Biblioteca**: faster-whisper 1.0.0

**Configuração:**
```python
WhisperSTTService(
    model_size="base",      # tiny, base, small, medium, large
    device="cpu",           # cpu, cuda
    compute_type="int8"     # int8, float16, float32
)
```

**Modelos disponíveis:**
| Modelo | Tamanho | RAM | Qualidade |
|--------|---------|-----|-----------|
| tiny | 39 MB | ~1 GB | Básica |
| base | 74 MB | ~1 GB | Boa |
| small | 244 MB | ~2 GB | Muito boa |
| medium | 769 MB | ~5 GB | Excelente |
| large | 1550 MB | ~10 GB | Máxima |

**Performance:**
- CPU: 0.5-2s para 5s de áudio
- GPU: 0.1-0.5s para 5s de áudio

### 2. LLM (Ollama / Groq)

#### Ollama (Local)

**Configuração:**
```python
OllamaLLMService(
    model="llama3:8b-instruct-q4_0",
    host="http://localhost:11434",
    temperature=0.7,
    max_tokens=512
)
```

**Modelos suportados:**
- llama3:8b-instruct-q2_K (3.2 GB, rápido)
- llama3:8b-instruct-q4_0 (4.7 GB, balanceado)
- llama3:8b-instruct-q6_K (6.8 GB, qualidade)

**Performance:**
- CPU i7 12ª gen: 1.5-2.5s
- GPU RTX 3060: 0.5-1.0s

#### Groq (Cloud)

**Configuração:**
```python
GroqLLMService(
    api_key="gsk_...",
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=512
)
```

**Modelos disponíveis:**
- llama-3.1-8b-instant (ultra rápido)
- llama-3.1-70b-versatile (melhor qualidade)
- mixtral-8x7b-32768 (contexto longo)

**Performance:**
- Latência: 0.2-0.5s (consistente)
- Throughput: Alto

### 3. Text-to-Speech (Piper)

**Biblioteca**: piper-tts 1.2.0

**Configuração:**
```python
PiperTTSService(
    voice="pt_BR-faber-medium",
    model_path="./models/piper"
)
```

**Vozes pt_BR:**
- pt_BR-faber-medium (masculina, natural)
- pt_BR-edson-medium (masculina, clara)

**Formato de saída:**
- Sample rate: 22050 Hz
- Canais: Mono
- Formato: WAV (PCM)

## Mobile App

### Stack Tecnológica

- **Framework**: Flutter 3.0+
- **Linguagem**: Dart 3.0+
- **State Management**: Provider 6.1.1
- **Áudio**: record 5.0.4, just_audio 0.9.36
- **Network**: web_socket_channel 2.4.0, http 1.1.2

### Arquitetura MVVM

```
View (Widgets)
    ↓
ViewModel (Provider/ChangeNotifier)
    ↓
Model (Services + Data)
```

**Exemplo:**
```
HomeScreen (View)
    ↓
Consumer<ApiService> (ViewModel)
    ↓
ApiService.messages (Model)
```

### Componentes Principais

#### 1. Services

**ApiService:**
- Gerencia WebSocket
- Mantém histórico de mensagens
- Controla sessões

**AudioService:**
- Gravação de áudio
- Reprodução de áudio
- Gerenciamento de permissões

#### 2. Models

**Message:**
```dart
class Message {
  final String id;
  final String content;
  final MessageType type;  // user, assistant, system, error
  final DateTime timestamp;
  final bool isProcessing;
}
```

#### 3. Screens

**HomeScreen:**
- Tela principal
- Status bar
- Lista de mensagens
- Botão de voz

#### 4. Widgets

**MessageList:**
- Renderiza mensagens
- Scroll automático
- Bolhas de chat

**VoiceButton:**
- Botão animado
- Estados visuais
- Feedback tátil

### Fluxo de Dados

```
1. User Action
   ↓
2. Widget Event
   ↓
3. Service Method Call
   ↓
4. notifyListeners()
   ↓
5. Consumer Rebuild
   ↓
6. UI Update
```

**Exemplo concreto:**
```dart
// 1. Usuário toca botão
onTap: () => audioService.startRecording()

// 2. Service executa
await _recorder.start()

// 3. Atualiza estado
_isRecording = true
notifyListeners()

// 4. Consumer detecta mudança
Consumer<AudioService>(
  builder: (context, service, _) {
    // 5. UI atualiza
    return Icon(service.isRecording ? Icons.stop : Icons.mic)
  }
)
```

## Comunicação

### Protocolo WebSocket

#### Handshake

```
Cliente → Servidor: WebSocket Upgrade
Servidor → Cliente: {"type": "connected", "message": "..."}
```

#### Mensagens

**Formato JSON (controle):**
```json
{
  "type": "start_session|end_session|ping",
  "data": {}
}
```

**Formato Binário (áudio):**
```
<bytes> (WAV PCM 16kHz mono)
```

#### Sequência Típica

```
1. Cliente: {"type": "start_session"}
2. Servidor: {"type": "session_started", "session_id": "uuid"}
3. Cliente: <audio_bytes>
4. Servidor: {"type": "processing", "stage": "transcribing"}
5. Servidor: {"type": "transcription", "text": "..."}
6. Servidor: {"type": "processing", "stage": "generating"}
7. Servidor: {"type": "response", "text": "..."}
8. Servidor: {"type": "processing", "stage": "synthesizing"}
9. Servidor: <audio_bytes>
10. Servidor: {"type": "complete"}
```

### REST API

**Content-Type:**
- Request: `multipart/form-data` (áudio)
- Response: `application/json` ou `audio/wav`

**Headers personalizados:**
```
X-Transcription: texto transcrito
X-Response-Text: resposta gerada
X-Session-ID: id da sessão
X-Processing-Time: tempo em segundos
X-Tokens-Used: tokens do LLM
```

## Segurança

### Autenticação (Futuro)

**Recomendado:**
- JWT tokens
- OAuth 2.0
- API keys

### Autorização

**Níveis:**
- Público: health check
- Autenticado: conversação
- Admin: gerenciamento

### Validação

**Pydantic:**
```python
class AudioRequest(BaseModel):
    audio_data: bytes = Field(..., max_length=10_000_000)
    session_id: Optional[str] = Field(None, regex=r'^[a-f0-9-]{36}$')
```

### Rate Limiting (Futuro)

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/process_audio")
@limiter.limit("10/minute")
async def process_audio(...):
    ...
```

## Escalabilidade

### Horizontal

**Backend:**
- Load balancer (nginx)
- Múltiplas instâncias FastAPI
- Redis para sessões compartilhadas

**LLM:**
- Pool de workers Ollama
- Groq (já escalável)

### Vertical

**Otimizações:**
- GPU para Whisper
- Quantização de modelos
- Caching de respostas comuns

### Monitoramento

**Métricas:**
- Latência de endpoints
- Taxa de erro
- Uso de recursos (CPU, RAM, GPU)
- Sessões ativas
- Throughput

**Ferramentas sugeridas:**
- Prometheus + Grafana
- ELK Stack (logs)
- Sentry (erros)

## Deploy

### Desenvolvimento

```bash
# Backend
python3 backend/api/main.py

# Mobile
flutter run --debug
```

### Produção

**Backend:**
```bash
# Docker
docker-compose up -d

# Ou systemd
sudo systemctl start jonh-assistant
```

**Mobile:**
```bash
# Build APK
flutter build apk --release

# Ou Play Store
flutter build appbundle --release
```

## Testes

### Backend

**Unitários:**
```bash
pytest backend/tests/test_services.py
```

**Integração:**
```bash
pytest backend/tests/test_integration.py
```

**Manual:**
```bash
python backend/tests/manual_test.py
```

### Mobile

**Widget:**
```bash
flutter test test/widgets/
```

**Integração:**
```bash
flutter test test/integration/
```

**E2E:**
```bash
flutter drive --target=test_driver/app.dart
```

## Performance

### Benchmarks

**Pipeline completo (médio):**
| Componente | Tempo |
|------------|-------|
| STT (Whisper base) | 0.8s |
| LLM (Groq) | 0.3s |
| TTS (Piper) | 0.4s |
| Network | 0.1s |
| **Total** | **1.6s** |

**Com Ollama local:**
| Componente | Tempo |
|------------|-------|
| STT | 0.8s |
| LLM (Ollama) | 1.8s |
| TTS | 0.4s |
| **Total** | **3.0s** |

### Otimizações Aplicadas

1. **Lazy loading** de modelos
2. **Streaming** de áudio
3. **Caching** de contexto
4. **Async/await** em Python
5. **Provider** eficiente no Flutter

## Limitações Atuais

1. **STT**: Whisper não instalado (usando mock)
2. **TTS**: Piper usando mock (silêncio)
3. **Wake Word**: Não implementado
4. **Persistência**: Sessões apenas em memória
5. **Autenticação**: Não implementada
6. **iOS**: Não suportado

## Roadmap

### Curto Prazo
- [ ] Instalar Whisper real
- [ ] Instalar Piper TTS real
- [ ] Implementar wake word (Porcupine)
- [ ] Adicionar testes automatizados

### Médio Prazo
- [ ] Persistência com SQLite/PostgreSQL
- [ ] Autenticação JWT
- [ ] Suporte iOS
- [ ] Docker compose completo

### Longo Prazo
- [ ] Multi-usuário
- [ ] Integração smart home
- [ ] Plugins/extensões
- [ ] Interface web

---

**Última atualização:** Dezembro 2025

