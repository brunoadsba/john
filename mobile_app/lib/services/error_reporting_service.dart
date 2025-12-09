/// Serviço para reportar erros ao backend
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../config/env.dart';

/// Serviço de reporte de erros para comunicação com API
class ErrorReportingService {
  static String get _baseUrl {
    return Env.backendUrl.isNotEmpty
        ? Env.backendUrl
        : 'http://192.168.1.5:8000';
  }

  /// Reporta erro ao backend
  ///
  /// [level] - Nível do erro: 'error', 'warning', 'critical'
  /// [type] - Tipo: 'network', 'audio', 'permission', 'crash', 'other'
  /// [message] - Mensagem do erro
  /// [stackTrace] - Stack trace completo (opcional)
  /// [context] - Contexto adicional (session_id, user_action, etc.)
  ///
  /// Retorna Map com error_id e suggested_solutions, ou null se falhar
  Future<Map<String, dynamic>?> reportError({
    required String level,
    required String type,
    required String message,
    String? stackTrace,
    Map<String, dynamic>? context,
  }) async {
    try {
      // Coleta informações do dispositivo
      final deviceInfo = await _getDeviceInfo();
      
      final url = Uri.parse('$_baseUrl/api/errors/report');
      
      final body = jsonEncode({
        'level': level,
        'type': type,
        'message': message,
        if (stackTrace != null && stackTrace.isNotEmpty) 'stack_trace': stackTrace,
        'device_info': deviceInfo,
        if (context != null) 'context': context,
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
          throw Exception('Timeout ao reportar erro');
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          debugPrint('✅ Erro reportado com sucesso: ${data['error_id']}');
          return {
            'error_id': data['error_id'],
            'suggested_solutions': data['suggested_solutions'] ?? [],
            'severity': data['severity'] ?? 'medium',
          };
        }
      }

      debugPrint('❌ Erro ao reportar erro: ${response.statusCode} - ${response.body}');
      return null;
    } catch (e) {
      debugPrint('❌ Exceção ao reportar erro: $e');
      return null;
    }
  }

  /// Obtém informações do dispositivo
  Future<Map<String, dynamic>> _getDeviceInfo() async {
    try {
      final deviceInfoPlugin = DeviceInfoPlugin();
      final packageInfo = await PackageInfo.fromPlatform();
      
      Map<String, dynamic> deviceInfo = {
        'app_version': packageInfo.version,
        'build_number': packageInfo.buildNumber,
        'package_name': packageInfo.packageName,
      };

      if (defaultTargetPlatform == TargetPlatform.android) {
        final androidInfo = await deviceInfoPlugin.androidInfo;
        deviceInfo.addAll({
          'platform': 'android',
          'os_version': androidInfo.version.release,
          'sdk_int': androidInfo.version.sdkInt,
          'device_model': androidInfo.model,
          'device_brand': androidInfo.brand,
          'device_manufacturer': androidInfo.manufacturer,
        });
      } else if (defaultTargetPlatform == TargetPlatform.iOS) {
        final iosInfo = await deviceInfoPlugin.iosInfo;
        deviceInfo.addAll({
          'platform': 'ios',
          'os_version': iosInfo.systemVersion,
          'device_model': iosInfo.model,
          'device_name': iosInfo.name,
          'device_identifier': iosInfo.identifierForVendor,
        });
      } else {
        deviceInfo['platform'] = 'unknown';
      }

      return deviceInfo;
    } catch (e) {
      debugPrint('⚠️ Erro ao obter informações do dispositivo: $e');
      return {
        'platform': 'unknown',
        'error': e.toString(),
      };
    }
  }

  /// Reporta erro de forma simplificada (usa defaults)
  Future<Map<String, dynamic>?> reportSimpleError(
    String message, {
    String type = 'other',
    String? stackTrace,
    Map<String, dynamic>? context,
  }) {
    return reportError(
      level: 'error',
      type: type,
      message: message,
      stackTrace: stackTrace,
      context: context,
    );
  }
}

