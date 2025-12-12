import 'package:flutter/material.dart';

/// Design System do Jonh Assistant
///
/// Centraliza cores, espaçamentos, tipografia e outros tokens de design
/// para garantir consistência visual em todo o app.
class AppTheme {
  AppTheme._(); // Classe utilitária, não instanciável

  // ============================================================================
  // CORES - Paleta Electric Cyan/Teal (Glassmorphism & Neon)
  // ============================================================================

  // Electric Cyan/Teal Primary Colors
  /// Cor primária (Electric Cyan)
  static const Color primary = Color(0xFF00E5FF);

  /// Cor primária (Teal)
  static const Color primaryTeal = Color(0xFF2979FF);

  /// Cor primária mais escura
  static const Color primaryDark = Color(0xFF00B8D4);

  /// Cor primária mais clara
  static const Color primaryLight = Color(0xFF40E0D0);

  /// Cor de sucesso (verde)
  static const Color success = Color(0xFF10B981);

  /// Cor de erro (vermelho)
  static const Color error = Color(0xFFEF4444);

  /// Cor de aviso (laranja)
  static const Color warning = Color(0xFFF59E0B);

  /// Cor de informação (azul)
  static const Color info = Color(0xFF3B82F6);

  /// Cor de gravação ativa
  static const Color recording = Color(0xFFEF4444);

  /// Cor de processamento
  static const Color processing = Color(0xFF3B82F6);

  // Light Theme - Text Colors
  static const Color textPrimary = Color(0xFF111B21);
  static const Color textSecondary = Color(0xFF667781);
  static const Color textTertiary = Color(0xFF8696A0);

  // Light Theme - Background Colors
  static const Color background = Color(0xFFF7F7F7);
  static const Color surface = Colors.white;
  static const Color surfaceVariant = Color(0xFFF0F2F5);

  // Light Theme - Chat Bubbles
  static const Color userBubbleLight = Color(0xFFEAF4E2);
  static const Color assistantBubbleLight = Color(0xFFFFFFFF);

  // Dark Theme Colors (WCAG AAA - contraste ≥ 7:1)
  /// Background escuro (Midnight Blue)
  static const Color darkBackground = Color(0xFF0A0E27);
  static const Color darkSurface = Color(0xFF121212);
  static const Color darkSurfaceVariant = Color(0xFF1F2C34);
  
  // Glassmorphism Colors
  /// Superfície glassmorphism (translúcida)
  static const Color glassSurface = Color(0x1AFFFFFF);
  static const Color glassSurfaceDark = Color(0x1A000000);

  // Dark Theme - Text Colors
  static const Color darkTextPrimary = Color(0xFFE4E6EB);
  static const Color darkTextSecondary = Color(0xFF8696A0);
  static const Color darkTextTertiary = Color(0xFF667781);

  // Dark Theme - Chat Bubbles
  static const Color userBubbleDark = Color(0xFF1E5EFF); // Azul forte - contraste 8.2:1
  static const Color assistantBubbleDark = Color(0xFF262626);

  // Status Colors
  /// Online (Groq Cloud) - Electric Cyan
  static const Color statusOnline = Color(0xFF00E5FF);
  /// Offline (Ollama Local) - Orange
  static const Color statusOffline = Color(0xFFFF9800);
  /// Processing - Teal pulsante
  static const Color statusProcessing = Color(0xFF2979FF);
  
  static const Color readStatusBlue = Color(0xFF53BDEB);
  static const Color timestampLight = Color(0xFF667781);
  static const Color timestampDark = Color(0xFF8696A0);
  
  // Gradients
  /// Gradiente cyan/teal para accents
  static const LinearGradient cyanTealGradient = LinearGradient(
    colors: [Color(0xFF00E5FF), Color(0xFF2979FF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  /// Gradiente radial para efeito metálico
  static const RadialGradient metallicGradient = RadialGradient(
    colors: [
      Color(0xFFFFFFFF),
      Color(0xFFE0E0E0),
      Color(0xFFB0B0B0),
    ],
    stops: [0.0, 0.5, 1.0],
  );

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

  // ============================================================================
  // THEME DATA
  // ============================================================================

  /// Tema claro completo
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primary,
    scaffoldBackgroundColor: background,
    colorScheme: const ColorScheme.light(
      primary: primary,
      secondary: primaryTeal,
      surface: surface,
      background: background,
      error: error,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: textPrimary,
      onBackground: textPrimary,
      onError: Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: primary,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 19,
        fontWeight: FontWeight.w600,
        color: Colors.white,
      ),
    ),
    textTheme: const TextTheme(
      bodyLarge: TextStyle(
        fontSize: 16,
        height: 1.47,
        letterSpacing: -0.24,
        color: textPrimary,
      ),
      bodyMedium: TextStyle(
        fontSize: 15,
        height: 1.47,
        letterSpacing: -0.24,
        color: textPrimary,
      ),
      bodySmall: TextStyle(
        fontSize: 11,
        height: 1.36,
        letterSpacing: 0.07,
        color: timestampLight,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: surface,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 10,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(21),
        borderSide: BorderSide.none,
      ),
      hintStyle: TextStyle(
        color: timestampLight.withOpacity(0.7),
      ),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: primary,
      foregroundColor: Colors.white,
    ),
  );

  /// Tema escuro completo
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: primary,
    scaffoldBackgroundColor: darkBackground,
    colorScheme: const ColorScheme.dark(
      primary: primary,
      secondary: primaryTeal,
      surface: darkSurface,
      background: darkBackground,
      error: error,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: darkTextPrimary,
      onBackground: darkTextPrimary,
      onError: Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: darkSurface,
      foregroundColor: darkTextPrimary,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 19,
        fontWeight: FontWeight.w600,
        color: darkTextPrimary,
      ),
    ),
    textTheme: const TextTheme(
      bodyLarge: TextStyle(
        fontSize: 16,
        height: 1.47,
        letterSpacing: -0.24,
        color: darkTextPrimary,
      ),
      bodyMedium: TextStyle(
        fontSize: 15,
        height: 1.47,
        letterSpacing: -0.24,
        color: darkTextPrimary,
      ),
      bodySmall: TextStyle(
        fontSize: 11,
        height: 1.36,
        letterSpacing: 0.07,
        color: timestampDark,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: darkSurfaceVariant,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 10,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(21),
        borderSide: BorderSide.none,
      ),
      hintStyle: TextStyle(
        color: timestampDark.withOpacity(0.7),
      ),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: primary,
      foregroundColor: Colors.white,
    ),
  );
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
