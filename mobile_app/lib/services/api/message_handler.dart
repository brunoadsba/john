/// Handler de mensagens WebSocket
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'dart:typed_data';
import '../../models/message.dart';
import '../../utils/performance_metrics.dart';

class MessageHandler {
  final List<Message> _messages = [];
  final PerformanceMetrics metrics = PerformanceMetrics();

  /// Callback para áudio recebido
  Function(Uint8List)? onAudioReceived;

  /// ID da mensagem sendo streamada
  String? _streamingMessageId;

  List<Message> get messages => List.unmodifiable(_messages);

  /// Processa mensagem recebida do WebSocket
  void handleMessage(dynamic data) {
    try {
      if (data is Uint8List || data is List<int>) {
        // Dados binários (áudio)
        final audioBytes = data is Uint8List ? data : Uint8List.fromList(data);
        debugPrint('🔊 Áudio recebido: ${audioBytes.length} bytes');
        if (onAudioReceived != null) {
          onAudioReceived!(audioBytes);
        }
        metrics.markResponseReceived();
        metrics.markAudioPlaybackStart();
        return;
      }

      if (data is String) {
        final json = jsonDecode(data);
        final type = json['type'] as String?;

        switch (type) {
          case 'connected':
            debugPrint('✅ Conectado ao assistente');
            _addSystemMessage('Conectado ao assistente Jonh');
            break;

          case 'session_started':
          case 'session_created':
            debugPrint('📝 Sessão criada: ${json['session_id']}');
            break;

          case 'transcription':
            final text = json['text'] as String? ?? '';
            final confidence = json['confidence'] as double? ?? 0.0;
            debugPrint('📝 Transcrição: "$text" (confiança: ${confidence.toStringAsFixed(2)})');
            if (text.isNotEmpty) {
              _addMessage(Message(
                id: 'transcription_${DateTime.now().millisecondsSinceEpoch}',
                type: MessageType.user,
                content: text,
                timestamp: DateTime.now(),
              ));
            }
            break;

          case 'response':
            final text = json['text'] as String? ?? '';
            final tokens = json['tokens'] as int? ?? 0;
            final conversationId = json['conversation_id'] as int?;
            final metricsData = json['metrics'] as Map<String, dynamic>?;
            
            if (metricsData != null) {
              final sttTime = metricsData['sttTime'] as int?;
              final llmTime = metricsData['llmTime'] as int?;
              final ttsTime = metricsData['ttsTime'] as int?;
              
              metrics.setBackendMetrics(
                sttTime: sttTime != null ? Duration(milliseconds: sttTime) : null,
                llmTime: llmTime != null ? Duration(milliseconds: llmTime) : null,
                ttsTime: ttsTime != null ? Duration(milliseconds: ttsTime) : null,
              );
            }
            
            debugPrint('🤖 Resposta: "$text" ($tokens tokens)${conversationId != null ? " [conversation_id: $conversationId]" : ""}');
            if (text.isNotEmpty) {
              _addMessage(Message(
                id: 'response_${DateTime.now().millisecondsSinceEpoch}',
                type: MessageType.assistant,
                content: text,
                timestamp: DateTime.now(),
                conversationId: conversationId,
              ));
            }
            metrics.markResponseReceived();
            break;

          case 'complete':
            final metricsData = json['metrics'] as Map<String, dynamic>?;
            if (metricsData != null) {
              final sttTime = metricsData['sttTime'] as int?;
              final llmTime = metricsData['llmTime'] as int?;
              final ttsTime = metricsData['ttsTime'] as int?;
              
              metrics.setBackendMetrics(
                sttTime: sttTime != null ? Duration(milliseconds: sttTime) : null,
                llmTime: llmTime != null ? Duration(milliseconds: llmTime) : null,
                ttsTime: ttsTime != null ? Duration(milliseconds: ttsTime) : null,
              );
            }
            debugPrint('✅ Processamento completo');
            break;

          case 'processing':
            final stage = json['stage'] as String? ?? '';
            debugPrint('⏳ Processando: $stage');
            break;

          case 'error':
            final errorMessage = json['message'] as String? ?? 'Erro desconhecido';
            debugPrint('❌ Erro: $errorMessage');
            _addMessage(Message(
              id: 'error_${DateTime.now().millisecondsSinceEpoch}',
              type: MessageType.error,
              content: 'Erro: $errorMessage',
              timestamp: DateTime.now(),
            ));
            break;

          case 'pong':
            debugPrint('🏓 Pong recebido');
            break;

          default:
            debugPrint('⚠️ Tipo de mensagem desconhecido: $type');
        }
      }
    } catch (e) {
      debugPrint('❌ Erro ao processar mensagem: $e');
    }
  }

  void _addMessage(Message message) {
    _messages.add(message);
  }

  void _addSystemMessage(String content) {
    _messages.add(Message(
      id: 'system_${DateTime.now().millisecondsSinceEpoch}',
      type: MessageType.system,
      content: content,
      timestamp: DateTime.now(),
    ));
  }

  /// Adiciona mensagem do usuário
  void addUserMessage(String text) {
    _addMessage(Message(
      id: 'user_${DateTime.now().millisecondsSinceEpoch}',
      type: MessageType.user,
      content: text,
      timestamp: DateTime.now(),
    ));
  }

  /// Processa token de streaming
  void handleStreamingToken(String token) {
    if (_streamingMessageId == null) {
      // Cria nova mensagem de assistente em modo streaming
      _streamingMessageId = 'streaming_${DateTime.now().millisecondsSinceEpoch}';
      _addMessage(Message(
        id: _streamingMessageId!,
        type: MessageType.assistant,
        content: token,
        timestamp: DateTime.now(),
        isProcessing: true,
      ));
    } else {
      // Atualiza mensagem existente com novo token
      final index = _messages.indexWhere((m) => m.id == _streamingMessageId);
      if (index != -1) {
        final currentMessage = _messages[index];
        _messages[index] = currentMessage.copyWith(
          content: currentMessage.content + token,
        );
      }
    }
  }

  /// Finaliza streaming
  void handleStreamingComplete(String fullText, int tokens, bool cached) {
    if (_streamingMessageId != null) {
      final index = _messages.indexWhere((m) => m.id == _streamingMessageId);
      if (index != -1) {
        _messages[index] = _messages[index].copyWith(
          content: fullText,
          isProcessing: false,
        );
      }
      _streamingMessageId = null;
    }
    
    debugPrint('✅ Streaming completo: "$fullText" ($tokens tokens, cached: $cached)');
    metrics.markResponseReceived();
  }

  /// Trata erro no streaming
  void handleStreamingError(String error) {
    if (_streamingMessageId != null) {
      final index = _messages.indexWhere((m) => m.id == _streamingMessageId);
      if (index != -1) {
        _messages[index] = _messages[index].copyWith(
          type: MessageType.error,
          content: 'Erro: $error',
          isProcessing: false,
        );
      }
      _streamingMessageId = null;
    }
    
    debugPrint('❌ Erro no streaming: $error');
  }

  void clearMessages() {
    _messages.clear();
    _streamingMessageId = null;
  }

  void resetMetrics() {
    metrics.reset();
  }
}

