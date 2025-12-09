#!/bin/bash
# Script para testar o sistema de monitoramento de erros

echo "============================================================"
echo "🧪 TESTE DO SISTEMA DE MONITORAMENTO DE ERROS"
echo "============================================================"
echo ""

# Verifica se servidor está rodando
echo "🔍 Verificando se servidor está rodando..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ Servidor está rodando!"
    echo ""
    echo "🚀 Executando testes..."
    echo ""
    python3 backend/tests/test_error_monitoring.py
else
    echo "❌ Servidor não está rodando!"
    echo ""
    echo "📋 Para iniciar o servidor, execute:"
    echo "   cd /home/brunoadsba/john"
    echo "   source .venv/bin/activate  # se estiver usando venv"
    echo "   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "   Ou em outra janela do terminal:"
    echo "   python3 -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi

