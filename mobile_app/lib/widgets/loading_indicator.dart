import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Indicador de carregamento reutilizável
class LoadingIndicator extends StatelessWidget {
  final String? message;
  final double? size;

  const LoadingIndicator({
    super.key,
    this.message,
    this.size,
  });

  @override
  Widget build(BuildContext context) {
    final indicatorSize = size ?? AppTheme.iconSizeM;

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: indicatorSize,
            height: indicatorSize,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primary),
            ),
          ),
          if (message != null) ...[
            SizedBox(height: AppTheme.spacingM),
            Text(
              message!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }
}

/// Indicador de carregamento inline (pequeno)
class InlineLoadingIndicator extends StatelessWidget {
  final double? size;

  const InlineLoadingIndicator({
    super.key,
    this.size,
  });

  @override
  Widget build(BuildContext context) {
    final indicatorSize = size ?? AppTheme.iconSizeS;

    return SizedBox(
      width: indicatorSize,
      height: indicatorSize,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primary),
      ),
    );
  }
}

