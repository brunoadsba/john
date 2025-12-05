#!/bin/bash
# Wrapper script: Atualiza IP e executa o app Flutter

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPDATE_SCRIPT="$PROJECT_ROOT/scripts/update_mobile_ip.sh"

echo "🚀 Iniciando Jonh Assistant Mobile App"
echo ""

# Atualiza IP automaticamente
if [ -f "$UPDATE_SCRIPT" ]; then
    "$UPDATE_SCRIPT"
    echo ""
else
    echo "⚠️  Script de atualização de IP não encontrado"
    echo "   Continuando sem atualizar IP..."
    echo ""
fi

# Executa Flutter
cd "$PROJECT_ROOT/mobile_app"

echo "📱 Executando app Flutter..."
echo ""

flutter run "$@"

