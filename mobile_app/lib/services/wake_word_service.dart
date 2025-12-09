import 'package:flutter/foundation.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';

// Imports condicionais - apenas para mobile (Android/iOS)
// No web, usa stub que não faz nada
import 'package:porcupine_flutter/porcupine_manager.dart'
    if (dart.library.html) 'package:jonh_assistant/services/wake_word_service_stub.dart'
    as porcupine;

/// Serviço de detecção de wake word usando Porcupine (Picovoice)
///
/// Funciona em background e detecta a palavra "Jonh" automaticamente.
///
/// Configuração necessária:
/// 1. Obter Access Key em https://console.picovoice.ai/
/// 2. Salvar em SharedPreferences ou variável de ambiente
/// 3. Treinar modelo customizado "Jonh" ou usar palavra padrão
class WakeWordService extends ChangeNotifier {
  // Usa dynamic para evitar erros de tipo em web
  dynamic _porcupineManager;
  bool _isListening = false;
  bool _isEnabled = false;
  String? _errorMessage;

  bool get isListening => _isListening;
  bool get isEnabled => _isEnabled;
  String? get errorMessage => _errorMessage;

  // Callback quando wake word é detectado
  Function()? onWakeWordDetected;

  /// Inicializa o serviço com Porcupine
  ///
  /// [accessKey] - Access Key do Picovoice (obter em https://console.picovoice.ai/)
  /// [keywordPath] - Caminho para arquivo .ppn do modelo customizado (opcional)
  /// [sensitivity] - Sensibilidade de detecção (0.0 a 1.0, padrão: 0.5)
  Future<void> initialize({
    String? accessKey,
    String? keywordPath,
    double sensitivity = 0.5,
  }) async {
    // Wake word não suportado em web
    if (kIsWeb) {
      debugPrint(
          '⚠️ WakeWordService: Wake word não suportado em web. Use Android ou iOS.');
      _isEnabled = false;
      _errorMessage = 'Wake word disponível apenas em Android/iOS';
      notifyListeners();
      return;
    }

    try {
      // Tenta obter access key de SharedPreferences se não fornecida
      if (accessKey == null || accessKey.isEmpty) {
        final prefs = await SharedPreferences.getInstance();
        accessKey = prefs.getString('picovoice_access_key');
      }

      // Se ainda não tiver access key, desabilita
      if (accessKey == null || accessKey.isEmpty) {
        debugPrint('⚠️ WakeWordService: Access Key não configurada');
        debugPrint('   Configure em: https://console.picovoice.ai/');
        debugPrint(
            '   Ou salve em SharedPreferences com chave: picovoice_access_key');
        _isEnabled = false;
        _errorMessage = 'Access Key não configurada';
        notifyListeners();
        return;
      }

      // PorcupineManager requer arquivo .ppn (modelo)
      // Se não tiver keywordPath, tenta usar modelo padrão "Alexa"
      String assetPath = 'assets/wake_words/alexa.ppn';
      if (keywordPath != null && keywordPath.isNotEmpty) {
        assetPath = keywordPath;
      }

      debugPrint('ℹ️ WakeWordService: Carregando modelo: $assetPath');

      // Porcupine precisa de um caminho de arquivo real, não asset do Flutter
      // Copia o asset para um arquivo temporário
      final modelFile = await _copyAssetToFile(assetPath);
      if (modelFile == null) {
        throw Exception(
            'Não foi possível carregar modelo de wake word: $assetPath');
      }

      debugPrint('ℹ️ WakeWordService: Modelo copiado para: ${modelFile.path}');

      // Inicializa com modelo customizado (.ppn)
      _porcupineManager = await porcupine.PorcupineManager.fromKeywordPaths(
        accessKey,
        [modelFile.path], // Usa caminho do arquivo real
        _wakeWordCallback,
        errorCallback: _errorCallback,
        sensitivities: [sensitivity],
      );

      _isEnabled = true;
      _errorMessage = null;
      notifyListeners();

      debugPrint('✅ WakeWordService: Inicializado com sucesso');
      debugPrint('   Escutando wake word: ${keywordPath ?? "Jarvis (padrão)"}');
    } catch (e) {
      // Trata erros do Porcupine
      String errorMsg = e.toString();

      // Melhora mensagens de erro comuns
      if (errorMsg.contains('InvalidArgument') ||
          errorMsg.contains('Invalid Argument')) {
        errorMsg = 'Erro ao inicializar wake word.\n'
            'Possíveis causas:\n'
            '1. Access Key inválida (verifique no console Picovoice)\n'
            '2. Modelo alexa.ppn não encontrado ou corrompido\n'
            '3. Problema ao copiar modelo para arquivo temporário\n'
            '\n'
            'Verifique os logs para mais detalhes.';
      } else if (errorMsg.contains('InvalidAccessKey') ||
          errorMsg.contains('Invalid access key')) {
        errorMsg = '❌ Access Key inválida.\n'
            'Obtenha uma Access Key válida em: https://console.picovoice.ai/\n'
            'As keys do Picovoice começam com "pv_"';
      } else if (errorMsg.contains('FileNotFound') ||
          errorMsg.contains('file not found')) {
        errorMsg = 'Erro: Modelo de wake word não encontrado.\n'
            'Verifique se o arquivo alexa.ppn está em assets/wake_words/';
      }

      debugPrint('❌ Erro ao inicializar Porcupine: $errorMsg');
      debugPrint('   Detalhes técnicos: $e');
      _isEnabled = false;
      _errorMessage = errorMsg;
      notifyListeners();
    }
  }

  /// Copia asset do Flutter para arquivo temporário
  Future<File?> _copyAssetToFile(String assetPath) async {
    try {
      debugPrint('📦 Iniciando cópia do asset: $assetPath');

      // Carrega o asset como bytes
      debugPrint('📥 Carregando asset do bundle...');
      final ByteData data = await rootBundle.load(assetPath);
      final bytes = data.buffer.asUint8List();
      debugPrint('✅ Asset carregado: ${bytes.length} bytes');

      // Obtém diretório temporário
      debugPrint('📁 Obtendo diretório temporário...');
      final tempDir = await getTemporaryDirectory();
      debugPrint('✅ Diretório temporário: ${tempDir.path}');

      final fileName = assetPath.split('/').last; // Ex: alexa.ppn
      final file = File('${tempDir.path}/$fileName');
      debugPrint('📝 Arquivo destino: ${file.path}');

      // Escreve o arquivo
      debugPrint('💾 Escrevendo arquivo...');
      await file.writeAsBytes(bytes);

      // Verifica se o arquivo foi criado
      if (await file.exists()) {
        final fileSize = await file.length();
        debugPrint(
            '✅ Asset copiado com sucesso: $assetPath -> ${file.path} (${fileSize} bytes)');
        return file;
      } else {
        debugPrint('❌ Arquivo não foi criado após escrita!');
        return null;
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Erro ao copiar asset $assetPath: $e');
      debugPrint('❌ Stack trace: $stackTrace');
      return null;
    }
  }

  /// Salva Access Key em SharedPreferences
  Future<void> saveAccessKey(String accessKey) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('picovoice_access_key', accessKey);
    debugPrint('✅ Access Key salva');
  }

  /// Inicia escuta de wake word
  Future<void> startListening() async {
    if (kIsWeb) {
      debugPrint('⚠️ WakeWordService: Wake word não suportado em web');
      return;
    }

    if (!_isEnabled || _porcupineManager == null) {
      debugPrint('⚠️ WakeWordService: Não habilitado ou não inicializado');
      return;
    }

    if (_isListening) {
      debugPrint('⚠️ WakeWordService: Já está escutando');
      return;
    }

    try {
      await _porcupineManager!.start();
      _isListening = true;
      _errorMessage = null;
      notifyListeners();

      debugPrint('🎤 WakeWordService: Escutando wake word...');
    } catch (e) {
      debugPrint('❌ Erro ao iniciar escuta: $e');
      _errorMessage = e.toString();
      _isListening = false;
      notifyListeners();
    }
  }

  /// Para escuta de wake word
  Future<void> stopListening() async {
    if (kIsWeb || !_isListening || _porcupineManager == null) return;

    try {
      await _porcupineManager!.stop();
      _isListening = false;
      notifyListeners();

      debugPrint('🔇 WakeWordService: Parou de escutar');
    } catch (e) {
      debugPrint('❌ Erro ao parar escuta: $e');
    }
  }

  /// Callback quando wake word é detectado
  void _wakeWordCallback(int keywordIndex) {
    debugPrint(
        '🎯 WakeWordService: Wake word detectado! (índice: $keywordIndex)');

    if (onWakeWordDetected != null) {
      onWakeWordDetected!();
    }

    notifyListeners();
  }

  /// Callback de erro do Porcupine
  void _errorCallback(dynamic error) {
    debugPrint('❌ WakeWordService: Erro do Porcupine: ${error.toString()}');
    _errorMessage = error.toString();
    _isListening = false;
    notifyListeners();
  }

  @override
  void dispose() {
    stopListening();
    _porcupineManager?.delete();
    super.dispose();
  }
}
