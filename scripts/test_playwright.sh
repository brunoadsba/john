#!/bin/bash
# Script para executar testes Playwright da interface web

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  🎭 TESTES PLAYWRIGHT - INTERFACE WEB"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Verificar se servidor está rodando
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Servidor não está rodando!"
    echo "   Execute: ./scripts/start_server.sh"
    exit 1
fi

echo "✅ Servidor está rodando"
echo ""

# Ativar ambiente virtual
cd "$(dirname "$0")/../backend"
source .venv/bin/activate

# Verificar se Playwright está instalado
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "📦 Instalando Playwright..."
    pip install playwright pytest-playwright -q
    playwright install chromium
fi

echo "✅ Playwright instalado"
echo ""

# Executar testes
echo "🧪 Executando testes..."
echo ""

# Voltar para raiz do projeto
PROJECT_ROOT="/home/brunoadsba/john"
cd "$PROJECT_ROOT" || exit 1
pytest backend/tests/test_web_interface_playwright.py -v -s

echo ""
echo "✅ Testes concluídos!"

