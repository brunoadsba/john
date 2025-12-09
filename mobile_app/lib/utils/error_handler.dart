import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/error_monitor.dart';

/// Handler centralizado para erros
///
/// Padroniza exibição de erros em todo o app, garantindo UX consistente
/// e reduzindo duplicação de código.
class ErrorHandler {
  ErrorHandler._(); // Classe utilitária, não instanciável

  /// Exibe erro em SnackBar padrão
  static void showError(
    BuildContext context,
    String message, {
    Duration duration = const Duration(seconds: 5),
    VoidCallback? onRetry,
  }) {
    if (!context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.white, size: 20),
            const SizedBox(width: AppTheme.spacingS),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: AppTheme.error,
        duration: duration,
        behavior: SnackBarBehavior.floating,
        action: onRetry != null
            ? SnackBarAction(
                label: 'Tentar novamente',
                textColor: Colors.white,
                onPressed: onRetry,
              )
            : null,
      ),
    );
  }

  /// Exibe aviso em SnackBar
  static void showWarning(
    BuildContext context,
    String message, {
    Duration duration = const Duration(seconds: 3),
  }) {
    if (!context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.warning_amber_rounded,
                color: Colors.white, size: 20),
            const SizedBox(width: AppTheme.spacingS),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: AppTheme.warning,
        duration: duration,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Exibe informação em SnackBar
  static void showInfo(
    BuildContext context,
    String message, {
    Duration duration = const Duration(seconds: 3),
  }) {
    if (!context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.info_outline, color: Colors.white, size: 20),
            const SizedBox(width: AppTheme.spacingS),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: AppTheme.info,
        duration: duration,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Exibe sucesso em SnackBar
  static void showSuccess(
    BuildContext context,
    String message, {
    Duration duration = const Duration(seconds: 2),
  }) {
    if (!context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle_outline,
                color: Colors.white, size: 20),
            const SizedBox(width: AppTheme.spacingS),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: AppTheme.success,
        duration: duration,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Exibe erro de conexão com opção de retry
  static void showConnectionError(
    BuildContext context, {
    required VoidCallback onRetry,
  }) {
    showError(
      context,
      'Erro ao conectar ao servidor. Verifique se o backend está rodando.',
      onRetry: onRetry,
      duration: const Duration(seconds: 8),
    );
  }

  /// Exibe erro de permissão
  static void showPermissionError(
    BuildContext context,
    String permission, {
    VoidCallback? onRequest,
  }) {
    showError(
      context,
      'Permissão de $permission necessária para usar esta funcionalidade.',
      onRetry: onRequest,
      duration: const Duration(seconds: 5),
    );
  }

  /// Exibe erro de áudio
  static void showAudioError(
    BuildContext context,
    String message, {
    VoidCallback? onRetry,
  }) {
    showError(
      context,
      'Erro ao processar áudio: $message',
      onRetry: onRetry,
      duration: const Duration(seconds: 5),
    );
  }

  /// Converte exceção para mensagem amigável
  static String getErrorMessage(Object error) {
    final message = error.toString().toLowerCase();
    
    // Reporta erro automaticamente
    ErrorMonitor.reportSimpleError(
      error.toString(),
      type: _inferErrorType(message),
    );

    if (message.contains('connection') || message.contains('network')) {
      return 'Erro de conexão. Verifique sua internet.';
    }
    if (message.contains('timeout')) {
      return 'Tempo de espera esgotado. Tente novamente.';
    }
    if (message.contains('permission')) {
      return 'Permissão negada. Verifique as configurações do app.';
    }
    if (message.contains('audio')) {
      return 'Erro ao processar áudio. Tente novamente.';
    }
    if (message.contains('server')) {
      return 'Erro no servidor. Tente novamente mais tarde.';
    }

    // Retorna mensagem original se não conseguir traduzir
    return error.toString().length > 100
        ? '${error.toString().substring(0, 100)}...'
        : error.toString();
  }
  
  /// Infere tipo de erro baseado na mensagem
  static String _inferErrorType(String message) {
    if (message.contains('connection') || 
        message.contains('network') || 
        message.contains('socket') ||
        message.contains('timeout')) {
      return 'network';
    }
    if (message.contains('audio') || 
        message.contains('microphone') || 
        message.contains('record') ||
        message.contains('playback')) {
      return 'audio';
    }
    if (message.contains('permission') || 
        message.contains('denied') || 
        message.contains('access')) {
      return 'permission';
    }
    if (message.contains('crash') || 
        message.contains('exception') || 
        message.contains('fatal')) {
      return 'crash';
    }
    return 'other';
  }
}
