/// Widget para renderizar conteúdo Markdown nas mensagens do assistente
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../theme/app_theme.dart';

/// Widget que detecta e renderiza Markdown, ou texto simples
class MarkdownContent extends StatelessWidget {
  final String content;
  final bool isDark;
  final TextStyle? textStyle;

  const MarkdownContent({
    super.key,
    required this.content,
    required this.isDark,
    this.textStyle,
  });

  /// Detecta se o conteúdo contém Markdown
  static bool isMarkdown(String text) {
    // Detecta padrões comuns de Markdown
    final markdownPatterns = [
      RegExp(r'^#{1,6}\s+.+', multiLine: true), // Headings
      RegExp(r'\[.+?\]\(.+?\)', multiLine: true), // Links
      RegExp(r'\*\*.*?\*\*', multiLine: true), // Bold
      RegExp(r'`.*?`', multiLine: true), // Code
      RegExp(r'^\s*[-*+]\s+', multiLine: true), // Lists
      RegExp(r'^\s*\d+\.\s+', multiLine: true), // Numbered lists
    ];

    return markdownPatterns.any((pattern) => pattern.hasMatch(text));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final effectiveTextStyle = textStyle ??
        theme.textTheme.bodyMedium?.copyWith(
          color: isDark
              ? AppTheme.assistantBubbleDark
              : theme.textTheme.bodyMedium?.color,
        );

    // Se não for Markdown, renderiza como texto simples
    if (!isMarkdown(content)) {
      return Text(
        content,
        style: effectiveTextStyle,
      );
    }

    // Renderiza Markdown
    return MarkdownBody(
      data: content,
      styleSheet: MarkdownStyleSheet(
        p: effectiveTextStyle,
        h1: effectiveTextStyle?.copyWith(
          fontSize: (effectiveTextStyle?.fontSize ?? 14) * 1.4,
          fontWeight: FontWeight.bold,
        ),
        h2: effectiveTextStyle?.copyWith(
          fontSize: (effectiveTextStyle?.fontSize ?? 14) * 1.3,
          fontWeight: FontWeight.bold,
        ),
        h3: effectiveTextStyle?.copyWith(
          fontSize: (effectiveTextStyle?.fontSize ?? 14) * 1.2,
          fontWeight: FontWeight.bold,
        ),
        strong: effectiveTextStyle?.copyWith(
          fontWeight: FontWeight.bold,
        ),
        em: effectiveTextStyle?.copyWith(
          fontStyle: FontStyle.italic,
        ),
        code: effectiveTextStyle?.copyWith(
          backgroundColor: isDark
              ? Colors.grey[800]
              : Colors.grey[200],
          fontFamily: 'monospace',
        ),
        listBullet: effectiveTextStyle,
        a: effectiveTextStyle?.copyWith(
          color: isDark
              ? Colors.lightBlue[300]
              : Colors.blue[700],
          decoration: TextDecoration.underline,
        ),
      ).copyWith(
        blockquoteDecoration: BoxDecoration(
          border: Border(
            left: BorderSide(
              color: isDark ? Colors.grey[600]! : Colors.grey[400]!,
              width: 4,
            ),
          ),
        ),
      ),
      onTapLink: (text, href, title) {
        // O URL será aberto pelo url_launcher no MessageList
        // Aqui apenas fazemos log
        debugPrint('Link clicado: $href');
      },
    );
  }
}

