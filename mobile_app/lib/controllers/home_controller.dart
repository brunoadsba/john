import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/wake_word_backend_service.dart';
import '../services/audio_stream_service.dart';
import '../utils/error_handler.dart';

/// Controller para gerenciar estado e lógica da HomeScreen
///
/// Separa lógica de negócio da UI, facilitando testes e manutenção.
class HomeController {
  final ApiService apiService;
  final AudioService audioService;
  final WakeWordBackendService wakeWordBackend;
  final AudioStreamService audioStream;

  HomeController({
    required this.apiService,
    required this.audioService,
    required this.wakeWordBackend,
    required this.audioStream,
  });

  /// Inicializa todos os serviços
  Future<void> initialize(BuildContext context) async {
    // Verifica permissões
    await audioService.checkPermissions();

    // Conecta à API automaticamente
    if (!apiService.isConnected) {
      try {
        await apiService.connect();
      } catch (e) {
        if (context.mounted) {
          ErrorHandler.showConnectionError(
            context,
            onRetry: () => initialize(context),
          );
        }
        return;
      }
    }

    // Testa conexão
    try {
      final connected = await apiService.testConnection();
      if (!connected && context.mounted) {
        ErrorHandler.showWarning(
          context,
          'Servidor não está acessível. Verifique se o backend está rodando.',
        );
      }
    } catch (e) {
      // Ignora erro de teste
    }
  }

  /// Configura callback para reproduzir áudio recebido
  void setupAudioCallback(
    BuildContext context,
    Function(bool) onPlayingStateChanged,
  ) {
    apiService.onAudioReceived = (audioBytes) async {
      // Validação já está no ApiService, aqui apenas chama callback
      if (context.mounted) {
        onPlayingStateChanged(true);
      }
      // A reprodução é feita pelo AudioService via callback
    };
  }

  /// Atualiza e reconecta todos os serviços
  Future<void> refresh(BuildContext context) async {
    if (!context.mounted) return;

    try {
      // Para todos os serviços
      if (audioStream.isStreaming) {
        await audioStream.stopStreaming();
      }
      if (wakeWordBackend.isConnected) {
        wakeWordBackend.disconnect();
      }
      if (audioService.isRecording) {
        await audioService.stopRecording();
      }
      if (audioService.isPlaying) {
        await audioService.stopPlaying();
      }
      if (apiService.isConnected) {
        apiService.disconnect();
      }

      // Aguarda um pouco
      await Future.delayed(const Duration(milliseconds: 500));

      // Reinicializa
      await initialize(context);
    } catch (e) {
      if (context.mounted) {
        ErrorHandler.showError(
          context,
          ErrorHandler.getErrorMessage(e),
        );
      }
    }
  }
}
