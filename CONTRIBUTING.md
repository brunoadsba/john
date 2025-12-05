# Guia de Contribuição

Obrigado por considerar contribuir com o Jonh Assistant! 🎉

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

## Como Contribuir

### Reportar Bugs

**Antes de reportar:**
1. Verifique se já não existe issue similar
2. Use a versão mais recente do código
3. Teste em ambiente limpo

**Ao reportar, inclua:**
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots/logs (se aplicável)
- Ambiente (OS, versões, hardware)

**Template:**
```markdown
## Descrição
[Descrição clara do bug]

## Passos para Reproduzir
1. ...
2. ...
3. ...

## Comportamento Esperado
[O que deveria acontecer]

## Comportamento Atual
[O que está acontecendo]

## Ambiente
- OS: Ubuntu 22.04
- Python: 3.10.12
- Flutter: 3.16.0
- Hardware: i7 12ª gen, 32GB RAM
```

### Sugerir Features

**Antes de sugerir:**
1. Verifique roadmap e issues existentes
2. Considere se alinha com objetivos do projeto

**Ao sugerir, inclua:**
- Problema que resolve
- Solução proposta
- Alternativas consideradas
- Impacto esperado

### Pull Requests

#### Workflow

1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie branch** a partir de `master`
4. **Faça mudanças**
5. **Teste** suas mudanças
6. **Commit** com mensagem descritiva
7. **Push** para seu fork
8. **Abra PR** para `master`

#### Branches

**Nomenclatura:**
- `feature/nome-da-feature` - Novas funcionalidades
- `fix/nome-do-bug` - Correções
- `docs/descricao` - Documentação
- `refactor/descricao` - Refatoração
- `test/descricao` - Testes

**Exemplos:**
```bash
git checkout -b feature/wake-word-detection
git checkout -b fix/websocket-reconnection
git checkout -b docs/api-endpoints
```

#### Commits

**Formato:** [Conventional Commits](https://www.conventionalcommits.org/)

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (sem mudança de código)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

**Exemplos:**
```bash
git commit -m "feat(mobile): adiciona wake word detection"
git commit -m "fix(api): corrige timeout em websocket"
git commit -m "docs(readme): atualiza instruções de instalação"
git commit -m "refactor(services): simplifica lógica de contexto"
```

#### Código

**Python:**
- Siga PEP 8
- Use type hints
- Docstrings em funções públicas
- Máximo 88 caracteres por linha (Black)

**Dart/Flutter:**
- Siga Effective Dart
- Use `flutter format`
- Documente widgets públicos
- Prefira const constructors

**Geral:**
- Nomes descritivos
- Funções pequenas e focadas
- Evite duplicação (DRY)
- Comentários quando necessário

#### Testes

**Obrigatório para:**
- Novas funcionalidades
- Correções de bugs
- Mudanças em lógica crítica

**Python:**
```python
def test_llm_service_response():
    service = OllamaLLMService()
    response, tokens = service.generate_response("teste")
    assert response is not None
    assert tokens > 0
```

**Flutter:**
```dart
testWidgets('VoiceButton shows mic icon', (tester) async {
  await tester.pumpWidget(MyApp());
  expect(find.byIcon(Icons.mic), findsOneWidget);
});
```

#### Documentação

**Atualize se mudar:**
- API endpoints
- Configurações
- Dependências
- Comportamento público

**Arquivos:**
- `README.md` - Overview
- `docs/API.md` - Documentação API
- `docs/MOBILE_APP.md` - Guia mobile
- `docs/ARQUITETURA.md` - Arquitetura

#### Review

**Checklist antes de abrir PR:**
- [ ] Código segue style guide
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Sem conflitos com master
- [ ] Commits bem formatados
- [ ] PR tem descrição clara

**Template de PR:**
```markdown
## Descrição
[Descrição das mudanças]

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. ...
2. ...

## Checklist
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Código formatado
```

## Estrutura do Projeto

```
john/
├── backend/          # API Python/FastAPI
├── mobile_app/       # App Flutter
├── docs/            # Documentação
├── scripts/         # Scripts utilitários
└── Doc/             # Documentos de design
```

## Configuração de Desenvolvimento

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Se existir
```

### Mobile

```bash
cd mobile_app
flutter pub get
flutter analyze
flutter test
```

### Pre-commit Hooks (Recomendado)

```bash
# Instale pre-commit
pip install pre-commit

# Configure
pre-commit install

# Hooks executarão automaticamente em cada commit
```

## Padrões de Código

### Python

**Imports:**
```python
# Standard library
import os
import sys

# Third party
from fastapi import FastAPI
import ollama

# Local
from backend.services import ApiService
```

**Type Hints:**
```python
def process_audio(
    audio_data: bytes,
    session_id: Optional[str] = None
) -> tuple[str, int]:
    ...
```

**Docstrings:**
```python
def generate_response(prompt: str) -> str:
    """
    Gera resposta usando LLM.
    
    Args:
        prompt: Texto da pergunta
        
    Returns:
        Resposta gerada
        
    Raises:
        RuntimeError: Se LLM não disponível
    """
    ...
```

### Dart/Flutter

**Imports:**
```dart
// Dart SDK
import 'dart:async';

// Flutter
import 'package:flutter/material.dart';

// Packages
import 'package:provider/provider.dart';

// Local
import '../services/api_service.dart';
```

**Widgets:**
```dart
/// Botão de gravação de voz
class VoiceButton extends StatelessWidget {
  /// Cria um [VoiceButton]
  const VoiceButton({super.key});
  
  @override
  Widget build(BuildContext context) {
    ...
  }
}
```

## Ferramentas Úteis

### Backend

- **Black**: Formatação de código
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testes

```bash
black backend/
flake8 backend/
mypy backend/
pytest backend/tests/
```

### Mobile

- **Flutter Analyze**: Análise estática
- **Flutter Format**: Formatação
- **Flutter Test**: Testes

```bash
flutter analyze
flutter format lib/
flutter test
```

## Perguntas?

- Abra uma issue com label `question`
- Entre em contato via [email/discord]
- Consulte documentação em `docs/`

## Agradecimentos

Contribuidores são reconhecidos em:
- README.md
- CONTRIBUTORS.md (se existir)
- Release notes

Obrigado por contribuir! 🚀
