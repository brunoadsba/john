import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/audio_service.dart';
import '../services/api_service.dart';
import 'package:provider/provider.dart';

/// Widget de ondas sonoras animadas (estilo WhatsApp/Telegram)
/// 
/// Exibe ondas animadas grandes no centro da tela durante a gravação
class ListeningWaveform extends StatefulWidget {
  final bool isActive;
  final Color? color;
  final VoidCallback onCancel;
  final VoidCallback onSend;
  final String statusLabel; // "Ouvindo", "Processando", "Respondendo"

  const ListeningWaveform({
    super.key,
    required this.isActive,
    this.color,
    required this.onCancel,
    required this.onSend,
    this.statusLabel = 'Ouvindo...',
  });

  @override
  State<ListeningWaveform> createState() => _ListeningWaveformState();
}

class _ListeningWaveformState extends State<ListeningWaveform>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    
    // Cria 5 barras de onda
    _controllers = List.generate(
      5,
      (index) => AnimationController(
        vsync: this,
        duration: Duration(milliseconds: 600 + (index * 100)),
      ),
    );

    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0.3, end: 1.0).animate(
        CurvedAnimation(
          parent: controller,
          curve: Curves.easeInOut,
        ),
      );
    }).toList();

    if (widget.isActive) {
      _startAnimation();
    }
  }

  @override
  void didUpdateWidget(ListeningWaveform oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) {
      _startAnimation();
    } else if (!widget.isActive && oldWidget.isActive) {
      _stopAnimation();
    }
  }

  void _startAnimation() {
    for (var controller in _controllers) {
      controller.repeat(reverse: true);
    }
  }

  void _stopAnimation() {
    for (var controller in _controllers) {
      controller.stop();
        controller.reset();
    }
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isActive) {
      return const SizedBox.shrink();
    }

    final color = widget.color ?? AppTheme.primary;
    final api = context.watch<ApiService>();
    final isStreaming = api.isStreaming;
    final label = widget.statusLabel;

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Ícone de microfone
          Icon(
            Icons.mic,
            size: 48,
            color: color,
          ),
          const SizedBox(height: 24),
          // Texto de status
          Text(
            label,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w500,
              color: Theme.of(context).textTheme.bodyLarge?.color,
            ),
          ),
          const SizedBox(height: 32),
          // Ondas animadas
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: List.generate(5, (index) {
              return AnimatedBuilder(
                animation: _animations[index],
                builder: (context, child) {
                  final height = 20.0 + (_animations[index].value * 40.0);
                  return Container(
                    width: 4,
                    height: height,
                    margin: const EdgeInsets.symmetric(horizontal: 3),
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  );
                },
              );
            }),
          ),
          const SizedBox(height: 24),
          // Botões de ação: Descarta / Enviar (ou Parar se streaming)
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade600,
                  foregroundColor: Colors.white,
                ),
                onPressed: widget.onCancel,
                icon: const Icon(Icons.close),
                label: const Text('Descartar'),
              ),
              const SizedBox(width: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                ),
                onPressed: widget.onSend,
                icon: Icon(isStreaming ? Icons.stop : Icons.send),
                label: Text(isStreaming ? 'Parar' : 'Enviar'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

