# ⚠️ AVISO DE SEGURANÇA - API KEY EXPOSTA

## 🚨 AÇÃO URGENTE NECESSÁRIA

Uma API key do Groq foi exposta em commits anteriores do repositório.

**Key exposta (redact):** `gsk_<redacted_compromised_key>`

## 📋 Passos para Resolver

### 1. Rotacionar a API Key Imediatamente

1. Acesse: https://console.groq.com/keys
2. Revogue a key exposta
3. Gere uma nova key
4. Atualize o arquivo `.env` com a nova key

### 2. Verificar Histórico do Git

Se o repositório foi compartilhado publicamente:

```bash
# Verificar se key está no histórico (use o valor comprometido já rotacionado)
git log --all --full-history -p | grep "gsk_<redacted_compromised_key>"

# Se encontrado, considere:
# - Rotacionar a key (já feito acima)
# - Limpar histórico do Git (git filter-branch ou BFG Repo-Cleaner)
# - Ou criar novo repositório sem histórico
```

### 3. Atualizar .env

```bash
# Edite .env e substitua pela nova key
nano .env

# Substitua:
GROQ_API_KEY=gsk_sua_nova_chave_aqui
```

### 4. Verificar Arquivos

Certifique-se de que `.env` está no `.gitignore`:

```bash
grep -q "^\.env$" .gitignore && echo "✅ .env está no .gitignore" || echo "⚠️ Adicione .env ao .gitignore"
```

## 🔒 Boas Práticas

1. **Nunca commite API keys** em arquivos de código ou documentação
2. **Use placeholders** em documentação: `GROQ_API_KEY=gsk_sua_chave_aqui`
3. **Mantenha .env no .gitignore**
4. **Use variáveis de ambiente** em produção
5. **Rotacione keys regularmente**

## ✅ Status Atual

- [x] API key removida da documentação (STATUS.md)
- [x] Placeholders adicionados em todos os arquivos
- [ ] **AÇÃO NECESSÁRIA:** Rotacionar key no console Groq
- [ ] **AÇÃO NECESSÁRIA:** Atualizar .env com nova key

---

**Última atualização:** 05/12/2024

