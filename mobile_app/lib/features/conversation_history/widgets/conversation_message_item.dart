/// Item de mensagem na visualização de conversa
import 'package:flutter/material.dart';
import '../../../models/conversation_history.dart';
import '../../../models/message.dart';
import '../../../widgets/modern_chat_bubble.dart';

class ConversationMessageItem extends StatelessWidget {
  final ConversationMessage message;

  const ConversationMessageItem({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == 'user';
    
    // Converte ConversationMessage para Message
    final messageModel = Message(
      id: 'conv_${message.content.hashCode}',
      content: message.content,
      type: isUser ? MessageType.user : MessageType.assistant,
      timestamp: DateTime.now(), // ConversationMessage não tem timestamp
      status: MessageStatus.sent,
    );

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor:
                  Theme.of(context).colorScheme.primaryContainer,
              child: Icon(
                Icons.smart_toy,
                size: 20,
                color: Theme.of(context).colorScheme.onPrimaryContainer,
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: ModernChatBubble(
              message: messageModel,
              isUser: isUser,
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor:
                  Theme.of(context).colorScheme.secondaryContainer,
              child: Icon(
                Icons.person,
                size: 20,
                color: Theme.of(context).colorScheme.onSecondaryContainer,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

