# Guia de Teste do Pipeline Completo

Como testar o pipeline completo: STT → LLM → TTS

## ⚠️ Requisito Importante

O pipeline completo **precisa de um arquivo de áudio com FALA REAL** para funcionar.

Arquivos gerados pelo TTS (mock) **não funcionam** porque não contêm fala reconhecível pelo Whisper.

## 📋 Formato de Áudio Recomendado

- **Formato**: WAV
- **Sample Rate**: 16kHz (ou 22.05kHz)
- **Canais**: Mono (1 canal)
- **Bits**: 16-bit PCM
- **Duração**: 1-10 segundos (recomendado)

## 🎤 Como Obter um Arquivo de Áudio

### Opção 1: Gravar com seu Microfone

**Linux (usando `arecord`):**
```bash
# Gravar 5 segundos de áudio
arecord -d 5 -f cd -t wav -r 16000 meu_audio.wav

# Falar algo como: "Olá, qual é a capital do Brasil?"
```

**Windows (PowerShell):**
```powershell
# Usar aplicativo Gravador de Voz ou Audacity
```

### Opção 2: Converter Áudio Existente

**Usando ffmpeg:**
```bash
# Converter para formato adequado
ffmpeg -i audio_original.mp3 \
  -ar 16000 \
  -ac 1 \
  -acodec pcm_s16le \
  audio_convertido.wav
```

### Opção 3: Baixar Exemplo

```bash
# Exemplo de áudio de teste (se disponível)
# Ou usar um arquivo de áudio que você já tenha
```

## 🧪 Testando o Pipeline

### Método 1: Usando o Script

```bash
cd ~/john
./scripts/test_pipeline.sh meu_audio.wav
```

### Método 2: Usando curl Diretamente

```bash
curl -X POST http://localhost:8000/api/process_audio \
  -F "audio=@meu_audio.wav" \
  -o resposta.wav
```

### Método 3: Verificar Resposta

```bash
# Ver metadados nos headers
curl -X POST http://localhost:8000/api/process_audio \
  -F "audio=@meu_audio.wav" \
  -o resposta.wav \
  -v 2>&1 | grep -E "X-Transcription|X-Response-Text|X-Processing-Time"
```

## ✅ Resultado Esperado

Se tudo funcionar, você receberá:

1. **Arquivo WAV** com a resposta do assistente
2. **Headers HTTP** com metadados:
   - `X-Transcription`: Texto transcrito do seu áudio
   - `X-Response-Text`: Resposta gerada pelo LLM
   - `X-Processing-Time`: Tempo total de processamento
   - `X-Tokens-Used`: Tokens usados pelo LLM
   - `X-Session-ID`: ID da sessão criada

## 🔍 Troubleshooting

### Erro 400: "Não foi possível transcrever o áudio"

**Causas:**
- Arquivo não contém fala real
- Formato de áudio não suportado
- Áudio muito curto ou silencioso

**Solução:**
- Use arquivo com fala real gravada
- Verifique formato (WAV, 16kHz mono)
- Teste com áudio de 2+ segundos

### Erro 500: Erro interno

**Causas:**
- Servidor não está rodando
- Serviço STT/LLM/TTS offline
- Erro no processamento

**Solução:**
- Verifique se servidor está rodando: `curl http://localhost:8000/health`
- Verifique logs do servidor
- Confirme que todos os serviços estão online

### Arquivo não encontrado

**Erro:** `curl: (26) Failed to open/read local data`

**Solução:**
- Verifique caminho do arquivo
- Use caminho absoluto ou relativo correto
- Confirme que arquivo existe: `ls -lh arquivo.wav`

## 📊 Exemplo Completo

```bash
# 1. Gravar áudio
arecord -d 5 -f cd -t wav -r 16000 pergunta.wav

# 2. Testar pipeline
curl -X POST http://localhost:8000/api/process_audio \
  -F "audio=@pergunta.wav" \
  -o resposta.wav \
  -w "\nHTTP Code: %{http_code}\n"

# 3. Verificar resultado
file resposta.wav
ls -lh resposta.wav

# 4. Reproduzir (se tiver player)
aplay resposta.wav  # Linux
# ou
open resposta.wav   # macOS
```

## 🎯 Próximos Passos

Após testar com sucesso:

1. ✅ Pipeline completo funcionando
2. 🔄 Testar WebSocket para tempo real
3. 📱 Testar mobile app (quando Flutter instalado)
4. 🚀 Fazer merge para master

---

**Última atualização:** 05/12/2024

