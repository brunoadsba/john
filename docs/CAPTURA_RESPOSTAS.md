# Captura de Respostas do Assistente

Script para capturar e analisar todas as respostas do assistente Jonh.

## Objetivo

Entender erros e problemas nas respostas do assistente através de análise sistemática.

## Uso

### Captura Automática

A captura é **automática** e acontece em todas as respostas do assistente:
- Via WebSocket (`/ws/listen`)
- Via API REST (`/api/process_text`)
- Via API REST (`/api/process_audio`)

Os logs são salvos em: `logs/assistant_responses/`

### Análise Manual

#### Ver resumo do dia

```bash
python3 backend/scripts/capture_assistant_responses.py --summary --today
```

#### Ver apenas erros

```bash
python3 backend/scripts/capture_assistant_responses.py --errors --today
```

#### Ver respostas com problemas

```bash
python3 backend/scripts/capture_assistant_responses.py --issues --today
```

#### Analisar arquivo específico

```bash
python3 backend/scripts/capture_assistant_responses.py --file logs/assistant_responses/responses_20251211.jsonl --summary
```

## Estrutura dos Logs

### Arquivo JSONL (`responses_YYYYMMDD.jsonl`)

Cada linha é um JSON com:

```json
{
  "timestamp": "2025-12-11T11:30:00.123456",
  "session_id": "uuid-123",
  "user_input": "Olá, como você está?",
  "assistant_response_original": "Olá! Estou funcionando normalmente...",
  "assistant_response_sanitized": "Olá! Como posso ajudar?",
  "was_sanitized": true,
  "tokens": 45,
  "processing_time_seconds": 1.23,
  "tools_used": ["web_search"],
  "context_message_count": 3,
  "context_messages": [...],
  "audio_size_bytes": 45678,
  "audio_duration_seconds": 3.45,
  "audio_available": true,
  "audio_file": "logs/assistant_responses/audio_samples/audio_20251211_113000_123456_uuid-123.wav",
  "error": null,
  "issues_detected": ["termo_sistema_vazado: estou funcionando normalmente"],
  "metadata": {}
}
```

### Arquivos de Áudio (`audio_samples/`)

O script também **salva os arquivos de áudio** enviados ao usuário em:

```
logs/assistant_responses/audio_samples/
├── audio_20251211_113000_123456_uuid-123.wav
├── audio_20251211_113015_234567_uuid-456.wav
└── ...
```

Cada arquivo de áudio corresponde a uma resposta capturada e permite:
- Ouvir exatamente o que o usuário recebeu
- Analisar qualidade do áudio
- Verificar problemas de síntese

### Arquivo de Resumo (`summary_YYYYMMDD.json`)

```json
{
  "date": "2025-12-11",
  "total_responses": 150,
  "total_errors": 5,
  "total_sanitizations": 23,
  "error_rate": 0.033,
  "sanitization_rate": 0.153
}
```

## Problemas Detectados Automaticamente

O script detecta automaticamente:

### Problemas de Texto:
- `resposta_muito_curta` - Resposta com menos de 10 caracteres
- `resposta_muito_longa` - Resposta com mais de 2000 caracteres
- `conteudo_repetitivo` - Menos de 30% de palavras únicas
- `termo_sistema_vazado: <termo>` - Termos do sistema aparecem na resposta
- `sanitizacao_excessiva` - Mais de 50% do conteúdo foi removido na sanitização
- `tokens_zero` - Zero tokens usados (indica problema)
- `tokens_muito_baixo` - Menos de 10 tokens
- `tempo_processamento_alto` - Mais de 10 segundos
- `resposta_apenas_numeros` - Resposta contém apenas números

### Problemas de Áudio:
- `audio_muito_pequeno` - Áudio com menos de 1KB (pode estar corrompido)
- `audio_muito_grande` - Áudio com mais de 10MB (pode ser problema)
- `audio_muito_lento` - Menos de 5 caracteres por segundo (fala muito lenta)
- `audio_muito_rapido` - Mais de 30 caracteres por segundo (fala muito rápida)
- `audio_nao_gerado` - Áudio não foi gerado quando deveria

## Exemplos de Uso

### 1. Ver problemas do dia

```bash
python3 backend/scripts/capture_assistant_responses.py --today --issues
```

### 2. Analisar erros recentes

```bash
python3 backend/scripts/capture_assistant_responses.py --today --errors | head -50
```

### 3. Estatísticas completas

```bash
python3 backend/scripts/capture_assistant_responses.py --today --summary
```

### 4. Buscar termo específico nos logs

```bash
grep "termo_sistema_vazado" logs/assistant_responses/responses_*.jsonl
```

## Integração no Código

A captura é integrada automaticamente em:

1. `backend/api/handlers/websocket_audio_processor.py` - WebSocket
2. `backend/api/handlers/text_processor.py` - API REST

Não é necessário fazer nada - funciona automaticamente!

## Localização dos Logs

Por padrão: `logs/assistant_responses/`

Estrutura:
```
logs/
└── assistant_responses/
    ├── responses_20251211.jsonl
    ├── summary_20251211.json
    ├── responses_20251212.jsonl
    └── summary_20251212.json
```

## Notas

- A captura não bloqueia as respostas (executa em background)
- Erros na captura não afetam o funcionamento do assistente
- Logs são salvos em formato JSONL (uma linha JSON por resposta)
- Arquivos são organizados por data
- Logs antigos podem ser removidos manualmente

