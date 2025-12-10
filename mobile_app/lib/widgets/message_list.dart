import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import '../services/feedback_service.dart';
import '../services/url_safety_service.dart';
import '../models/message.dart';
import '../theme/app_theme.dart';
import 'modern_chat_bubble.dart';
import 'typing_indicator.dart';

/// Lista de mensagens da conversa
class MessageList extends StatelessWidget {
  const MessageList({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ApiService>(
      builder: (context, apiService, _) {
        final messages = apiService.messages;

        if (messages.isEmpty) {
          final theme = Theme.of(context);
          final primary = theme.colorScheme.primary;
          final secondary = theme.colorScheme.secondary;
          return Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Avatar / logo central
                  Container(
                    width: 88,
                    height: 88,
                    decoration: BoxDecoration(
                      color: secondary.withOpacity(0.12),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.smart_toy,
                      color: secondary,
                      size: 44,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Olá, eu sou o Jonh',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Seu assistente virtual inteligente.',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: theme.textTheme.bodySmall?.color,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 28),
                  // Chips de sugestão
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    alignment: WrapAlignment.center,
                    children: [
                      _SuggestionChip(
                        label: 'Escrever um e-mail',
                        onTap: () => apiService.sendText('Escreva um e-mail profissional'),
                        primary: primary,
                      ),
                      _SuggestionChip(
                        label: 'Dicas de produtividade',
                        onTap: () => apiService.sendText('Quero dicas de produtividade no trabalho'),
                        primary: primary,
                      ),
                      _SuggestionChip(
                        label: 'Criar um produto',
                        onTap: () => apiService.sendText('Me ajude a criar um novo produto'),
                        primary: primary,
                      ),
                      _SuggestionChip(
                        label: 'Contar uma piada',
                        onTap: () => apiService.sendText('Conte uma piada curta e engraçada'),
                        primary: primary,
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Digite uma mensagem ou use o botão de voz',
                    style: theme.textTheme.bodySmall,
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
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
          itemCount: messages.length + (apiService.isStreaming ? 1 : 0),
          itemBuilder: (context, index) {
            // Mostra TypingIndicator no início se está streaming
            if (apiService.isStreaming && index == 0) {
              return const TypingIndicator();
            }

            // Ajusta índice se está streaming
            final messageIndex = apiService.isStreaming ? index - 1 : index;
            final message = messages[messages.length - 1 - messageIndex];
            final previousMessage = messageIndex < messages.length - 1
                ? messages[messages.length - 2 - messageIndex]
                : null;

            // Detecta agrupamento de mensagens
            final isLastInGroup = previousMessage == null ||
                previousMessage.type != message.type ||
                previousMessage.type == MessageType.system ||
                previousMessage.type == MessageType.error ||
                message.type == MessageType.system ||
                message.type == MessageType.error;

            // Cabeçalho de data (estilo WhatsApp)
            final currDate = DateTime(
              message.timestamp.year,
              message.timestamp.month,
              message.timestamp.day,
            );
            final prevDate = previousMessage == null
                ? null
                : DateTime(
                    previousMessage.timestamp.year,
                    previousMessage.timestamp.month,
                    previousMessage.timestamp.day,
                  );
            final isNewDay = prevDate == null || prevDate != currDate;

            final widgets = <Widget>[];

            if (isNewDay) {
              widgets.add(
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context)
                            .colorScheme
                            .surfaceVariant
                            .withOpacity(0.8),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        _formatDateHeader(message.timestamp),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color:
                                  Theme.of(context).textTheme.bodyMedium?.color,
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ),
                  ),
                ),
              );
            }

            // Usa ModernChatBubble para mensagens normais
            if (message.type == MessageType.user ||
                message.type == MessageType.assistant) {
              widgets.add(
                RepaintBoundary(
                  child: _AnimatedMessage(
                    key: ValueKey(message.id),
                    child: ModernChatBubble(
                      message: message,
                      isUser: message.type == MessageType.user,
                      isLastInGroup: isLastInGroup,
                    ),
                  ),
                ),
              );
            } else {
              widgets.add(MessageBubble(message: message));
            }

            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: widgets,
            );
          },
        );
      },
    );
  }
}

String _formatDateHeader(DateTime dt) {
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final yesterday = today.subtract(const Duration(days: 1));
  final target = DateTime(dt.year, dt.month, dt.day);

  if (target == today) return 'Hoje';
  if (target == yesterday) return 'Ontem';

  const weekdays = [
    'Segunda-feira',
    'Terça-feira',
    'Quarta-feira',
    'Quinta-feira',
    'Sexta-feira',
    'Sábado',
    'Domingo',
  ];
  // weekday em Dart: Monday = 1 ... Sunday = 7
  final weekdayLabel = weekdays[(dt.weekday - 1) % 7];
  return '$weekdayLabel, ${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}';
}

class _SuggestionChip extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  final Color primary;

  const _SuggestionChip({
    required this.label,
    required this.onTap,
    required this.primary,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: primary.withOpacity(0.12),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: primary.withOpacity(0.35)),
        ),
        child: Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: primary,
                fontWeight: FontWeight.w600,
              ),
        ),
      ),
    );
  }
}

/// Widget animado para mensagens (slide + fade)
class _AnimatedMessage extends StatefulWidget {
  final Widget child;

  const _AnimatedMessage({
    super.key,
    required this.child,
  });

  @override
  State<_AnimatedMessage> createState() => _AnimatedMessageState();
}

class _AnimatedMessageState extends State<_AnimatedMessage>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.05),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutQuart,
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: widget.child,
      ),
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

    final detectedUrl = UrlSafetyService.detectFirstUrl(message.content);

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
            child: InkWell(
              onTap: detectedUrl == null
                  ? null
                  : () => _handleLinkTap(
                        context,
                        url: detectedUrl,
                        messageText: message.content,
                      ),
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
                            style: Theme.of(context)
                                .textTheme
                                .bodyLarge
                                ?.copyWith(
                                  fontSize: isTablet
                                      ? AppTheme.fontSizeL
                                      : AppTheme.fontSizeM,
                                ),
                          ),
                        ),
                        if (message.isProcessing)
                          const Padding(
                            padding: EdgeInsets.only(left: 8.0),
                            child: SizedBox(
                              width: 12,
                              height: 12,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
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
                        if (!isUser &&
                            !isSystem &&
                            !isError &&
                            !message.isProcessing)
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
          ),
          if (isUser) ...[
            SizedBox(width: isTablet ? AppTheme.spacingM : AppTheme.spacingS),
            CircleAvatar(
              radius: isTablet ? AppTheme.avatarSizeM : AppTheme.avatarSizeS,
              backgroundColor: AppTheme.primary,
              child: const Icon(
                Icons.person,
                color: Colors.white,
                size: 18,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _handleLinkTap(
    BuildContext context, {
    required String url,
    required String messageText,
  }) async {
    final isSuspicious = UrlSafetyService.isSuspicious(url, messageText);

    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        backgroundColor: isSuspicious ? const Color(0xFF8B1A1A) : null,
        title: Row(
          children: [
            Icon(
              isSuspicious ? Icons.warning_amber : Icons.open_in_new,
              color: isSuspicious ? Colors.white : null,
            ),
            const SizedBox(width: 8),
            Text(
              isSuspicious ? 'GOLPE DETECTADO' : 'Abrir link externo',
              style: TextStyle(
                color: isSuspicious ? Colors.white : null,
              ),
            ),
          ],
        ),
        content: Text(
          isSuspicious
              ? 'Esta mensagem contém sinais claros de golpe financeiro.\n\nNUNCA informe senhas, códigos SMS ou dados bancários.\n\nDeseja bloquear e denunciar este contato?'
              : 'Você está prestes a sair do app e abrir:\n\n$url\n\nNunca informe senhas, códigos SMS ou dados bancários.',
          style: TextStyle(
            color: isSuspicious ? Colors.white : null,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancelar',
              style: TextStyle(
                color: isSuspicious ? Colors.white70 : null,
              ),
            ),
          ),
          if (isSuspicious)
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
              ),
              onPressed: () {
                // TODO: bloquear contato + enviar report pro backend
                Navigator.pop(context);
              },
              child: const Text(
                'Bloquear e Denunciar',
                style: TextStyle(color: Colors.white),
              ),
            )
          else
            TextButton(
              onPressed: () async {
                Navigator.pop(context);
                final uri = Uri.parse(url);
                if (await canLaunchUrl(uri)) {
                  await launchUrl(uri, mode: LaunchMode.externalApplication);
                }
              },
              child: const Text('Abrir mesmo assim'),
            ),
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
