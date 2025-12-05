# Configuração do Groq

O Groq oferece inferência de LLM ultra-rápida em cloud, ideal para o assistente Jonh quando você precisa de respostas instantâneas.

## Vantagens do Groq

- **Velocidade**: Até 10x mais rápido que Ollama local
- **Sem hardware**: Não precisa de GPU ou CPU potente
- **Modelos atualizados**: Acesso aos modelos mais recentes
- **Escalável**: Suporta múltiplos usuários simultâneos

## Desvantagens

- **Requer internet**: Não funciona offline
- **Custo**: Plano gratuito limitado (depois paga por token)
- **Privacidade**: Dados enviados para cloud (não 100% local)

## Passo a Passo

### 1. Criar Conta no Groq

Acesse: https://console.groq.com/

- Clique em "Sign Up"
- Use Google, GitHub ou email
- Confirme sua conta

### 2. Obter API Key

Após login:

1. Vá em "API Keys" no menu lateral
2. Clique em "Create API Key"
3. Dê um nome (ex: "Jonh Assistant")
4. Copie a chave (começa com `gsk_...`)

**⚠️ IMPORTANTE**: Salve a chave em local seguro. Ela só é mostrada uma vez!

### 3. Configurar no Projeto

Edite o arquivo `.env`:

```bash
# Mude o provider para groq
LLM_PROVIDER=groq

# Cole sua API key
GROQ_API_KEY=gsk_sua_chave_aqui

# Modelo recomendado (mais rápido)
GROQ_MODEL=llama-3.1-8b-instant
```

### 4. Instalar Dependência

```bash
source backend/.venv/bin/activate
pip install groq
```

### 5. Testar

```bash
# Inicie o servidor
./scripts/start_server.sh

# Em outro terminal, teste
curl http://localhost:8000/health
```

Você deve ver `"llm": "online"` na resposta.

## Modelos Disponíveis no Groq

| Modelo | Velocidade | Qualidade | Recomendado para |
|--------|-----------|-----------|------------------|
| `llama-3.1-8b-instant` | ⚡⚡⚡ | ⭐⭐⭐ | Conversação geral (RECOMENDADO) |
| `llama-3.1-70b-versatile` | ⚡⚡ | ⭐⭐⭐⭐⭐ | Tarefas complexas |
| `mixtral-8x7b-32768` | ⚡⚡ | ⭐⭐⭐⭐ | Contexto longo |
| `gemma-7b-it` | ⚡⚡⚡ | ⭐⭐⭐ | Alternativa rápida |

Para mudar o modelo, edite `GROQ_MODEL` no `.env`.

## Comparação: Ollama vs Groq

### Ollama (Local)

**Prós:**
- ✅ 100% privado
- ✅ Funciona offline
- ✅ Zero custo
- ✅ Sem limites de uso

**Contras:**
- ❌ Mais lento (1-3 segundos)
- ❌ Requer hardware potente
- ❌ Consome RAM/CPU

**Quando usar:**
- Privacidade é prioridade
- Sem internet confiável
- Uso pessoal intenso

### Groq (Cloud)

**Prós:**
- ✅ Ultra rápido (0.2-0.5 segundos)
- ✅ Não precisa de hardware
- ✅ Sempre disponível
- ✅ Modelos atualizados

**Contras:**
- ❌ Requer internet
- ❌ Dados vão para cloud
- ❌ Custo após limite gratuito

**Quando usar:**
- Velocidade é prioridade
- Hardware limitado
- Prototipagem rápida
- Demonstrações

## Limites do Plano Gratuito

O Groq oferece um plano gratuito generoso:

- **Requests por minuto**: 30
- **Requests por dia**: 14.400
- **Tokens por minuto**: 6.000

Para uso pessoal do assistente Jonh, isso é mais que suficiente!

## Alternando Entre Ollama e Groq

Você pode alternar facilmente editando o `.env`:

```bash
# Usar Ollama (local)
LLM_PROVIDER=ollama

# Usar Groq (cloud)
LLM_PROVIDER=groq
```

Reinicie o servidor após mudar.

## Segurança da API Key

**NUNCA** compartilhe ou commite sua API key!

### Boas Práticas

1. **Mantenha no .env**: Nunca hardcode no código
2. **Adicione ao .gitignore**: Já está configurado
3. **Rotacione regularmente**: Crie nova key a cada 3 meses
4. **Use variáveis de ambiente**: Em produção, use secrets manager

### Se Vazou a Key

1. Acesse https://console.groq.com/
2. Vá em "API Keys"
3. Delete a key comprometida
4. Crie uma nova
5. Atualize o `.env`

## Troubleshooting

### Erro: "Invalid API key"

- Verifique se copiou a key completa (começa com `gsk_`)
- Confirme que está no `.env` correto
- Tente gerar nova key

### Erro: "Rate limit exceeded"

- Você excedeu o limite gratuito
- Aguarde 1 minuto e tente novamente
- Considere upgrade para plano pago

### Erro: "Connection timeout"

- Verifique sua conexão com internet
- Tente novamente em alguns segundos
- Groq pode estar em manutenção

### LLM aparece como "offline"

```bash
# Verifique se a biblioteca está instalada
pip list | grep groq

# Se não estiver, instale
pip install groq

# Verifique o .env
cat .env | grep GROQ
```

## Custos (após limite gratuito)

Se você ultrapassar o limite gratuito:

- **Llama 3.1 8B**: $0.05 / 1M tokens
- **Llama 3.1 70B**: $0.59 / 1M tokens

Para referência, uma conversa típica usa ~100-200 tokens.

**Exemplo de custo:**
- 1000 conversas/mês = ~150k tokens
- Com Llama 3.1 8B = $0.0075 (menos de 1 centavo!)

## Recomendação

Para o assistente Jonh:

**Desenvolvimento/Testes**: Use Groq (mais rápido para iterar)
**Produção pessoal**: Use Ollama (privacidade e zero custo)
**Demonstrações**: Use Groq (impressiona com velocidade)

Você pode ter os dois configurados e alternar conforme necessário!

## Suporte

- Documentação oficial: https://console.groq.com/docs
- Discord da Groq: https://discord.gg/groq
- Issues do projeto: GitHub

