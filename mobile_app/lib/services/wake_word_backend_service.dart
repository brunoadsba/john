import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import '../config/env.dart';

/// Serviço de detecção de wake word usando OpenWakeWord no backend
///
/// Conecta-se ao endpoint /ws/wake_word do backend e envia chunks
/// de áudio continuamente para detecção em tempo real.
class WakeWordBackendService extends ChangeNotifier {
  WebSocketChannel? _channel;
  bool _isConnected = false;
  bool _isListening = false;
  String? _errorMessage;
  List<String> _loadedModels = [];
  double _threshold = 0.5;

  bool get isConnected => _isConnected;
  bool get isListening => _isListening;
  String? get errorMessage => _errorMessage;
  List<String> get loadedModels => List.unmodifiable(_loadedModels);
  double get threshold => _threshold;

  /// Callback quando wake word é detectado
  Function(String wakeWord, double confidence)? onWakeWordDetected;

  /// URL base do backend (mesma do ApiService)
  static String get baseUrl => Env.backendUrl.isNotEmpty
      ? Env.backendUrl
      : 'http://192.168.1.5:8000'; // IP do Windows na rede WiFi (mesma rede do celular)

  static String get wsUrl => baseUrl
      .replaceFirst('http://', 'ws://')
      .replaceFirst('https://', 'wss://');

  /// Conecta ao WebSocket de wake word
  Future<void> connect() async {
    if (_isConnected && _channel != null) {
      debugPrint('WakeWordBackend: Já está conectado');
      return;
    }

    try {
      final url = '$wsUrl/ws/wake_word';
      debugPrint('🔄 WakeWordBackend: Conectando ao WebSocket: $url');

      _channel = WebSocketChannel.connect(Uri.parse(url));

      _channel!.stream.listen(
        (data) {
          if (!_isConnected) {
            debugPrint('✅ WakeWordBackend: Conectado com sucesso!');
            _isConnected = true;
            notifyListeners();
          }
          _handleMessage(data);
        },
        onError: (error) {
          debugPrint('❌ WakeWordBackend: Erro no WebSocket: $error');
          _isConnected = false;
          _errorMessage = error.toString();
          _channel = null;
          notifyListeners();
        },
        onDone: () {
          debugPrint('⚠️ WakeWordBackend: WebSocket fechado');
          _isConnected = false;
          _channel = null;
          _isListening = false;
          notifyListeners();
        },
        cancelOnError: false,
      );

      // Aguarda confirmação de conexão
      await Future.delayed(const Duration(milliseconds: 500));

      if (!_isConnected && _channel != null) {
        // Tenta marcar como conectado mesmo sem mensagem ainda
        _isConnected = true;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('❌ WakeWordBackend: Erro ao conectar: $e');
      _isConnected = false;
      _errorMessage = e.toString();
      _channel = null;
      notifyListeners();
      rethrow;
    }
  }

  /// Desconecta do WebSocket
  void disconnect() {
    if (_isListening) {
      stopListening();
    }
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
    _isListening = false;
    notifyListeners();
  }

  /// Inicia escuta (começa a enviar chunks)
  Future<void> startListening() async {
    if (!_isConnected || _channel == null) {
      debugPrint('⚠️ WakeWordBackend: Não conectado. Conectando...');
      await connect();
    }

    if (_isListening) {
      debugPrint('⚠️ WakeWordBackend: Já está escutando');
      return;
    }

    _isListening = true;
    _errorMessage = null;
    notifyListeners();

    debugPrint('🎤 WakeWordBackend: Escutando wake word...');
  }

  /// Para escuta
  void stopListening() {
    if (!_isListening) return;

    try {
      // Envia comando para parar
      _sendControlMessage({'type': 'stop_wake_word'});
      _isListening = false;
      notifyListeners();
      debugPrint('🔇 WakeWordBackend: Parou de escutar');
    } catch (e) {
      debugPrint('❌ WakeWordBackend: Erro ao parar: $e');
    }
  }

  /// Envia chunk de áudio para detecção
  ///
  /// [audioChunk] - Chunk de áudio (16-bit PCM, 16kHz, mono)
  /// Tamanho recomendado: ~1280 bytes (~80ms de áudio)
  void sendAudioChunk(Uint8List audioChunk) {
    if (!_isConnected || _channel == null || !_isListening) {
      return;
    }

    try {
      _channel!.sink.add(audioChunk);
    } catch (e) {
      debugPrint('❌ WakeWordBackend: Erro ao enviar chunk: $e');
      _isConnected = false;
      _isListening = false;
      notifyListeners();
    }
  }

  /// Envia mensagem de controle
  void _sendControlMessage(Map<String, dynamic> message) {
    if (!_isConnected || _channel == null) return;
    try {
      _channel!.sink.add(jsonEncode(message));
    } catch (e) {
      debugPrint('❌ WakeWordBackend: Erro ao enviar mensagem: $e');
    }
  }

  /// Processa mensagens recebidas do servidor
  void _handleMessage(dynamic data) {
    if (data is String) {
      try {
        final json = jsonDecode(data);
        final type = json['type'];

        switch (type) {
          case 'connected':
            debugPrint('✅ WakeWordBackend: Mensagem de conexão recebida');
            _loadedModels = (json['models'] as List<dynamic>?)
                    ?.map((e) => e.toString())
                    .toList() ??
                [];
            _threshold = (json['threshold'] as num?)?.toDouble() ?? 0.5;
            debugPrint('   Modelos carregados: $_loadedModels');
            debugPrint('   Threshold: $_threshold');
            notifyListeners();
            break;

          case 'wake_word_detected':
            final wakeWord = json['wake_word'] as String? ?? 'unknown';
            final confidence = (json['confidence'] as num?)?.toDouble() ?? 0.0;
            final threshold = (json['threshold'] as num?)?.toDouble();

            debugPrint('🎯 WakeWordBackend: Wake word detectado!');
            debugPrint('   Palavra: $wakeWord');
            debugPrint('   Confiança: ${confidence.toStringAsFixed(3)}');
            if (threshold != null) {
              debugPrint('   Threshold: ${threshold.toStringAsFixed(3)}');
            }

            // CORREÇÃO: Valida confiança antes de acionar callback
            // Garante que confiança é alta o suficiente (duplo filtro)
            final minConfidence = 0.85;
            if (confidence >= minConfidence) {
              if (onWakeWordDetected != null) {
                debugPrint('✅ Wake word validado - acionando callback');
                try {
                  onWakeWordDetected!(wakeWord, confidence);
                } catch (e, stackTrace) {
                  debugPrint(
                      '❌ Erro ao executar callback onWakeWordDetected: $e');
                  debugPrint('Stack trace: $stackTrace');
                }
              } else {
                debugPrint('⚠️ Callback onWakeWordDetected não configurado');
              }
            } else {
              debugPrint(
                  '⚠️ Wake word ignorado: confiança ${confidence.toStringAsFixed(3)} < $minConfidence');
            }
            break;

          case 'error':
            final message = json['message'] as String? ?? 'Erro desconhecido';
            debugPrint('❌ WakeWordBackend: Erro do servidor: $message');
            _errorMessage = message;
            notifyListeners();
            break;

          case 'wake_word_stats':
            final stats = json['stats'];
            if (stats != null) {
              _loadedModels = (stats['models'] as List<dynamic>?)
                      ?.map((e) => e.toString())
                      .toList() ??
                  [];
              _threshold = (stats['threshold'] as num?)?.toDouble() ?? 0.5;
              notifyListeners();
            }
            break;

          case 'pong':
            debugPrint('💓 WakeWordBackend: Pong recebido (conexão ativa)');
            break;
        }
      } catch (e) {
        debugPrint('❌ WakeWordBackend: Erro ao processar mensagem: $e');
      }
    }
  }

  /// Solicita estatísticas do servidor
  void requestStats() {
    _sendControlMessage({'type': 'get_wake_word_stats'});
  }

  /// Envia ping para manter conexão WebSocket ativa (heartbeat)
  void ping() {
    _sendControlMessage({'type': 'ping'});
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
