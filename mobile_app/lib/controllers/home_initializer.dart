import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/wake_word_backend_service.dart';
import '../services/audio_stream_service.dart';
import 'home_controller.dart';
import '../features/wake_word/index.dart' as wake_word;
import '../features/voice/index.dart' as voice;

/// Inicializador centralizado para HomeScreen
/// 
/// Separa toda lógica de inicialização da UI.
class HomeInitializer {
  final BuildContext context;
  final Function(bool) onPlayingStateChanged;

  HomeInitializer({
    required this.context,
    required this.onPlayingStateChanged,
  });

  /// Inicializa todos os serviços e handlers
  Future<void> initialize() async {
    if (!context.mounted) return;

    final apiService = context.read<ApiService>();
    final audioService = context.read<AudioService>();
    final wakeWordBackend = context.read<WakeWordBackendService>();
    final audioStream = context.read<AudioStreamService>();

    // Configura callback de áudio
    final audioCallbackHandler = voice.AudioCallbackHandler(
      audioService: audioService,
      onPlayingStateChanged: onPlayingStateChanged,
    );
    audioCallbackHandler.setupCallback(apiService, context);

    // Inicializa home controller
    final homeController = HomeController(
      apiService: apiService,
      audioService: audioService,
      wakeWordBackend: wakeWordBackend,
      audioStream: audioStream,
    );
    await homeController.initialize(context);

    // Cria wake word handler
    final wakeWordHandler = wake_word.WakeWordHandler(
      apiService: apiService,
      audioService: audioService,
      audioStream: audioStream,
    );

    // Inicializa wake word detection
    await wake_word.WakeWordInitializer.initialize(
      context,
      wakeWordBackend: wakeWordBackend,
      audioStream: audioStream,
      apiService: apiService,
      audioService: audioService,
      onWakeWordDetected: (wakeWord, confidence) async {
        debugPrint(
            '🎯 Wake word detectado no backend: $wakeWord (confiança: ${confidence.toStringAsFixed(3)})');
        if (context.mounted) {
          await wakeWordHandler.onWakeWordDetected(
            context,
            onPlayingStateChanged: onPlayingStateChanged,
          );
        }
      },
    );
  }
}

