import 'package:flutter/material.dart';
import '../models/message.dart';
import '../theme/app_theme.dart';

/// Bubble moderna estilo WhatsApp/ChatGPT
/// Suporta agrupamento de mensagens e design moderno
class ModernChatBubble extends StatelessWidget {
  final Message message;
  final bool isUser;
  final bool isLastInGroup;
  final VoidCallback? onLongPress;

  const ModernChatBubble({
    super.key,
    required this.message,
    required this.isUser,
    this.isLastInGroup = true,
    this.onLongPress,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.only(
        left: 8,
        right: 8,
        top: 2,
        bottom: 2,
      ),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Avatar assistente (esquerda)
          if (!isUser && isLastInGroup) _buildAvatar(context, isDark),
          if (!isUser && !isLastInGroup) const SizedBox(width: 34),

          // Bubble content
          Flexible(
            child: GestureDetector(
              onLongPress: () => _showReportMenu(context),
              child: Container(
                constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.75,
                ),
                decoration: BoxDecoration(
                  color: _getBubbleColor(isDark),
                  borderRadius: _getBubbleRadius(),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 1,
                      offset: const Offset(0, 0.5),
                    ),
                  ],
                ),
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 6,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Conteúdo da mensagem
                    Text(
                      message.content,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: isUser && !isDark
                            ? AppTheme.textPrimary
                            : theme.textTheme.bodyMedium?.color,
                      ),
                    ),
                    const SizedBox(height: 2),

                    // Footer (timestamp + status)
                    _buildFooter(theme, isDark),
                  ],
                ),
              ),
            ),
          ),

          // Avatar usuário (direita)
          if (isUser && isLastInGroup) _buildAvatar(context, isDark),
        ],
      ),
    );
  }

  Widget _buildAvatar(BuildContext context, bool isDark) {
    final isAssistant = !isUser;

    return Container(
      width: 26,
      height: 26,
      margin: EdgeInsets.only(
        left: isUser ? 4 : 0,
        right: isUser ? 0 : 4,
      ),
      decoration: BoxDecoration(
        color: isAssistant
            ? Theme.of(context).colorScheme.secondary
            : Theme.of(context).colorScheme.primary,
        shape: BoxShape.circle,
        image: isAssistant
            ? const DecorationImage(
                image: AssetImage('assets/icons/logo sem backgrounf.jpeg'),
                fit: BoxFit.cover,
              )
            : null,
      ),
      child: Center(
        child: isAssistant
            ? const SizedBox.shrink()
            : const Text(
                'V',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
      ),
    );
  }

  Color _getBubbleColor(bool isDark) {
    if (isUser) {
      return isDark ? AppTheme.userBubbleDark : AppTheme.userBubbleLight;
    } else {
      return isDark
          ? AppTheme.assistantBubbleDark
          : AppTheme.assistantBubbleLight;
    }
  }

  BorderRadius _getBubbleRadius() {
    // Ajuste estilo WhatsApp real: 18px, exceto canto cortado do remetente
    return BorderRadius.only(
      topLeft: Radius.circular(isUser ? 18 : 4),
      topRight: const Radius.circular(18),
      bottomLeft: const Radius.circular(18),
      bottomRight: Radius.circular(isUser ? 4 : 18),
    );
  }

  Widget _buildFooter(ThemeData theme, bool isDark) {
    final timestampColor = isUser && !isDark
        ? AppTheme.timestampLight.withOpacity(0.8)
        : AppTheme.timestampDark;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          _formatTimestamp(message.timestamp),
          style: theme.textTheme.bodySmall?.copyWith(
            color: timestampColor,
          ),
        ),
        if (isUser) ...[
          const SizedBox(width: 4),
          _buildStatusIndicator(timestampColor),
        ],
      ],
    );
  }

  Widget _buildStatusIndicator(Color color) {
    // Indicador de status WhatsApp (✓✓)
    return Icon(
      Icons.done_all,
      size: 16,
      color: message.isProcessing
          ? color
          : AppTheme.readStatusBlue, // Azul quando lido
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    // Exibe horário absoluto (HH:mm) estilo WhatsApp
    final hh = timestamp.hour.toString().padLeft(2, '0');
    final mm = timestamp.minute.toString().padLeft(2, '0');
    return '$hh:$mm';
  }

  Future<void> _showReportMenu(BuildContext context) async {
    await showModalBottomSheet<void>(
      context: context,
      builder: (_) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.flag),
                title: const Text('Denunciar mensagem'),
                subtitle: const Text('Reportar como suspeita ou inadequada'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: integrar com backend de denúncias
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Mensagem denunciada. Obrigado pelo aviso.'),
                    ),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.close),
                title: const Text('Cancelar'),
                onTap: () => Navigator.pop(context),
              ),
            ],
          ),
        );
      },
    );
  }
}

