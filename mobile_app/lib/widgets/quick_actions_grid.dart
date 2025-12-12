import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../theme/responsive.dart';

/// Dados de uma ação rápida
class QuickActionData {
  final String icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const QuickActionData({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });
}

/// Grid de ações rápidas (2x2)
class QuickActionsGrid extends StatelessWidget {
  final List<QuickActionData> actions;
  final Function(String)? onActionTap;

  const QuickActionsGrid({
    super.key,
    required this.actions,
    this.onActionTap,
  });

  @override
  Widget build(BuildContext context) {
    if (actions.isEmpty) {
      return const SizedBox.shrink();
    }

    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: Responsive.spacing(context),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Label da seção
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              'AÇÕES RÁPIDAS',
              style: theme.textTheme.labelSmall?.copyWith(
                color: isDark
                    ? AppTheme.darkTextTertiary
                    : AppTheme.textTertiary,
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.8,
              ),
            ),
          ),
          // Grid 2x2
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: 1.1,
            ),
            itemCount: actions.length > 4 ? 4 : actions.length,
            itemBuilder: (context, index) {
              final action = actions[index];
              return _QuickActionCard(
                action: action,
                onTap: () {
                  action.onTap();
                  if (onActionTap != null) {
                    onActionTap!(action.title);
                  }
                },
              );
            },
          ),
        ],
      ),
    );
  }
}

/// Card de ação rápida individual
class _QuickActionCard extends StatelessWidget {
  final QuickActionData action;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.action,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppTheme.primary.withOpacity(0.08),
                AppTheme.primaryTeal.withOpacity(0.08),
              ],
            ),
            border: Border.all(
              color: AppTheme.primary.withOpacity(0.2),
              width: 1,
            ),
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.all(18),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Ícone
              Text(
                action.icon,
                style: const TextStyle(fontSize: 28),
              ),
              const SizedBox(height: 6),
              // Título
              Text(
                action.title,
                style: theme.textTheme.titleSmall?.copyWith(
                  color: isDark
                      ? AppTheme.darkTextPrimary
                      : AppTheme.textPrimary,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 3),
              // Subtítulo
              Text(
                action.subtitle,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: isDark
                      ? AppTheme.darkTextTertiary
                      : AppTheme.textTertiary,
                  fontSize: 10,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

