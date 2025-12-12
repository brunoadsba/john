# Diagnóstico: Áudio Truncado

## 🔍 Problema Reportado

O áudio está saindo truncado - o usuário recebe apenas parte do áudio gerado, não o áudio completo.

## 📊 Pontos de Verificação

### 1. **Piper TTS Service** (`backend/services/tts/piper_service.py`)

**Código atual:**
```python
async def synthesize(self, text: str) -> bytes:
    # ...
    self.voice.synthesize(text, wav_file=wav_file)
    # ...
```

**Possíveis problemas:**
- Piper TTS pode ter limite de caracteres por chamada
- Textos longos podem precisar ser divididos em chunks
- O método `synthesize` pode estar truncando silenciosamente

**Verificação necessária:**
- Testar com textos de diferentes tamanhos
- Verificar se há limite no Piper TTS
- Verificar logs durante síntese

### 2. **WebSocket - Envio de Bytes** (`backend/api/routes/websocket_utils.py`)

**Código atual:**
```python
async def safe_send_bytes(websocket: WebSocket, data: bytes) -> bool:
    await websocket.send_bytes(data)
```

**Possíveis problemas:**
- WebSocket pode ter limite de tamanho de mensagem
- FastAPI/Starlette pode estar truncando mensagens grandes
- Buffer pode estar sendo cortado

**Limites conhecidos:**
- FastAPI WebSocket: Sem limite padrão explícito
- Starlette WebSocket: Pode ter limite de buffer
- Navegadores: Geralmente 1MB por mensagem WebSocket

### 3. **Processamento de Texto** (`backend/services/tts_service.py`)

**Código atual:**
```python
# Processar texto (Fase 2)
texto_processado = texto
if self.text_processor:
    texto_processado = self.text_processor.process(texto_processado)
```

**Possíveis problemas:**
- Processadores de texto podem estar truncando
- Normalização pode estar removendo partes
- SSML pode estar malformado

### 4. **Mobile - Recepção e Reprodução**

**Possíveis problemas:**
- `just_audio` pode estar truncando ao ler arquivo
- Buffer de reprodução pode estar limitado
- Arquivo temporário pode estar sendo cortado

## 🧪 Testes Recomendados

### Teste 1: TTS Direto (sem WebSocket)
```bash
python3 backend/scripts/test_tts_via_api.py
```
- Testa síntese via API HTTP
- Salva arquivos WAV para análise manual
- Verifica se problema está no TTS ou no WebSocket

### Teste 2: WebSocket Completo
```bash
python3 backend/scripts/test_websocket_audio.py
```
- Testa fluxo completo via WebSocket
- Verifica se áudio chega completo
- Compara tamanho enviado vs recebido

### Teste 3: Logs Detalhados
Adicionar logs em pontos críticos:
- Tamanho do texto antes de sintetizar
- Tamanho do áudio gerado pelo TTS
- Tamanho do áudio antes de enviar via WebSocket
- Tamanho do áudio recebido no mobile

## 🔧 Possíveis Soluções

### Solução 1: Dividir Texto em Chunks (se Piper TTS tiver limite)

```python
async def synthesize(self, text: str) -> bytes:
    MAX_CHARS = 500  # Ajustar conforme limite do Piper
    
    if len(text) <= MAX_CHARS:
        return await self._synthesize_chunk(text)
    
    # Dividir em chunks
    chunks = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
    audio_chunks = []
    
    for chunk in chunks:
        audio_chunk = await self._synthesize_chunk(chunk)
        audio_chunks.append(audio_chunk)
    
    # Concatenar áudios
    return self._concatenate_audio(audio_chunks)
```

### Solução 2: Enviar Áudio em Chunks via WebSocket

```python
async def safe_send_bytes_chunked(websocket: WebSocket, data: bytes, chunk_size: int = 64*1024):
    """Envia bytes em chunks para evitar limite de mensagem"""
    total_size = len(data)
    sent = 0
    
    while sent < total_size:
        chunk = data[sent:sent+chunk_size]
        await websocket.send_bytes(chunk)
        sent += len(chunk)
```

### Solução 3: Verificar e Corrigir Processamento de Texto

Adicionar validação:
```python
# Antes de sintetizar
if len(texto_processado) < len(texto) * 0.8:
    logger.warning(f"Texto processado muito menor: {len(texto)} -> {len(texto_processado)}")
```

## 📝 Próximos Passos

1. **Executar teste via API** para isolar problema
2. **Verificar logs** durante síntese
3. **Comparar tamanhos** de áudio gerado vs enviado vs recebido
4. **Testar com textos de diferentes tamanhos**
5. **Verificar documentação do Piper TTS** para limites

## 🔗 Arquivos Relacionados

- `backend/services/tts/piper_service.py` - Implementação Piper TTS
- `backend/services/tts_service.py` - Wrapper TTS
- `backend/api/routes/websocket_utils.py` - Envio WebSocket
- `backend/api/handlers/websocket_audio_processor.py` - Processamento áudio
- `mobile_app/lib/services/audio/audio_playback.dart` - Reprodução mobile

---

**Status:** 🔍 Em investigação
**Prioridade:** 🔴 Alta
**Data:** 2025-12-11

