/// Cliente WebSocket para comunicação com o backend
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:typed_data';
import 'dart:async';
import '../../config/env.dart';
import '../../services/error_monitor.dart';

class WebSocketClient {
  static String get wsUrl {
    final baseUrl = Env.backendUrl.isNotEmpty
        ? Env.backendUrl
        : 'http://192.168.1.5:8000';
    return baseUrl
            .replaceFirst('http://', 'ws://')
            .replaceFirst('https://', 'wss://') +
        '/ws/listen';
  }

  WebSocketChannel? _channel;
  bool _isConnected = false;
  bool _isConnecting = false;

  bool get isConnected => _isConnected;
  bool get isConnecting => _isConnecting;

  /// Callback para mensagens recebidas
  Function(dynamic)? onMessage;
  Function(dynamic)? onError;
  Function()? onDone;

  /// Conecta ao WebSocket
  Future<void> connect() async {
    if (_isConnected && _channel != null) {
      debugPrint('✅ WebSocket já está conectado');
      return;
    }

    if (_isConnecting) {
      debugPrint('⏳ Conexão já em andamento...');
      return;
    }

    _isConnecting = true;

    try {
      debugPrint('🔄 Conectando ao WebSocket: $wsUrl');
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));

      _channel!.stream.listen(
        (data) {
          if (!_isConnected) {
            debugPrint('✅ WebSocket conectado com sucesso!');
            _isConnected = true;
            _isConnecting = false;
          }
          if (onMessage != null) {
            onMessage!(data);
          }
        },
        onError: (error) {
          debugPrint('❌ WebSocket error: $error');
          ErrorMonitor.reportError(
            message: 'WebSocket error: $error',
            level: 'error',
            type: 'network',
            additionalContext: {'action': 'websocket_stream'},
          );
          _isConnected = false;
          _isConnecting = false;
          if (onError != null) {
            onError!(error);
          }
        },
        onDone: () {
          debugPrint('⚠️ WebSocket closed');
          _isConnected = false;
          _isConnecting = false;
          if (onDone != null) {
            onDone!();
          }
        },
        cancelOnError: false,
      );

      await Future.delayed(const Duration(milliseconds: 1000));
      if (!_isConnected) {
        throw Exception('Conexão não estabelecida após timeout');
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Erro ao conectar WebSocket: $e');
      ErrorMonitor.reportError(
        message: 'Erro ao conectar WebSocket: $e',
        stackTrace: stackTrace.toString(),
        level: 'error',
        type: 'network',
        additionalContext: {'action': 'connect', 'url': wsUrl},
      );
      _isConnected = false;
      _isConnecting = false;
      rethrow;
    }
  }

  /// Envia dados via WebSocket
  void send(dynamic data) {
    if (_channel == null || !_isConnected) {
      debugPrint('⚠️ WebSocket não conectado, não é possível enviar dados');
      return;
    }

    try {
      if (data is String) {
        _channel!.sink.add(data);
      } else if (data is Uint8List || data is List<int>) {
        _channel!.sink.add(data);
      } else {
        _channel!.sink.add(data);
      }
    } catch (e) {
      debugPrint('❌ Erro ao enviar dados: $e');
    }
  }

  /// Desconecta do WebSocket
  void disconnect() {
    try {
      _channel?.sink.close();
    } catch (e) {
      debugPrint('⚠️ Erro ao fechar WebSocket: $e');
    } finally {
      _channel = null;
      _isConnected = false;
      _isConnecting = false;
    }
  }

  void dispose() {
    disconnect();
  }
}

