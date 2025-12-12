# Sistema de Evolução de Agentes - Jonh Assistant

Sistema de evolução automática de prompts usando torneios locais com Ollama.

## 🎯 Objetivo

Evoluir automaticamente o system prompt do Jonh através de torneios onde diferentes variações competem e o melhor é selecionado.

## 🚀 Como Usar

### Pré-requisitos

1. Servidor Jonh rodando: `uvicorn backend.api.main:app --reload`
2. Ollama instalado e rodando (para o juiz)
3. Modelo `llama3.1:8b` disponível no Ollama (ou ajuste `JUDGE_MODEL` em `config.py`)

### Execução Básica

```bash
# No diretório raiz do projeto
cd evo
python tournament.py
```

### Personalização

Edite `evo/config.py` para ajustar:
- `POPULATION_SIZE`: Quantos prompts competem (padrão: 8)
- `GENERATIONS`: Quantas rodadas de evolução (padrão: 5)
- `MUTATION_RATE`: Chance de mutação forte (padrão: 0.3)
- `JUDGE_MODEL`: Modelo Ollama para julgar (padrão: "llama3.1:8b")

### Casos de Teste

Por padrão, usa `DEFAULT_TEST_CASES` em `tournament.py`. Você pode:

1. **Modificar diretamente no código**: Edite `DEFAULT_TEST_CASES` em `tournament.py`
2. **Passar como parâmetro**: Modifique `tournament.py` para aceitar arquivo de testes

Exemplo de casos de teste:
```python
test_cases = [
    "Olá, como você está?",
    "Qual é a capital do Brasil?",
    "Pesquise o último jogo do Flamengo",  # Testa tool calling
    "Preciso de ajuda com arquitetura",    # Testa Architecture Advisor
]
```

## 📊 Resultados

Os resultados são salvos em:
- `evo/generations/gen_XXX_score_YY.Y.txt`: Prompts dos campeões
- `evo/generations/history.json`: Histórico completo do torneio

## 🔧 Estrutura

```
evo/
├── __init__.py          # Módulo
├── config.py            # Configurações
├── generator.py         # Gera variações de prompts
├── judge.py             # Sistema de juiz (Ollama)
├── runner.py            # Executa testes via API
├── tournament.py        # Orquestra o torneio
├── tests/               # Áudios de teste (futuro)
└── generations/         # Histórico de evoluções
```

## 💡 Ideias de Melhorias

1. **Testes com áudio real**: Adicione arquivos WAV em `evo/tests/` e modifique `runner.py`
2. **Múltiplas personalidades**: Crie torneios separados para diferentes modos
3. **Auto-evolução contínua**: Rode automaticamente a cada semana
4. **Integração com CI/CD**: Execute torneios em pipelines

## ⚠️ Notas

- O sistema usa Ollama local (custo zero)
- Cada geração pode levar 10-30 minutos dependendo do número de testes
- Certifique-se de que o servidor está rodando antes de executar
- O modelo do juiz pode ser menor que o modelo principal (economiza recursos)

