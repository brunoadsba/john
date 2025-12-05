import 'package:flutter/foundation.dart';

/// Serviço de detecção de wake word
/// 
/// Para usar Porcupine (Picovoice):
/// 1. Crie conta em https://console.picovoice.ai/
/// 2. Adicione picovoice_flutter ao pubspec.yaml
/// 3. Treine modelo customizado para "Jonh"
/// 4. Configure access key
class WakeWordService extends ChangeNotifier {
  bool _isListening = false;
  bool _isEnabled = false;
  
  bool get isListening => _isListening;
  bool get isEnabled => _isEnabled;
  
  // Callback quando wake word é detectado
  Function()? onWakeWordDetected;
  
  /// Inicializa o serviço
  Future<void> initialize({String? accessKey}) async {
    try {
      // TODO: Implementar com Porcupine quando configurado
      // final porcupineManager = await PorcupineManager.fromKeywords(
      //   accessKey,
      //   ['jonh'],
      //   _wakeWordCallback,
      // );
      
      _isEnabled = false; // Mude para true quando implementar
      notifyListeners();
      
      debugPrint('WakeWordService: Inicializado (mock)');
    } catch (e) {
      debugPrint('Erro ao inicializar wake word: $e');
      _isEnabled = false;
      notifyListeners();
    }
  }
  
  /// Inicia escuta de wake word
  Future<void> startListening() async {
    if (!_isEnabled) {
      debugPrint('WakeWordService: Não habilitado');
      return;
    }
    
    try {
      // TODO: Iniciar Porcupine
      // await _porcupineManager?.start();
      
      _isListening = true;
      notifyListeners();
      
      debugPrint('WakeWordService: Escutando wake word');
    } catch (e) {
      debugPrint('Erro ao iniciar escuta: $e');
      _isListening = false;
      notifyListeners();
    }
  }
  
  /// Para escuta de wake word
  Future<void> stopListening() async {
    if (!_isListening) return;
    
    try {
      // TODO: Parar Porcupine
      // await _porcupineManager?.stop();
      
      _isListening = false;
      notifyListeners();
      
      debugPrint('WakeWordService: Parou de escutar');
    } catch (e) {
      debugPrint('Erro ao parar escuta: $e');
    }
  }
  
  /// Callback quando wake word é detectado
  void _wakeWordCallback(int keywordIndex) {
    debugPrint('WakeWordService: Wake word detectado!');
    
    if (onWakeWordDetected != null) {
      onWakeWordDetected!();
    }
  }
  
  @override
  void dispose() {
    stopListening();
    // TODO: Dispose Porcupine
    // _porcupineManager?.delete();
    super.dispose();
  }
}

/// Implementação futura com Porcupine
/// 
/// Exemplo de uso:
/// ```dart
/// final wakeWordService = WakeWordService();
/// 
/// await wakeWordService.initialize(
///   accessKey: 'YOUR_PICOVOICE_ACCESS_KEY',
/// );
/// 
/// wakeWordService.onWakeWordDetected = () {
///   print('Jonh detectado!');
///   // Iniciar gravação
/// };
/// 
/// await wakeWordService.startListening();
/// ```
/// 
/// Configuração necessária:
/// 
/// 1. pubspec.yaml:
/// ```yaml
/// dependencies:
///   picovoice_flutter: ^3.0.0
/// ```
/// 
/// 2. Android (android/app/src/main/AndroidManifest.xml):
/// ```xml
/// <uses-permission android:name="android.permission.RECORD_AUDIO" />
/// <service android:name="ai.picovoice.flutter.picovoice.PicovoiceService" />
/// ```
/// 
/// 3. iOS (ios/Runner/Info.plist):
/// ```xml
/// <key>NSMicrophoneUsageDescription</key>
/// <string>Para detectar wake word</string>
/// ```
/// 
/// 4. Treinar modelo customizado:
/// - Acesse https://console.picovoice.ai/
/// - Crie projeto
/// - Treine modelo para palavra "Jonh"
/// - Baixe arquivo .ppn
/// - Adicione em assets/wake_words/jonh.ppn
/// 
/// 5. Implementação real:
/// ```dart
/// import 'package:picovoice_flutter/picovoice.dart';
/// import 'package:picovoice_flutter/picovoice_manager.dart';
/// import 'package:picovoice_flutter/picovoice_error.dart';
/// 
/// class WakeWordService extends ChangeNotifier {
///   PorcupineManager? _porcupineManager;
///   
///   Future<void> initialize({required String accessKey}) async {
///     try {
///       _porcupineManager = await PorcupineManager.fromKeywordPaths(
///         accessKey,
///         ['assets/wake_words/jonh.ppn'],
///         _wakeWordCallback,
///         errorCallback: _errorCallback,
///       );
///       
///       _isEnabled = true;
///       notifyListeners();
///     } on PorcupineException catch (e) {
///       debugPrint('Erro Porcupine: ${e.message}');
///     }
///   }
///   
///   void _errorCallback(PorcupineException error) {
///     debugPrint('Erro no wake word: ${error.message}');
///   }
/// }
/// ```

