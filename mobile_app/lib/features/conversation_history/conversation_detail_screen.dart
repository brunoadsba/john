/// Tela de detalhes de uma conversa salva
import 'package:flutter/material.dart';
import '../../services/conversation_history_service.dart';
import '../../models/conversation_history.dart';
import '../../models/conversation_history_extensions.dart';
import 'widgets/conversation_message_item.dart';
import 'widgets/edit_title_dialog.dart';
import 'widgets/conversation_error_state.dart';

class ConversationDetailScreen extends StatefulWidget {
  final int id;

  const ConversationDetailScreen({super.key, required this.id});

  @override
  State<ConversationDetailScreen> createState() =>
      _ConversationDetailScreenState();
}

class _ConversationDetailScreenState extends State<ConversationDetailScreen> {
  final ConversationHistoryService _service = ConversationHistoryService();
  ConversationHistory? _conversation;
  bool _isLoading = true;
  String? _error;
  final TextEditingController _titleController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadConversation();
  }

  @override
  void dispose() {
    _titleController.dispose();
    super.dispose();
  }

  Future<void> _loadConversation() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final conversation = await _service.getConversation(widget.id);
      setState(() {
        _conversation = conversation;
        _titleController.text = conversation.title;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _updateTitle() async {
    final newTitle = _titleController.text.trim();
    if (newTitle.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('O título não pode estar vazio')),
      );
      return;
    }

    try {
      await _service.updateTitle(widget.id, newTitle);
      setState(() {
        _conversation = _conversation!.copyWith(title: newTitle);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Título atualizado')),
        );
        Navigator.pop(context, true); // Retorna true para indicar atualização
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erro ao atualizar: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _showEditTitleDialog() async {
    final newTitle = await EditTitleDialog.show(
      context,
      _titleController.text,
    );
    if (newTitle != null && newTitle != _titleController.text) {
      _titleController.text = newTitle;
      await _updateTitle();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: _conversation != null
            ? Text(_conversation!.title)
            : const Text('Detalhes da Conversa'),
        actions: [
          if (_conversation != null)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: _showEditTitleDialog,
              tooltip: 'Editar título',
            ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return ConversationErrorState(
        error: _error!,
        onRetry: _loadConversation,
        title: 'Erro ao carregar conversa',
      );
    }

    if (_conversation == null) {
      return const Center(child: Text('Conversa não encontrada'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _conversation!.messages.length,
      itemBuilder: (context, index) {
        final message = _conversation!.messages[index];
        return ConversationMessageItem(message: message);
      },
    );
  }
}

