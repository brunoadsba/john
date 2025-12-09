import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../screens/settings_screen.dart';

/// Ações da AppBar (botões de ação)
class AppBarActions extends StatelessWidget {
  final VoidCallback onRefresh;

  const AppBarActions({
    super.key,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Botão de atualizar/reconectar
        IconButton(
          icon: const Icon(Icons.refresh),
          tooltip: 'Atualizar e reconectar',
          onPressed: onRefresh,
        ),
        // Botão de conexão
        _ConnectionButton(),
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

/// Botão de conexão (mostra status e permite conectar/desconectar)
class _ConnectionButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<ApiService>(
      builder: (context, apiService, _) {
        return IconButton(
          icon: Icon(
            apiService.isConnected ? Icons.cloud_done : Icons.cloud_off,
            color: apiService.isConnected
                ? AppTheme.success
                : AppTheme.error,
          ),
          tooltip: apiService.isConnected ? 'Desconectar' : 'Conectar',
          onPressed: () async {
            if (apiService.isConnected) {
              apiService.disconnect();
            } else {
              await apiService.connect();
            }
          },
        );
      },
    );
  }
}

