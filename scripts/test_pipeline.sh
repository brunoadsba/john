#!/bin/bash
# Script para testar o pipeline completo do Jonh Assistant

set -e

API_URL="http://localhost:8000"
AUDIO_FILE="${1:-teste_final.wav}"

echo "═══════════════════════════════════════════════════════════════"
echo "  TESTE DO PIPELINE COMPLETO - JONH ASSISTANT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Verificar se servidor está rodando
if ! curl -s "${API_URL}/health" > /dev/null; then
    echo "❌ Erro: Servidor não está rodando em ${API_URL}"
    echo "   Execute: python3 backend/api/main.py"
    exit 1
fi

echo "✅ Servidor está rodando"
echo ""

# Verificar se arquivo existe
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Erro: Arquivo não encontrado: $AUDIO_FILE"
    echo ""
    echo "Arquivos WAV disponíveis:"
    ls -lh *.wav 2>/dev/null || echo "  Nenhum arquivo WAV encontrado"
    echo ""
    echo "Uso: $0 <arquivo.wav>"
    exit 1
fi

echo "📁 Arquivo: $AUDIO_FILE"
FILE_SIZE=$(stat -c%s "$AUDIO_FILE" 2>/dev/null || stat -f%z "$AUDIO_FILE" 2>/dev/null)
echo "   Tamanho: $((FILE_SIZE / 1024)) KB"
echo ""

# Testar pipeline completo
echo "🔄 Processando: STT → LLM → TTS"
echo ""

RESPONSE_FILE="resposta_pipeline_$(date +%s).wav"

HTTP_CODE=$(curl -s -w "%{http_code}" -X POST "${API_URL}/api/process_audio" \
    -F "audio=@${AUDIO_FILE}" \
    -o "$RESPONSE_FILE" \
    -H "Accept: audio/wav")

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCESSO!"
    echo ""
    echo "📄 Arquivo de resposta: $RESPONSE_FILE"
    ls -lh "$RESPONSE_FILE"
    echo ""
    
    # Mostrar headers se possível
    echo "📊 Metadados:"
    curl -s -I -X POST "${API_URL}/api/process_audio" \
        -F "audio=@${AUDIO_FILE}" 2>/dev/null | \
        grep -E "X-Transcription|X-Response-Text|X-Processing-Time|X-Tokens-Used" || true
    
elif [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️ ERRO 400: Requisição inválida"
    echo ""
    echo "Resposta:"
    cat "$RESPONSE_FILE" | python3 -m json.tool 2>/dev/null || cat "$RESPONSE_FILE"
    echo ""
    echo "💡 Dica: Verifique se o arquivo contém fala real e está em formato WAV"
    
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ ERRO 500: Erro interno do servidor"
    echo ""
    echo "Resposta:"
    cat "$RESPONSE_FILE" | python3 -m json.tool 2>/dev/null || cat "$RESPONSE_FILE"
    echo ""
    echo "💡 Verifique os logs do servidor para mais detalhes"
    
else
    echo "❌ ERRO HTTP $HTTP_CODE"
    echo ""
    echo "Resposta:"
    cat "$RESPONSE_FILE" | python3 -m json.tool 2>/dev/null || cat "$RESPONSE_FILE"
fi

echo "═══════════════════════════════════════════════════════════════"

