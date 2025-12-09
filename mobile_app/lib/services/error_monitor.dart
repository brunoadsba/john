/// Monitor global de erros para captura automática
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'dart:async';
import 'error_reporting_service.dart';

/// Monitor global de erros
/// 
/// Captura automaticamente:
/// - Exceções não tratadas (FlutterError.onError)
/// - Erros de Zone (runZonedGuarded)
/// - Erros assíncronos
class ErrorMonitor {
  static final ErrorReportingService _reportingService = ErrorReportingService();
  static bool _initialized = false;
  static String? _currentSessionId;
  static String? _currentScreen;
  static String? _lastUserAction;

  /// Inicializa monitoramento global de erros
  static void initialize() {
    if (_initialized) {
      debugPrint('⚠️ ErrorMonitor já está inicializado');
      return;
    }

    // Captura erros do Flutter
    FlutterError.onError = (FlutterErrorDetails details) {
      _handleError(
        message: details.exceptionAsString(),
        stackTrace: details.stack?.toString(),
        level: 'error',
        type: 'crash',
        context: {
          'library': details.library,
          'context': details.context?.toString(),
          'information': details.informationCollector?.call().join('\n'),
        },
      );
      
      // Chama handler padrão do Flutter (mostra no console em debug)
      FlutterError.presentError(details);
    };

    // Em release, também captura erros assíncronos
    if (kReleaseMode) {
      PlatformDispatcher.instance.onError = (error, stack) {
        _handleError(
          message: error.toString(),
          stackTrace: stack?.toString(),
          level: 'critical',
          type: 'crash',
        );
        return true;
      };
    }

    _initialized = true;
    debugPrint('✅ ErrorMonitor inicializado');
  }

  /// Define contexto atual (session_id, screen, user_action)
  static void setContext({
    String? sessionId,
    String? screen,
    String? userAction,
  }) {
    if (sessionId != null) _currentSessionId = sessionId;
    if (screen != null) _currentScreen = screen;
    if (userAction != null) _lastUserAction = userAction;
  }

  /// Reporta erro manualmente
  static Future<void> reportError({
    required String message,
    String? stackTrace,
    String level = 'error',
    String type = 'other',
    Map<String, dynamic>? additionalContext,
  }) async {
    await _handleError(
      message: message,
      stackTrace: stackTrace,
      level: level,
      type: type,
      context: additionalContext,
    );
  }

  /// Reporta erro simples (wrapper para reportError)
  static void reportSimpleError(
    String message, {
    String type = 'other',
  }) {
    reportError(
      message: message,
      level: 'error',
      type: type,
    );
  }

  /// Handler interno de erros
  static Future<void> _handleError({
    required String message,
    String? stackTrace,
    required String level,
    required String type,
    Map<String, dynamic>? context,
  }) async {
    try {
      // Prepara contexto completo
      final fullContext = <String, dynamic>{
        if (_currentSessionId != null) 'session_id': _currentSessionId,
        if (_currentScreen != null) 'screen': _currentScreen,
        if (_lastUserAction != null) 'user_action': _lastUserAction,
        'timestamp': DateTime.now().toIso8601String(),
        if (context != null) ...context,
      };

      // Reporta ao backend (não bloqueia UI)
      _reportingService.reportError(
        level: level,
        type: type,
        message: message,
        stackTrace: stackTrace,
        context: fullContext.isNotEmpty ? fullContext : null,
      ).then((result) {
        if (result != null && result['suggested_solutions'] != null) {
          final solutions = result['suggested_solutions'] as List;
          debugPrint('💡 Soluções sugeridas:');
          for (var solution in solutions) {
            debugPrint('   - $solution');
          }
        }
      }).catchError((e) {
        debugPrint('❌ Erro ao reportar erro ao backend: $e');
      });

      // Log local
      debugPrint('📋 Erro capturado: [$level/$type] $message');
      if (stackTrace != null) {
        debugPrint('Stack trace: $stackTrace');
      }
    } catch (e) {
      // Se falhar ao reportar, pelo menos loga localmente
      debugPrint('❌ Erro crítico no ErrorMonitor: $e');
    }
  }

  /// Wrapper para executar código com captura de erros
  static Future<T?> runGuarded<T>(Future<T> Function() fn) async {
    try {
      return await fn();
    } catch (e, stackTrace) {
      await reportError(
        message: e.toString(),
        stackTrace: stackTrace.toString(),
        level: 'error',
        type: 'other',
      );
      return null;
    }
  }

  /// Wrapper síncrono
  static T? runGuardedSync<T>(T Function() fn) {
    try {
      return fn();
    } catch (e, stackTrace) {
      reportError(
        message: e.toString(),
        stackTrace: stackTrace.toString(),
        level: 'error',
        type: 'other',
      );
      return null;
    }
  }
}

