# Wake Word Detection - Guia Completo

Implementação de detecção de palavra de ativação "Jonh" usando Porcupine (Picovoice).

## Visão Geral

Wake word detection permite que o assistente seja ativado por voz, sem necessidade de tocar botões. O usuário simplesmente diz "Jonh" e o app inicia automaticamente a gravação.

### Características

- ✅ Detecção local (no dispositivo)
- ✅ Baixo consumo de bateria (~5%)
- ✅ Sempre ativo em background
- ✅ Palavra customizável
- ✅ Alta precisão (>95%)

## Tecnologia: Porcupine (Picovoice)

### Por que Porcupine?

**Vantagens:**
- Processamento on-device (privacidade)
- Baixíssima latência (<100ms)
- Modelos customizáveis
- Plano gratuito generoso
- Excelente integração Flutter

**Alternativas consideradas:**
- Snowboy (descontinuado)
- OpenWakeWord (complexo de integrar)
- Tensorflow Lite (requer treinamento próprio)

## Passo a Passo

### 1. Criar Conta Picovoice

**Acesse:** https://console.picovoice.ai/

1. Clique em "Sign Up"
2. Use Google ou email
3. Confirme email
4. Faça login

### 2. Obter Access Key

1. No console, vá em "Access Keys"
2. Copie sua chave (começa com `pv_...`)
3. **Guarde em local seguro!**

### 3. Treinar Modelo Customizado

#### Opção A: Usar Palavra Padrão

Porcupine já tem palavras pré-treinadas:
- "Jarvis"
- "Computer"
- "Alexa"
- "Hey Google"

Para usar uma dessas, pule para passo 4.

#### Opção B: Treinar "Jonh" (Recomendado)

**No console Picovoice:**

1. Vá em "Porcupine" → "Train"
2. Clique em "New Wake Word"
3. Digite "Jonh"
4. Selecione idioma: "Portuguese (Brazil)"
5. Clique em "Train"
6. Aguarde 5-10 minutos
7. Baixe o arquivo `.ppn`

**Resultado:** `jonh_pt_br_android_v3_0_0.ppn`

### 4. Configurar Projeto Flutter

#### 4.1. Adicionar Dependência

**Edite `pubspec.yaml`:**

```yaml
dependencies:
  picovoice_flutter: ^3.0.0
```

**Instale:**
```bash
flutter pub get
```

#### 4.2. Adicionar Modelo

**Crie diretório:**
```bash
mkdir -p mobile_app/assets/wake_words
```

**Copie arquivo `.ppn`:**
```bash
cp ~/Downloads/jonh_pt_br_android_v3_0_0.ppn mobile_app/assets/wake_words/jonh.ppn
```

**Atualize `pubspec.yaml`:**
```yaml
flutter:
  assets:
    - assets/wake_words/jonh.ppn
```

#### 4.3. Configurar Permissões

**Android** (`android/app/src/main/AndroidManifest.xml`):

```xml
<!-- Já configurado -->
<uses-permission android:name="android.permission.RECORD_AUDIO" />

<!-- Adicione se quiser wake word em background -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

<!-- Service do Porcupine -->
<service 
    android:name="ai.picovoice.flutter.porcupine.PorcupineService"
    android:exported="false" />
```

**iOS** (`ios/Runner/Info.plist`):

```xml
<key>NSMicrophoneUsageDescription</key>
<string>Necessário para detectar palavra de ativação "Jonh"</string>

<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

### 5. Implementar no App

#### 5.1. Atualizar WakeWordService

**Edite `lib/services/wake_word_service.dart`:**

```dart
import 'package:flutter/foundation.dart';
import 'package:picovoice_flutter/picovoice.dart';
import 'package:picovoice_flutter/picovoice_manager.dart';
import 'package:picovoice_flutter/picovoice_error.dart';

class WakeWordService extends ChangeNotifier {
  PorcupineManager? _porcupineManager;
  bool _isListening = false;
  bool _isEnabled = false;
  
  bool get isListening => _isListening;
  bool get isEnabled => _isEnabled;
  
  Function()? onWakeWordDetected;
  
  Future<void> initialize({required String accessKey}) async {
    try {
      _porcupineManager = await PorcupineManager.fromKeywordPaths(
        accessKey,
        ['assets/wake_words/jonh.ppn'],
        _wakeWordCallback,
        errorCallback: _errorCallback,
      );
      
      _isEnabled = true;
      notifyListeners();
      
      debugPrint('WakeWordService: Inicializado com sucesso');
    } on PorcupineException catch (e) {
      debugPrint('Erro ao inicializar Porcupine: ${e.message}');
      _isEnabled = false;
      notifyListeners();
    }
  }
  
  Future<void> startListening() async {
    if (!_isEnabled || _porcupineManager == null) return;
    
    try {
      await _porcupineManager!.start();
      _isListening = true;
      notifyListeners();
      
      debugPrint('WakeWordService: Escutando "Jonh"');
    } on PorcupineException catch (e) {
      debugPrint('Erro ao iniciar: ${e.message}');
    }
  }
  
  Future<void> stopListening() async {
    if (!_isListening || _porcupineManager == null) return;
    
    try {
      await _porcupineManager!.stop();
      _isListening = false;
      notifyListeners();
      
      debugPrint('WakeWordService: Parou de escutar');
    } on PorcupineException catch (e) {
      debugPrint('Erro ao parar: ${e.message}');
    }
  }
  
  void _wakeWordCallback(int keywordIndex) {
    debugPrint('WakeWordService: "Jonh" detectado!');
    
    if (onWakeWordDetected != null) {
      onWakeWordDetected!();
    }
  }
  
  void _errorCallback(PorcupineException error) {
    debugPrint('Erro no wake word: ${error.message}');
  }
  
  @override
  void dispose() {
    _porcupineManager?.delete();
    super.dispose();
  }
}
```

#### 5.2. Integrar no App

**Edite `lib/main.dart`:**

```dart
import 'services/wake_word_service.dart';

class JonhAssistantApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ApiService()),
        ChangeNotifierProvider(create: (_) => AudioService()),
        ChangeNotifierProvider(create: (_) => WakeWordService()), // Adicione
      ],
      child: MaterialApp(
        // ...
      ),
    );
  }
}
```

**Edite `lib/screens/home_screen.dart`:**

```dart
@override
void initState() {
  super.initState();
  _initialize();
}

Future<void> _initialize() async {
  final apiService = context.read<ApiService>();
  final audioService = context.read<AudioService>();
  final wakeWordService = context.read<WakeWordService>();
  
  // Inicializa wake word
  await wakeWordService.initialize(
    accessKey: 'SUA_ACCESS_KEY_AQUI', // TODO: Mover para .env
  );
  
  // Configura callback
  wakeWordService.onWakeWordDetected = () {
    _onWakeWordDetected();
  };
  
  // Inicia escuta
  if (wakeWordService.isEnabled) {
    await wakeWordService.startListening();
  }
  
  // ... resto do código
}

void _onWakeWordDetected() async {
  final audioService = context.read<AudioService>();
  final apiService = context.read<ApiService>();
  
  // Feedback sonoro (opcional)
  // await audioService.playBeep();
  
  // Conecta se necessário
  if (!apiService.isConnected) {
    await apiService.connect();
    apiService.startSession();
  }
  
  // Inicia gravação automaticamente
  await audioService.startRecording();
  
  // Para após 5 segundos (ou detectar silêncio)
  await Future.delayed(Duration(seconds: 5));
  final audioBytes = await audioService.stopRecording();
  
  if (audioBytes != null) {
    await apiService.sendAudio(audioBytes);
  }
}
```

### 6. Configurar Access Key

**Opção A: Hardcoded (desenvolvimento)**

```dart
await wakeWordService.initialize(
  accessKey: 'pv_SEU_ACCESS_KEY_AQUI',
);
```

**Opção B: Variável de ambiente (produção)**

1. Crie `lib/config/env.dart`:
```dart
class Env {
  static const picovoiceAccessKey = String.fromEnvironment(
    'PICOVOICE_ACCESS_KEY',
    defaultValue: '',
  );
}
```

2. Execute com:
```bash
flutter run --dart-define=PICOVOICE_ACCESS_KEY=pv_sua_key
```

3. Use:
```dart
await wakeWordService.initialize(
  accessKey: Env.picovoiceAccessKey,
);
```

### 7. Testar

**1. Execute o app:**
```bash
flutter run
```

**2. Verifique logs:**
```
WakeWordService: Inicializado com sucesso
WakeWordService: Escutando "Jonh"
```

**3. Diga "Jonh"**

**4. Deve aparecer:**
```
WakeWordService: "Jonh" detectado!
```

## Uso

### Fluxo Completo

```
1. App inicia
   ↓
2. WakeWordService inicializa
   ↓
3. Porcupine começa a escutar
   ↓
4. Usuário diz "Jonh"
   ↓
5. Callback é chamado
   ↓
6. App inicia gravação
   ↓
7. Usuário fala pergunta
   ↓
8. App envia para backend
   ↓
9. Resposta é reproduzida
   ↓
10. Volta a escutar "Jonh"
```

### Estados do Wake Word

- **Disabled**: Não inicializado ou erro
- **Listening**: Escutando palavra
- **Detected**: Palavra detectada (transitório)

## Otimizações

### Consumo de Bateria

**Porcupine é otimizado**, mas você pode:

1. **Pausar em background:**
```dart
@override
void didChangeAppLifecycleState(AppLifecycleState state) {
  if (state == AppLifecycleState.paused) {
    wakeWordService.stopListening();
  } else if (state == AppLifecycleState.resumed) {
    wakeWordService.startListening();
  }
}
```

2. **Desativar à noite:**
```dart
final now = DateTime.now();
if (now.hour >= 23 || now.hour < 7) {
  await wakeWordService.stopListening();
}
```

3. **Modo economia:**
```dart
// Usuário pode desativar nas configurações
if (settings.wakeWordEnabled) {
  await wakeWordService.startListening();
}
```

### Precisão

**Melhorar detecção:**

1. **Sensibilidade:**
```dart
_porcupineManager = await PorcupineManager.fromKeywordPaths(
  accessKey,
  ['assets/wake_words/jonh.ppn'],
  _wakeWordCallback,
  sensitivities: [0.7], // 0.0 a 1.0 (padrão: 0.5)
);
```

- `0.3`: Menos sensível (menos falsos positivos)
- `0.5`: Balanceado
- `0.7`: Mais sensível (detecta mais facilmente)

2. **Treinar com mais amostras:**
- Grave "Jonh" em diferentes tons
- Use sotaques variados
- Retreine modelo no console Picovoice

## Troubleshooting

### Erro: "Invalid access key"

**Solução:**
- Verifique se copiou a key completa
- Key deve começar com `pv_`
- Gere nova key no console

### Erro: "Failed to load model"

**Solução:**
- Verifique caminho do arquivo `.ppn`
- Confirme que está em `assets/wake_words/`
- Verifique `pubspec.yaml` tem o asset

### Não detecta "Jonh"

**Soluções:**
1. Aumente sensibilidade
2. Fale mais alto/claro
3. Verifique se microfone funciona
4. Teste em ambiente silencioso
5. Retreine modelo

### Muitos falsos positivos

**Soluções:**
1. Reduza sensibilidade
2. Retreine modelo com mais amostras
3. Use palavra mais única

### Consumo alto de bateria

**Soluções:**
1. Pause em background
2. Use sensibilidade menor
3. Desative quando não necessário

## Limites do Plano Gratuito

**Picovoice Free Tier:**
- Dispositivos: Ilimitados
- Detecções: Ilimitadas
- Modelos customizados: 3
- Suporte: Comunidade

**Para uso pessoal é suficiente!**

## Alternativas

Se não quiser usar Porcupine:

### 1. Botão Manual

Já implementado - usuário toca botão para gravar.

### 2. Sempre Escutando

App sempre grava e envia para backend detectar palavra.

**Contras:**
- Alto consumo de bateria
- Alto uso de dados
- Privacidade comprometida

### 3. Google Assistant Integration

Integrar com Google Assistant nativo.

**Contras:**
- Requer Google Services
- Menos controle
- Não é 100% local

## Próximos Passos

1. **Implementar feedback visual** quando detectar
2. **Adicionar configurações** de sensibilidade
3. **Estatísticas** de detecções
4. **Múltiplas palavras** de ativação
5. **Comandos por voz** (além de conversação)

## Recursos

- **Picovoice Console**: https://console.picovoice.ai/
- **Documentação**: https://picovoice.ai/docs/
- **Flutter Package**: https://pub.dev/packages/picovoice_flutter
- **Suporte**: https://github.com/Picovoice/porcupine

---

**Wake word detection transforma o Jonh em um verdadeiro assistente mãos-livres!** 🎤

