import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Botão circular metálico com efeito glow elétrico
class MetallicGlowButton extends StatefulWidget {
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final VoidCallback? onLongPressEnd;
  final IconData icon;
  final double size;
  final bool isActive;
  final Color? glowColor;
  final String? tooltip;

  const MetallicGlowButton({
    super.key,
    required this.onTap,
    this.onLongPress,
    this.onLongPressEnd,
    required this.icon,
    this.size = AppTheme.buttonSizeL,
    this.isActive = false,
    this.glowColor,
    this.tooltip,
  });

  @override
  State<MetallicGlowButton> createState() => _MetallicGlowButtonState();
}

class _MetallicGlowButtonState extends State<MetallicGlowButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _glowAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );

    if (widget.isActive) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(MetallicGlowButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive != oldWidget.isActive) {
      if (widget.isActive) {
        _controller.repeat(reverse: true);
      } else {
        _controller.stop();
        _controller.reset();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final glowColor = widget.glowColor ?? AppTheme.primary;
    final glowOpacity = widget.isActive ? _glowAnimation.value : 0.3;

    Widget button = GestureDetector(
      onTap: widget.onTap,
      onLongPress: widget.onLongPress,
      onLongPressEnd: widget.onLongPressEnd != null
          ? (_) => widget.onLongPressEnd!()
          : null,
      child: AnimatedBuilder(
        animation: _glowAnimation,
        builder: (context, child) {
          return Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppTheme.metallicGradient,
              boxShadow: [
                // Sombra principal
                BoxShadow(
                  color: glowColor.withOpacity(glowOpacity * 0.6),
                  blurRadius: 20,
                  spreadRadius: 4,
                ),
                // Sombra secundária (anéis concêntricos)
                BoxShadow(
                  color: glowColor.withOpacity(glowOpacity * 0.4),
                  blurRadius: 30,
                  spreadRadius: 8,
                ),
                // Sombra externa suave
                BoxShadow(
                  color: glowColor.withOpacity(glowOpacity * 0.2),
                  blurRadius: 40,
                  spreadRadius: 12,
                ),
              ],
            ),
            child: Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    Colors.white.withOpacity(0.3),
                    Colors.transparent,
                  ],
                  stops: const [0.0, 0.7],
                ),
              ),
              child: Icon(
                widget.icon,
                size: widget.size * 0.4,
                color: Colors.white,
              ),
            ),
          );
        },
      ),
    );

    if (widget.tooltip != null) {
      return Tooltip(
        message: widget.tooltip!,
        child: button,
      );
    }

    return button;
  }
}

