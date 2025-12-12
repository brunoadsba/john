Claude:


# Análise Técnica do Plano de Implementação - Jonh Assistant

**Analista:** Especialista Senior em Arquitetura de Software  
**Data:** 10/12/2025  
**Status:** Análise Completa com Recomendações

---

## 1. VISÃO GERAL DA ANÁLISE

### 1.1 Pontos Fortes Identificados

✅ **Estrutura Sólida:**
- Organização em fases com dependências claras
- Critérios de sucesso mensuráveis
- Cronograma realista (6 semanas)
- Foco em validação antes de expansão

✅ **Cobertura Técnica:**
- Aborda débito técnico crítico (validação física)
- Priorização adequada (crítico → importante → melhorias)
- Documentação como entregável em cada fase

✅ **Gestão de Riscos:**
- Riscos identificados com mitigações
- Fallbacks planejados
- Abordagem incremental

### 1.2 Gaps Críticos Identificados

🔴 **Problemas de Arquitetura:**
1. Falta de estratégia de rollback entre fases
2. Testes de carga/stress não mencionados
3. Monitoramento de produção ausente
4. Estratégia de CI/CD só na fase 4 (deveria ser desde fase 1)

🟡 **Problemas de Processo:**
1. Falta de checkpoints intermediários nas fases longas
2. Dependências entre fases não explicitamente mapeadas
3. Critérios de "pronto para produção" não definidos

---

## 2. ANÁLISE DETALHADA POR FASE

### FASE 1: Validação Física (CRÍTICO)

#### Pontos Fortes
- Foco em validação real é essencial
- Documentação sistemática de problemas
- Cobertura adequada de features 015-021

#### Problemas Identificados

**🔴 CRÍTICO - Falta de Baseline de Performance**
```yaml
Problema: Validação sem baseline prévia
Impacto: Impossível saber se houve regressão
Solução: Criar baseline ANTES da validação
```

**Recomendação:**
```bash
# Adicionar tarefa 1.0: Estabelecer Baseline
- Executar testes automatizados no emulador
- Coletar métricas atuais (latência, CPU, memória)
- Documentar em docs/BASELINE_PRE_VALIDACAO.md
- Usar como referência para comparação
```

**🟡 IMPORTANTE - Testes Manuais Demais**
```yaml
Problema: Muitos testes manuais (ex: 10+ tentativas)
Impacto: Não escalável, propenso a erro humano
Solução: Automatizar testes repetitivos
```

**Recomendação:**
```python
# Criar: backend/tests/integration/test_physical_device.py
import pytest
from mobile_automation import AndroidDevice

@pytest.mark.physical
class TestFeature015PhysicalDevice:
    def test_websocket_stability_10_iterations(self, device):
        """Testa 10 conexões WebSocket consecutivas"""
        success_rate = 0
        for i in range(10):
            result = device.send_audio_and_wait_response()
            if result.success:
                success_rate += 1
        
        assert success_rate >= 9, f"Taxa de sucesso: {success_rate}/10"
    
    def test_audio_playback_completion(self, device):
        """Valida que áudio nunca corta no meio"""
        responses = device.send_multiple_queries(10)
        incomplete = [r for r in responses if r.audio_incomplete]
        
        assert len(incomplete) == 0, f"Áudios incompletos: {incomplete}"
```

**🟡 IMPORTANTE - Validação Wake Word Insuficiente**
```yaml
Problema: Taxa de falsos positivos testada manualmente
Impacto: Difícil reproduzir, dados não confiáveis
Solução: Dataset de teste + automação
```

**Recomendação:**
```python
# Criar: backend/tests/data/wake_word_test_dataset.json
{
  "positive_samples": [
    "alexa_sample_001.wav", # 50 amostras
    "alexa_sample_002.wav",
    ...
  ],
  "negative_samples": [
    "conversation_001.wav", # 100 amostras
    "conversation_002.wav",
    ...
  ]
}

# Criar: backend/tests/integration/test_wake_word_accuracy.py
def test_wake_word_false_positive_rate():
    """Taxa de falsos positivos < 5%"""
    dataset = load_test_dataset()
    false_positives = 0
    
    for audio in dataset['negative_samples']:
        if wake_word_service.detect(audio):
            false_positives += 1
    
    rate = false_positives / len(dataset['negative_samples'])
    assert rate < 0.05, f"Taxa de falsos positivos: {rate:.2%}"
```

#### Ajustes Recomendados

**Adicionar Tarefa 1.0:**
```markdown
### 1.0 Estabelecer Baseline de Performance
**Arquivos:** `docs/BASELINE_PRE_VALIDACAO.md`, `scripts/collect_baseline_metrics.py`

**Implementação:**
- Executar suite de testes automatizados no emulador
- Coletar métricas atuais:
  - Latência média por etapa (STT, LLM, TTS)
  - Uso de CPU/memória
  - Taxa de sucesso de conexão WebSocket
  - Taxa de detecção wake word (com dataset de teste)
- Documentar em `docs/BASELINE_PRE_VALIDACAO.md`
- Usar como referência para detectar regressões

**Critérios de Sucesso:**
- Baseline documentado com dados mensuráveis
- Script de coleta automatizado e reproduzível
- Comparação pré/pós validação possível

**Estimativa:** 0.5 dia
```

**Adicionar Tarefa 1.9.1:**
```markdown
### 1.9.1 Comparação Baseline vs Pós-Validação
**Arquivos:** `scripts/compare_metrics.py`, `docs/ANALISE_REGRESSAO.md`

**Implementação:**
- Executar mesma suite de testes do baseline
- Comparar métricas pré/pós validação
- Identificar regressões (latência aumentou > 10%, taxa de sucesso diminuiu, etc.)
- Documentar diferenças e causas prováveis

**Critérios de Sucesso:**
- Comparação lado a lado documentada
- Regressões identificadas e justificadas
- Plano de correção para regressões críticas

**Estimativa:** 0.5 dia
```

**Cronograma Ajustado Fase 1:**
- 1.0 Baseline: 0.5 dia
- 1.1 Setup: 0.5 dia
- 1.2-1.8 Validação: 3 dias
- 1.9 Documentação problemas: 0.5 dia
- 1.9.1 Comparação baseline: 0.5 dia
- 1.10 Correções críticas: 1 dia
- **Total: 6 dias (1.2 semanas)**

---

### FASE 2: Qualidade TTS

#### Pontos Fortes
- Abordagem sistemática de melhoria
- Dicionário de pronúncia é excelente ideia
- Foco em normalização de texto

#### Problemas Identificados

**🟡 IMPORTANTE - Avaliação Subjetiva Não Escalável**
```yaml
Problema: "Avaliação subjetiva > 4/5"
Impacto: Não reproduzível, viés do avaliador
Solução: Métricas objetivas + painel de avaliadores
```

**Recomendação:**
```python
# Usar métricas objetivas de qualidade TTS
from pesq import pesq  # Perceptual Evaluation of Speech Quality
from pystoi import stoi  # Short-Time Objective Intelligibility

def avaliar_qualidade_tts(audio_sintetizado, audio_referencia):
    """
    Métricas objetivas:
    - PESQ: 1.0 (ruim) a 4.5 (excelente)
    - STOI: 0.0 (ruim) a 1.0 (excelente)
    """
    pesq_score = pesq(16000, audio_referencia, audio_sintetizado, 'wb')
    stoi_score = stoi(audio_referencia, audio_sintetizado, 16000)
    
    return {
        'pesq': pesq_score,  # Target: > 3.0
        'stoi': stoi_score,  # Target: > 0.8
        'approved': pesq_score > 3.0 and stoi_score > 0.8
    }
```

**Adicionar ao Plano:**
```markdown
#### 2.6.1 Métricas Objetivas de Qualidade
**Arquivos:** `backend/tests/test_tts_objective_metrics.py`

**Implementação:**
- Instalar bibliotecas: `pesq`, `pystoi`
- Criar dataset de referência (áudio humano de alta qualidade)
- Sintetizar mesmas frases com cada voz
- Calcular PESQ e STOI
- Comparar resultados objetivamente

**Critérios de Sucesso:**
- PESQ > 3.0 (boa qualidade perceptual)
- STOI > 0.8 (boa inteligibilidade)
- Seleção de voz baseada em dados

**Estimativa:** +0.5 dia
```

**🟡 IMPORTANTE - Dicionário Estático Limitado**
```yaml
Problema: Dicionário JSON estático com 100 entradas
Impacto: Não escala, difícil manter
Solução: Sistema de aprendizado online
```

**Recomendação de Arquitetura:**
```python
# backend/services/tts/adaptive_pronunciation.py
class AdaptivePronunciationDict:
    """
    Sistema que aprende pronúncias corretas ao longo do tempo
    """
    def __init__(self):
        self.static_dict = self.load_static_dict()
        self.learned_dict = self.load_learned_dict()
        self.feedback_queue = []
    
    def get_pronunciation(self, word):
        """Busca em ordem: learned > static > None"""
        return (
            self.learned_dict.get(word) or 
            self.static_dict.get(word) or 
            None
        )
    
    def record_feedback(self, word, was_correct):
        """Usuário marca se pronúncia foi correta"""
        self.feedback_queue.append({
            'word': word,
            'correct': was_correct,
            'timestamp': datetime.now()
        })
    
    def learn_from_feedback(self):
        """
        Aprende com feedback:
        - Se palavra sempre incorreta, busca pronúncia alternativa
        - Se sempre correta, adiciona ao learned_dict
        """
        pass
```

**Adicionar Feature (Fase 4):**
```markdown
#### 4.8 Sistema de Feedback de Pronúncia (Novo)
**Arquivos:** `backend/services/tts/adaptive_pronunciation.py`, `mobile_app/lib/widgets/pronunciation_feedback.dart`

**Implementação:**
- UI: Botão "Pronúncia incorreta?" após TTS
- Backend: Endpoint para receber feedback
- Sistema aprende pronúncias corretas ao longo do tempo
- Dicionário adaptativo > dicionário estático

**Estimativa:** 2 dias
```

**🔴 CRÍTICO - Pós-processamento Pode Causar Latência**
```yaml
Problema: Normalização + fade in/out + redução ruído
Impacto: Adiciona 100-300ms de latência
Solução: Fazer apenas se necessário, em paralelo
```

**Recomendação:**
```python
# backend/services/tts_service.py
async def synthesize_with_postprocessing(self, text):
    # Síntese básica (sempre)
    audio = await self.piper_synthesize(text)
    
    # Pós-processamento condicional (apenas se configurado)
    if self.config.tts_postprocessing_enabled:
        # Executar em paralelo se possível
        audio = await asyncio.gather(
            self.normalize_volume(audio),
            self.apply_fade(audio),
            # Redução de ruído apenas se SNR < threshold
            self.reduce_noise_if_needed(audio)
        )
    
    return audio
```

**Adicionar ao Plano:**
```markdown
**Monitoramento de Latência:**
- Medir impacto de cada etapa de pós-processamento
- Se latência TTS > 1.2s, desabilitar etapas menos críticas
- Documentar trade-offs (qualidade vs latência)
```

#### Ajustes Cronograma Fase 2

**Adicionar:**
- 2.6.1 Métricas objetivas: +0.5 dia
- **Total ajustado: 5.5 dias (1.1 semanas)**

---

### FASE 3: Modernização UI

#### Pontos Fortes
- Design system é fundação sólida
- Foco em UX similar a apps populares
- Acessibilidade considerada desde o início

#### Problemas Identificados

**🔴 CRÍTICO - Falta de Design Review**
```yaml
Problema: Nenhuma etapa de design review/approval
Impacto: Risco de retrabalho após implementação
Solução: Adicionar checkpoints de design
```

**Recomendação de Processo:**
```markdown
### 3.0 Design Review e Prototipação (NOVO)
**Arquivos:** `docs/design/UI_MOCKUPS.md`, `docs/design/DESIGN_DECISIONS.md`

**Implementação:**
1. Criar mockups de baixa fidelidade (Figma/Sketch)
2. Validar fluxos de usuário
3. Revisar com stakeholders
4. Criar protótipo interativo (opcional)
5. Documentar decisões de design

**Checkpoints:**
- Design aprovado antes de implementação
- Protótipo testado com usuários (se possível)
- Documentação de decisões (por que escolhemos X?)

**Estimativa:** 1 dia
```

**🟡 IMPORTANTE - Animações 60fps Pode Ser Otimista**
```yaml
Problema: "Animações a 60fps" sem testes de performance
Impacto: Dispositivos antigos podem não atingir
Solução: Animações adaptativas + fallback
```

**Recomendação:**
```dart
// mobile_app/lib/utils/adaptive_animations.dart
class AdaptiveAnimations {
  static Duration getDuration(BuildContext context) {
    // Detecta performance do dispositivo
    final isHighEnd = MediaQuery.of(context).devicePixelRatio > 2.5;
    
    return isHighEnd 
      ? DesignTokens.animationNormal  // 300ms
      : DesignTokens.animationFast;   // 200ms
  }
  
  static Curve getCurve(BuildContext context) {
    final isHighEnd = MediaQuery.of(context).devicePixelRatio > 2.5;
    
    return isHighEnd 
      ? Curves.easeInOutCubic  // Suave mas pesado
      : Curves.easeInOut;      // Mais leve
  }
  
  static bool shouldAnimate(BuildContext context) {
    // Desabilita animações se FPS < 30
    return PerformanceMonitor.currentFPS > 30;
  }
}
```

**Adicionar ao Plano:**
```markdown
#### 3.6.1 Sistema de Animações Adaptativas
**Arquivos:** `mobile_app/lib/utils/adaptive_animations.dart`

**Implementação:**
- Detectar performance do dispositivo
- Ajustar complexidade de animações automaticamente
- Fallback para animações simples se FPS < 30
- Permitir usuário desabilitar animações

**Critérios de Sucesso:**
- Animações adaptam-se ao dispositivo
- Performance mantida em dispositivos low-end
- Opção de desabilitar em configurações

**Estimativa:** +0.5 dia
```

**🟡 IMPORTANTE - Histórico de Conversas Complexo Demais**
```yaml
Problema: Muitas features (busca, delete, sync) em 2 dias
Impacto: Scope creep, difícil completar
Solução: Dividir em MVP + melhorias
```

**Recomendação - Dividir em Duas Entregas:**

**3.4a - Histórico MVP (2 dias):**
- Lista de conversas
- Preview última mensagem
- Timestamp
- Abrir conversa

**3.4b - Histórico Avançado (Fase 4, 1 dia):**
- Busca
- Delete
- Sincronização cloud (se aplicável)

**Ajustar Cronograma:**
```markdown
#### 3.4 Histórico de Conversas (MVP)
**Funcionalidades:**
- [x] Lista de conversas (ordenada por data)
- [x] Preview última mensagem
- [x] Timestamp
- [x] Abrir conversa ao tocar
- [ ] ~~Busca~~ (mover para 4.9)
- [ ] ~~Delete~~ (mover para 4.9)

**Estimativa:** 2 dias (mantido)

#### 4.9 Histórico Avançado (Novo - Fase 4)
**Funcionalidades:**
- Busca de conversas
- Delete conversas (swipe to delete)
- Sincronização cloud (se aplicável)

**Estimativa:** 1 dia
```

**🟡 IMPORTANTE - Acessibilidade Superficial**
```yaml
Problema: "Acessibilidade básica" é muito vago
Impacto: Pode não cumprir WCAG 2.1
Solução: Checklist específico + testes automatizados
```

**Recomendação:**
```markdown
#### 3.8 Acessibilidade (EXPANDIDO)
**Arquivos:** `mobile_app/test/accessibility/a11y_test.dart`

**Checklist WCAG 2.1 AA:**
- [ ] **Contraste:** Texto/background > 4.5:1 (testar com ferramentas)
- [ ] **Tamanho de toque:** Botões > 44x44 pixels
- [ ] **Labels semânticos:** Todos os widgets interativos
- [ ] **Navegação por teclado:** Tab order lógico (web)
- [ ] **Screen reader:** Testar com TalkBack/VoiceOver
- [ ] **Fonte ajustável:** Respeitar `textScaleFactor` (100%-200%)
- [ ] **Animações:** Respeitar `prefers-reduced-motion`
- [ ] **Foco visual:** Indicador claro quando navegando

**Testes Automatizados:**
```dart
// mobile_app/test/accessibility/a11y_test.dart
void main() {
  testWidgets('Contraste adequado', (tester) async {
    final theme = AppTheme.lightTheme;
    final contrast = calculateContrast(
      theme.colorScheme.primary,
      theme.colorScheme.background
    );
    expect(contrast, greaterThan(4.5));
  });
  
  testWidgets('Tamanho de toque adequado', (tester) async {
    await tester.pumpWidget(MyApp());
    final buttons = find.byType(ElevatedButton);
    for (final button in buttons.evaluate()) {
      final size = tester.getSize(button);
      expect(size.width, greaterThanOrEqualTo(44));
      expect(size.height, greaterThanOrEqualTo(44));
    }
  });
}
```

**Estimativa:** +1 dia (total 2 dias para acessibilidade completa)
```

#### Ajustes Cronograma Fase 3

**Original:** 10 dias  
**Ajustado:**
- 3.0 Design review: +1 dia
- 3.6.1 Animações adaptativas: +0.5 dia
- 3.8 Acessibilidade expandida: +1 dia
- **Total ajustado: 12.5 dias (2.5 semanas)**

---

### FASE 4: Features Adicionais

#### Pontos Fortes
- Foco em melhorias baseadas em feedback
- Tools adicionais aumentam utilidade
- Documentação final completa

#### Problemas Identificados

**🔴 CRÍTICO - Falta de Estratégia de Deploy**
```yaml
Problema: Nenhuma menção a como fazer deploy das melhorias
Impacto: Features prontas mas não em produção
Solução: Adicionar estratégia de deploy incremental
```

**Recomendação:**
```markdown
### 4.10 Estratégia de Deploy e Rollout (NOVO - CRÍTICO)
**Arquivos:** `docs/DEPLOY_STRATEGY.md`, `scripts/deploy_incremental.sh`

**Implementação:**
1. **Feature Flags:**
   - Implementar sistema de feature flags
   - Habilitar features incrementalmente
   - Rollback rápido se problemas

2. **Deploy Canário:**
   - Deploy para 10% dos usuários primeiro
   - Monitorar métricas por 24h
   - Expandir gradualmente se OK

3. **Monitoramento Pós-Deploy:**
   - Alertas para erros críticos
   - Dashboard de métricas em tempo real
   - Plano de rollback documentado

**Exemplo Feature Flag:**
```python
# backend/config/feature_flags.py
class FeatureFlags:
    def __init__(self):
        self.flags = {
            'new_tts_voice': {
                'enabled': False,
                'rollout_percentage': 0,  # 0-100
                'whitelist_users': []
            },
            'adaptive_animations': {
                'enabled': True,
                'rollout_percentage': 100
            }
        }
    
    def is_enabled(self, feature, user_id=None):
        flag = self.flags.get(feature)
        if not flag or not flag['enabled']:
            return False
        
        # Whitelist tem prioridade
        if user_id in flag.get('whitelist_users', []):
            return True
        
        # Rollout gradual
        if random.randint(0, 100) <= flag['rollout_percentage']:
            return True
        
        return False
```

**Critérios de Sucesso:**
- Feature flags implementados
- Deploy canário testado
- Rollback funciona em < 5 minutos
- Monitoramento em tempo real ativo

**Estimativa:** 2 dias
```

**🟡 IMPORTANTE - Novos Tools Sem Validação de Segurança**
```yaml
Problema: Calculator plugin usa eval() - INSEGURO
Impacto: Vulnerabilidade crítica (RCE)
Solução: Usar biblioteca segura de parsing
```

**Recomendação CRÍTICA:**
```python
# backend/plugins/calculator_plugin.py
# ❌ NUNCA FAZER ISSO:
result = eval(expression)  # VULNERÁVEL A RCE

# ✅ FAZER ISSO:
import ast
import operator

class SafeCalculator:
    """Calculadora segura que previne RCE"""
    
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def eval_expr(self, expr_string):
        """Avalia expressão matematicamente segura"""
        try:
            node = ast.parse(expr_string, mode='eval').body
            return self._eval_node(node)
        except Exception as e:
            raise ValueError(f"Expressão inválida: {e}")
    
    def _eval_node(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.OPERATORS[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            return self.OPERATORS[type(node.op)](operand)
        else:
            raise ValueError(f"Operação não suportada: {type(node)}")

# Uso:
calc = SafeCalculator()
result = calc.eval_expr("2 + 2 * 3")  # OK: 8
result = calc.eval_expr("__import__('os').system('rm -rf /')") # ERRO: operação não suportada
```

**Adicionar ao Plano:**
```markdown
#### 4.1.1 Revisão de Segurança de Plugins (NOVO - CRÍTICO)
**Arquivos:** `backend/tests/security/test_plugin_security.py`

**Implementação:**
- Revisar todos os plugins para vulnerabilidades
- Calculator: trocar eval() por parser seguro
- Currency/Weather: validar inputs, sanitizar outputs
- Adicionar rate limiting para prevenir abuse
- Testes de segurança automatizados

**Testes de Segurança:**
```python
def test_calculator_prevents_rce():
    """Previne Remote Code Execution"""
    malicious_inputs = [
        "__import__('os').system('rm -rf /')",
        "exec('print(1)')",
        "eval('2+2')",
        "open('/etc/passwd').read()",
    ]
    
    for malicious in malicious_inputs:
        with pytest.raises(ValueError):
            calculator.eval_expr(malicious)

def test_rate_limiting():
    """Previne abuse de API"""
    for i in range(100):
        result = plugin.execute("calculate", {"expression": "2+2"})
    
    # 101ª requisição deve falhar
    with pytest.raises(RateLimitExceeded):
        plugin.execute("calculate", {"expression": "2+2"})
```

**Critérios de Sucesso:**
- Zero vulnerabilidades conhecidas
- Testes de segurança passando
- Rate limiting implementado
- Inputs sanitizados

**Estimativa:** 1 dia
```

**🟡 IMPORTANTE - Cache de Buscas Pode Crescer Sem Controle**
```yaml
Problema: Cache de 50 buscas com TTL 1h
Impacto: Uso de memória pode crescer em produção
Solução: LRU cache + limite de memória
```

**Recomendação:**
```python
# backend/services/web_search_cache.py
from cachetools import LRUCache, TTLCache
import psutil

class WebSearchCache:
    def __init__(self, max_size=50, ttl=3600, max_memory_mb=100):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_bytes = 0
    
    def set(self, search_term, results):
        # Estimar tamanho do resultado
        result_size = len(str(results).encode('utf-8'))
        
        # Se exceder memória máxima, limpar cache
        if self.current_memory_bytes + result_size > self.max_memory_bytes:
            self.clear_oldest_entries()
        
        self.cache[search_term] = results
        self.current_memory_bytes += result_size
    
    def clear_oldest_entries(self):
        """Remove 25% das entradas mais antigas"""
        items = sorted(self.cache.items(), key=lambda x: x[1]['timestamp'])
        to_remove = len(items) // 4
        
        for term, _ in items[:to_remove]:
            del self.cache[term]
        
        # Recalcular memória
        self.current_memory_bytes = sum(
            len(str(v).encode('utf-8')) 
            for v in self.cache.values()
        )
```

**Adicionar ao Plano:**
```markdown
**Monitoramento de Cache:**
- Adicionar métricas de uso de memória do cache
- Alertar se memória > 80% do limite
- Documentar estratégia de eviction
```

#### Ajustes Cronograma Fase 4

**Original:** 10 dias  
**Ajustado:**
- 4.1.1 Segurança plugins: +1 dia
- 4.9 Histórico avançado: +1 dia (movido da Fase 3)
- 4.10 Estratégia deploy: +2 dias
- **Total ajustado: 14 dias (2.8 semanas)**

---

## 3. RECOMENDAÇÕES DE ARQUITETURA

### 3.1 Implementar CI/CD Desde o Início

**❌ Problema:** CI/CD só aparece como "planejado" para futuro

**✅ Solução:** Implementar pipeline básico na Fase 1

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest backend/tests --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  test-mobile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.35.4'
      - name: Run tests
        run: |
          cd mobile_app
          flutter pub get
          flutter test
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint Python
        run: |
          pip install flake8 black
          flake8 backend --max-line-length=100
          black backend --check
      - name: Lint Dart
        run: |
          cd mobile_app
          flutter analyze
```

**Adicionar ao Plano:**
```markdown
### 1.0.1 Setup de CI/CD (

    https://claude.ai/share/41ebfdd6-bfad-4b98-aa64-d2441bc31875