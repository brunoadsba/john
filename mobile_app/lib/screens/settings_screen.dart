import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wake_word_backend_service.dart';
import '../services/api_service.dart';
import '../config/env.dart';

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
          ],
        ),
      ),
    );
  }
}
