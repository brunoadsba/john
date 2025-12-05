# Quick Start - Jonh Assistant

Comece a usar o assistente Jonh em 5 minutos!

## Opção 1: Groq (Mais Rápido) ⚡

### Passo 1: Obter API Key
1. Acesse: https://console.groq.com/
2. Faça login/cadastro
3. Vá em "API Keys" → "Create API Key"
4. Copie a chave (começa com `gsk_...`)

### Passo 2: Configurar
```bash
cd /home/brunoadsba/john

# Edite o .env
nano .env
# Mude: LLM_PROVIDER=groq
# Cole sua key em: GROQ_API_KEY=gsk_sua_chave_aqui
```

### Passo 3: Instalar e Rodar
```bash
# Instale dependências
backend/.venv/bin/pip install groq

# Inicie servidor
./scripts/start_server.sh
```

### Passo 4: Testar
```bash
# Em outro terminal
curl http://localhost:8000/health
```

✅ **Pronto!** API rodando em http://localhost:8000

---

## Opção 2: Ollama (100% Local) 🔒

### Passo 1: Instalar Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

### Passo 2: Baixar Modelo
```bash
ollama pull llama3:8b-instruct-q4_0
```

### Passo 3: Rodar
```bash
cd /home/brunoadsba/john
./scripts/start_server.sh
```

### Passo 4: Testar
```bash
curl http://localhost:8000/health
```

✅ **Pronto!** API rodando localmente.

---

## Testar Conversação

```bash
# Sintetizar voz
curl -X POST http://localhost:8000/api/synthesize \
  -F "texto=Olá, eu sou o Jonh, seu assistente pessoal" \
  -o resposta.wav

# Tocar áudio (Linux)
aplay resposta.wav
```

## Próximos Passos

1. **Documentação completa**: [README.md](README.md)
2. **API docs**: http://localhost:8000/docs
3. **Comparação Ollama vs Groq**: [docs/COMPARACAO_LLM.md](docs/COMPARACAO_LLM.md)

## Problemas?

### Groq não conecta
- Verifique se copiou a API key completa
- Confirme que tem internet
- Teste em: https://console.groq.com/playground

### Ollama não funciona
```bash
# Verifique se está rodando
ps aux | grep ollama

# Se não, inicie
ollama serve &
```

### Porta 8000 em uso
```bash
# Mude a porta no .env
nano .env
# PORT=8001
```

---

**Dúvidas?** Abra uma issue no GitHub!
