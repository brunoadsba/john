import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../theme/responsive.dart';

/// Hero Section - Avatar animado e saudação
class HeroSection extends StatefulWidget {
  const HeroSection({super.key});

  @override
  State<HeroSection> createState() => _HeroSectionState();
}

class _HeroSectionState extends State<HeroSection> {

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Bom dia! ☀️';
    } else if (hour < 18) {
      return 'Boa tarde! 🌤️';
    } else {
      return 'Boa noite! 🌙';
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: Responsive.spacing(context),
        vertical: 32,
      ),
      child: Column(
        children: [
          // Saudação
          Text(
            _getGreeting(),
            style: theme.textTheme.bodyMedium?.copyWith(
              color: isDark
                  ? AppTheme.darkTextSecondary
                  : AppTheme.textSecondary,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 6),
          // Título principal
          Text(
            'Como posso ajudar hoje?',
            style: theme.textTheme.headlineSmall?.copyWith(
              color: isDark
                  ? AppTheme.darkTextPrimary
                  : AppTheme.textPrimary,
              fontSize: 24,
              fontWeight: FontWeight.w700,
              height: 1.2,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 10),
          // Subtítulo
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'Seu assistente inteligente está pronto para criar, buscar e resolver',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: isDark
                    ? AppTheme.darkTextSecondary
                    : AppTheme.textSecondary,
                fontSize: 14,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

