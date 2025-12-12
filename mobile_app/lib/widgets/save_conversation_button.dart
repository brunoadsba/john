/// Botão flutuante para salvar conversa atual
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/conversation_history_service.dart';
import '../utils/error_handler.dart';
import '../features/conversation_history/conversation_history_screen.dart';

class SaveConversationButton extends StatelessWidget {
  const SaveConversationButton({super.key});

  Future<void> _showSaveDialog(BuildContext context) async {
    final apiService = context.read<ApiService>();
    final sessionId = apiService.sessionId;
    final messages = apiService.messages;

    // Verifica se há mensagens para salvar
    if (sessionId == null || messages.isEmpty) {
      if (context.mounted) {
        ErrorHandler.showInfo(
          context,
          'Nenhuma conversa para salvar. Envie uma mensagem primeiro.',
        );
      }
      return;
    }

    // Gera título sugerido baseado na primeira mensagem do usuário
    String suggestedTitle = 'Nova Conversa';
    final firstUserMessage = messages.firstWhere(
      (m) => m.type.name == 'user',
      orElse: () => messages.first,
    );
    if (firstUserMessage.content.isNotEmpty) {
      suggestedTitle = firstUserMessage.content.length > 30
          ? '${firstUserMessage.content.substring(0, 30)}...'
          : firstUserMessage.content;
    }

    final titleController = TextEditingController(text: suggestedTitle);

    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Salvar Conversa'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Dê um nome para esta conversa:'),
            const SizedBox(height: 16),
            TextField(
              controller: titleController,
              autofocus: true,
              maxLength: 200,
              decoration: const InputDecoration(
                hintText: 'Nome da conversa',
                border: OutlineInputBorder(),
                labelText: 'Título',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Salvar'),
          ),
        ],
      ),
    );

    if (result == true && context.mounted) {
      await _saveConversation(
        context,
        sessionId,
        titleController.text.trim(),
      );
    }

    titleController.dispose();
  }

  Future<void> _saveConversation(
    BuildContext context,
    String sessionId,
    String title,
  ) async {
    if (title.isEmpty) {
      ErrorHandler.showError(context, 'O título não pode estar vazio');
      return;
    }

    try {
      final service = ConversationHistoryService();
      
      // Mostra loading
      if (context.mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const Center(
            child: CircularProgressIndicator(),
          ),
        );
      }

      final conversationId = await service.saveConversation(
        sessionId: sessionId,
        title: title,
      );

      // Fecha loading
      if (context.mounted) {
        Navigator.pop(context);
      }

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Conversa salva: "$title"'),
            action: SnackBarAction(
              label: 'Ver histórico',
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ConversationHistoryScreen(),
                  ),
                );
              },
            ),
          ),
        );
      }
    } catch (e) {
      // Fecha loading se ainda estiver aberto
      if (context.mounted && Navigator.canPop(context)) {
        Navigator.pop(context);
      }

      if (context.mounted) {
        ErrorHandler.showError(
          context,
          'Erro ao salvar conversa: ${ErrorHandler.getErrorMessage(e)}',
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ApiService>(
      builder: (context, apiService, _) {
        // Só mostra o botão se há mensagens
        if (apiService.messages.isEmpty) {
          return const SizedBox.shrink();
        }

        return FloatingActionButton.extended(
          onPressed: () => _showSaveDialog(context),
          icon: const Icon(Icons.bookmark_outline),
          label: const Text('Salvar'),
          tooltip: 'Salvar conversa atual',
        );
      },
    );
  }
}

