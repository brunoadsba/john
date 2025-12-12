import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'app_theme.dart';

/// Helpers para responsividade web e mobile
class Responsive {
  Responsive._();

  /// Retorna se é web
  static bool get isWeb => kIsWeb;

  /// Retorna se é mobile (não web)
  static bool get isMobile => !kIsWeb;

  /// Retorna tamanho da tela
  static Size screenSize(BuildContext context) {
    return MediaQuery.of(context).size;
  }

  /// Retorna largura da tela
  static double screenWidth(BuildContext context) {
    return MediaQuery.of(context).size.width;
  }

  /// Retorna altura da tela
  static double screenHeight(BuildContext context) {
    return MediaQuery.of(context).size.height;
  }

  /// Retorna se é tela pequena
  static bool isSmallScreen(BuildContext context) {
    return AppTheme.isSmallScreen(screenWidth(context));
  }

  /// Retorna se é tablet
  static bool isTablet(BuildContext context) {
    return AppTheme.isTablet(screenWidth(context));
  }

  /// Retorna se é desktop/web
  static bool isDesktop(BuildContext context) {
    return AppTheme.isDesktop(screenWidth(context)) || isWeb;
  }

  /// Retorna espaçamento responsivo
  static double spacing(
    BuildContext context, {
    double? small,
    double? medium,
    double? large,
  }) {
    return AppTheme.responsiveSpacing(
      screenWidth(context),
      small: small ?? AppTheme.spacingS,
      medium: medium ?? AppTheme.spacingM,
      large: large ?? AppTheme.spacingL,
    );
  }

  /// Retorna tamanho de botão responsivo
  static double buttonSize(BuildContext context) {
    final width = screenWidth(context);
    if (AppTheme.isSmallScreen(width)) return AppTheme.buttonSizeM;
    if (AppTheme.isTablet(width)) return AppTheme.buttonSizeL;
    if (isDesktop(context)) return AppTheme.buttonSizeXL;
    return AppTheme.buttonSizeM;
  }

  /// Retorna padding horizontal responsivo
  static EdgeInsets horizontalPadding(BuildContext context) {
    final padding = spacing(context);
    return EdgeInsets.symmetric(horizontal: padding);
  }

  /// Retorna padding vertical responsivo
  static EdgeInsets verticalPadding(BuildContext context) {
    final padding = spacing(context);
    return EdgeInsets.symmetric(vertical: padding);
  }

  /// Retorna padding responsivo completo
  static EdgeInsets padding(BuildContext context) {
    final padding = spacing(context);
    return EdgeInsets.all(padding);
  }

  /// Retorna número de colunas baseado no tamanho da tela
  static int columns(BuildContext context) {
    final width = screenWidth(context);
    if (width < AppTheme.breakpointTablet) return 1;
    if (width < AppTheme.breakpointDesktop) return 2;
    return 3;
  }

  /// Retorna se deve mostrar layout horizontal (desktop)
  static bool shouldShowHorizontalLayout(BuildContext context) {
    return isDesktop(context);
  }

  /// Retorna tamanho máximo de largura para conteúdo
  static double maxContentWidth(BuildContext context) {
    final width = screenWidth(context);
    if (width < AppTheme.breakpointTablet) return double.infinity;
    if (width < AppTheme.breakpointDesktop) return 800;
    return 1200;
  }
}

