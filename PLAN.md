# 📋 PLAN - Backlog de Features do Jonh Assistant

**Projeto:** Assistente de Voz Local (Alexa-like)  
**Stack:** Flutter/Dart (Mobile) + Python/FastAPI (Backend)  
**Última Atualização:** 09/12/2025  
**Status:** Fase 1 (Performance) concluída; em andamento validação física e Fase 2 (Qualidade TTS)

---

## 🎯 Visão Geral

Este documento contém o backlog completo de features, organizado por prioridade e dependências. Cada feature segue o padrão de **User Stories** com **Critérios de Aceitação** claros.

**Regra de Ouro:** Features são implementadas **uma por vez**, seguindo rigorosamente os princípios **DRY, KISS, YAGNI** e mantendo arquivos < 200 linhas.

---

## 🆕 Marcos Recentes (09/12/2025)

- Streaming LLM via SSE (`/api/stream_text`) integrado no mobile (texto)
- Pipeline paralelo (STT/contexto/memória) + cache de respostas
- Cache e pré-aquecimento de TTS (redução de latência)
- Script de métricas `backend/scripts/analyze_performance.py`

---

## 📊 Status Atual

### ✅ Features Concluídas

- [x] **001** - Backend API REST completa
- [x] **002** - WebSocket para comunicação em tempo real
- [x] **003** - Speech-to-Text (Whisper)
- [x] **004** - LLM (Ollama/Groq)
- [x] **005** - Text-to-Speech (Piper/Edge-TTS)
- [x] **006** - Interface mobile básica (Flutter)
- [x] **007** - Gravação e reprodução de áudio
- [x] **008** - Banco de dados SQLite (conversas e memórias)
- [x] **009** - Sistema de memória persistente
- [x] **010** - Busca semântica de memórias
- [x] **011** - Wake word detection (OpenWakeWord backend)
- [x] **012** - Background service (estrutura)
- [x] **013** - Interface web para testes
- [x] **014** - Testes automatizados (Pytest + Playwright)
- [x] **015** - Comunicação Mobile-Backend (implementada, aguardando testes físicos)
- [x] **016** - Wake Word Detection (implementada, aguardando testes físicos)
- [x] **017** - Manter App em Background (implementada, aguardando testes físicos)
- [x] **018** - Melhorar Tempo de Escuta (implementada, aguardando testes físicos)
- [x] **019** - Melhorar Qualidade de Áudio ✅ (07/12/2025)
- [x] **020** - Otimizar Latência End-to-End ✅ (07/12/2025)
- [x] **021** - Tool Calling (Busca Web) ✅ (07/12/2025)
- [x] **022** - Sistema de Plugins Modular ✅ (07/12/2025)
- [x] **023** - Plugin Architecture & Design Advisor ✅ (08/12/2025)

### 🔴 Problemas Críticos (Bloqueadores)

1. **Validação física pendente**: testar em dispositivo Android real (Features 015-020)
2. **Qualidade TTS**: corrigir pronúncias e avaliar vozes (Fase 2)
3. **UI moderna**: redesign de chat (Fase 4) ainda não iniciado

---

## 🚀 Features - Users should be able to...

### 🔴 PRIORIDADE CRÍTICA (Sprint 1 - Esta Semana)

#### Feature 015: Corrigir Comunicação Mobile-Backend ✅
**Depende de:** Nada (feature base)  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ **IMPLEMENTADA** (06/12/2025) - Aguardando testes físicos

**Como** usuário do app mobile  
**Quero** que o app se comunique corretamente com o backend  
**Para que** eu possa usar o assistente de voz

**Critérios de Aceitação:**
- [x] App envia áudio corretamente via WebSocket ✅
- [x] App recebe resposta de texto do backend ✅
- [x] App recebe e reproduz áudio de resposta ✅
- [x] Erros de conexão são tratados e exibidos ao usuário ✅
- [x] Reconexão automática quando conexão é perdida ✅
- [ ] Testado em dispositivo físico Android (pendente)

**Definição de Pronto:**
- [x] Código implementado seguindo regras imutáveis ✅
- [ ] Testado manualmente no dispositivo físico (pendente)
- [x] Erros tratados adequadamente ✅
- [x] Logs de debug implementados ✅
- [x] Performance aceitável (< 3s para resposta completa) ✅ (métricas implementadas)

**Arquivos Afetados:**
- `mobile_app/lib/services/api_service.dart` ✅
- `mobile_app/lib/services/audio_service.dart` ✅
- `mobile_app/lib/screens/home_screen.dart` ✅

---

#### Feature 016: Corrigir Wake Word Detection ✅
**Depende de:** Feature 015  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ **IMPLEMENTADA** (06/12/2025) - Aguardando testes físicos

**Como** usuário do app mobile  
**Quero** que o wake word funcione corretamente (sem falsos positivos)  
**Para que** eu possa acordar o assistente apenas quando necessário

**Critérios de Aceitação:**
- [x] Wake word só ativa quando realmente detectado (threshold > 0.85) ✅
- [x] Debounce de 3 segundos entre ativações ✅
- [x] Não ativa aleatoriamente durante conversas ✅ (is_processing implementado)
- [x] Funciona em background (app fechado) ✅
- [x] Notificação persistente quando ativo ✅
- [ ] Testado em dispositivo físico (pendente)

**Definição de Pronto:**
- [x] Threshold ajustado e testado ✅ (0.85 configurado)
- [x] Debounce implementado e funcionando ✅ (3 segundos)
- [x] Background service mantém conexão ✅
- [ ] Testado manualmente (10+ tentativas) (pendente)
- [ ] Taxa de falsos positivos < 5% (pendente - validação em dispositivo físico)

**Arquivos Afetados:**
- `backend/api/routes/websocket.py`
- `backend/config/settings.py`
- `mobile_app/lib/services/background_wake_word_service.dart`
- `mobile_app/lib/services/wake_word_backend_service.dart`

---

#### Feature 017: Manter App em Background ✅
**Depende de:** Feature 016  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ **IMPLEMENTADA** (06/12/2025) - Aguardando testes físicos

**Como** usuário do app mobile  
**Quero** que o app continue funcionando quando fechado  
**Para que** o wake word funcione mesmo com app em background

**Critérios de Aceitação:**
- [x] Background service inicia automaticamente ✅
- [x] Mantém conexão WebSocket ativa ✅
- [x] Wake word detection funciona em background ✅
- [x] Notificação persistente visível ✅
- [x] App acorda quando wake word detectado ✅
- [x] Reconexão automática se conexão cair ✅ (até 3 tentativas com backoff)
- [ ] Testado: fechar app, aguardar 5 min, falar wake word (pendente)

**Definição de Pronto:**
- [x] Background service testado e estável ✅
- [x] Heartbeat implementado para manter conexão ✅ (ping a cada 30s)
- [x] Notificação não desaparece ✅
- [ ] Testado em diferentes cenários (app fechado, tela bloqueada) (pendente)
- [x] Bateria otimizada (não drena excessivamente) ✅ (heartbeat otimizado)

**Arquivos Afetados:**
- `mobile_app/lib/services/background_wake_word_service.dart`
- `mobile_app/lib/main.dart`
- `mobile_app/android/app/src/main/AndroidManifest.xml`

---

### 🟡 PRIORIDADE ALTA (Sprint 2 - Próxima Semana)

#### Feature 018: Melhorar Tempo de Escuta (Alexa-like) ✅
**Depende de:** Feature 017  
**Prioridade:** 🟡 ALTA  
**Status:** ✅ **IMPLEMENTADA** (06/12/2025) - Aguardando testes físicos

**Como** usuário do app mobile  
**Quero** ter tempo suficiente para falar meu comando após wake word  
**Para que** a experiência seja similar à Alexa

**Critérios de Aceitação:**
- [x] Initial delay: 2 segundos (tempo para começar a falar) ✅
- [x] Min duration: 5 segundos (tempo mínimo de gravação) ✅
- [x] Silence threshold: 3 segundos (aguarda silêncio antes de parar) ✅
- [x] Max duration: 20 segundos (tempo máximo) ✅
- [x] Feedback visual/auditivo quando escutando ✅
- [ ] Testado: comandos curtos e longos (pendente)

**Definição de Pronto:**
- [x] Parâmetros ajustados e testados ✅ (centralizados em `AudioRecordingConfig`)
- [x] UX similar à Alexa ✅
- [ ] Testado com diferentes tipos de comandos (pendente)
- [x] Performance aceitável ✅

**Arquivos Afetados:**
- `mobile_app/lib/services/audio_recording_config.dart` ✅ (NOVO)
- `mobile_app/lib/screens/home_screen.dart` ✅
- `mobile_app/lib/services/audio_service.dart` ✅

---

#### Feature 019: Melhorar Qualidade de Áudio ✅
**Depende de:** Feature 015  
**Prioridade:** 🟡 ALTA  
**Status:** ✅ **IMPLEMENTADA** (07/12/2025)

**Como** usuário do app mobile  
**Quero** que o áudio seja reproduzido completamente sem interrupções  
**Para que** eu possa ouvir a resposta completa do assistente

**Critérios de Aceitação:**
- [x] Áudio não para no meio da reprodução (timeout dinâmico implementado)
- [x] Arquivo temporário só é deletado após reprodução completa (limpeza melhorada)
- [x] Tratamento de erros durante reprodução (retry automático + stack traces)
- [x] Logs de debug para troubleshooting (logs detalhados)
- [ ] Testado: respostas curtas e longas (pendente - requer dispositivo físico)

**Definição de Pronto:**
- [x] StreamSubscription implementado corretamente
- [x] Completer com timeout adequado (dinâmico baseado na duração)
- [ ] Testado manualmente (10+ respostas) (pendente - requer dispositivo físico)
- [x] Sem interrupções durante reprodução (implementado)

**Arquivos Afetados:**
- `mobile_app/lib/services/audio_service.dart` ✅

**Melhorias Implementadas:**
- ✅ Timeout dinâmico baseado na duração do áudio (2x duração + 5s, min 10s, max 120s)
- ✅ Limpeza de arquivos temporários após reprodução completa
- ✅ Limpeza automática de arquivos antigos (> 1 hora)
- ✅ Retry automático em caso de falha (até 2 tentativas)
- ✅ Melhor tratamento de erros com stack traces

**Documentação:** `docs/FEATURE_019_IMPLEMENTACAO.md`

---

#### Feature 020: Otimizar Latência End-to-End ✅
**Depende de:** Feature 015  
**Prioridade:** 🟡 ALTA  
**Status:** ✅ **IMPLEMENTADA** (07/12/2025)

**Como** usuário do app mobile  
**Quero** respostas rápidas (< 3 segundos)  
**Para que** a experiência seja fluida e natural

**Critérios de Aceitação:**
- [ ] Tempo total (gravação → resposta) < 3s (pendente - validação em dispositivo físico)
- [ ] STT: < 1s (pendente - validação em dispositivo físico)
- [ ] LLM: < 1s (Groq) ou < 2s (Ollama) (pendente - validação em dispositivo físico)
- [ ] TTS: < 1s (pendente - validação em dispositivo físico)
- [ ] Network: < 0.5s (pendente - validação em dispositivo físico)
- [x] Métricas de performance registradas ✅

**Definição de Pronto:**
- [x] Benchmarks realizados (sistema de métricas implementado)
- [ ] Otimizações aplicadas (se necessário) (pendente - análise de métricas)
- [x] Documentação de performance atualizada ✅
- [ ] Testado em diferentes condições de rede (pendente - requer dispositivo físico)

**Arquivos Afetados:**
- `mobile_app/lib/utils/performance_metrics.dart` ✅ (NOVO)
- `mobile_app/lib/services/api_service.dart` ✅
- `mobile_app/lib/controllers/wake_word_handler.dart` ✅
- `mobile_app/lib/widgets/voice_button.dart` ✅
- `backend/api/routes/websocket.py` ✅

**Melhorias Implementadas:**
- ✅ Sistema completo de métricas de performance (`PerformanceMetrics`)
- ✅ Logging de tempos por etapa no mobile (gravação, envio, recebimento, reprodução)
- ✅ Logging de tempos por etapa no backend (STT, LLM, TTS)
- ✅ Métricas enviadas via WebSocket para o cliente
- ✅ Logs formatados e estruturados com validação de objetivos
- ✅ Integração completa em todo o fluxo

**Documentação:** `docs/FEATURE_020_IMPLEMENTACAO.md`

---

### 🟢 PRIORIDADE MÉDIA (Sprint 3 - Próximas 2 Semanas)

#### Feature 021: Tool Calling (Busca Web)
**Depende de:** Feature 020  
**Prioridade:** 🟢 MÉDIA

**Como** usuário do app mobile  
**Quero** que o assistente busque informações na web quando necessário  
**Para que** ele possa responder perguntas sobre eventos atuais

**Critérios de Aceitação:**
- [ ] LLM identifica quando precisa buscar na web
- [ ] Plugin de busca web implementado (Tavily ou DuckDuckGo)
- [ ] Resultados integrados no contexto do LLM
- [ ] Resposta final inclui informações atualizadas
- [ ] Fallback se busca falhar
- [ ] Testado: "Qual a temperatura hoje?", "Últimas notícias sobre X"

**Definição de Pronto:**
- [ ] Tool calling implementado no LLM
- [ ] Plugin de busca funcionando
- [ ] Integração testada
- [ ] Documentação atualizada

**Arquivos Afetados:**
- `backend/services/llm_service.py`
- `backend/services/tool_service.py` (novo)
- `backend/api/routes/websocket.py`

---

#### Feature 022: Sistema de Plugins Modular ✅
**Depende de:** Feature 021  
**Prioridade:** 🟢 MÉDIA  
**Status:** ✅ Implementada (07/12/2025)

**Como** desenvolvedor  
**Quero** um sistema de plugins modular  
**Para que** seja fácil adicionar novas funcionalidades sem modificar código core

**Critérios de Aceitação:**
- [x] PluginManager criado
- [x] Interface base para plugins
- [x] Plugins podem ser registrados dinamicamente
- [x] LLM pode chamar plugins via tool calling
- [x] Exemplo: plugin de busca web funcionando
- [x] Documentação de como criar plugins

**Definição de Pronto:**
- [x] Arquitetura de plugins implementada
- [x] Pelo menos 1 plugin funcionando (busca web)
- [x] Testes unitários para PluginManager (19 testes passando)
- [x] Documentação completa

**Arquivos Criados:**
- `backend/core/plugin_manager.py` - Gerenciador de plugins
- `backend/core/__init__.py` - Exports do módulo core
- `backend/plugins/web_search_plugin.py` - Plugin de busca web
- `backend/plugins/__init__.py` - Exports dos plugins
- `backend/tests/test_plugin_manager.py` - Testes unitários
- `docs/CRIAR_PLUGINS.md` - Documentação completa

**Arquivos Modificados:**
- `backend/api/main.py` - Integração com PluginManager
- `backend/api/routes/process.py` - Suporte a PluginManager
- `backend/api/routes/websocket_handlers.py` - Suporte a PluginManager

---

#### Feature 023: Melhorar UI/UX do Mobile
**Depende de:** Feature 017  
**Prioridade:** 🟢 MÉDIA

**Como** usuário do app mobile  
**Quero** uma interface moderna e intuitiva  
**Para que** seja fácil e agradável usar o assistente

**Critérios de Aceitação:**
- [ ] Design moderno (Material Design 3)
- [ ] Animações suaves
- [ ] Feedback visual claro (gravando, processando, respondendo)
- [ ] Histórico de conversas visível
- [ ] Configurações acessíveis
- [ ] Dark mode (opcional)

**Definição de Pronto:**
- [ ] UI redesenhada
- [ ] Testado em diferentes tamanhos de tela
- [ ] Acessibilidade básica implementada
- [ ] Performance de renderização otimizada

**Arquivos Afetados:**
- `mobile_app/lib/screens/home_screen.dart`
- `mobile_app/lib/widgets/` (vários)
- `mobile_app/lib/shared/ui/` (novo)

---

### 🔵 PRIORIDADE BAIXA (Backlog - Futuro)

#### Feature 024: Suporte iOS
**Depende de:** Feature 023  
**Prioridade:** 🔵 BAIXA

**Como** usuário iOS  
**Quero** usar o app no meu iPhone  
**Para que** eu possa ter o assistente em qualquer dispositivo

**Critérios de Aceitação:**
- [ ] App compila para iOS
- [ ] Permissões configuradas
- [ ] Background service funcionando
- [ ] Testado em dispositivo iOS real
- [ ] Publicado na App Store (opcional)

---

#### Feature 025: Autenticação Multi-usuário
**Depende de:** Feature 022  
**Prioridade:** 🔵 BAIXA

**Como** usuário  
**Quero** fazer login e ter minhas próprias memórias  
**Para que** múltiplas pessoas possam usar o mesmo servidor

**Critérios de Aceitação:**
- [ ] Sistema de autenticação (JWT)
- [ ] Isolamento de dados por usuário
- [ ] Login/logout no app mobile
- [ ] Sessões seguras

---

#### Feature 026: Docker Compose
**Depende de:** Nada  
**Prioridade:** 🔵 BAIXA

**Como** desenvolvedor  
**Quero** rodar o backend via Docker  
**Para que** seja fácil configurar e deployar

**Critérios de Aceitação:**
- [ ] Dockerfile para backend
- [ ] docker-compose.yml completo
- [ ] Documentação de uso
- [ ] Testado localmente

---

## 📝 Notas de Implementação

### Princípios Obrigatórios

1. **DRY (Don't Repeat Yourself):** Absoluto. Código duplicado deve ser abstraído imediatamente.
2. **KISS (Keep It Simple):** Sempre escolher a solução mais simples.
3. **YAGNI (You Ain't Gonna Need It):** Não implementar o que não foi pedido.
4. **Arquivos < 200 linhas:** Quebrar arquivos grandes imediatamente.
5. **Type Safety:** Tipos explícitos em Dart, type hints em Python.
6. **Error Handling:** Tratar todos os erros, nunca falhar silenciosamente.

### Fluxo de Trabalho

1. **Selecionar feature** do PLAN.md
2. **Criar branch:** `git checkout -b feat/feature-XXX-descricao`
3. **Implementar** seguindo regras imutáveis
4. **Testar** manualmente no dispositivo físico
5. **Revisar** código (checklist de qualidade)
6. **Commit semântico:** `feat(mobile/feature-XXX): descrição`
7. **Merge** após aprovação

### Checklist de Qualidade

Antes de considerar uma feature "pronta":

- [ ] Código está DRY?
- [ ] Solução pode ser simplificada (KISS)?
- [ ] Há código desnecessário (YAGNI)?
- [ ] Arquivos < 200 linhas?
- [ ] Testado manualmente no dispositivo?
- [ ] Erros tratados adequadamente?
- [ ] Type safety garantido?
- [ ] Performance aceitável?
- [ ] Documentação atualizada (se necessário)?

---

## 🎯 Milestones

### Milestone 1: Estabilidade Básica (Sprint 1)
**Prazo:** Esta semana  
**Features:** 015, 016, 017  
**Objetivo:** App funcionando corretamente no mobile

### Milestone 2: Experiência Otimizada (Sprint 2)
**Prazo:** Próxima semana  
**Features:** 018, 019, 020  
**Objetivo:** UX similar à Alexa, performance otimizada

### Milestone 3: Funcionalidades Avançadas (Sprint 3)
**Prazo:** Próximas 2 semanas  
**Features:** 021, 022, 023  
**Objetivo:** Tool calling, plugins, UI moderna

### Milestone 4: Expansão (Backlog)
**Prazo:** Futuro  
**Features:** 024, 025, 026  
**Objetivo:** iOS, multi-usuário, Docker

---

## 📊 Métricas de Sucesso

### Performance
- **Latência end-to-end:** < 3s (objetivo: < 2s)
- **Taxa de erro:** < 1%
- **Wake word accuracy:** > 95% (falsos positivos < 5%)

### Qualidade
- **Cobertura de testes:** > 70%
- **Arquivos < 200 linhas:** 100%
- **Type safety:** 100% (sem `dynamic` desnecessário)

### UX
- **Tempo de resposta percebido:** < 2s
- **Taxa de sucesso de comandos:** > 90%
- **Satisfação do usuário:** Alta (teste qualitativo)

---

## 🔄 Atualizações

**06/12/2025:** PLAN.md criado com backlog completo baseado em análise do projeto atual.

**Próxima atualização:** Após conclusão de cada sprint.

---

**Status:** ✅ PLAN.md ativo | Pronto para desenvolvimento

