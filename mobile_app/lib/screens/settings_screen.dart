import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wake_word_backend_service.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/theme_service.dart';
import '../config/env.dart';
import '../widgets/status_bar.dart';
import '../utils/error_handler.dart';

/// Tela de configurações do app
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configurações'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Seção Wake Word (OpenWakeWord)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Wake Word (OpenWakeWord)',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'O wake word é processado no servidor usando OpenWakeWord. Não é necessária configuração adicional.',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const SizedBox(height: 16),
                    Consumer2<WakeWordBackendService, ApiService>(
                      builder: (context, wakeWordBackend, apiService, _) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Status do Backend
                            Row(
                              children: [
                                Icon(
                                  wakeWordBackend.isConnected
                                      ? Icons.check_circle
                                      : Icons.cancel,
                                  color: wakeWordBackend.isConnected
                                      ? Colors.green
                                      : Colors.red,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Backend: ${wakeWordBackend.isConnected ? "Conectado" : "Desconectado"}',
                                  style: TextStyle(
                                    color: wakeWordBackend.isConnected
                                        ? Colors.green
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            // Status da Escuta
                            Row(
                              children: [
                                Icon(
                                  wakeWordBackend.isListening
                                      ? Icons.mic
                                      : Icons.mic_off,
                                  color: wakeWordBackend.isListening
                                      ? Colors.blue
                                      : Colors.grey,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  wakeWordBackend.isListening
                                      ? 'Escutando wake word...'
                                      : 'Wake word não está escutando',
                                  style: TextStyle(
                                    color: wakeWordBackend.isListening
                                        ? Colors.blue
                                        : Colors.grey,
                                  ),
                                ),
                              ],
                            ),
                            if (wakeWordBackend.errorMessage != null) ...[
                              const SizedBox(height: 8),
                              Text(
                                'Erro: ${wakeWordBackend.errorMessage}',
                                style: const TextStyle(color: Colors.red),
                              ),
                            ],
                            // Modelos carregados
                            if (wakeWordBackend.loadedModels.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Text(
                                'Modelos: ${wakeWordBackend.loadedModels.join(", ")}',
                                style: const TextStyle(
                                    color: Colors.grey, fontSize: 12),
                              ),
                            ],
                          ],
                        );
                      },
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),
                    const Text(
                      'Sobre OpenWakeWord:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      '• Wake word processado no servidor',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const Text(
                      '• Modelo padrão: "Alexa"',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const Text(
                      '• Não requer configuração adicional',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const Text(
                      '• Funciona automaticamente quando conectado ao backend',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),

            // Seção Backend
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Servidor Backend',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Consumer<ApiService>(
                      builder: (context, apiService, _) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  apiService.isConnected
                                      ? Icons.cloud_done
                                      : Icons.cloud_off,
                                  color: apiService.isConnected
                                      ? Colors.green
                                      : Colors.red,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Status: ${apiService.isConnected ? "Conectado" : "Desconectado"}',
                                  style: TextStyle(
                                    color: apiService.isConnected
                                        ? Colors.green
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'URL: ${Env.backendUrl}',
                              style: const TextStyle(
                                color: Colors.grey,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),

            // Seção Ações Rápidas
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Ações Rápidas',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Toggle de tema
                    Consumer<ThemeService>(
                      builder: (context, themeService, _) {
                        final isDark = themeService.isDarkMode;
                        return ListTile(
                          leading: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
                          title: Text(isDark ? 'Tema Claro' : 'Tema Escuro'),
                          subtitle: const Text('Alternar entre tema claro e escuro'),
                          trailing: Switch(
                            value: isDark,
                            onChanged: (_) => themeService.toggleTheme(),
                          ),
                          onTap: () => themeService.toggleTheme(),
                        );
                      },
                    ),
                    const Divider(),
                    // Botão de atualizar/reconectar
                    Consumer<ApiService>(
                      builder: (context, apiService, _) {
                        return ListTile(
                          leading: const Icon(Icons.refresh),
                          title: const Text('Atualizar e Reconectar'),
                          subtitle: const Text('Reconecta todos os serviços'),
                          onTap: () async {
                            try {
                              ErrorHandler.showInfo(context, 'Atualizando e reconectando...');
                              apiService.disconnect();
                              await apiService.connect();
                              if (mounted) {
                                ErrorHandler.showSuccess(
                                  context,
                                  'App atualizado e reconectado com sucesso!',
                                );
                              }
                            } catch (e) {
                              if (mounted) {
                                ErrorHandler.showError(
                                  context,
                                  ErrorHandler.getErrorMessage(e),
                                );
                              }
                            }
                          },
                        );
                      },
                    ),
                    const Divider(),
                    // Botão de conexão
                    Consumer<ApiService>(
                      builder: (context, apiService, _) {
                        return ListTile(
                          leading: Icon(
                            apiService.isConnected
                                ? Icons.cloud_done
                                : Icons.cloud_off,
                            color: apiService.isConnected
                                ? Colors.green
                                : Colors.red,
                          ),
                          title: Text(
                            apiService.isConnected ? 'Desconectar' : 'Conectar',
                          ),
                          subtitle: Text(
                            apiService.isConnected
                                ? 'Desconectar do servidor'
                                : 'Conectar ao servidor',
                          ),
                          onTap: () async {
                            if (apiService.isConnected) {
                              apiService.disconnect();
                              if (mounted) {
                                ErrorHandler.showInfo(context, 'Desconectado');
                              }
                            } else {
                              try {
                                ErrorHandler.showInfo(context, 'Conectando...');
                                await apiService.connect();
                                if (mounted) {
                                  ErrorHandler.showSuccess(context, 'Conectado!');
                                }
                              } catch (e) {
                                if (mounted) {
                                  ErrorHandler.showConnectionError(
                                    context,
                                    onRetry: () => apiService.connect(),
                                  );
                                }
                              }
                            }
                          },
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),

            // Seção Status Técnico (StatusBar)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Status Técnico',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Status dos serviços do sistema:',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const SizedBox(height: 16),
                    const StatusBar(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
