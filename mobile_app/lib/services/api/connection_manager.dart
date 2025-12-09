/// Gerenciador de conexão e reconexão
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:async';
import '../../config/env.dart';

class ConnectionManager {
  static String get baseUrl => Env.backendUrl.isNotEmpty
      ? Env.backendUrl
      : 'http://192.168.1.5:8000';

  static const int maxReconnectAttempts = 5;
  static const Duration reconnectDelay = Duration(seconds: 3);

  int _reconnectAttempts = 0;
  Timer? _reconnectTimer;

  int get reconnectAttempts => _reconnectAttempts;

  /// Testa conexão com o servidor
  Future<bool> testConnection() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('❌ Erro ao testar conexão: $e');
      return false;
    }
  }

  /// Agenda reconexão
  void scheduleReconnect(Function() onReconnect) {
    if (_reconnectAttempts >= maxReconnectAttempts) {
      debugPrint('❌ Máximo de tentativas de reconexão atingido');
      return;
    }

    _reconnectAttempts++;
    final delay = Duration(
        seconds: reconnectDelay.inSeconds * _reconnectAttempts);

    debugPrint(
        '⏳ Agendando reconexão em ${delay.inSeconds}s (tentativa $_reconnectAttempts/$maxReconnectAttempts)');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(delay, () {
      debugPrint('🔄 Tentando reconectar...');
      onReconnect();
    });
  }

  /// Cancela reconexão agendada
  void cancelReconnect() {
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
  }

  /// Reseta contador de tentativas
  void resetAttempts() {
    _reconnectAttempts = 0;
    cancelReconnect();
  }

  void dispose() {
    cancelReconnect();
  }
}

