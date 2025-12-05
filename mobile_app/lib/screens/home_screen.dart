import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../widgets/message_list.dart';
import '../widgets/voice_button.dart';

/// Tela principal do assistente
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    final apiService = context.read<ApiService>();
    final audioService = context.read<AudioService>();
    
    // Verifica permissões (mas não solicita automaticamente)
    await audioService.checkPermissions();
    
    // Conecta à API automaticamente
    if (!apiService.isConnected) {
      try {
        await apiService.connect();
        apiService.startSession();
      } catch (e) {
        debugPrint('Erro ao conectar API: $e');
      }
    }
    
    // Testa conexão com API
    final connected = await apiService.testConnection();
    if (!connected && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Não foi possível conectar ao servidor'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Jonh Assistant'),
        actions: [
          Consumer<ApiService>(
            builder: (context, apiService, _) {
              return IconButton(
                icon: Icon(
                  apiService.isConnected 
                    ? Icons.cloud_done 
                    : Icons.cloud_off,
                  color: apiService.isConnected 
                    ? Colors.green 
                    : Colors.red,
                ),
                onPressed: () async {
                  if (apiService.isConnected) {
                    apiService.disconnect();
                  } else {
                    await apiService.connect();
                  }
                },
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: Abrir configurações
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Status bar
          Consumer2<ApiService, AudioService>(
            builder: (context, apiService, audioService, _) {
              return Container(
                padding: const EdgeInsets.all(8),
                color: Theme.of(context).colorScheme.surfaceVariant,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _StatusChip(
                      label: 'API',
                      isActive: apiService.isConnected,
                    ),
                    _StatusChip(
                      label: 'Microfone',
                      isActive: audioService.hasPermission,
                    ),
                    _StatusChip(
                      label: 'Gravando',
                      isActive: audioService.isRecording,
                    ),
                  ],
                ),
              );
            },
          ),
          
          // Lista de mensagens
          const Expanded(
            child: MessageList(),
          ),
          
          // Botão de voz
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: VoiceButton(),
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final String label;
  final bool isActive;

  const _StatusChip({
    required this.label,
    required this.isActive,
  });

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(label),
      avatar: Icon(
        isActive ? Icons.check_circle : Icons.cancel,
        color: isActive ? Colors.green : Colors.red,
        size: 16,
      ),
      backgroundColor: isActive 
        ? Colors.green.withOpacity(0.1)
        : Colors.red.withOpacity(0.1),
    );
  }
}

