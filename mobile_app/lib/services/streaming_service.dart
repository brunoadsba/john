/// Serviço para streaming de respostas LLM via Server-Sent Events (SSE)
import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/env.dart';
import 'error_monitor.dart';

/// Eventos SSE do streaming
enum StreamingEventType {
  start,
  token,
  complete,
  error,
}

/// Evento SSE
class StreamingEvent {
  final StreamingEventType type;
  final String? text;
  final String? sessionId;
  final int? tokens;
  final bool? cached;
  final String? errorMessage;

  StreamingEvent({
    required this.type,
    this.text,
    this.sessionId,
    this.tokens,
    this.cached,
    this.errorMessage,
  });

  factory StreamingEvent.fromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String;
    StreamingEventType type;
    
    switch (typeStr) {
      case 'start':
        type = StreamingEventType.start;
        break;
      case 'token':
        type = StreamingEventType.token;
        break;
      case 'complete':
        type = StreamingEventType.complete;
        break;
      case 'error':
        type = StreamingEventType.error;
        break;
      default:
        type = StreamingEventType.error;
    }

    return StreamingEvent(
      type: type,
      text: json['text'] as String?,
      sessionId: json['session_id'] as String?,
      tokens: json['tokens'] as int?,
      cached: json['cached'] as bool?,
      errorMessage: json['message'] as String?,
    );
  }
}

/// Callbacks do streaming
typedef OnTokenReceived = void Function(String token);
typedef OnComplete = void Function(String fullText, int tokens, bool cached);
typedef OnError = void Function(String error);
typedef OnStart = void Function(String sessionId);

/// Serviço de streaming SSE
class StreamingService {
  StreamSubscription<String>? _subscription;
  bool _isStreaming = false;
  String? _currentSessionId;

  bool get isStreaming => _isStreaming;
  String? get currentSessionId => _currentSessionId;

  /// Callbacks
  OnTokenReceived? onTokenReceived;
  OnComplete? onComplete;
  OnError? onError;
  OnStart? onStart;

  /// Inicia streaming de resposta
  Future<void> streamText({
    required String text,
    String? sessionId,
  }) async {
    if (_isStreaming) {
      debugPrint('⚠️ Streaming já está ativo. Cancelando anterior...');
      await cancel();
    }

    try {
      _isStreaming = true;
      
      // Monta URL
      final uri = Uri.parse('${Env.backendUrl}/api/stream_text').replace(
        queryParameters: {
          'texto': text,
          if (sessionId != null) 'session_id': sessionId,
        },
      );

      debugPrint('📡 Iniciando streaming: $uri');

      // Faz requisição HTTP com streaming
      final request = http.Request('GET', uri);
      final streamedResponse = await http.Client().send(request);

      if (streamedResponse.statusCode != 200) {
        final errorBody = await streamedResponse.stream.bytesToString();
        throw Exception(
          'Erro no streaming: ${streamedResponse.statusCode} - $errorBody'
        );
      }

      // Processa stream SSE
      String buffer = '';
      await for (final chunk in streamedResponse.stream
          .transform(utf8.decoder)) {
        if (!_isStreaming) break; // Cancelado

        buffer += chunk;
        
        // Processa linhas completas (SSE termina com \n\n)
        while (buffer.contains('\n\n')) {
          final lineEnd = buffer.indexOf('\n\n');
          final line = buffer.substring(0, lineEnd);
          buffer = buffer.substring(lineEnd + 2);

          if (line.startsWith('data: ')) {
            final jsonStr = line.substring(6); // Remove "data: "
            try {
              final json = jsonDecode(jsonStr) as Map<String, dynamic>;
              final event = StreamingEvent.fromJson(json);
              _handleEvent(event);
            } catch (e) {
              debugPrint('⚠️ Erro ao processar evento SSE: $e');
            }
          }
        }
      }

      _isStreaming = false;
    } catch (e, stackTrace) {
      _isStreaming = false;
      debugPrint('❌ Erro no streaming: $e');
      
      ErrorMonitor.reportError(
        message: 'Erro no streaming SSE: $e',
        stackTrace: stackTrace.toString(),
        level: 'error',
        type: 'network',
        additionalContext: {'action': 'stream_text'},
      );

      if (onError != null) {
        onError!(e.toString());
      }
    }
  }

  /// Processa evento SSE
  void _handleEvent(StreamingEvent event) {
    switch (event.type) {
      case StreamingEventType.start:
        _currentSessionId = event.sessionId;
        if (onStart != null && event.sessionId != null) {
          onStart!(event.sessionId!);
        }
        break;

      case StreamingEventType.token:
        if (event.text != null && onTokenReceived != null) {
          onTokenReceived!(event.text!);
        }
        break;

      case StreamingEventType.complete:
        if (event.text != null && onComplete != null) {
          onComplete!(
            event.text!,
            event.tokens ?? 0,
            event.cached ?? false,
          );
        }
        _isStreaming = false;
        break;

      case StreamingEventType.error:
        _isStreaming = false;
        if (onError != null) {
          onError!(event.errorMessage ?? 'Erro desconhecido no streaming');
        }
        break;
    }
  }

  /// Cancela streaming atual
  Future<void> cancel() async {
    if (_isStreaming) {
      _isStreaming = false;
      await _subscription?.cancel();
      _subscription = null;
      _currentSessionId = null;
      debugPrint('🛑 Streaming cancelado');
    }
  }

  /// Dispose
  void dispose() {
    cancel();
  }
}

