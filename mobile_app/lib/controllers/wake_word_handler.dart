import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/audio_stream_service.dart';
import '../services/audio_recording_config.dart';
import '../utils/error_handler.dart';

/// Handler para gerenciar detecção e processamento de wake word
///
/// Separa lógica complexa de wake word da UI.
class WakeWordHandler {
  final ApiService apiService;
  final AudioService audioService;
  final AudioStreamService? audioStream;

  WakeWordHandler({
    required this.apiService,
    required this.audioService,
    this.audioStream,
  });

  /// Processa quando wake word é detectado
  Future<void> onWakeWordDetected(
    BuildContext context, {
    required Function(bool) onPlayingStateChanged,
  }) async {
    try {
      // Para streaming de wake word se estiver ativo
      if (audioStream != null && audioStream!.isStreaming) {
        await audioStream!.stopStreaming();
        await Future.delayed(const Duration(milliseconds: 300));
      }

      // Feedback visual
      if (context.mounted) {
        ErrorHandler.showInfo(context, 'Wake word detectado! Gravando...');
      }

      // Conecta à API se necessário
      if (!apiService.isConnected) {
        await apiService.connect();
        apiService.startSession();
      }

      // Solicita permissão de microfone se necessário
      if (!audioService.hasPermission) {
        final granted = await audioService.requestPermissions();
        if (!granted) {
          if (context.mounted) {
            ErrorHandler.showPermissionError(
              context,
              'microfone',
              onRequest: () => audioService.requestPermissions(),
            );
          }
          return;
        }
      }

      // Aguarda recorder estar disponível
      await Future.delayed(const Duration(milliseconds: 200));

      // Marca início da gravação para métricas
      apiService.metrics.markRecordingStart();
      
      // Inicia gravação
      try {
        await audioService.startRecording();
      } catch (e) {
        if (context.mounted) {
          ErrorHandler.showError(
            context,
            ErrorHandler.getErrorMessage(e),
          );
        }
        return;
      }

      // Aguarda inicialização do recorder
      await Future.delayed(AudioRecordingConfig.recorderInitDelay);

      if (context.mounted) {
        ErrorHandler.showInfo(context, '🎤 Escutando... Fale seu comando');
      }

      // Aguarda comando do usuário (detecta silêncio ou timeout)
      await _waitForUserCommand();

      // Para gravação e processa
      if (audioService.isRecording) {
        final audioBytes = await audioService.stopRecording();

        if (audioBytes != null && apiService.isConnected) {
          await apiService.sendAudio(audioBytes);

          // Aguarda reprodução terminar
          await _waitForAudioPlayback(context, onPlayingStateChanged);
        }
      }

      // Reinicia streaming de wake word
      await _restartWakeWordStream();
    } catch (e) {
      if (context.mounted) {
        ErrorHandler.showError(
          context,
          ErrorHandler.getErrorMessage(e),
        );
      }
    }
  }

  /// Aguarda comando do usuário (detecta silêncio ou timeout)
  Future<void> _waitForUserCommand() async {
    final maxDuration = AudioRecordingConfig.maxDuration;
    final minDuration = AudioRecordingConfig.minDuration;
    final silenceThreshold = AudioRecordingConfig.silenceThreshold;
    final initialDelay = AudioRecordingConfig.initialDelay;

    DateTime startTime = DateTime.now();
    DateTime lastSoundTime = DateTime.now();
    bool shouldStop = false;
    bool initialDelayPassed = false;

    while (audioService.isRecording && !shouldStop) {
      await Future.delayed(AudioRecordingConfig.checkInterval);

      final elapsed = DateTime.now().difference(startTime);

      if (!initialDelayPassed && elapsed >= initialDelay) {
        initialDelayPassed = true;
        lastSoundTime = DateTime.now();
        continue;
      }

      if (!initialDelayPassed) continue;

      final silenceElapsed = DateTime.now().difference(lastSoundTime);

      if (elapsed >= maxDuration) {
        shouldStop = true;
      } else if (elapsed >= minDuration && silenceElapsed >= silenceThreshold) {
        shouldStop = true;
      }
    }
  }

  /// Aguarda reprodução de áudio terminar
  Future<void> _waitForAudioPlayback(
    BuildContext context,
    Function(bool) onPlayingStateChanged,
  ) async {
    // Aguarda callback ser chamado (até 5 segundos)
    int waitForCallback = 0;
    while (!audioService.isPlaying && waitForCallback < 10) {
      await Future.delayed(const Duration(milliseconds: 500));
      waitForCallback += 1;
    }

    // Aguarda reprodução terminar (máximo 60 segundos)
    int maxWaitTime = 60;
    int waited = 0;
    while (audioService.isPlaying && waited < maxWaitTime) {
      await Future.delayed(const Duration(milliseconds: 500));
      waited += 1;
    }

    // Aguarda um pouco mais para garantir
    await Future.delayed(const Duration(milliseconds: 1000));

    if (context.mounted) {
      onPlayingStateChanged(false);
    }
  }

  /// Reinicia streaming de wake word
  Future<void> _restartWakeWordStream() async {
    if (audioStream != null && !audioStream!.isStreaming) {
      await Future.delayed(const Duration(milliseconds: 300));
      try {
        await audioStream!.startStreaming();
      } catch (e) {
        // Tenta novamente após delay maior
        await Future.delayed(const Duration(seconds: 2));
        try {
          await audioStream!.startStreaming();
        } catch (e2) {
          // Ignora erro - será reconectado automaticamente
        }
      }
    }
  }
}
