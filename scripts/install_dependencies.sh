#!/bin/bash
# Script para instalar dependências do backend de forma inteligente

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📦 INSTALAÇÃO INTELIGENTE DE DEPENDÊNCIAS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Ativa ambiente virtual
if [ -z "$VIRTUAL_ENV" ] && [ -f "${PROJECT_ROOT}/backend/.venv/bin/activate" ]; then
    source "${PROJECT_ROOT}/backend/.venv/bin/activate"
    echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"
fi

cd "$PROJECT_ROOT"

# 1. Instala dependências essenciais
echo -e "${BLUE}1. Instalando dependências ESSENCIAIS...${NC}"
if pip install -q -r backend/requirements-essential.txt 2>&1; then
    echo -e "${GREEN}✅ Dependências essenciais instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências essenciais${NC}"
    exit 1
fi

echo ""

# 2. Tenta instalar dependências opcionais (sem falhar se der erro)
echo -e "${BLUE}2. Tentando instalar dependências OPCIONAIS...${NC}"
if [ -f "backend/requirements-optional.txt" ]; then
    pip install -q -r backend/requirements-optional.txt 2>&1 || {
        echo -e "${YELLOW}⚠️  Algumas dependências opcionais não puderam ser instaladas${NC}"
        echo -e "${YELLOW}   Isso é normal. O servidor funcionará sem elas.${NC}"
    }
else
    echo -e "${YELLOW}⚠️  Arquivo de dependências opcionais não encontrado${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ INSTALAÇÃO CONCLUÍDA!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Dependências essenciais instaladas. O servidor está pronto!"
echo ""

