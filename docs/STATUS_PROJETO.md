# Status do Projeto Jonh Assistant

**Última Atualização:** 11/12/2025  
**Versão:** 1.0.1-beta

## 📊 Visão Geral

O Jonh Assistant é um assistente de voz local, similar à Alexa, desenvolvido com Flutter (mobile) e Python/FastAPI (backend). O projeto está em desenvolvimento ativo com foco em privacidade, performance e qualidade de experiência do usuário.

## ✅ Features Implementadas

### Backend (20 features concluídas)

#### Features Base (001-014)
- ✅ API REST completa
- ✅ WebSocket para comunicação em tempo real
- ✅ Speech-to-Text (Whisper)
- ✅ LLM (Ollama/Groq)
- ⚠️ Text-to-Speech (Piper/Edge-TTS) - Implementado mas desabilitado no fluxo principal
- ✅ Banco de dados SQLite
- ✅ Sistema de memória persistente
- ✅ Busca semântica de memórias
- ⚠️ Wake word detection - Backend (OpenWakeWord) funcional; Mobile (Porcupine) requer configuração
- ✅ Background service
- ✅ Interface web para testes
- ✅ Testes automatizados

#### Features Críticas (015-018)
- ✅ Comunicação Mobile-Backend
- ✅ Wake Word Detection
- ✅ Manter App em Background
- ✅ Melhorar Tempo de Escuta (Alexa-like)

**Status:** Implementadas, aguardando testes físicos em dispositivo Android

#### Features de Qualidade (019-022)
- ✅ **Feature 019**: Melhorar Qualidade de Áudio (07/12/2025)
  - Timeout dinâmico baseado na duração do áudio
  - Limpeza automática de arquivos temporários
  - Retry automático em caso de falha
  - Logs detalhados para troubleshooting

- ✅ **Feature 020**: Otimizar Latência End-to-End (07/12/2025)
  - Sistema completo de métricas de performance
  - Logging de tempos por etapa (gravação, rede, STT, LLM, TTS, reprodução)
  - Métricas enviadas via WebSocket
  - Validação de objetivos (< 3s total)

- ✅ **Feature 021**: Tool Calling (Busca Web) (07/12/2025)
  - Busca web automática (DuckDuckGo padrão, Tavily fallback)
  - LLM decide quando buscar informações atualizadas
  - Integração completa no WebSocket
  - Suporte a Ollama e Groq

- ✅ **Feature 022**: Sistema de Plugins Modular (09/12/2025)
  - PluginManager com registro dinâmico
  - Plugin de busca web integrado
  - Arquitetura extensível para novos plugins

#### Novos Plugins (09/12/2025)
- ✅ **CalculatorPlugin**
  - Operações matemáticas básicas (+, -, *, /)
  - Operações avançadas (potências, raiz quadrada, funções trigonométricas)
  - Suporte a expressões em português natural
  - Avaliação segura de expressões matemáticas

- ✅ **CurrencyConverterPlugin**
  - Conversão entre moedas (BRL, USD, EUR, GBP, JPY, CNY, ARS, CLP)
  - Taxas de câmbio com cache
  - Suporte a API externa (opcional)
  - Normalização de códigos de moeda

#### Fase 2 - Melhoria de Qualidade TTS (09/12/2025)
- ✅ **TTSTextProcessor aprimorado**
  - Normalização de números inteiros, decimais e grandes (milhares, milhões)
  - Normalização de datas (múltiplos formatos)
  - Normalização de horas (HH:MM → "quatorze horas e trinta minutos")
  - Normalização de moeda (R$, $, €) com suporte a centavos
  - Normalização de porcentagens (50% → "cinquenta por cento")
  - Normalização de medidas (kg, g, m, cm, km, l, ml, km/h, etc.)
  - Expansão de abreviações comuns em português (Dr., etc., vs., etc.)
  - Normalização de siglas brasileiras (CPF, CNPJ, RG, SUS, etc.)

- ✅ **TTSPronunciationDict expandido**
  - Dicionário com 50+ termos técnicos em português
  - Suporte para termos de tecnologia (API, JSON, HTTP, etc.)
  - Substituições case-insensitive com word boundaries

- ✅ **TTSSSMLProcessor melhorado**
  - Pausas automáticas após pontuação (., !, ?, ,, ;, :)
  - Pausas contextuais (parênteses)
  - Controle de prosody (velocidade reduzida para números grandes)
  - Envolvimento automático em tag <speak>
  - Detecção inteligente de SSML já presente

- ✅ **Utilitário de teste**
  - Script `test_tts_pronunciation.py` para testar pronúncias
  - Modo interativo e exemplos pré-definidos
  - Exibe cada etapa do processamento

- ✅ **Testes automatizados**
  - Testes unitários para TTSTextProcessor (11 testes)
  - Testes unitários para TTSSSMLProcessor (7 testes)
  - Testes unitários para TTSPronunciationDict (4 testes)

#### Melhorias Adicionais (09/12/2025)
- ✅ **Cache de Buscas Recentes**
  - Cache TTL de 1 hora para WebSearchPlugin
  - Reduz chamadas às APIs de busca
  - Melhora latência em buscas repetidas
  - Cache size configurável (padrão: 100 entradas)

- ✅ **Health Check Aprimorado**
  - Status detalhado de todos os serviços
  - Informações de plugins (total, lista, tools)
  - Estatísticas de memória e cache
  - Sessões ativas
  - Status granular (healthy/degraded/unhealthy)

- ✅ **Normalizações TTS Adicionais**
  - Temperatura: "25°C" → "vinte e cinco graus Celsius"
  - Tamanhos: "P, M, G" → "pequeno, médio, grande"
  - Suporte completo para unidades de temperatura (C, F, K)

#### Otimizações de Performance (Fase 1 - 09/12/2025)
- ✅ Streaming LLM via SSE (`/api/stream_text`) com Groq/Ollama
- ✅ Pipeline paralelo (contexto/memórias/tools) e cache semântico de respostas
- ✅ Cache e pré-aquecimento de TTS (frases frequentes)
- ✅ Script de métricas `backend/scripts/analyze_performance.py`

### Mobile App (Flutter)

#### Refatoração Completa (4 Fases)
- ✅ **Fase 1**: Design System, Error Handling, Audio Validation
- ✅ **Fase 2**: Separação de Responsabilidades (Controllers, Widgets)
- ✅ **Fase 3**: Arquitetura Feature-Based
- ✅ **Fase 4**: State Management e Testes (33 testes passando)

#### Funcionalidades
- ✅ Interface de chat moderna
- ✅ Gravação de áudio otimizada
- ⚠️ Reprodução de áudio - Código implementado mas não usado (TTS desabilitado)
- ✅ Métricas de performance (Feature 020)
- ✅ WebSocket para comunicação em tempo real
- ✅ Background service para wake word
- ✅ Notificações persistentes
- ✅ Tela de configurações

#### Fase 1 - Histórico de Conversas (11/12/2025)
- ✅ **Backend - ConversationHistoryService**
  - Serviço completo para gerenciar histórico de conversas salvas
  - Persistência em SQLite (tabela `saved_conversations`)
  - Métodos: save, get, list, delete, update_title
  - Integração com ContextManager para obter mensagens da sessão
  - Testes unitários (8 testes passando)

- ✅ **Backend - Endpoints REST**
  - `POST /api/conversations/save` - Salvar conversa
  - `GET /api/conversations` - Listar conversas (paginado)
  - `GET /api/conversations/{id}` - Recuperar conversa completa
  - `DELETE /api/conversations/{id}` - Deletar conversa
  - `PATCH /api/conversations/{id}/title` - Atualizar título

- ✅ **Mobile App - Feature de Histórico**
  - Modelo de dados (`ConversationHistory`, `ConversationSummary`)
  - Serviço HTTP (`ConversationHistoryService`)
  - Tela de listagem (`ConversationHistoryScreen`) com pull-to-refresh
  - Tela de detalhes (`ConversationDetailScreen`) com edição de título
  - Botão flutuante (FAB) para salvar conversa atual
  - Integração completa com ApiService
  - Arquitetura feature-based (todos arquivos < 200 linhas)

- ✅ **Melhorias de UX**
  - Dialog para nomear conversa ao salvar
  - Confirmação antes de deletar
  - Estados: loading, erro, vazio
  - Formatação inteligente de datas
  - Cards visuais para listagem

## 📈 Métricas de Qualidade

### Testes

**Backend:**
- ✅ 6 testes base passando
- ✅ 12 testes Feature 021 (Tool Calling) passando
- ✅ 8 testes ConversationHistoryService passando
- ✅ Cobertura: STT, LLM, TTS, Database, Memória, Tools, Histórico

**Mobile App:**
- ✅ 33 testes passando (Unit, Widget, Integration)
- ✅ Cobertura: Controllers, Services, Widgets, Utils

**Interface Web:**
- ✅ 10 testes Playwright passando (100%)

### Performance

**Objetivos (Feature 020):**
- Tempo total (gravação → resposta): < 3s
- STT: < 1s
- LLM: < 1s (Groq) ou < 2s (Ollama)
- TTS: < 1s
- Network: < 0.5s

**Status:** Sistema de métricas implementado, aguardando validação em dispositivo físico

## 🔴 Bloqueadores Atuais

1. **Testes físicos pendentes**
   - Validar Features 015-021 e streaming SSE em dispositivo Android real

2. **Qualidade TTS**
   - Ajustar pronúncias e avaliar vozes (Fase 2)

3. **UI moderna**
   - Redesenho de chat (Fase 4) ainda não iniciado

## 🚀 Próximos Passos

### Curto Prazo (Esta Semana)
- [ ] Testes físicos em dispositivo Android (Features 015-021 + streaming)
- [ ] Ajustes de TTS (vozes e pronúncia)
- [ ] Análise das métricas coletadas (script de performance)

### Médio Prazo (Próximas 2 Semanas)
- [ ] Fase 2: Especialista em Vagas de Emprego (JobSearchPlugin)
- [ ] Fase 3: Geolocalização/GPS (LocationPlugin)
- [ ] Fase 4: UI moderna (chat estilo WhatsApp + ChatGPT)
- [ ] Otimizações adicionais baseadas nas métricas

### Longo Prazo
- [ ] Visão computacional (upload/imagens)
- [ ] Docker compose completo
- [ ] CI/CD pipeline
- [ ] Suporte iOS

## 📚 Documentação

### Documentação Principal
- [README.md](../README.md) - Visão geral do projeto
- [PLAN.md](../PLAN.md) - Backlog completo de features
- [docs/ARQUITETURA.md](ARQUITETURA.md) - Arquitetura do sistema
- [docs/INSTALACAO.md](INSTALACAO.md) - Guia de instalação

### Features Recentes
- [docs/FEATURE_019_IMPLEMENTACAO.md](FEATURE_019_IMPLEMENTACAO.md) - Qualidade de Áudio
- [docs/FEATURE_020_IMPLEMENTACAO.md](FEATURE_020_IMPLEMENTACAO.md) - Otimização de Latência
- [docs/FEATURE_021_IMPLEMENTACAO.md](FEATURE_021_IMPLEMENTACAO.md) - Tool Calling
- [docs/TESTES_FEATURE_021.md](TESTES_FEATURE_021.md) - Testes da Feature 021

### Refatoração Mobile
- [docs/REFATORACAO_FASE2_RESUMO.md](REFATORACAO_FASE2_RESUMO.md) - Fase 2
- [docs/REFATORACAO_FASE3_RESUMO.md](REFATORACAO_FASE3_RESUMO.md) - Fase 3
- [docs/REFATORACAO_FASE4_RESUMO.md](REFATORACAO_FASE4_RESUMO.md) - Fase 4
- [docs/STATUS_TESTES.md](STATUS_TESTES.md) - Status dos Testes

### Troubleshooting
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guia de troubleshooting
- [docs/DEBUGGING_MOBILE.md](DEBUGGING_MOBILE.md) - Debug mobile

## 🛠️ Stack Tecnológica

### Backend
- **Framework**: FastAPI
- **LLM**: Ollama (local) ou Groq (cloud)
- **STT**: faster-whisper (Whisper otimizado)
- **TTS**: Piper TTS + Edge-TTS (fallback)
- **Database**: SQLite (aiosqlite)
- **Wake Word**: OpenWakeWord
- **Busca Web**: DuckDuckGo + Tavily

### Mobile
- **Framework**: Flutter 3.35+
- **Arquitetura**: Feature-Based
- **State Management**: Provider
- **Testes**: Unit, Widget, Integration

### Infraestrutura
- **Ambiente**: WSL2 (Ubuntu 22.04/24.04)
- **Deploy**: Local (desenvolvimento)
- **Monitoramento**: Logs estruturados (loguru)

## 📝 Notas para Desenvolvedores

### Princípios de Desenvolvimento
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Ain't Gonna Need It
- **Arquivos < 200 linhas**: Quebrar antes de crescer
- **Feature-Based**: Organização por domínios

### Fluxo de Trabalho
1. Selecionar feature do PLAN.md
2. Implementar seguindo regras imutáveis
3. Testar (unitários + integração)
4. Documentar (se necessário)
5. Commit semântico

### Testes
- Backend: `pytest tests/ -v`
- Mobile: `flutter test`
- Web: `./scripts/test_playwright.sh`

## 🎯 Objetivos do Projeto

1. **Privacidade**: 100% local, sem dependência de nuvem
2. **Performance**: Resposta em < 3 segundos
3. **Qualidade**: Experiência similar à Alexa
4. **Extensibilidade**: Sistema de plugins modular
5. **Manutenibilidade**: Código limpo e testado

---

**Mantido por:** Equipe de Desenvolvimento  
**Última Revisão:** 15/12/2025

---

## ⚠️ Status Atual Importante

### TTS (Text-to-Speech)

**Status**: Implementado mas **DESABILITADO** no fluxo principal de respostas.

- ✅ Piper TTS completamente implementado
- ✅ Endpoint `/api/synthesize` funcional para uso manual
- ❌ TTS não é usado nas respostas automáticas do assistente
- 📖 Ver [STATUS_ATUAL_TTS.md](STATUS_ATUAL_TTS.md) para detalhes completos

O assistente responde **apenas via texto** atualmente.

### Wake Word

**Status**: Implementado mas requer configuração manual.

- ✅ Backend: OpenWakeWord funcional
- ⚠️ Mobile: Porcupine requer Access Key do Picovoice + modelo

