# POC - Android Background Service

**Objetivo:** Validar viabilidade da Feature 017 (Wake Word em Background) antes da validação física completa.

**Problema:** Android 12+ (especialmente Android 14) pode matar serviços em background silenciosamente devido a Battery Optimization.

---

## 🎯 Objetivo do POC

Criar um app de teste isolado que valide:
1. ✅ Serviço mantém conexão WebSocket por > 30 minutos em background
2. ✅ Wake word funciona com tela bloqueada
3. ✅ Serviço não é morto pelo Battery Optimization
4. ✅ App abre automaticamente quando wake word detectado

---

## 📋 Teste a Realizar

### Cenário 1: Background com Tela Bloqueada
1. Abrir app POC
2. Iniciar serviço de background
3. Bloquear tela
4. Aguardar 30 minutos
5. Falar "Alexa"
6. **Esperado:** App abre automaticamente

### Cenário 2: Background com App Fechado (não force stop)
1. Abrir app POC
2. Iniciar serviço de background
3. Fechar app (não force stop)
4. Aguardar 30 minutos
5. Falar "Alexa"
6. **Esperado:** App abre automaticamente

### Cenário 3: Battery Optimization
1. Verificar se app está em lista de otimização de bateria
2. Se estiver, solicitar desativar otimização
3. Repetir Cenário 1 e 2
4. **Esperado:** Funciona melhor sem otimização

---

## 🔧 Implementação do POC

### Estrutura do App POC

```
mobile_app/test_poc_background/
├── main.dart              # App mínimo
├── services/
│   └── test_background_service.dart
└── screens/
    └── test_screen.dart
```

### Funcionalidades Mínimas

1. **Botão "Iniciar Teste"**
   - Inicia serviço de background
   - Conecta WebSocket
   - Mostra status

2. **Log de Eventos**
   - Timestamp de cada evento
   - Status do serviço
   - Detecções de wake word
   - Reconexões

3. **Métricas**
   - Tempo desde início
   - Número de reconexões
   - Número de detecções
   - Status atual (rodando/parado/morto)

---

## 📊 Critérios de Sucesso

### ✅ POC Passou Se:
- Serviço mantém conexão por > 30 minutos
- Wake word detecta com tela bloqueada
- App abre automaticamente quando wake word detectado
- Reconexão funciona após perda de conexão

### ❌ POC Falhou Se:
- Serviço é morto pelo sistema em < 30 minutos
- Wake word não funciona com tela bloqueada
- App não abre quando wake word detectado
- Reconexão não funciona

---

## 🚨 Se POC Falhar

**Ações Necessárias:**
1. Documentar comportamento observado
2. Testar com Battery Optimization desativado
3. Avaliar alternativas:
   - WorkManager para heartbeat
   - Push Notifications (FCM) para acordar app
   - Wake word apenas com tela ligada/carregando
4. Reescrever estratégia da Feature 017

---

## 📝 Próximos Passos

1. **Criar app POC isolado** (1 dia)
2. **Executar testes** (2 horas)
3. **Documentar resultados**
4. **Decidir:** Continuar Feature 017 ou ajustar estratégia

---

## 🔗 Referências

- `mobile_app/lib/services/background_wake_word_service.dart` - Implementação atual
- `docs/ANALISE_CONSOLIDADA_RECOMENDACOES.md` - Análise completa
- Android Background Service Limitations: https://developer.android.com/about/versions/oreo/background

---

**Status:** Planejado  
**Prioridade:** 🔴 Crítica  
**Estimativa:** 1 dia

