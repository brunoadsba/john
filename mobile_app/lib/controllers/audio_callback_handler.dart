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

  /// Configura callback no ApiService (DESABILITADO - TTS desabilitado)
  @Deprecated('TTS desabilitado - agente responde apenas via texto')
  void setupCallback(ApiService apiService, BuildContext context) {
    // NOTA: Callback de áudio removido - TTS desabilitado
    // O agente agora responde apenas via texto, não há mais reprodução de áudio
    // apiService.onAudioReceived não é mais configurado
    debugPrint('ℹ️ AudioCallbackHandler desabilitado - TTS desabilitado');
  }
}

