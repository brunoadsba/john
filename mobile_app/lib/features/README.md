# Features - Arquitetura Feature-Based

Este diretório contém todas as features do app organizadas por domínio.

## Estrutura

Cada feature segue a estrutura:

```
feature_name/
├── components/     # Widgets específicos da feature
├── controllers/    # Lógica de negócio e handlers
├── services/       # Serviços específicos (se necessário)
├── models/        # Modelos de dados (se necessário)
└── index.dart     # Barrel export (facilita imports)
```

## Features

- **voice** - Gravação, reprodução e processamento de áudio
- **wake_word** - Detecção de wake word (backend e local)
- **home** - Tela principal e orquestração
- **settings** - Configurações do app
- **messages** - Lista e gerenciamento de mensagens

## Princípios

- Cada feature é autocontida
- Imports entre features devem ser mínimos
- Serviços globais ficam em `lib/services/`
- Componentes globais ficam em `lib/widgets/`
