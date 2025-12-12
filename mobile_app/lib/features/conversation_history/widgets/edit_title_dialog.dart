/// Dialog para editar título da conversa
import 'package:flutter/material.dart';

class EditTitleDialog extends StatelessWidget {
  final String currentTitle;
  final Function(String) onSave;

  const EditTitleDialog({
    super.key,
    required this.currentTitle,
    required this.onSave,
  });

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink(); // Não usado como widget, apenas método estático
  }

  static Future<String?> show(BuildContext context, String currentTitle) async {
    final controller = TextEditingController(text: currentTitle);
    
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Editar título'),
        content: TextField(
          controller: controller,
          autofocus: true,
          maxLength: 200,
          decoration: const InputDecoration(
            hintText: 'Digite o novo título',
            border: OutlineInputBorder(),
          ),
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

    if (result == true) {
      return controller.text.trim();
    }
    return null;
  }
}

