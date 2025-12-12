# Documentação Completa: Sistema de Áudio - Jonh Assistant

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema de Áudio](#arquitetura-do-sistema-de-áudio)
3. [Fluxo Completo de Áudio](#fluxo-completo-de-áudio)
4. [Mobile: Gravação e Envio](#mobile-gravação-e-envio)
5. [Backend: Recepção e Processamento](#backend-recepção-e-processamento)
6. [Backend: STT (Speech-to-Text)](#backend-stt-speech-to-text)
7. [Backend: LLM (Geração de Resposta)](#backend-llm-geração-de-resposta)
8. [Backend: TTS (Text-to-Speech)](#backend-tts-text-to-speech)
9. [Backend: Retorno de Áudio](#backend-retorno-de-áudio)
10. [Mobile: Recepção e Reprodução](#mobile-recepção-e-reprodução)
11. [Configurações de Áudio](#configurações-de-áudio)
12. [Troubleshooting: Áudio Enviado Mas Sem Resposta](#troubleshooting-áudio-enviado-mas-sem-resposta)

---

## Visão Geral

O sistema de áudio do Jonh Assistant implementa um pipeline completo de processamento de voz:
1. **Gravação** (Mobile) → Áudio WAV 16kHz mono
2. **Transmissão** (WebSocket) → Bytes binários
3. **Transcrição** (Backend - Whisper) → Texto
4. **Processamento** (Backend - LLM) → Resposta em texto
5. **Síntese** (Backend - Piper TTS) → Áudio WAV
6. **Transmissão** (WebSocket) → Bytes binários
7. **Reprodução** (Mobile) → Áudio tocado

---

## Arquitetura do Sistema de Áudio

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOBILE APP (Flutter)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ VoiceButton  │───▶│ AudioService │───▶│ ApiService   │     │
│  │  (UI Widget) │    │              │    │              │     │
│  └──────────────┘    │ AudioRecord  │    │ WebSocket    │     │
│                      │ AudioPlayback│    │ Client       │     │
│                      └──────────────┘    └──────┬───────┘     │
│                                                  │             │
└──────────────────────────────────────────────────┼─────────────┘
                                                   │ WebSocket
                                                   │ (ws://.../ws/listen)
┌──────────────────────────────────────────────────┼─────────────┐
│                   BACKEND (FastAPI)              │             │
├──────────────────────────────────────────────────┼─────────────┤
│                                                  │             │
│  ┌──────────────┐    ┌──────────────┐          │             │
│  │ WebSocket    │───▶│ WebSocket    │          │             │
│  │ /ws/listen   │    │ Handler      │          │             │
│  └──────────────┘    └──────┬───────┘          │             │
│                              │                  │             │
│                    ┌─────────┴──────────┐       │             │
│                    │                    │       │             │
│            ┌───────▼───────┐   ┌───────▼──────┐│             │
│            │ process_audio │   │ handle_audio ││             │
│            │ _complete     │   │ _data        ││             │
│            └───────┬───────┘   └───────┬──────┘│             │
│                    │                    │       │             │
│         ┌──────────┴──────────┐        │       │             │
│         │                     │        │       │             │
│  ┌──────▼──────┐    ┌────────▼───┐    │       │             │
│  │ WhisperSTT  │    │  PiperTTS  │    │       │             │
│  │   Service   │    │   Service  │    │       │             │
│  └──────┬──────┘    └──────┬─────┘    │       │             │
│         │                  │          │       │             │
│         │ STT: Audio → Text           │       │             │
│         │                  │          │       │             │
│  ┌──────▼──────────────────▼──────┐  │       │             │
│  │     LLM Service (Groq/Ollama)  │  │       │             │
│  │     Text → Response            │  │       │             │
│  └────────────────────────────────┘  │       │             │
│                                       │       │             │
│                              ┌────────┴───────┘             │
│                              │                              │
│                      ┌───────▼───────┐                      │
│                      │ safe_send_bytes│                      │
│                      │ (WebSocket)    │                      │
│                      └────────────────┘                      │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Fluxo Completo de Áudio

### 1. Mobile: Gravação e Envio

**Arquivo:** `mobile_app/lib/widgets/voice_button.dart`

```dart
// 1. Usuário pressiona botão de gravação
await audioService.startRecording(); // AudioService.startRecording()

// 2. Usuário solta botão
final audioBytes = await audioService.stopRecording(); // Retorna Uint8List

// 3. Envia via WebSocket
await apiService.sendAudio(audioBytes); // ApiService.sendAudio()
```

**Arquivo:** `mobile_app/lib/services/audio/audio_recording.dart`

Configuração de gravação:
- **Formato:** WAV
- **Sample Rate:** 16000 Hz (16kHz)
- **Canais:** 1 (mono)
- **Encoder:** `AudioEncoder.wav`
- **Caminho:** `/temp/audio_{timestamp}.wav`

```dart
await _recorder.start(
  const RecordConfig(
    encoder: AudioEncoder.wav,
    sampleRate: 16000,  // ← CRÍTICO: 16kHz
    numChannels: 1,     // ← CRÍTICO: Mono
  ),
  path: path,
);
```

**Arquivo:** `mobile_app/lib/services/api_service.dart`

Envio via WebSocket:
```dart
Future<void> sendAudio(List<int> audioBytes) async {
  if (!_isConnected) {
    debugPrint('⚠️ WebSocket não conectado');
    return;
  }
  
  _wsClient.send(Uint8List.fromList(audioBytes));
  debugPrint('📤 Áudio enviado: ${audioBytes.length} bytes');
}
```

**Arquivo:** `mobile_app/lib/services/api/websocket_client.dart`

URL do WebSocket:
```dart
static String get wsUrl {
  final baseUrl = Env.backendUrl.isNotEmpty
      ? Env.backendUrl
      : 'http://192.168.1.5:8000';
  return baseUrl
          .replaceFirst('http://', 'ws://')
          .replaceFirst('https://', 'wss://') +
      '/ws/listen';  // ← Endpoint: /ws/listen
}
```

---

### 2. Backend: Recepção e Processamento

**Arquivo:** `backend/api/routes/websocket.py`

Endpoint WebSocket:
```python
@router.websocket("/ws/listen")
async def websocket_listen(websocket: WebSocket):
    await handle_listen_websocket(websocket, context_manager)
```

**Arquivo:** `backend/api/handlers/websocket_listen_handler.py`

Handler principal:
```python
async def handle_listen_websocket(websocket: WebSocket, context_manager):
    await websocket.accept()
    session_id = None
    
    while True:
        data = await websocket.receive()
        
        if "bytes" in data:
            # Dados de áudio recebidos
            audio_data = data["bytes"]
            session_id = await handle_audio_data(websocket, audio_data, session_id)
```

**Arquivo:** `backend/api/routes/websocket_handlers.py`

Roteamento para processamento:
```python
async def handle_audio_data(websocket, audio_data, session_id):
    return await process_audio_complete(
        websocket=websocket,
        audio_data=audio_data,  # ← Bytes do áudio
        session_id=session_id,
        stt_service=stt_service,
        llm_service=llm_service,
        tts_service=tts_service,
        context_manager=context_manager,
        memory_service=memory_service,
        plugin_manager=plugin_manager,
        web_search_tool=web_search_tool,
        feedback_service=feedback_service
    )
```

---

### 3. Backend: STT (Speech-to-Text)

**Arquivo:** `backend/api/handlers/websocket_audio_processor.py`

Processamento completo:
```python
async def process_audio_complete(...):
    # 1. Transcreve áudio
    logger.info("🎙️ Iniciando transcrição de áudio...")
    texto_transcrito, confianca, duracao = stt_service.transcribe_audio(audio_data)
    
    # Envia status de transcrição
    await safe_send_json(websocket, {
        "type": "processing",
        "stage": "transcribing"
    })
    
    # Envia transcrição
    await safe_send_json(websocket, {
        "type": "transcription",
        "text": texto_transcrito,
        "confidence": confianca
    })
```

**Arquivo:** `backend/services/stt_service.py`

Serviço Whisper:
```python
class WhisperSTTService:
    def __init__(
        self,
        model_size: str = "large-v3",  # ← Configurado em settings
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
    
    def transcribe_audio(self, audio_data: bytes, language: str = "pt"):
        # Converte bytes para array numpy
        audio_array, sample_rate = self._bytes_to_audio(audio_data)
        
        # Transcreve com Whisper
        segments, info = self.model.transcribe(
            audio_array,
            language=language,
            beam_size=3,  # Otimizado para performance
            vad_filter=use_vad_optimized,  # VAD para áudios > 2s
        )
        
        texto_completo = " ".join([segment.text for segment in segments])
        return texto_completo.strip(), info.language_probability, duracao
```

**Configuração (settings.py):**
```python
whisper_model: str = "large-v3"      # Modelo Whisper
whisper_device: str = "cpu"          # CPU ou CUDA
whisper_compute_type: str = "int8"   # int8, float16, float32
```

**Formato esperado pelo Whisper:**
- Sample Rate: Qualquer (Whisper converte internamente para 16kHz)
- Canais: Mono (convertido automaticamente se estéreo)
- Formato: Qualquer suportado por `soundfile` (WAV, MP3, OGG, FLAC)

---

### 4. Backend: LLM (Geração de Resposta)

**Arquivo:** `backend/api/handlers/websocket_audio_processor.py`

Geração de resposta:
```python
    # 2. Gera resposta com LLM
    await safe_send_json(websocket, {
        "type": "processing",
        "stage": "generating"
    })
    
    await context_manager.add_message(session_id, "user", texto_transcrito)
    contexto = await context_manager.get_context(session_id)
    
    # Prepara tools e tool executor
    tools, tool_executor = prepare_tools_for_websocket(plugin_manager, web_search_tool)
    
    # Gera resposta
    resposta_texto, tokens = llm_service.generate_response(
        texto_transcrito,
        contexto,
        memorias_contexto=memoria_contexto,
        tools=tools,
        tool_executor=tool_executor
    )
    
    # Sanitiza resposta
    sanitizer = get_sanitizer()
    resposta_texto = sanitizer.sanitize(resposta_texto)
    
    await context_manager.add_message(session_id, "assistant", resposta_texto)
    
    # Envia resposta de texto
    await safe_send_json(websocket, {
        "type": "response",
        "text": resposta_texto,
        "tokens": tokens,
        "metrics": {
            "sttTime": int(stt_time),
            "llmTime": int(llm_time),
            "ttsTime": None
        }
    })
```

**Problema potencial:** Se o LLM não retornar resposta ou retornar vazio, a mensagem `type: "response"` pode não ser enviada ou estar vazia.

---

### 5. Backend: TTS (Text-to-Speech)

**Arquivo:** `backend/api/handlers/websocket_audio_processor.py`

Síntese de voz:
```python
    # 3. Sintetiza áudio
    await safe_send_json(websocket, {
        "type": "processing",
        "stage": "synthesizing"
    })
    
    tts_start = time.time()
    logger.info("🔊 Iniciando síntese de voz...")
    audio_resposta = await tts_service.synthesize(resposta_texto)
    tts_time = (time.time() - tts_start) * 1000
    
    # Envia áudio via WebSocket
    if not await safe_send_bytes(websocket, audio_resposta):
        logger.warning("Conexão fechada antes de enviar áudio")
        return session_id
```

**Arquivo:** `backend/services/tts_service.py`

Serviço Piper TTS:
```python
class PiperTTSService:
    def __init__(self, ...):
        # Inicializa Piper TTS (Fase 2)
        if settings.tts_engine == "piper":
            self.piper_service = NewPiperTTSService(
                model_path=settings.tts_model_path,
                config_path=settings.tts_config_path,
                use_cuda=settings.tts_use_cuda
            )
    
    async def synthesize(self, texto: str) -> bytes:
        # Processa texto (normalização, pronúncia, SSML)
        texto_processado = texto
        if self.text_processor:
            texto_processado = self.text_processor.process(texto_processado)
        
        # Verifica cache
        if self.cache:
            cached_audio = self.cache.get(texto_processado)
            if cached_audio:
                return cached_audio
        
        # Sintetiza
        if self.piper_service and self.piper_service.is_ready():
            audio_bytes = await self.piper_service.synthesize(texto_processado)
        elif EdgeTTSAvailable:
            audio_bytes = await self._synthesize_edge_tts(texto_processado)
        else:
            audio_bytes = self._synthesize_mock(texto_processado)  # Fallback
        
        # Armazena no cache
        if self.cache:
            self.cache.set(texto_processado, audio_bytes)
        
        return audio_bytes  # ← WAV bytes
```

**Configuração (settings.py):**
```python
tts_engine: str = "piper"  # "piper" ou "edge" (fallback)
tts_model_path: str = "models/tts/pt_BR-jeff-medium.onnx"
tts_config_path: Optional[str] = "models/tts/pt_BR-jeff-medium.onnx.json"
tts_use_cuda: bool = False  # CPU por padrão
```

**Formato de saída do TTS:**
- Formato: WAV
- Sample Rate: 22050 Hz (Piper padrão) ou 16000 Hz (edge-tts)
- Canais: 1 (mono)
- Bits por amostra: 16-bit PCM

---

### 6. Backend: Retorno de Áudio

**Arquivo:** `backend/api/routes/websocket_utils.py`

Envio seguro de bytes:
```python
async def safe_send_bytes(websocket: WebSocket, data: bytes) -> bool:
    try:
        if websocket.client_state.name != "CONNECTED":
            logger.debug("Conexão WebSocket não está mais conectada")
            return False
        
        await websocket.send_bytes(data)
        return True
    except (RuntimeError, ConnectionError) as e:
        logger.debug("Conexão WebSocket fechada durante envio de bytes")
        return False
```

**Fluxo de mensagens enviadas:**
1. `{"type": "processing", "stage": "transcribing"}` - Início de transcrição
2. `{"type": "transcription", "text": "...", "confidence": 0.95}` - Transcrição completa
3. `{"type": "processing", "stage": "generating"}` - Início de geração
4. `{"type": "response", "text": "...", "tokens": 150}` - Resposta de texto
5. `{"type": "processing", "stage": "synthesizing"}` - Início de síntese
6. `[BINARY DATA]` - Bytes do áudio WAV
7. `{"type": "complete", "metrics": {...}}` - Processamento completo

---

### 7. Mobile: Recepção e Reprodução

**Arquivo:** `mobile_app/lib/services/api/websocket_client.dart`

Recebimento de mensagens:
```dart
_channel!.stream.listen(
  (data) {
    if (onMessage != null) {
      onMessage!(data);  // ← Chama MessageHandler.handleMessage()
    }
  },
);
```

**Arquivo:** `mobile_app/lib/services/api/message_handler.dart`

Processamento de mensagens:
```dart
void handleMessage(dynamic data) {
  if (data is Uint8List || data is List<int>) {
    // Dados binários (áudio)
    final audioBytes = data is Uint8List ? data : Uint8List.fromList(data);
    debugPrint('🔊 Áudio recebido: ${audioBytes.length} bytes');
    if (onAudioReceived != null) {
      onAudioReceived!(audioBytes);  // ← Chama callback do ApiService
    }
    return;
  }
  
  if (data is String) {
    final json = jsonDecode(data);
    final type = json['type'] as String?;
    
    switch (type) {
      case 'transcription':
        // Atualiza mensagem do usuário com transcrição
        break;
      case 'response':
        // Adiciona mensagem de resposta do assistente
        break;
      case 'processing':
        // Atualiza status de processamento
        break;
      // ...
    }
  }
}
```

**Arquivo:** `mobile_app/lib/services/api_service.dart`

Callback de áudio:
```dart
ApiService() {
  _messageHandler.onAudioReceived = (audio) {
    if (onAudioReceived != null) {
      onAudioReceived!(audio);  // ← Callback configurado externamente
    }
  };
}
```

**Arquivo:** `mobile_app/lib/screens/home_screen.dart`

Configuração do callback:
```dart
@override
void initState() {
  super.initState();
  final apiService = context.read<ApiService>();
  final audioService = context.read<AudioService>();
  
  // Configura callback para reproduzir áudio quando recebido
  apiService.onAudioReceived = (audioBytes) {
    audioService.playAudio(audioBytes);
  };
}
```

**Arquivo:** `mobile_app/lib/services/audio/audio_playback.dart`

Reprodução:
```dart
Future<void> playAudio(Uint8List audioBytes, {int maxRetries = 2}) async {
  // Valida tamanho mínimo (44 bytes = header WAV)
  if (audioBytes.length < 44) {
    throw Exception('Áudio inválido: muito pequeno');
  }
  
  // Salva em arquivo temporário
  final tempFile = File('$tempPath/audio_response_{timestamp}.wav');
  await tempFile.writeAsBytes(audioBytes);
  
  // Reproduz com just_audio
  await _player.setFilePath(tempFile.path);
  await _player.play();
  
  // Aguarda conclusão
  await completer.future.timeout(timeout);
  
  // Limpa arquivo temporário
  await tempFile.delete();
}
```

**Biblioteca:** `just_audio`
- Suporta WAV, MP3, OGG, FLAC
- Auto-detecta sample rate e canais do WAV
- Reproduz em formato nativo do dispositivo

---

## Configurações de Áudio

### Mobile (Gravação)

**Arquivo:** `mobile_app/lib/services/audio/audio_recording.dart`

```dart
RecordConfig(
  encoder: AudioEncoder.wav,    // Formato: WAV
  sampleRate: 16000,            // 16kHz (ideal para Whisper)
  numChannels: 1,               // Mono
)
```

### Backend (STT - Whisper)

**Arquivo:** `backend/config/settings.py`

```python
whisper_model: str = "large-v3"      # Modelo: large-v3 (melhor PT-BR)
whisper_device: str = "cpu"          # CPU ou cuda
whisper_compute_type: str = "int8"   # int8 (rápido), float16 (balanceado), float32 (melhor qualidade)
```

**Parâmetros de transcrição:**
- `beam_size`: 3 (otimizado para velocidade)
- `vad_filter`: Habilitado para áudios > 2s
- `language`: "pt" (português)

### Backend (TTS - Piper)

**Arquivo:** `backend/config/settings.py`

```python
tts_engine: str = "piper"                              # Engine: piper ou edge
tts_model_path: str = "models/tts/pt_BR-jeff-medium.onnx"
tts_config_path: str = "models/tts/pt_BR-jeff-medium.onnx.json"
tts_use_cuda: bool = False                            # CPU por padrão
tts_pronunciation_dict_path: str = "backend/data/tts_pronunciation_dict.json"
tts_enable_ssml: bool = True                          # SSML habilitado
tts_enable_numbers: bool = True                       # Normalização de números
tts_enable_dates: bool = True                         # Normalização de datas
```

**Formato de saída:**
- Sample Rate: 22050 Hz (Piper padrão) ou 16000 Hz (edge-tts)
- Formato: WAV 16-bit PCM
- Canais: 1 (mono)

### Validações

**Backend:** `backend/api/validators/audio_validator.py`

```python
MAX_AUDIO_SIZE = 10 * 1024 * 1024      # 10 MB máximo
MIN_AUDIO_SIZE = 100                    # 100 bytes mínimo
SUPPORTED_FORMATS = ["wav", "mp3", "ogg", "flac"]
MAX_DURATION_SECONDS = 300              # 5 minutos máximo
```

**Mobile:** `mobile_app/lib/utils/audio_validator.dart`

```dart
static const int minWavHeaderSize = 44;  // Header WAV mínimo
```

---

## Troubleshooting: Áudio Enviado Mas Sem Resposta

### 🔍 Diagnóstico Passo a Passo

#### 1. Verificar se áudio está sendo enviado

**Mobile (logs):**
```dart
debugPrint('📤 Áudio enviado: ${audioBytes.length} bytes');
```

**Backend (logs):**
```
🎤 Áudio recebido de {client_ip}: {audio_size} bytes
🎵 Iniciando processamento de áudio: {len(audio_data)} bytes
```

**Ação:** Verifique logs do mobile e backend. Se não aparecer "Áudio recebido", problema é na conexão WebSocket.

#### 2. Verificar transcrição (STT)

**Backend (logs):**
```
🎙️ Iniciando transcrição de áudio...
✅ Transcrição concluída: '...' (confiança: 0.95, segmentos: 1)
```

**Mensagem WebSocket enviada:**
```json
{"type": "transcription", "text": "...", "confidence": 0.95}
```

**Problemas comuns:**
- Transcrição vazia: Áudio sem fala ou muito baixo
- Confiança muito baixa (< 0.5): Ruído excessivo ou modelo incorreto
- Erro no STT: Modelo Whisper não carregado ou formato inválido

**Ação:** Verifique se `whisper_model` está correto e se modelo está disponível.

#### 3. Verificar geração de resposta (LLM)

**Backend (logs):**
```
🤖 Gerando resposta com LLM...
✅ Resposta gerada: '...' (150 tokens)
```

**Mensagem WebSocket enviada:**
```json
{"type": "response", "text": "...", "tokens": 150}
```

**Problemas comuns:**
- LLM não retorna resposta: Timeout, erro de conexão (Groq), ou modelo offline (Ollama)
- Resposta vazia ou "None": Erro no LLM service
- Resposta sanitizada ficou vazia: Sanitizer removeu todo o conteúdo

**Ação:** Verifique:
- Conexão com Groq (API key válida)
- Ollama rodando (`ollama serve`)
- Modelo configurado corretamente

#### 4. Verificar síntese de áudio (TTS)

**Backend (logs):**
```
🔊 Iniciando síntese de voz...
✅ Áudio sintetizado: {len(audio_resposta)} bytes
```

**Mensagem WebSocket enviada:**
```
[BINARY DATA] - Bytes do áudio WAV
```

**Problemas comuns:**
- TTS retorna vazio: Modelo Piper não carregado ou erro no edge-tts
- Áudio muito pequeno: Erro na síntese, retornando apenas header WAV
- Erro no TTS: Modelo não encontrado ou caminho incorreto

**Ação:** Verifique:
- Modelo Piper existe: `models/tts/pt_BR-jeff-medium.onnx`
- Config JSON existe: `models/tts/pt_BR-jeff-medium.onnx.json`
- edge-tts disponível como fallback

#### 5. Verificar envio de áudio via WebSocket

**Backend (logs):**
```
📤 Áudio enviado ao cliente
```

**Código:** `backend/api/handlers/websocket_audio_processor.py:225`

```python
if not await safe_send_bytes(websocket, audio_resposta):
    logger.warning("Conexão fechada antes de enviar áudio")
    return session_id
```

**Problemas comuns:**
- Conexão fechada: Cliente desconectou antes de receber áudio
- Erro ao enviar: WebSocket em estado inválido

**Ação:** Verifique se conexão WebSocket ainda está ativa.

#### 6. Verificar recepção no Mobile

**Mobile (logs):**
```dart
debugPrint('🔊 Áudio recebido: ${audioBytes.length} bytes');
```

**Problemas comuns:**
- Áudio não chega: WebSocket desconectado ou filtrado
- Áudio vazio: Backend enviou dados vazios
- Callback não configurado: `onAudioReceived` não foi definido

**Ação:** Verifique:
- Callback configurado em `home_screen.dart`
- WebSocket ainda conectado (`apiService.isConnected`)

#### 7. Verificar reprodução no Mobile

**Mobile (logs):**
```dart
debugPrint('🔊 Iniciando reprodução de áudio: ${audioBytes.length} bytes');
```

**Problemas comuns:**
- Áudio muito pequeno: < 44 bytes (header WAV mínimo)
- Erro no just_audio: Formato inválido ou arquivo corrompido
- Permissão de áudio negada: Android não permite reprodução

**Ação:** Verifique logs de erro do `AudioPlayback`.

---

### 🛠️ Checklist de Troubleshooting

#### Backend

- [ ] Servidor rodando (`curl http://localhost:8000/health`)
- [ ] Whisper modelo carregado (logs: "Modelo Whisper carregado")
- [ ] LLM service inicializado (Groq key válida OU Ollama rodando)
- [ ] TTS service inicializado (Piper modelo existe OU edge-tts disponível)
- [ ] WebSocket endpoint acessível (`ws://localhost:8000/ws/listen`)
- [ ] Logs mostram "Áudio recebido"
- [ ] Logs mostram "Transcrição concluída"
- [ ] Logs mostram "Resposta gerada"
- [ ] Logs mostram "Áudio sintetizado"
- [ ] Logs mostram "Áudio enviado ao cliente"

#### Mobile

- [ ] App conectado ao WebSocket (`apiService.isConnected == true`)
- [ ] Permissão de microfone concedida
- [ ] Gravação funciona (logs: "Gravação iniciada")
- [ ] Áudio enviado (logs: "Áudio enviado: X bytes")
- [ ] Callback `onAudioReceived` configurado
- [ ] Áudio recebido (logs: "Áudio recebido: X bytes")
- [ ] Reprodução inicia (logs: "Iniciando reprodução")
- [ ] Permissão de áudio no Android (manifest.xml)

#### WebSocket

- [ ] Conexão estabelecida (logs: "Conectado ao assistente")
- [ ] Mensagens de status recebidas (`processing`, `transcription`, `response`)
- [ ] Áudio binário recebido (tipo `Uint8List`)
- [ ] Conexão não fecha durante processamento

---

### 🐛 Pontos Críticos de Falha

#### 1. STT retorna texto vazio

**Sintoma:** Backend loga "Transcrição vazia"

**Causas possíveis:**
- Áudio sem fala detectada
- Áudio muito curto (< 0.5s)
- Ruído excessivo
- Modelo Whisper incorreto

**Solução:**
- Verificar qualidade do áudio gravado
- Aumentar duração mínima de gravação
- Usar modelo Whisper maior (large-v3 → melhor qualidade)

#### 2. LLM não retorna resposta

**Sintoma:** Backend não loga "Resposta gerada" OU resposta vazia

**Causas possíveis:**
- Groq API key inválida ou expirada
- Ollama não está rodando
- Timeout do LLM
- Erro na chamada do LLM

**Solução:**
- Verificar API key Groq
- Iniciar Ollama: `ollama serve`
- Aumentar timeout
- Verificar logs de erro do LLM service

#### 3. TTS retorna áudio vazio

**Sintoma:** Backend loga "Áudio sintetizado: 0 bytes" ou muito pequeno

**Causas possíveis:**
- Modelo Piper não encontrado
- Erro no edge-tts
- Texto vazio após sanitização

**Solução:**
- Verificar caminho do modelo Piper
- Testar edge-tts manualmente
- Verificar resposta de texto antes do TTS

#### 4. Áudio não chega no Mobile

**Sintoma:** Mobile não loga "Áudio recebido"

**Causas possíveis:**
- WebSocket desconectado antes de enviar áudio
- Erro ao enviar bytes (`safe_send_bytes` retorna False)
- Cliente não está escutando mensagens binárias

**Solução:**
- Verificar se WebSocket ainda está conectado
- Verificar logs de erro do `safe_send_bytes`
- Testar recepção de mensagens JSON primeiro

#### 5. Áudio recebido mas não reproduz

**Sintoma:** Mobile loga "Áudio recebido" mas não toca

**Causas possíveis:**
- Callback `onAudioReceived` não configurado
- Erro no `AudioPlayback.playAudio()`
- Permissão de áudio negada (Android)
- Formato inválido

**Solução:**
- Verificar callback em `home_screen.dart`
- Verificar logs de erro do `AudioPlayback`
- Verificar permissões no AndroidManifest.xml
- Validar formato do áudio recebido

---

### 📊 Logs para Análise

**Backend (Python - loguru):**
```
INFO: 🎤 Áudio recebido de 192.168.1.6: 12345 bytes
INFO: 🎵 Iniciando processamento de áudio: 12345 bytes
INFO: 🎙️ Iniciando transcrição de áudio...
INFO: ✅ Transcrição concluída: 'olá' (confiança: 0.95)
INFO: 🤖 Gerando resposta com LLM...
INFO: ✅ Resposta gerada: 'Olá! Como posso ajudar?' (150 tokens)
INFO: 🔊 Iniciando síntese de voz...
INFO: ✅ Áudio sintetizado: 54321 bytes
INFO: 📤 Áudio enviado ao cliente
```

**Mobile (Flutter - debugPrint):**
```dart
📤 Áudio enviado: 12345 bytes
✅ Conectado ao assistente
📝 Transcrição: "olá" (confiança: 0.95)
🤖 Resposta: "Olá! Como posso ajudar?" (150 tokens)
🔊 Áudio recebido: 54321 bytes
🔊 Iniciando reprodução de áudio: 54321 bytes
✅ Reprodução concluída
```

---

### 🔧 Comandos Úteis

**Testar conexão WebSocket:**
```bash
# Backend
curl http://localhost:8000/health

# WebSocket (use wscat ou Postman)
wscat -c ws://localhost:8000/ws/listen
```

**Verificar modelo Whisper:**
```python
from backend.services.stt_service import WhisperSTTService
stt = WhisperSTTService()
print(stt.is_ready())  # True se modelo carregado
```

**Verificar modelo TTS:**
```python
from backend.services.tts_service import PiperTTSService
tts = PiperTTSService()
print(tts.is_ready())  # True se serviço disponível
```

**Testar TTS manualmente:**
```python
audio_bytes = await tts.synthesize("Olá, teste")
print(f"Áudio gerado: {len(audio_bytes)} bytes")
```

---

## 📝 Notas Finais

- **Formato de áudio:** WAV é o formato padrão em todo o pipeline
- **Sample rate:** 16kHz na gravação, 22kHz na síntese (Piper), compatível entre si
- **Canais:** Mono (1 canal) em todo o pipeline
- **WebSocket:** Protocolo binário para áudio, JSON para mensagens de controle
- **Timeouts:** Configurar timeouts adequados para STT, LLM e TTS
- **Cache:** TTS tem cache para evitar re-síntese de textos repetidos
- **Fallback:** edge-tts como fallback se Piper não estiver disponível

---

**Última atualização:** 2025-12-11
**Versão:** 1.0.0

