import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';

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
      
      if (audioBytes != null && apiService.isConnected) {
        // Envia para API
        try {
          await apiService.sendAudio(audioBytes);
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Erro ao enviar áudio: $e'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    } else {
      // Inicia gravação
      if (!apiService.isConnected) {
        await apiService.connect();
        apiService.startSession();
      }
      
      try {
        await audioService.startRecording();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Erro ao gravar: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<AudioService, ApiService>(
      builder: (context, audioService, apiService, _) {
        final isRecording = audioService.isRecording;
        final canRecord = audioService.hasPermission;
        
        return GestureDetector(
          onTap: canRecord ? _handlePress : null,
          onLongPress: canRecord ? _handlePress : null,
          onLongPressEnd: canRecord && isRecording 
            ? (_) => _handlePress() 
            : null,
          child: AnimatedBuilder(
            animation: _scaleAnimation,
            builder: (context, child) {
              return Transform.scale(
                scale: isRecording ? _scaleAnimation.value : 1.0,
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isRecording
                      ? Colors.red
                      : canRecord
                        ? Theme.of(context).colorScheme.primary
                        : Colors.grey,
                    boxShadow: [
                      BoxShadow(
                        color: (isRecording ? Colors.red : Colors.blue)
                          .withOpacity(0.3),
                        blurRadius: isRecording ? 20 : 10,
                        spreadRadius: isRecording ? 5 : 2,
                      ),
                    ],
                  ),
                  child: Icon(
                    isRecording ? Icons.stop : Icons.mic,
                    size: 40,
                    color: Colors.white,
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}

