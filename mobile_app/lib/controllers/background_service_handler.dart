import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_background_service/flutter_background_service.dart';
import '../services/background_wake_word_service.dart';
import 'wake_word_handler.dart';

/// Handler para gerenciar serviço de background
/// 
/// Separa lógica de background service da UI.
class BackgroundServiceHandler {
  final WakeWordHandler? wakeWordHandler;

  BackgroundServiceHandler({
    this.wakeWordHandler,
  });

  /// Inicializa serviço de background
  Future<void> initialize(
    BuildContext context, {
    required Function(bool) onPlayingStateChanged,
  }) async {
    // Background service só funciona em Android/iOS, não no web
    if (kIsWeb) {
      debugPrint(
          'ℹ️ Background service não disponível no web (apenas Android/iOS)');
      return;
    }

    try {
      // Verifica se já está rodando (pode ter sido iniciado no main)
      final bgService = FlutterBackgroundService();
      final isRunning = await bgService.isRunning();

      if (!isRunning) {
        // Inicia serviço de background para wake word
        await BackgroundWakeWordService.instance.start();
        debugPrint('✅ Serviço de background iniciado no HomeScreen');
      } else {
        debugPrint('ℹ️ Serviço de background já está rodando');
      }

      // Escuta eventos do background service
      bgService.on('wake_word_detected').listen((event) {
        if (event != null) {
          final wakeWord = event['wake_word'] as String?;
          final confidence = event['confidence'] as double?;
          debugPrint(
              '🎤 Wake word detectado em background: $wakeWord (confiança: $confidence)');

          // Acorda o app e processa comando
          if (wakeWordHandler != null && context.mounted) {
            wakeWordHandler!.onWakeWordDetected(
              context,
              onPlayingStateChanged: onPlayingStateChanged,
            );
          }
        }
      });
    } catch (e) {
      debugPrint('❌ Erro ao iniciar serviço de background: $e');
    }
  }
}

