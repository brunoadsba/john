# Documentação da API - Jonh Assistant

## Visão Geral

A API do Jonh Assistant oferece endpoints REST e WebSocket para processamento de voz e conversação com IA local.

**Base URL**: `http://localhost:8000`

## Autenticação

Atualmente não há autenticação. Em produção, implemente autenticação adequada.

## Endpoints REST

### 1. Informações da API

**GET** `/`

Retorna informações básicas sobre a API.

**Resposta**:
```json
{
  "nome": "Jonh Assistant API",
  "versao": "1.0.0",
  "status": "online",
  "timestamp": "2025-12-05T10:30:00"
}
```

### 2. Health Check

**GET** `/health`

Verifica o status de todos os serviços.

**Resposta**:
```json
{
  "status": "healthy",
  "versao": "1.0.0",
  "servicos": {
    "stt": "online",
    "llm": "online",
    "tts": "online",
    "context": "online"
  },
  "timestamp": "2025-12-05T10:30:00",
  "configuracao": {
    "whisper_model": "base",
    "ollama_model": "llama3:8b-instruct-q4_0",
    "piper_voice": "pt_BR-faber-medium"
  }
}
```

**Status possíveis**:
- `healthy`: Todos os serviços funcionando
- `degraded`: Alguns serviços offline

### 3. Processamento Completo de Áudio

**POST** `/api/process_audio`

Pipeline completo: Speech-to-Text → LLM → Text-to-Speech

**Parâmetros**:
- `audio` (file, obrigatório): Arquivo de áudio (WAV, MP3, etc)
- `session_id` (string, opcional): ID da sessão para manter contexto

**Exemplo**:
```bash
curl -X POST http://localhost:8000/api/process_audio \
  -F "audio=@meu_audio.wav" \
  -F "session_id=uuid-123" \
  -o resposta.wav
```

**Resposta**:
- Content-Type: `audio/wav`
- Headers informativos:
  - `X-Transcription`: Texto transcrito do áudio enviado
  - `X-Response-Text`: Texto da resposta gerada
  - `X-Session-ID`: ID da sessão
  - `X-Processing-Time`: Tempo de processamento em segundos
  - `X-Tokens-Used`: Tokens utilizados pelo LLM

### 4. Transcrição de Áudio

**POST** `/api/transcribe`

Apenas transcreve áudio para texto (sem LLM ou TTS).

**Parâmetros**:
- `audio` (file, obrigatório): Arquivo de áudio

**Resposta**:
```json
{
  "texto": "Olá Jonh, qual é a previsão do tempo?",
  "confianca": 0.95,
  "duracao": 2.5,
  "idioma": "pt"
}
```

### 5. Síntese de Voz

**POST** `/api/synthesize`

Converte texto em áudio (sem STT ou LLM).

**Parâmetros**:
- `texto` (string, obrigatório): Texto para sintetizar

**Exemplo**:
```bash
curl -X POST http://localhost:8000/api/synthesize \
  -F "texto=Olá, este é o assistente Jonh" \
  -o audio.wav
```

**Resposta**:
- Content-Type: `audio/wav`
- Body: Áudio WAV

### 6. Informações da Sessão

**GET** `/api/session/{session_id}`

Obtém informações sobre uma sessão específica.

**Resposta**:
```json
{
  "session_id": "uuid-123",
  "created_at": "2025-12-05T10:00:00",
  "last_activity": "2025-12-05T10:30:00",
  "message_count": 5,
  "is_active": true
}
```

### 7. Remover Sessão

**DELETE** `/api/session/{session_id}`

Remove uma sessão e seu histórico.

**Resposta**:
```json
{
  "message": "Sessão removida com sucesso"
}
```

### 8. Listar Sessões

**GET** `/sessions`

Lista todas as sessões ativas.

**Resposta**:
```json
{
  "sessions": [
    {
      "session_id": "uuid-123",
      "created_at": "2025-12-05T10:00:00",
      "last_activity": "2025-12-05T10:30:00",
      "message_count": 5,
      "is_active": true
    }
  ],
  "total": 1
}
```

## WebSocket

### Endpoint: `/ws/listen`

Comunicação em tempo real para conversação contínua.

**URL**: `ws://localhost:8000/ws/listen`

#### Protocolo

**1. Conexão**

Cliente conecta ao WebSocket.

Servidor envia:
```json
{
  "type": "connected",
  "message": "Conectado ao assistente Jonh"
}
```

**2. Iniciar Sessão**

Cliente envia:
```json
{
  "type": "start_session"
}
```

Servidor responde:
```json
{
  "type": "session_started",
  "session_id": "uuid-123"
}
```

**3. Enviar Áudio**

Cliente envia dados de áudio como bytes.

Servidor processa e envia atualizações:

```json
{"type": "processing", "stage": "transcribing"}
{"type": "transcription", "text": "olá jonh", "confidence": 0.95}
{"type": "processing", "stage": "generating"}
{"type": "response", "text": "Olá! Como posso ajudar?", "tokens": 15}
{"type": "processing", "stage": "synthesizing"}
```

Depois envia o áudio da resposta como bytes.

Finaliza com:
```json
{"type": "complete", "session_id": "uuid-123"}
```

**4. Encerrar Sessão**

Cliente envia:
```json
{
  "type": "end_session"
}
```

Servidor responde:
```json
{
  "type": "session_ended"
}
```

**5. Ping/Pong**

Cliente envia:
```json
{
  "type": "ping"
}
```

Servidor responde:
```json
{
  "type": "pong"
}
```

#### Tipos de Mensagem

| Tipo | Direção | Descrição |
|------|---------|-----------|
| `connected` | S→C | Confirmação de conexão |
| `start_session` | C→S | Solicita nova sessão |
| `session_started` | S→C | Sessão criada |
| `session_created` | S→C | Sessão criada automaticamente |
| `end_session` | C→S | Encerra sessão |
| `session_ended` | S→C | Sessão encerrada |
| `processing` | S→C | Status de processamento |
| `transcription` | S→C | Resultado da transcrição |
| `response` | S→C | Resposta do LLM |
| `complete` | S→C | Processamento completo |
| `error` | S→C | Erro ocorrido |
| `ping` | C→S | Keep-alive |
| `pong` | S→C | Resposta ao ping |

### Endpoint: `/ws/stream`

Streaming contínuo de áudio.

**URL**: `ws://localhost:8000/ws/stream`

Similar ao `/ws/listen`, mas aceita chunks de áudio em tempo real e processa quando buffer atinge tamanho suficiente.

## Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 400 | Requisição inválida |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

## Formatos de Áudio Suportados

### Entrada (STT)
- WAV (recomendado)
- MP3
- FLAC
- OGG

**Recomendações**:
- Sample rate: 16kHz
- Canais: Mono
- Bit depth: 16-bit

### Saída (TTS)
- WAV (22.05kHz, mono, 16-bit)

## Limites e Quotas

- **Tamanho máximo de áudio**: 10 MB
- **Duração máxima de áudio**: 60 segundos
- **Histórico de contexto**: 10 mensagens por sessão
- **Timeout de sessão**: 3600 segundos (1 hora)
- **Tokens máximos LLM**: 512 por resposta

## Exemplos de Uso

### Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Processar áudio
with open("audio.wav", "rb") as f:
    files = {"audio": f}
    response = requests.post(
        "http://localhost:8000/api/process_audio",
        files=files
    )
    
    with open("resposta.wav", "wb") as out:
        out.write(response.content)
```

### JavaScript (WebSocket)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/listen');

ws.onopen = () => {
    console.log('Conectado');
    
    // Inicia sessão
    ws.send(JSON.stringify({type: 'start_session'}));
};

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Áudio recebido
        console.log('Áudio recebido');
    } else {
        // Mensagem JSON
        const msg = JSON.parse(event.data);
        console.log('Mensagem:', msg);
    }
};

// Enviar áudio
function enviarAudio(audioBlob) {
    ws.send(audioBlob);
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Transcrever
curl -X POST http://localhost:8000/api/transcribe \
  -F "audio=@audio.wav"

# Sintetizar
curl -X POST http://localhost:8000/api/synthesize \
  -F "texto=Olá mundo" \
  -o output.wav

# Processar completo
curl -X POST http://localhost:8000/api/process_audio \
  -F "audio=@input.wav" \
  -o output.wav
```

## Erros Comuns

### 400 Bad Request
- Áudio inválido ou corrompido
- Formato não suportado
- Parâmetros ausentes

### 404 Not Found
- Sessão não encontrada
- Endpoint inválido

### 500 Internal Server Error
- Serviço de IA offline
- Erro no processamento
- Modelo não carregado

**Solução**: Verifique `/health` para status dos serviços.

## Performance

### Tempos Esperados (Hardware Recomendado)

- **Transcrição (STT)**: 0.3-0.8s para 5s de áudio
- **LLM**: 0.5-1.5s para resposta curta
- **Síntese (TTS)**: 0.2-0.5s para frase curta
- **Pipeline completo**: 1.5-2.5s

### Otimizações

1. **Use WebSocket** para múltiplas interações
2. **Mantenha sessão ativa** para preservar contexto
3. **Áudio em 16kHz mono** reduz processamento
4. **GPU CUDA** acelera Whisper significativamente

## Segurança

⚠️ **Importante**: Esta API não possui autenticação por padrão.

Para produção, implemente:
- Autenticação (JWT, OAuth, etc)
- Rate limiting
- HTTPS/WSS
- Validação de entrada rigorosa
- CORS configurado adequadamente

## Suporte

Para problemas ou dúvidas:
1. Verifique `/health`
2. Consulte logs do servidor
3. Abra issue no GitHub

