import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../theme/app_theme.dart';
import '../theme/responsive.dart';
import '../utils/error_handler.dart';
import 'metallic_glow_button.dart';

/// Botão de gravação de voz
class VoiceButton extends StatefulWidget {
  const VoiceButton({super.key});

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton> {

  Future<void> _handlePress() async {
    final audioService = context.read<AudioService>();
    final apiService = context.read<ApiService>();

    if (audioService.isRecording) {
      // Para gravação
      final audioBytes = await audioService.stopRecording();

      if (audioBytes == null) {
        if (mounted) {
          ErrorHandler.showWarning(context, 'Nenhum áudio foi gravado');
        }
        return;
      }

      // Verifica e garante conexão antes de enviar
      if (!apiService.isConnected) {
        if (mounted) {
          ErrorHandler.showInfo(context, 'Reconectando ao servidor...');
        }

        try {
          await apiService.connect();
        } catch (e) {
          if (mounted) {
            ErrorHandler.showConnectionError(
              context,
              onRetry: () async {
                try {
                  await apiService.connect();
                  await apiService.sendAudio(audioBytes);
                } catch (e) {
                  // Erro já será tratado pelo ErrorHandler
                }
              },
            );
          }
          return;
        }
      }

      // Envia para API
      try {
        await apiService.sendAudio(audioBytes);
      } catch (e) {
        if (mounted) {
          ErrorHandler.showAudioError(
            context,
            ErrorHandler.getErrorMessage(e),
            onRetry: () async {
              try {
                await apiService.sendAudio(audioBytes);
              } catch (e) {
                // Erro já será tratado
              }
            },
          );
        }
      }
    } else {
      // Solicita permissão se não tiver
      if (!audioService.hasPermission) {
        final granted = await audioService.requestPermissions();
        if (!granted) {
          if (mounted) {
            ErrorHandler.showPermissionError(
              context,
              'microfone',
              onRequest: () => audioService.requestPermissions(),
            );
          }
          return;
        }
      }

      // Conecta à API se não estiver conectado
      if (!apiService.isConnected) {
        if (mounted) {
          ErrorHandler.showInfo(context, 'Conectando ao servidor...');
        }

        try {
          await apiService.connect();
        } catch (e) {
          if (mounted) {
            ErrorHandler.showConnectionError(
              context,
              onRetry: () => apiService.connect(),
            );
          }
          return;
        }
      }

      // Marca início da gravação para métricas
      apiService.metrics.markRecordingStart();
      
      // Inicia gravação
      try {
        await audioService.startRecording();
      } catch (e) {
        if (mounted) {
          ErrorHandler.showError(
            context,
            ErrorHandler.getErrorMessage(e),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final buttonSize = Responsive.buttonSize(context);

    return Consumer2<AudioService, ApiService>(
      builder: (context, audioService, apiService, _) {
        final isRecording = audioService.isRecording;
        final canRecord = audioService.hasPermission;

        if (!canRecord) {
          // Fallback para botão desabilitado
          return Center(
            child: MetallicGlowButton(
              onTap: null,
              icon: Icons.mic_off,
              size: buttonSize,
              isActive: false,
              glowColor: AppTheme.textTertiary,
              tooltip: 'Permissão de microfone necessária',
            ),
          );
        }

        return Center(
          child: MetallicGlowButton(
            onTap: _handlePress,
            onLongPress: canRecord ? _handlePress : null,
            onLongPressEnd:
                canRecord && isRecording ? () => _handlePress() : null,
            icon: isRecording ? Icons.stop : Icons.mic,
            size: buttonSize,
            isActive: isRecording,
            glowColor: isRecording ? AppTheme.recording : AppTheme.primary,
            tooltip: isRecording ? 'Parar gravação' : 'Gravar áudio',
          ),
        );
      },
    );
  }
}
