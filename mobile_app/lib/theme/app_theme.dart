import 'package:flutter/material.dart';

/// Design System do Jonh Assistant
///
/// Centraliza cores, espaçamentos, tipografia e outros tokens de design
/// para garantir consistência visual em todo o app.
class AppTheme {
  AppTheme._(); // Classe utilitária, não instanciável

  // ============================================================================
  // CORES
  // ============================================================================

  /// Cor primária do app
  static const Color primary = Color(0xFF6366F1); // Indigo-500

  /// Cor primária mais escura (hover/pressed states)
  static const Color primaryDark = Color(0xFF4F46E5); // Indigo-600

  /// Cor primária mais clara (backgrounds sutis)
  static const Color primaryLight = Color(0xFF818CF8); // Indigo-400

  /// Cor de sucesso (verde)
  static const Color success = Color(0xFF10B981); // Emerald-500

  /// Cor de erro (vermelho)
  static const Color error = Color(0xFFEF4444); // Red-500

  /// Cor de aviso (laranja)
  static const Color warning = Color(0xFFF59E0B); // Amber-500

  /// Cor de informação (azul)
  static const Color info = Color(0xFF3B82F6); // Blue-500

  /// Cor de gravação ativa
  static const Color recording = Color(0xFFEF4444); // Red-500

  /// Cor de processamento
  static const Color processing = Color(0xFF3B82F6); // Blue-500

  /// Cor de texto primária
  static const Color textPrimary = Color(0xFF1F2937); // Gray-800

  /// Cor de texto secundária
  static const Color textSecondary = Color(0xFF6B7280); // Gray-500

  /// Cor de texto terciária (subtítulos, timestamps)
  static const Color textTertiary = Color(0xFF9CA3AF); // Gray-400

  /// Cor de background
  static const Color background = Color(0xFFF9FAFB); // Gray-50

  /// Cor de surface (cards, containers)
  static const Color surface = Colors.white;

  /// Cor de surface variant (status bars, dividers)
  static const Color surfaceVariant = Color(0xFFF3F4F6); // Gray-100

  // ============================================================================
  // ESPAÇAMENTOS
  // ============================================================================

  /// Espaçamento extra pequeno (4px)
  static const double spacingXS = 4.0;

  /// Espaçamento pequeno (8px)
  static const double spacingS = 8.0;

  /// Espaçamento médio (16px)
  static const double spacingM = 16.0;

  /// Espaçamento grande (24px)
  static const double spacingL = 24.0;

  /// Espaçamento extra grande (32px)
  static const double spacingXL = 32.0;

  /// Espaçamento extra extra grande (48px)
  static const double spacingXXL = 48.0;

  // ============================================================================
  // BORDAS E RADIUS
  // ============================================================================

  /// Border radius pequeno (8px)
  static const double radiusS = 8.0;

  /// Border radius médio (12px)
  static const double radiusM = 12.0;

  /// Border radius grande (16px)
  static const double radiusL = 16.0;

  /// Border radius extra grande (24px)
  static const double radiusXL = 24.0;

  /// Border radius circular (botões, avatares)
  static const double radiusCircular = 9999.0;

  // ============================================================================
  // TIPOGRAFIA
  // ============================================================================

  /// Tamanho de fonte extra pequeno (10px)
  static const double fontSizeXS = 10.0;

  /// Tamanho de fonte pequeno (12px)
  static const double fontSizeS = 12.0;

  /// Tamanho de fonte médio (14px)
  static const double fontSizeM = 14.0;

  /// Tamanho de fonte grande (16px)
  static const double fontSizeL = 16.0;

  /// Tamanho de fonte extra grande (18px)
  static const double fontSizeXL = 18.0;

  /// Tamanho de fonte título (20px)
  static const double fontSizeTitle = 20.0;

  /// Tamanho de fonte título grande (24px)
  static const double fontSizeTitleL = 24.0;

  // ============================================================================
  // ELEVAÇÕES E SOMBRAS
  // ============================================================================

  /// Sombra padrão para cards
  static List<BoxShadow> get cardShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.05),
          blurRadius: 4.0,
          offset: const Offset(0, 2),
        ),
      ];

  /// Sombra para botões
  static List<BoxShadow> get buttonShadow => [
        BoxShadow(
          color: primary.withOpacity(0.3),
          blurRadius: 8.0,
          offset: const Offset(0, 4),
        ),
      ];

  /// Sombra para botão de gravação ativo
  static List<BoxShadow> get recordingShadow => [
        BoxShadow(
          color: recording.withOpacity(0.4),
          blurRadius: 20.0,
          spreadRadius: 5.0,
          offset: const Offset(0, 0),
        ),
      ];

  // ============================================================================
  // DURAÇÕES (ANIMAÇÕES)
  // ============================================================================

  /// Duração curta de animação (150ms)
  static const Duration animationShort = Duration(milliseconds: 150);

  /// Duração média de animação (300ms)
  static const Duration animationMedium = Duration(milliseconds: 300);

  /// Duração longa de animação (500ms)
  static const Duration animationLong = Duration(milliseconds: 500);

  // ============================================================================
  // TAMANHOS DE COMPONENTES
  // ============================================================================

  /// Tamanho de botão pequeno
  static const double buttonSizeS = 40.0;

  /// Tamanho de botão médio
  static const double buttonSizeM = 56.0;

  /// Tamanho de botão grande
  static const double buttonSizeL = 80.0;

  /// Tamanho de botão extra grande (gravação)
  static const double buttonSizeXL = 100.0;

  /// Tamanho de avatar pequeno
  static const double avatarSizeS = 24.0;

  /// Tamanho de avatar médio
  static const double avatarSizeM = 32.0;

  /// Tamanho de avatar grande
  static const double avatarSizeL = 48.0;

  /// Tamanho de ícone pequeno
  static const double iconSizeS = 16.0;

  /// Tamanho de ícone médio
  static const double iconSizeM = 24.0;

  /// Tamanho de ícone grande
  static const double iconSizeL = 40.0;

  // ============================================================================
  // BREAKPOINTS (RESPONSIVIDADE)
  // ============================================================================

  /// Breakpoint para tela pequena (< 360px)
  static const double breakpointSmall = 360.0;

  /// Breakpoint para tablet (> 600px)
  static const double breakpointTablet = 600.0;

  /// Breakpoint para desktop (> 1200px)
  static const double breakpointDesktop = 1200.0;

  // ============================================================================
  // HELPERS
  // ============================================================================

  /// Retorna se a tela é pequena
  static bool isSmallScreen(double width) => width < breakpointSmall;

  /// Retorna se a tela é tablet
  static bool isTablet(double width) => width >= breakpointTablet;

  /// Retorna se a tela é desktop
  static bool isDesktop(double width) => width >= breakpointDesktop;

  /// Retorna espaçamento responsivo baseado no tamanho da tela
  static double responsiveSpacing(
    double width, {
    double small = spacingS,
    double medium = spacingM,
    double large = spacingL,
  }) {
    if (isSmallScreen(width)) return small;
    if (isTablet(width)) return large;
    return medium;
  }
}

/// Extension para facilitar uso de cores com opacidade
extension AppColorExtensions on Color {
  /// Retorna cor com opacidade específica
  Color withAppOpacity(double opacity) => withOpacity(opacity);

  /// Retorna cor de sucesso
  Color get success => AppTheme.success;

  /// Retorna cor de erro
  Color get error => AppTheme.error;

  /// Retorna cor de aviso
  Color get warning => AppTheme.warning;
}
