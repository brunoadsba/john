import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../theme/app_theme.dart';
import '../utils/error_handler.dart';

/// Botão de gravação de voz
class VoiceButton extends StatefulWidget {
  const VoiceButton({super.key});

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

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
    final screenWidth = MediaQuery.of(context).size.width;
    final isTablet = AppTheme.isTablet(screenWidth);
    final buttonSize = isTablet ? AppTheme.buttonSizeXL : AppTheme.buttonSizeL;
    final iconSize = isTablet ? AppTheme.iconSizeL : AppTheme.iconSizeL - 8;

    return Consumer2<AudioService, ApiService>(
      builder: (context, audioService, apiService, _) {
        final isRecording = audioService.isRecording;
        final canRecord = audioService.hasPermission;

        return Center(
          child: GestureDetector(
            onTap: _handlePress,
            onLongPress: canRecord ? _handlePress : null,
            onLongPressEnd:
                canRecord && isRecording ? (_) => _handlePress() : null,
            child: AnimatedBuilder(
              animation: _scaleAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: isRecording ? _scaleAnimation.value : 1.0,
                  child: Container(
                    width: buttonSize,
                    height: buttonSize,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isRecording
                          ? AppTheme.recording
                          : canRecord
                              ? AppTheme.primary
                              : AppTheme.textTertiary,
                      boxShadow: isRecording
                          ? AppTheme.recordingShadow
                          : AppTheme.buttonShadow,
                    ),
                    child: Icon(
                      isRecording ? Icons.stop : Icons.mic,
                      size: iconSize,
                      color: Colors.white,
                    ),
                  ),
                );
              },
            ),
          ),
        );
      },
    );
  }
}
