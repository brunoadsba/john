/// Serviço de comunicação com a API do Jonh Assistant
import 'package:flutter/foundation.dart';
import 'dart:typed_data';
import 'dart:convert';
import 'dart:async';

import 'api/websocket_client.dart';
import 'api/connection_manager.dart';
import 'api/message_handler.dart';
import 'streaming_service.dart';
import '../models/message.dart';
import '../utils/performance_metrics.dart';
import 'error_monitor.dart';

class ApiService extends ChangeNotifier {
  final WebSocketClient _wsClient = WebSocketClient();
  final ConnectionManager _connectionManager = ConnectionManager();
  final MessageHandler _messageHandler = MessageHandler();
  final StreamingService _streamingService = StreamingService();

  String? _sessionId;
  bool _isConnected = false;
  bool _isStreaming = false;

  bool get isConnected => _isConnected;
  bool get isStreaming => _isStreaming;
  String? get sessionId => _sessionId;
  PerformanceMetrics get metrics => _messageHandler.metrics;
  List<Message> get messages => _messageHandler.messages;

  /// Callback para reproduzir áudio quando recebido (DESABILITADO - TTS desabilitado)
  @Deprecated('TTS desabilitado - agente responde apenas via texto')
  Function(Uint8List)? onAudioReceived;

  ApiService() {
    _wsClient.onMessage = (data) => _messageHandler.handleMessage(data);
    _wsClient.onError = (_) => _handleDisconnection();
    _wsClient.onDone = () => _handleDisconnection();
    // NOTA: Callback de áudio removido - TTS desabilitado
    // _messageHandler.onAudioReceived removido pois não processamos mais áudio
    
    // Configura callbacks do streaming
    _streamingService.onStart = (sessionId) {
      _sessionId = sessionId;
      _isStreaming = true;
      notifyListeners();
    };
    
    _streamingService.onTokenReceived = (token) {
      _messageHandler.handleStreamingToken(token);
      notifyListeners();
    };
    
    _streamingService.onComplete = (fullText, tokens, cached) {
      _isStreaming = false;
      _messageHandler.handleStreamingComplete(fullText, tokens, cached);
      notifyListeners();
    };
    
    _streamingService.onError = (error) {
      _isStreaming = false;
      _messageHandler.handleStreamingError(error);
      notifyListeners();
    };
  }

  /// Testa conexão com o servidor
  Future<bool> testConnection() async {
    return await _connectionManager.testConnection();
  }

  /// Conecta ao WebSocket (não lança exceção - permite modo offline)
  Future<void> connect() async {
    if (_isConnected) {
      debugPrint('✅ WebSocket já está conectado');
      return;
    }

    try {
      final isServerAvailable = await _connectionManager.testConnection();
      if (!isServerAvailable) {
        debugPrint('⚠️ Servidor não está acessível - app funcionará em modo offline');
        return; // Não lança exceção, apenas retorna
      }

      await _wsClient.connect();
      _isConnected = _wsClient.isConnected;
      
      if (_isConnected) {
        _connectionManager.resetAttempts();
        startSession();
        notifyListeners();
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Erro ao conectar: $e');
      // Não reporta como erro crítico - permite modo offline
      ErrorMonitor.reportError(
        message: 'Erro ao conectar WebSocket: $e',
        stackTrace: stackTrace.toString(),
        level: 'warning', // Muda para warning em vez de error
        type: 'network',
        additionalContext: {'action': 'connect'},
      );
      _handleDisconnection();
      // Não relança exceção - permite app funcionar offline
    }
  }

  void _handleDisconnection() {
    if (_isConnected) {
      _isConnected = false;
      notifyListeners();
      _connectionManager.scheduleReconnect(() => connect());
    }
  }

  /// Desconecta do WebSocket
  void disconnect() {
    _connectionManager.cancelReconnect();
    _wsClient.disconnect();
    _isConnected = false;
    _sessionId = null;
    notifyListeners();
  }

  /// Envia áudio via WebSocket
  Future<void> sendAudio(List<int> audioBytes) async {
    if (!_isConnected) {
      debugPrint('⚠️ WebSocket não conectado');
      return;
    }

    try {
      metrics.markAudioSent();
      
      // Adiciona mensagem do usuário imediatamente (Optimistic UI)
      _messageHandler.addUserMessage("🎤 Áudio enviado...", status: MessageStatus.sending);
      notifyListeners();
      
      _wsClient.send(Uint8List.fromList(audioBytes));
      debugPrint('📤 Áudio enviado: ${audioBytes.length} bytes');
    } catch (e) {
      debugPrint('❌ Erro ao enviar áudio: $e');
    }
  }

  /// Envia texto e recebe streaming de resposta
  Future<void> sendText(String text) async {
    if (_isStreaming) {
      debugPrint('⚠️ Streaming já está ativo');
      return;
    }

    try {
      // Adiciona mensagem do usuário
      _messageHandler.addUserMessage(text);
      notifyListeners();

      // Inicia streaming
      await _streamingService.streamText(
        text: text,
        sessionId: _sessionId,
      );
    } catch (e) {
      debugPrint('❌ Erro ao enviar texto: $e');
      _isStreaming = false;
      notifyListeners();
    }
  }

  /// Cancela streaming atual
  Future<void> cancelStreaming() async {
    if (_isStreaming) {
      await _streamingService.cancel();
      _isStreaming = false;
      notifyListeners();
    }
  }

  /// Envia mensagem de controle
  void sendControlMessage(Map<String, dynamic> message) {
    if (!_isConnected) {
      debugPrint('⚠️ WebSocket não conectado');
      return;
    }

    _wsClient.send(jsonEncode(message));
  }

  /// Inicia sessão
  void startSession() {
    sendControlMessage({'type': 'start_session'});
    
    // Notifica que uma nova sessão foi criada (para LocationService)
    notifyListeners();
  }

  /// Encerra sessão
  void endSession() {
    sendControlMessage({'type': 'end_session'});
    _sessionId = null;
  }

  /// Limpa mensagens
  void clearMessages() {
    _messageHandler.clearMessages();
    notifyListeners();
  }

  /// Reseta métricas
  void resetMetrics() {
    _messageHandler.resetMetrics();
  }

  /// Cancela reconexão
  void cancelReconnect() {
    _connectionManager.cancelReconnect();
  }

  @override
  void dispose() {
    disconnect();
    _streamingService.dispose();
    _wsClient.dispose();
    _connectionManager.dispose();
    super.dispose();
  }
}
