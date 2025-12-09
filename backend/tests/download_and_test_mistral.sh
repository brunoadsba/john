#!/bin/bash
# Script para baixar e testar modelos Mistral no Ollama

echo "🚀 Script de Download e Teste de Modelos Mistral"
echo "================================================"
echo ""

# Modelos para baixar e testar (em ordem de recomendação)
MODELS=(
    "mistral-small:latest"
    "mistral:7b-instruct"
    "mistral:latest"
)

echo "📋 Modelos que serão baixados e testados:"
for model in "${MODELS[@]}"; do
    echo "   - $model"
done
echo ""

# Verifica se Ollama está instalado
if ! command -v ollama &> /dev/null; then
    echo "❌ Erro: Ollama não está instalado"
    echo "Instale em: https://ollama.com"
    exit 1
fi

echo "✅ Ollama encontrado"
echo ""

# Função para baixar modelo
download_model() {
    local model=$1
    echo "📥 Baixando modelo: $model"
    echo "   (Isso pode levar alguns minutos dependendo da sua conexão...)"
    ollama pull "$model"
    
    if [ $? -eq 0 ]; then
        echo "✅ Modelo $model baixado com sucesso"
        return 0
    else
        echo "❌ Erro ao baixar modelo $model"
        return 1
    fi
}

# Baixa modelos
SUCCESSFUL_DOWNLOADS=()
for model in "${MODELS[@]}"; do
    if download_model "$model"; then
        SUCCESSFUL_DOWNLOADS+=("$model")
    fi
    echo ""
done

# Se pelo menos um modelo foi baixado, executa testes
if [ ${#SUCCESSFUL_DOWNLOADS[@]} -gt 0 ]; then
    echo "✅ Modelos baixados com sucesso: ${#SUCCESSFUL_DOWNLOADS[@]}"
    echo ""
    echo "🧪 Executando testes..."
    echo ""
    
    # Executa script de teste Python
    python3 backend/tests/test_mistral_models.py
    
    echo ""
    echo "✅ Processo concluído!"
else
    echo "⚠️  Nenhum modelo foi baixado com sucesso"
    exit 1
fi

