# Guia Completo - App Mobile Flutter

Documentação completa do aplicativo mobile do assistente Jonh.

## Índice

1. [Visão Geral](#visão-geral)
2. [Requisitos](#requisitos)
3. [Instalação](#instalação)
4. [Configuração](#configuração)
5. [Arquitetura](#arquitetura)
6. [Funcionalidades](#funcionalidades)
7. [Uso](#uso)
8. [Desenvolvimento](#desenvolvimento)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Visão Geral

O app mobile Jonh Assistant é uma interface Flutter para interagir com o assistente de voz local. Permite gravação de áudio, comunicação em tempo real via WebSocket e visualização de conversas.

### Características

- 🎨 Interface moderna Material Design 3
- 🎤 Gravação de áudio otimizada (16kHz, mono)
- 🔌 WebSocket para comunicação em tempo real
- 💬 Interface de chat intuitiva
- 🔒 Gerenciamento de permissões
- 📱 Suporte Android (iOS futuro)

## Requisitos

### Software

- **Flutter**: 3.0.0 ou superior
- **Dart**: 3.0.0 ou superior
- **Android Studio**: 2022.1+ (para desenvolvimento Android)
- **Android SDK**: API Level 21+ (Android 5.0+)

### Hardware

- **Dispositivo Android**: Android 5.0+ (API 21+)
- **Emulador**: Android Virtual Device (AVD)
- **Computador**: 8GB RAM mínimo, 16GB recomendado

### Servidor

- Backend Jonh Assistant rodando
- Rede local compartilhada entre servidor e dispositivo

## Instalação

### Passo 1: Verificar Flutter

```bash
flutter doctor
```

**Saída esperada:**
```
[✓] Flutter (Channel stable, 3.x.x)
[✓] Android toolchain
[✓] Android Studio
```

Se houver problemas, siga: https://docs.flutter.dev/get-started/install

### Passo 2: Clonar Projeto

```bash
cd mobile_app
```

### Passo 3: Instalar Dependências

```bash
flutter pub get
```

**Dependências principais:**
- `record`: Gravação de áudio
- `just_audio`: Reprodução de áudio
- `web_socket_channel`: WebSocket
- `permission_handler`: Permissões
- `provider`: State management

### Passo 4: Verificar Dispositivos

```bash
flutter devices
```

**Opções:**
- Dispositivo físico conectado via USB
- Emulador Android (AVD)
- Chrome (para testes web)

## Configuração

### 1. Configurar IP do Servidor

O app precisa saber onde está o backend. Edite:

**Arquivo:** `lib/services/api_service.dart`

```dart
class ApiService extends ChangeNotifier {
  // Mude para o IP da sua máquina na rede local
  static const String baseUrl = 'http://192.168.1.100:8000';
  static const String wsUrl = 'ws://192.168.1.100:8000/ws/listen';
  // ...
}
```

#### Como descobrir seu IP:

**Linux/WSL:**
```bash
ip addr show | grep inet
# ou
hostname -I
```

**Windows:**
```cmd
ipconfig
```

Procure por `inet` ou `IPv4 Address` na interface de rede ativa (geralmente `eth0` ou `wlan0`).

**Exemplo:** Se seu IP é `192.168.1.50`, use:
```dart
static const String baseUrl = 'http://192.168.1.50:8000';
static const String wsUrl = 'ws://192.168.1.50:8000/ws/listen';
```

### 2. Configurar Permissões (Já configurado)

O arquivo `android/app/src/main/AndroidManifest.xml` já contém:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

### 3. Configurar Rede (Importante!)

**Firewall no servidor:**
```bash
# Permitir porta 8000
sudo ufw allow 8000/tcp
```

**Testar conectividade:**
```bash
# Do celular, use um app de terminal ou navegador
# Acesse: http://SEU_IP:8000/health
```

## Arquitetura

### Estrutura de Diretórios

```
mobile_app/
├── lib/
│   ├── main.dart                 # Entry point
│   ├── models/                   # Modelos de dados
│   │   └── message.dart          # Modelo de mensagem
│   ├── screens/                  # Telas
│   │   └── home_screen.dart      # Tela principal
│   ├── services/                 # Lógica de negócio
│   │   ├── api_service.dart      # Comunicação API
│   │   └── audio_service.dart    # Áudio
│   └── widgets/                  # Componentes reutilizáveis
│       ├── message_list.dart     # Lista de mensagens
│       └── voice_button.dart     # Botão de voz
├── android/                      # Configuração Android
├── ios/                          # Configuração iOS (futuro)
├── test/                         # Testes
└── pubspec.yaml                  # Dependências
```

### Padrão de Arquitetura

**Provider Pattern** para gerenciamento de estado:

```
UI (Widgets)
    ↓
Consumer/Provider
    ↓
Services (Business Logic)
    ↓
Models (Data)
```

### Fluxo de Dados

```
1. Usuário toca botão → VoiceButton
2. VoiceButton → AudioService.startRecording()
3. AudioService grava áudio
4. Usuário solta botão → AudioService.stopRecording()
5. AudioService retorna bytes → ApiService.sendAudio()
6. ApiService envia via WebSocket
7. Servidor processa
8. ApiService recebe resposta
9. ApiService atualiza messages
10. MessageList renderiza nova mensagem
```

## Funcionalidades

### 1. Gravação de Áudio

**Configuração:**
- Sample rate: 16kHz
- Canais: Mono
- Formato: WAV
- Encoder: PCM

**Uso:**
```dart
final audioService = context.read<AudioService>();

// Iniciar
await audioService.startRecording();

// Parar e obter bytes
final bytes = await audioService.stopRecording();
```

### 2. WebSocket

**Protocolo de mensagens:**

**Cliente → Servidor:**
```json
// Controle
{"type": "start_session"}
{"type": "end_session"}
{"type": "ping"}

// Dados
<audio_bytes>
```

**Servidor → Cliente:**
```json
{"type": "session_started", "session_id": "uuid"}
{"type": "transcription", "text": "olá", "confidence": 0.95}
{"type": "response", "text": "Olá! Como posso ajudar?", "tokens": 15}
{"type": "processing", "stage": "transcribing"}
{"type": "error", "message": "erro"}
<audio_bytes>
```

### 3. Interface de Chat

**Tipos de mensagem:**
- `user`: Mensagens do usuário (direita, azul)
- `assistant`: Respostas do Jonh (esquerda, cinza)
- `system`: Notificações (centro, chip)
- `error`: Erros (esquerda, vermelho)

### 4. Gerenciamento de Estado

**ApiService:**
- Conexão WebSocket
- Sessões
- Histórico de mensagens

**AudioService:**
- Gravação
- Reprodução
- Permissões

## Uso

### Primeira Execução

**1. Inicie o servidor backend:**
```bash
cd <project-root>
python3 backend/api/main.py
```

**2. Execute o app:**
```bash
cd mobile_app
flutter run
```

**3. No app:**
- Permita acesso ao microfone
- Toque no ícone de nuvem (canto superior direito)
- Status deve mudar para verde

### Conversação

**Método 1: Toque e Segure**
1. Toque e segure o botão do microfone
2. Fale sua pergunta
3. Solte o botão
4. Aguarde resposta

**Método 2: Toque Único**
1. Toque o botão (inicia gravação)
2. Fale sua pergunta
3. Toque novamente (para e envia)

### Indicadores de Status

**Barra superior:**
- 🟢 API: Conectado ao servidor
- 🟢 Microfone: Permissão concedida
- 🟢 Gravando: Gravação ativa

**Botão de voz:**
- 🔵 Normal: Pronto para gravar
- 🔴 Pulsando: Gravando
- ⚪ Cinza: Sem permissão

## Desenvolvimento

### Executar em Modo Debug

```bash
flutter run --debug
```

**Hot Reload:** Pressione `r` no terminal
**Hot Restart:** Pressione `R` no terminal
**Quit:** Pressione `q` no terminal

### Executar em Modo Release

```bash
flutter run --release
```

**Diferenças:**
- Mais rápido
- Menor tamanho
- Sem debug info
- Otimizado

### Build APK

```bash
flutter build apk --release
```

**Saída:** `build/app/outputs/flutter-apk/app-release.apk`

**Instalar:**
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Logs

**Ver logs em tempo real:**
```bash
flutter logs
```

**Filtrar logs:**
```bash
flutter logs | grep "ApiService"
```

### Testes

**Executar todos os testes:**
```bash
flutter test
```

**Teste específico:**
```bash
flutter test test/services/api_service_test.dart
```

### Adicionar Dependência

**1. Edite `pubspec.yaml`:**
```yaml
dependencies:
  nova_lib: ^1.0.0
```

**2. Instale:**
```bash
flutter pub get
```

**3. Importe:**
```dart
import 'package:nova_lib/nova_lib.dart';
```

## Troubleshooting

### Problema: "Não conecta ao servidor"

**Sintomas:**
- Ícone de nuvem vermelho
- Mensagem "Não foi possível conectar"

**Soluções:**
1. Verifique se servidor está rodando: `curl http://localhost:8000/health`
2. Confirme IP correto no código
3. Teste conectividade: `ping SEU_IP`
4. Verifique firewall: `sudo ufw status`
5. Use IP da rede local, não `localhost` ou `127.0.0.1`

### Problema: "Permissão de microfone negada"

**Sintomas:**
- Botão cinza
- Erro ao gravar

**Soluções:**
1. Configurações > Apps > Jonh Assistant > Permissões > Microfone
2. Desinstale e reinstale o app
3. Verifique `AndroidManifest.xml`

### Problema: "WebSocket fecha imediatamente"

**Sintomas:**
- Conecta e desconecta rapidamente
- Logs mostram "WebSocket closed"

**Soluções:**
1. Verifique logs do servidor
2. Confirme URL do WebSocket (deve começar com `ws://`)
3. Teste WebSocket com ferramenta online
4. Verifique se servidor aceita conexões externas

### Problema: "Build falha"

**Sintomas:**
- Erro ao executar `flutter run`
- Dependências não resolvem

**Soluções:**
```bash
flutter clean
flutter pub get
flutter pub upgrade
flutter run
```

### Problema: "App lento"

**Soluções:**
1. Execute em modo release: `flutter run --release`
2. Verifique logs por erros
3. Reduza animações
4. Otimize lista de mensagens (use `ListView.builder`)

### Problema: "Áudio não grava"

**Sintomas:**
- Botão não responde
- Sem erro visível

**Soluções:**
1. Verifique permissões
2. Teste em dispositivo físico (emulador pode ter problemas)
3. Verifique logs: `flutter logs | grep "AudioService"`
4. Reinicie app

## FAQ

### O app funciona offline?

Não. O app precisa de conexão com o servidor backend para processar áudio e gerar respostas.

### Posso usar em iOS?

Atualmente apenas Android está configurado. iOS requer:
- Configuração de permissões em `Info.plist`
- Ajustes específicos de iOS
- Conta de desenvolvedor Apple (para dispositivo físico)

### Como adicionar wake word?

Requer integração com Porcupine (Picovoice):
1. Crie conta em https://console.picovoice.ai/
2. Adicione `picovoice_flutter` ao `pubspec.yaml`
3. Treine modelo customizado para "Jonh"
4. Implemente serviço de wake word
5. Execute em background

### Posso mudar o design?

Sim! Edite:
- `lib/main.dart`: Tema geral
- `lib/widgets/*.dart`: Componentes individuais
- Cores, fontes, espaçamentos são customizáveis

### Como adicionar mais idiomas?

1. Configure Whisper para detectar idioma
2. Ajuste prompts do LLM
3. Use vozes TTS apropriadas
4. Implemente seleção de idioma no app

### O app consome muita bateria?

**Consumo normal:**
- Idle: Baixo (~2-5%)
- Gravando: Médio (~10-15%)
- Wake word ativo: Médio (~5-10%)

**Otimizações:**
- Desconecte WebSocket quando não usar
- Desative wake word quando não necessário
- Use modo de economia de energia

### Posso gravar conversas?

Sim, mas requer:
1. Salvar mensagens em banco local (SQLite)
2. Armazenar áudios (opcional)
3. Implementar tela de histórico
4. Respeitar LGPD/privacidade

### Como atualizar o app?

**Desenvolvimento:**
```bash
git pull
cd mobile_app
flutter pub get
flutter run
```

**Produção:**
- Gere novo APK
- Distribua via Play Store ou sideload

### Preciso de conta Google?

Não para desenvolvimento. Sim para:
- Publicar na Play Store
- Usar serviços Google (Analytics, etc)
- Notificações push (Firebase)

## Recursos Adicionais

### Documentação Oficial

- Flutter: https://docs.flutter.dev/
- Dart: https://dart.dev/guides
- Provider: https://pub.dev/packages/provider
- Record: https://pub.dev/packages/record

### Tutoriais

- Flutter Codelabs: https://docs.flutter.dev/codelabs
- Flutter YouTube: https://www.youtube.com/@flutterdev
- Dart Pad (playground): https://dartpad.dev/

### Comunidade

- Flutter Discord: https://discord.gg/flutter
- Stack Overflow: Tag `flutter`
- Reddit: r/FlutterDev

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'feat: Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra Pull Request

## Licença

MIT License - veja LICENSE para detalhes

---

**Desenvolvido com ❤️ para o Projeto Jonh Assistant**

