/// Serviço para gerenciar histórico de conversas
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/env.dart';
import '../models/conversation_history.dart';

class ConversationHistoryService {
  static const String baseUrl = '${Env.backendUrl}/api/conversations';

  /// Salva uma conversa
  Future<int> saveConversation({
    required String sessionId,
    required String title,
    String? userId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/save'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'title': title,
          'user_id': userId,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        if (data['success'] == true) {
          return data['conversation_id'] as int;
        } else {
          throw Exception('Falha ao salvar conversa: ${data['detail']}');
        }
      } else if (response.statusCode == 404) {
        throw Exception('Sessão não encontrada. Envie uma mensagem primeiro.');
      } else {
        final error = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(error['detail'] ?? 'Erro ao salvar conversa');
      }
    } catch (e) {
      debugPrint('❌ Erro ao salvar conversa: $e');
      rethrow;
    }
  }

  /// Lista conversas salvas
  Future<List<ConversationSummary>> getConversations({
    int limit = 50,
    int offset = 0,
    String? userId,
  }) async {
    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
        'offset': offset.toString(),
      };
      if (userId != null) {
        queryParams['user_id'] = userId;
      }

      final uri = Uri.parse(baseUrl).replace(queryParameters: queryParams);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        if (data['success'] == true) {
          final conversationsJson = data['conversations'] as List<dynamic>;
          return conversationsJson
              .map((json) => ConversationSummary.fromJson(
                  json as Map<String, dynamic>))
              .toList();
        } else {
          throw Exception('Falha ao listar conversas');
        }
      } else {
        final error = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(error['detail'] ?? 'Erro ao listar conversas');
      }
    } catch (e) {
      debugPrint('❌ Erro ao listar conversas: $e');
      rethrow;
    }
  }

  /// Recupera uma conversa específica
  Future<ConversationHistory> getConversation(int conversationId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/$conversationId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        if (data['success'] == true) {
          return ConversationHistory.fromJson(
              data['conversation'] as Map<String, dynamic>);
        } else {
          throw Exception('Falha ao recuperar conversa');
        }
      } else if (response.statusCode == 404) {
        throw Exception('Conversa não encontrada');
      } else {
        final error = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(error['detail'] ?? 'Erro ao recuperar conversa');
      }
    } catch (e) {
      debugPrint('❌ Erro ao recuperar conversa: $e');
      rethrow;
    }
  }

  /// Deleta uma conversa
  Future<void> deleteConversation(int conversationId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/$conversationId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        if (data['success'] != true) {
          throw Exception('Falha ao deletar conversa');
        }
      } else if (response.statusCode == 404) {
        throw Exception('Conversa não encontrada');
      } else {
        final error = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(error['detail'] ?? 'Erro ao deletar conversa');
      }
    } catch (e) {
      debugPrint('❌ Erro ao deletar conversa: $e');
      rethrow;
    }
  }

  /// Atualiza o título de uma conversa
  Future<void> updateTitle(int conversationId, String newTitle) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/$conversationId/title'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'title': newTitle}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        if (data['success'] != true) {
          throw Exception('Falha ao atualizar título');
        }
      } else if (response.statusCode == 404) {
        throw Exception('Conversa não encontrada');
      } else {
        final error = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(error['detail'] ?? 'Erro ao atualizar título');
      }
    } catch (e) {
      debugPrint('❌ Erro ao atualizar título: $e');
      rethrow;
    }
  }
}

