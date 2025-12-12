import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../theme/responsive.dart';
import 'glassmorphic_container.dart';

/// Chip de sugestão individual
class _SuggestionChip extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback onTap;
  final bool isWeb;

  const _SuggestionChip({
    required this.label,
    this.icon,
    required this.onTap,
    this.isWeb = false,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: isWeb ? SystemMouseCursors.click : MouseCursor.defer,
      child: GestureDetector(
        onTap: onTap,
        child: GlassmorphicContainer(
          padding: EdgeInsets.symmetric(
            horizontal: AppTheme.spacingM,
            vertical: AppTheme.spacingS,
          ),
          margin: EdgeInsets.only(right: AppTheme.spacingS),
          borderRadius: BorderRadius.circular(AppTheme.radiusCircular),
          blur: 5.0,
          opacity: 0.15,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(icon, size: AppTheme.iconSizeS, color: AppTheme.primary),
                const SizedBox(width: AppTheme.spacingXS),
              ],
              Text(
                label,
                style: TextStyle(
                  fontSize: AppTheme.fontSizeM,
                  color: Theme.of(context).textTheme.bodyMedium?.color,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Carrossel horizontal de chips de sugestão
class SuggestionChipsCarousel extends StatelessWidget {
  final List<SuggestionChipData> suggestions;
  final Function(String)? onSuggestionTap;

  const SuggestionChipsCarousel({
    super.key,
    required this.suggestions,
    this.onSuggestionTap,
  });

  @override
  Widget build(BuildContext context) {
    if (suggestions.isEmpty) return const SizedBox.shrink();

    final isWeb = Responsive.isWeb;

    return SizedBox(
      height: 40,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(
          horizontal: Responsive.horizontalPadding(context).horizontal,
        ),
        itemCount: suggestions.length,
        itemBuilder: (context, index) {
          final suggestion = suggestions[index];
          return _SuggestionChip(
            label: suggestion.label,
            icon: suggestion.icon,
            isWeb: isWeb,
            onTap: () {
              if (onSuggestionTap != null) {
                onSuggestionTap!(suggestion.text);
              } else {
                suggestion.onTap();
              }
            },
          );
        },
      ),
    );
  }
}

/// Dados para um chip de sugestão
class SuggestionChipData {
  final String label;
  final String text;
  final IconData? icon;
  final VoidCallback onTap;

  SuggestionChipData({
    required this.label,
    required this.text,
    this.icon,
    required this.onTap,
  });
}

