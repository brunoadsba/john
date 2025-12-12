import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Indicador de status de conexão (Online/Offline)
class ConnectionStatusIndicator extends StatefulWidget {
  final bool isOnline;
  final String? statusText;

  const ConnectionStatusIndicator({
    super.key,
    required this.isOnline,
    this.statusText,
  });

  @override
  State<ConnectionStatusIndicator> createState() =>
      _ConnectionStatusIndicatorState();
}

class _ConnectionStatusIndicatorState
    extends State<ConnectionStatusIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = widget.isOnline
        ? AppTheme.statusOnline
        : AppTheme.statusOffline;
    final defaultText = widget.isOnline ? 'Online' : 'Offline';

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: statusColor,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: statusColor.withOpacity(0.5),
                      blurRadius: 8,
                      spreadRadius: 2,
                    ),
                  ],
                ),
              ),
            );
          },
        ),
        if (widget.statusText != null || defaultText != null) ...[
          const SizedBox(width: AppTheme.spacingXS),
          Text(
            widget.statusText ?? defaultText,
            style: TextStyle(
              fontSize: AppTheme.fontSizeXS,
              color: statusColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }
}

