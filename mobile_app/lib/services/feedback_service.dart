/// Serviço para enviar feedback ao backend
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/env.dart';

/// Serviço de feedback para comunicação com API
class FeedbackService {
  static String get _baseUrl {
    return Env.backendUrl.isNotEmpty
        ? Env.backendUrl
        : 'http://192.168.1.5:8000';
  }

  /// Envia feedback positivo ou negativo
  ///
  /// [conversationId] - ID da conversa (opcional)
  /// [rating] - 1 para positivo (👍), -1 para negativo (👎)
  /// [comment] - Comentário opcional
  ///
  /// Retorna true se sucesso, false caso contrário
  Future<bool> submitFeedback({
    int? conversationId,
    required int rating,
    String? comment,
  }) async {
    try {
      final url = Uri.parse('$_baseUrl/api/feedback');
      
      final body = jsonEncode({
        if (conversationId != null) 'conversation_id': conversationId,
        'rating': rating,
        if (comment != null && comment.isNotEmpty) 'comment': comment,
      });

      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Timeout ao enviar feedback');
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          debugPrint('✅ Feedback enviado com sucesso: ${data['feedback_id']}');
          return true;
        }
      }

      debugPrint('❌ Erro ao enviar feedback: ${response.statusCode} - ${response.body}');
      return false;
    } catch (e) {
      debugPrint('❌ Erro ao enviar feedback: $e');
      return false;
    }
  }

  /// Envia feedback positivo (👍)
  Future<bool> submitPositiveFeedback({
    int? conversationId,
    String? comment,
  }) async {
    return submitFeedback(
      conversationId: conversationId,
      rating: 1,
      comment: comment,
    );
  }

  /// Envia feedback negativo (👎)
  Future<bool> submitNegativeFeedback({
    int? conversationId,
    String? comment,
  }) async {
    return submitFeedback(
      conversationId: conversationId,
      rating: -1,
      comment: comment,
    );
  }
}

