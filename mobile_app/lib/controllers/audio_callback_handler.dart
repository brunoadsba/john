import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../utils/audio_validator.dart';
import '../utils/error_handler.dart';

/// Handler para gerenciar callback de áudio recebido
/// 
/// Separa lógica de reprodução de áudio da UI.
class AudioCallbackHandler {
  final AudioService audioService;
  final Function(bool) onPlayingStateChanged;

  AudioCallbackHandler({
    required this.audioService,
    required this.onPlayingStateChanged,
  });

  /// Configura callback no ApiService
  void setupCallback(ApiService apiService, BuildContext context) {
    apiService.onAudioReceived = (audioBytes) async {
      debugPrint('🔊 Áudio recebido do servidor: ${audioBytes.length} bytes');

      // Validação centralizada usando AudioValidator
      final validation = AudioValidator.validateAll(audioBytes);
      if (!validation.isValid) {
        debugPrint('⚠️ Validação falhou: ${validation.errorMessage}');
        if (context.mounted) {
          ErrorHandler.showWarning(
            context,
            AudioValidator.getUserFriendlyErrorMessage(validation.errorMessage),
          );
        }
        return;
      }

      try {
        onPlayingStateChanged(true);
        debugPrint('▶️ Iniciando reprodução...');
        await audioService.playAudio(audioBytes);
        debugPrint('✅ Reprodução concluída');
      } catch (e, stackTrace) {
        debugPrint('❌ Erro ao reproduzir áudio: $e');
        debugPrint('Stack trace: $stackTrace');
        if (context.mounted) {
          ErrorHandler.showAudioError(
            context,
            ErrorHandler.getErrorMessage(e),
          );
        }
      } finally {
        onPlayingStateChanged(false);
        debugPrint('🏁 Flag de reprodução resetada');
      }
    };
  }
}

