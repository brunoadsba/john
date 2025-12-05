# Jonh Assistant - Mobile App

App Flutter para o assistente de voz Jonh.

## Funcionalidades

- ✅ Interface de conversação
- ✅ Gravação de áudio
- ✅ Comunicação WebSocket com backend
- ✅ Gerenciamento de sessões
- ⏳ Wake word detection (futuro)
- ⏳ Reprodução de áudio TTS (futuro)

## Requisitos

- Flutter 3.0+
- Android SDK 21+ (Android 5.0+)
- Servidor Jonh Assistant rodando

## Instalação

### 1. Instalar dependências

```bash
cd mobile_app
flutter pub get
```

### 2. Configurar servidor

Edite `lib/services/api_service.dart` e ajuste as URLs:

```dart
static const String baseUrl = 'http://SEU_IP:8000';
static const String wsUrl = 'ws://SEU_IP:8000/ws/listen';
```

**Nota**: Use o IP da sua máquina na rede local, não `localhost`.

### 3. Executar

```bash
# Conecte um dispositivo Android ou inicie um emulador
flutter devices

# Execute o app
flutter run
```

## Estrutura do Projeto

```
lib/
├── main.dart                 # Entrada do app
├── models/
│   └── message.dart          # Modelo de mensagem
├── screens/
│   └── home_screen.dart      # Tela principal
├── services/
│   ├── api_service.dart      # Comunicação com API
│   └── audio_service.dart    # Gravação/reprodução
└── widgets/
    ├── message_list.dart     # Lista de mensagens
    └── voice_button.dart     # Botão de gravação
```

## Uso

1. **Inicie o servidor backend**
2. **Abra o app**
3. **Toque no ícone de nuvem** para conectar ao servidor
4. **Toque e segure o botão do microfone** para gravar
5. **Solte para enviar** o áudio

## Permissões

O app solicita:
- **Microfone**: Para gravação de voz
- **Internet**: Para comunicação com servidor

## Desenvolvimento

### Adicionar nova tela

```dart
// lib/screens/nova_tela.dart
import 'package:flutter/material.dart';

class NovaTela extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Nova Tela')),
      body: Center(child: Text('Conteúdo')),
    );
  }
}
```

### Adicionar novo serviço

```dart
// lib/services/novo_service.dart
import 'package:flutter/foundation.dart';

class NovoService extends ChangeNotifier {
  // Implementação
}
```

## Troubleshooting

### Erro de conexão

- Verifique se o servidor está rodando
- Use IP da rede local, não localhost
- Verifique firewall

### Permissão de microfone negada

- Vá em Configurações > Apps > Jonh Assistant > Permissões
- Ative "Microfone"

### Build falha

```bash
flutter clean
flutter pub get
flutter run
```

## Próximos Passos

- [ ] Implementar wake word detection (Porcupine)
- [ ] Reprodução de áudio TTS
- [ ] Configurações do app
- [ ] Temas claro/escuro
- [ ] Histórico de conversas
- [ ] Notificações

## Licença

MIT

