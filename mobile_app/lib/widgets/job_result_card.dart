import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme/app_theme.dart';
import '../theme/responsive.dart';
import 'glassmorphic_container.dart';

/// Dados de uma vaga de emprego
class JobResult {
  final String title;
  final String? snippet;
  final String? url;
  final int? index;

  JobResult({
    required this.title,
    this.snippet,
    this.url,
    this.index,
  });
}

/// Card visual para exibir uma vaga de emprego
class JobResultCard extends StatelessWidget {
  final JobResult job;
  final VoidCallback? onTap;

  const JobResultCard({
    super.key,
    required this.job,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final isWeb = Responsive.isWeb;

    return MouseRegion(
      cursor: isWeb ? SystemMouseCursors.click : MouseCursor.defer,
      child: GestureDetector(
        onTap: () async {
          if (onTap != null) {
            onTap!();
          } else if (job.url != null) {
            await _openUrl(job.url!);
          }
        },
        child: GlassmorphicContainer(
          margin: EdgeInsets.only(
            bottom: Responsive.spacing(context, small: 8, medium: 12),
          ),
          padding: Responsive.padding(context),
          borderRadius: BorderRadius.circular(AppTheme.radiusM),
          blur: 8.0,
          opacity: 0.12,
          boxShadow: [
            BoxShadow(
              color: AppTheme.primary.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Título com índice
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (job.index != null) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppTheme.spacingS,
                        vertical: AppTheme.spacingXS,
                      ),
                      decoration: BoxDecoration(
                        gradient: AppTheme.cyanTealGradient,
                        borderRadius: BorderRadius.circular(AppTheme.radiusS),
                      ),
                      child: Text(
                        '${job.index}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: AppTheme.fontSizeS,
                        ),
                      ),
                    ),
                    const SizedBox(width: AppTheme.spacingS),
                  ],
                  Expanded(
                    child: Text(
                      job.title,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.primary,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              if (job.snippet != null) ...[
                const SizedBox(height: AppTheme.spacingS),
                Text(
                  job.snippet!,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: isDark
                        ? AppTheme.darkTextSecondary
                        : AppTheme.textSecondary,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              if (job.url != null) ...[
                const SizedBox(height: AppTheme.spacingM),
                Row(
                  children: [
                    Icon(
                      Icons.link,
                      size: AppTheme.iconSizeS,
                      color: AppTheme.primary,
                    ),
                    const SizedBox(width: AppTheme.spacingXS),
                    Expanded(
                      child: Text(
                        'Ver detalhes',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AppTheme.primary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _openUrl(String url) async {
    try {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      debugPrint('Erro ao abrir URL: $e');
    }
  }
}

/// Parser para extrair vagas de texto Markdown
class JobResultParser {
  /// Extrai lista de vagas de um texto Markdown formatado pelo backend
  static List<JobResult> parseMarkdown(String markdown) {
    final List<JobResult> jobs = [];
    
    // Regex para encontrar títulos de vagas (### 1. Título)
    final titlePattern = RegExp(r'###\s+(\d+)\.\s+(.+?)(?=\n|$)');
    final urlPattern = RegExp(r'🔗\s+\[([^\]]+)\]\(([^)]+)\)');
    
    final lines = markdown.split('\n');
    String? currentTitle;
    int? currentIndex;
    String? currentSnippet;
    String? currentUrl;
    
    for (int i = 0; i < lines.length; i++) {
      final line = lines[i].trim();
      
      // Detecta título de vaga
      final titleMatch = titlePattern.firstMatch(line);
      if (titleMatch != null) {
        // Salva vaga anterior se existir
        if (currentTitle != null) {
          jobs.add(JobResult(
            title: currentTitle,
            snippet: currentSnippet,
            url: currentUrl,
            index: currentIndex,
          ));
        }
        
        currentIndex = int.tryParse(titleMatch.group(1) ?? '');
        currentTitle = titleMatch.group(2) ?? '';
        currentSnippet = null;
        currentUrl = null;
        continue;
      }
      
      // Detecta URL
      final urlMatch = urlPattern.firstMatch(line);
      if (urlMatch != null) {
        currentUrl = urlMatch.group(2) ?? '';
        continue;
      }
      
      // Detecta snippet (texto que não é título nem URL)
      if (line.isNotEmpty &&
          !line.startsWith('#') &&
          !line.startsWith('🔗') &&
          !line.startsWith('**') &&
          !line.startsWith('---') &&
          !line.startsWith('*') &&
          currentTitle != null &&
          currentSnippet == null) {
        currentSnippet = line.length > 200 ? '${line.substring(0, 200)}...' : line;
      }
    }
    
    // Adiciona última vaga
    if (currentTitle != null) {
      jobs.add(JobResult(
        title: currentTitle,
        snippet: currentSnippet,
        url: currentUrl,
        index: currentIndex,
      ));
    }
    
    return jobs;
  }
}

