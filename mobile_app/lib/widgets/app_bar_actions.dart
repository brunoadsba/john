import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../screens/settings_screen.dart';
import '../services/api_service.dart';
import '../features/conversation_history/conversation_history_screen.dart';

/// Ações da AppBar (botões de histórico e configurações)
class AppBarActions extends StatelessWidget {
  const AppBarActions({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Botão de histórico
        IconButton(
          icon: const Icon(Icons.history),
          tooltip: 'Histórico de conversas',
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const ConversationHistoryScreen(),
              ),
            );
          },
        ),
        // Botão de configurações
        IconButton(
          icon: const Icon(Icons.settings),
          tooltip: 'Configurações',
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const SettingsScreen(),
              ),
            );
          },
        ),
      ],
    );
  }
}

