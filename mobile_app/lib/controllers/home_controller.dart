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

    // Tenta conectar à API automaticamente (não bloqueia se falhar)
    if (!apiService.isConnected) {
      try {
        await apiService.connect();
      } catch (e) {
        // Não bloqueia a inicialização - app funciona offline
        // Conexão será tentada quando usuário interagir
        debugPrint('⚠️ Servidor não disponível no momento. App funcionará em modo offline.');
      }
    }

    // Testa conexão silenciosamente (não mostra erro se falhar)
    try {
      final connected = await apiService.testConnection();
      if (!connected) {
        debugPrint('ℹ️ Servidor offline - funcionalidades que requerem servidor estarão indisponíveis.');
      }
    } catch (e) {
      // Ignora erro de teste - app continua funcionando
    }
  }

  /// Configura callback para reproduzir áudio recebido (DESABILITADO - TTS desabilitado)
  @Deprecated('TTS desabilitado - agente responde apenas via texto')
  void setupAudioCallback(
    BuildContext context,
    Function(bool) onPlayingStateChanged,
  ) {
    // NOTA: Callback de áudio removido - TTS desabilitado
    // O agente agora responde apenas via texto, não há mais reprodução de áudio
    // apiService.onAudioReceived não é mais configurado
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
