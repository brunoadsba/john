import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../config/env.dart';

/// Serviço para gerenciar Modo Privacidade no backend
class PrivacyService {
  final String baseUrl = Env.backendUrl;

  /// Ativa ou desativa modo privacidade
  Future<bool> setPrivacyMode(bool enabled) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/settings/privacy-mode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'enabled': enabled}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('🛡️ Privacy Mode: ${data['message']}');
        return true;
      } else {
        debugPrint('❌ Erro ao alterar modo privacidade: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('❌ Erro de conexão: $e');
      return false;
    }
  }

  /// Obtém status atual do modo privacidade
  Future<Map<String, dynamic>?> getStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/settings/privacy-status'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('❌ Erro ao obter status: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      debugPrint('❌ Erro de conexão: $e');
      return null;
    }
  }
}

