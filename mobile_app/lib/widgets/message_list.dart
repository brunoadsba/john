import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/feedback_service.dart';
import '../models/message.dart';
import '../theme/app_theme.dart';

/// Lista de mensagens da conversa
class MessageList extends StatelessWidget {
  const MessageList({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ApiService>(
      builder: (context, apiService, _) {
        final messages = apiService.messages;

        if (messages.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.mic,
                  size: 64,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(height: 16),
                Text(
                  'Diga "Alexa" para começar',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  'Ou toque no botão abaixo',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          );
        }

        final screenWidth = MediaQuery.of(context).size.width;
        final isTablet = AppTheme.isTablet(screenWidth);
        final horizontalPadding = AppTheme.responsiveSpacing(
          screenWidth,
          small: AppTheme.spacingM,
          medium: AppTheme.spacingM,
          large: AppTheme.spacingL,
        );

        return ListView.builder(
          reverse: true,
          padding: EdgeInsets.symmetric(
            horizontal: horizontalPadding,
            vertical: 12,
          ),
          itemCount: messages.length,
          itemBuilder: (context, index) {
            final message = messages[messages.length - 1 - index];
            return MessageBubble(message: message);
          },
        );
      },
    );
  }
}

/// Bolha de mensagem individual
class MessageBubble extends StatelessWidget {
  final Message message;

  const MessageBubble({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.type == MessageType.user;
    final isSystem = message.type == MessageType.system;
    final isError = message.type == MessageType.error;
    final screenWidth = MediaQuery.of(context).size.width;
    final isTablet = AppTheme.isTablet(screenWidth);
    final maxWidth = isTablet ? screenWidth * 0.6 : screenWidth * 0.75;

    if (isSystem) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: AppTheme.spacingS),
        child: Center(
          child: Chip(
            label: Text(
              message.content,
              style: TextStyle(
                  fontSize: isTablet ? AppTheme.fontSizeM : AppTheme.fontSizeS),
            ),
            avatar: Icon(
              Icons.info_outline,
              size: isTablet ? AppTheme.iconSizeM - 2 : AppTheme.iconSizeS + 2,
            ),
          ),
        ),
      );
    }

    return Padding(
      padding: EdgeInsets.symmetric(
        vertical: isTablet ? AppTheme.spacingS : AppTheme.spacingXS,
      ),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: isTablet ? AppTheme.avatarSizeM : AppTheme.avatarSizeS,
              backgroundColor: isError ? AppTheme.error : AppTheme.primary,
              child: Icon(
                isError ? Icons.error : Icons.assistant,
                color: Colors.white,
                size:
                    isTablet ? AppTheme.iconSizeM - 4 : AppTheme.iconSizeS + 2,
              ),
            ),
            SizedBox(width: isTablet ? AppTheme.spacingM : AppTheme.spacingS),
          ],
          ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: Container(
              padding: EdgeInsets.symmetric(
                horizontal: isTablet ? AppTheme.spacingL : AppTheme.spacingM,
                vertical: isTablet ? AppTheme.spacingM : AppTheme.spacingS,
              ),
              decoration: BoxDecoration(
                color: isUser
                    ? AppTheme.primary.withOpacity(0.1)
                    : isError
                        ? AppTheme.error.withOpacity(0.1)
                        : AppTheme.surfaceVariant,
                borderRadius: BorderRadius.circular(
                  isTablet ? AppTheme.radiusL : AppTheme.radiusM,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          message.content,
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                fontSize: isTablet
                                    ? AppTheme.fontSizeL
                                    : AppTheme.fontSizeM,
                              ),
                        ),
                      ),
                      // Indicador de streaming
                      if (message.isProcessing)
                        Padding(
                          padding: const EdgeInsets.only(left: 8.0),
                          child: SizedBox(
                            width: 12,
                            height: 12,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Theme.of(context).colorScheme.primary,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: AppTheme.spacingXS),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _formatTime(message.timestamp),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontSize: isTablet
                                  ? AppTheme.fontSizeS
                                  : AppTheme.fontSizeXS,
                              color: AppTheme.textTertiary,
                            ),
                      ),
                      // Botões de feedback apenas para mensagens do assistant
                      if (!isUser && !isSystem && !isError && !message.isProcessing)
                        _FeedbackButtons(
                          conversationId: message.conversationId,
                          isTablet: isTablet,
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (isUser) ...[
            SizedBox(width: isTablet ? AppTheme.spacingM : AppTheme.spacingS),
            CircleAvatar(
              radius: isTablet ? AppTheme.avatarSizeM : AppTheme.avatarSizeS,
              backgroundColor: AppTheme.primary,
              child: Icon(
                Icons.person,
                color: Colors.white,
                size:
                    isTablet ? AppTheme.iconSizeM - 4 : AppTheme.iconSizeS + 2,
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

/// Botões de feedback (👍/👎) para mensagens do assistant
class _FeedbackButtons extends StatefulWidget {
  final int? conversationId;
  final bool isTablet;

  const _FeedbackButtons({
    required this.conversationId,
    required this.isTablet,
  });

  @override
  State<_FeedbackButtons> createState() => _FeedbackButtonsState();
}

class _FeedbackButtonsState extends State<_FeedbackButtons> {
  final _feedbackService = FeedbackService();
  bool _isSubmitting = false;
  int? _selectedRating; // 1 para positivo, -1 para negativo

  Future<void> _submitFeedback(int rating) async {
    if (_isSubmitting || _selectedRating == rating) return;

    setState(() {
      _isSubmitting = true;
      _selectedRating = rating;
    });

    try {
      final success = await _feedbackService.submitFeedback(
        conversationId: widget.conversationId,
        rating: rating,
      );

      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                rating == 1
                    ? 'Obrigado pelo feedback positivo! 👍'
                    : 'Obrigado pelo feedback. Vamos melhorar! 👎',
              ),
              duration: const Duration(seconds: 2),
              backgroundColor: rating == 1
                  ? Colors.green
                  : Colors.orange,
            ),
          );
        } else {
          setState(() {
            _selectedRating = null; // Reverte se falhar
          });
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Erro ao enviar feedback. Tente novamente.'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _selectedRating = null;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro ao enviar feedback. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final iconSize = widget.isTablet
        ? AppTheme.iconSizeS + 2
        : AppTheme.iconSizeS;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Botão positivo (👍)
        IconButton(
          icon: Icon(
            Icons.thumb_up,
            size: iconSize,
            color: _selectedRating == 1
                ? Colors.green
                : AppTheme.textTertiary,
          ),
          onPressed: _isSubmitting
              ? null
              : () => _submitFeedback(1),
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
          tooltip: 'Feedback positivo',
        ),
        SizedBox(width: widget.isTablet ? AppTheme.spacingXS : 4),
        // Botão negativo (👎)
        IconButton(
          icon: Icon(
            Icons.thumb_down,
            size: iconSize,
            color: _selectedRating == -1
                ? Colors.orange
                : AppTheme.textTertiary,
          ),
          onPressed: _isSubmitting
              ? null
              : () => _submitFeedback(-1),
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
          tooltip: 'Feedback negativo',
        ),
      ],
    );
  }
}
