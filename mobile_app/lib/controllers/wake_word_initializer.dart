import 'package:flutter/material.dart';
import '../services/wake_word_backend_service.dart';
import '../services/audio_stream_service.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../utils/error_handler.dart';

/// Inicializador para wake word do backend (OpenWakeWord)
///
/// Separa lógica de inicialização de wake word da UI.
class WakeWordInitializer {
  /// Inicializa wake word detection do backend (OpenWakeWord)
  static Future<void> initialize(
    BuildContext context, {
    required WakeWordBackendService wakeWordBackend,
    required AudioStreamService audioStream,
    required ApiService apiService,
    required AudioService audioService,
    required Function(String, double) onWakeWordDetected,
  }) async {
    try {
      debugPrint('🚀 Inicializando wake word do backend (OpenWakeWord)...');

      // Conecta ao WebSocket de wake word
      await wakeWordBackend.connect();

      // Configura callback quando wake word é detectado
      wakeWordBackend.onWakeWordDetected = onWakeWordDetected;

      // Configura streaming de áudio
      audioStream.onAudioChunk = (chunk) {
        wakeWordBackend.sendAudioChunk(chunk);
      };

      // Inicia streaming de áudio
      await audioStream.startStreaming();

      // Inicia escuta de wake word
      await wakeWordBackend.startListening();

      debugPrint('✅ Wake word do backend inicializado e escutando');

      if (context.mounted) {
        ErrorHandler.showSuccess(context, 'Wake word ativado (OpenWakeWord)');
      }
    } catch (e) {
      debugPrint('❌ Erro ao inicializar wake word do backend: $e');
      if (context.mounted) {
        ErrorHandler.showError(
          context,
          ErrorHandler.getErrorMessage(e),
        );
      }
    }
  }
}
