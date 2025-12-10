import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:provider/provider.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/wake_word_backend_service.dart';
import '../services/audio_stream_service.dart';
import '../services/background_wake_word_service.dart';
import '../widgets/message_list.dart';
import '../widgets/text_input_bar.dart';
import '../widgets/app_bar_actions.dart';
import '../widgets/listening_waveform.dart';
import '../theme/app_theme.dart';
import '../utils/error_handler.dart';
import '../utils/audio_validator.dart';
import '../features/home/index.dart' as home;
import '../features/wake_word/index.dart' as wake_word;

/// Tela principal do assistente
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // Flag para controlar se áudio está sendo reproduzido
  bool _isPlayingAudio = false;

  // #region agent log helper
  void _logDebug({
    required String location,
    required String message,
    required String hypothesisId,
    Map<String, dynamic>? data,
    String runId = 'pre-fix',
  }) {
    const sessionId = 'debug-session';
    const logPath = '/home/brunoadsba/john/.cursor/debug.log';
    final entry = {
      'sessionId': sessionId,
      'runId': runId,
      'hypothesisId': hypothesisId,
      'location': location,
      'message': message,
      'data': data ?? {},
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };
    try {
      File(logPath).writeAsStringSync(
        jsonEncode(entry) + '\n',
        mode: FileMode.append,
        flush: true,
      );
    } catch (_) {
      // silencioso para não quebrar UI
    }
  }
  // #endregion

  // Controllers
  late home.HomeController _homeController;
  wake_word.WakeWordHandler? _wakeWordHandler;
  wake_word.BackgroundServiceHandler? _backgroundServiceHandler;

  @override
  void initState() {
    super.initState();
    _initialize();
    _initializeBackgroundService();
  }

  /// Inicializa controllers
  void _initializeControllers() {
    final apiService = context.read<ApiService>();
    final audioService = context.read<AudioService>();
    final audioStream = context.read<AudioStreamService>();

    _homeController = home.HomeController(
      apiService: apiService,
      audioService: audioService,
      wakeWordBackend: context.read<WakeWordBackendService>(),
      audioStream: audioStream,
    );

    _wakeWordHandler = wake_word.WakeWordHandler(
      apiService: apiService,
      audioService: audioService,
      audioStream: audioStream,
    );

    _backgroundServiceHandler = wake_word.BackgroundServiceHandler(
      wakeWordHandler: _wakeWordHandler,
    );
  }

  /// Inicializa serviço de background
  Future<void> _initializeBackgroundService() async {
    if (_backgroundServiceHandler != null) {
      await _backgroundServiceHandler!.initialize(
        context,
        onPlayingStateChanged: (isPlaying) {
          if (mounted) {
            setState(() {
              _isPlayingAudio = isPlaying;
            });
          }
        },
      );
    }
  }

  Future<void> _initialize() async {
    if (!mounted) return;

    _initializeControllers();

    // Usa inicializador centralizado
    final initializer = home.HomeInitializer(
      context: context,
      onPlayingStateChanged: (isPlaying) {
        if (mounted) {
          setState(() {
            _isPlayingAudio = isPlaying;
          });
        }
      },
    );
    await initializer.initialize();
  }

  /// Atualiza e reconecta todos os serviços
  Future<void> _refreshApp(BuildContext context) async {
    if (!mounted) return;

    try {
      ErrorHandler.showInfo(context, 'Atualizando e reconectando...');

      // Usa controller para refresh
      await _homeController.refresh(context);

      if (mounted) {
        ErrorHandler.showSuccess(
            context, 'App atualizado e reconectado com sucesso!');
      }
    } catch (e) {
      if (mounted) {
        ErrorHandler.showError(
          context,
          ErrorHandler.getErrorMessage(e),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            // Avatar do assistente com logo fornecido
            Container(
              width: 32,
              height: 32,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                image: DecorationImage(
                  image: AssetImage('assets/icons/logo sem backgrounf.jpeg'),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Nome completo + status
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'John',
                    style: TextStyle(fontSize: 18),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Consumer<ApiService>(
                    builder: (context, apiService, _) {
                      return Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            apiService.isConnected
                                ? Icons.circle
                                : Icons.circle_outlined,
                            size: 10,
                            color: apiService.isConnected
                                ? Colors.lightGreenAccent
                                : Colors.orangeAccent,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            apiService.isConnected ? 'Online' : 'Reconectando',
                            style: TextStyle(
                              fontSize: 12,
                              color: apiService.isConnected
                                  ? Colors.green
                                  : Colors.grey,
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
        centerTitle: false,
        actions: const [
          AppBarActions(),
        ],
      ),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                // Lista de mensagens (StatusBar removido - agora em Settings)
                const Expanded(
                  child: MessageList(),
                ),

                // Barra de input de texto (com streaming e microfone)
                const TextInputBar(),
              ],
            ),
            // Ondas sonoras durante gravação (sobrepõe o conteúdo)
            Consumer<AudioService>(
              builder: (context, audioService, _) {
                final theme = Theme.of(context);
                final api = context.read<ApiService>();

                if (audioService.isRecording) {
                  return Container(
                    color: theme.scaffoldBackgroundColor.withValues(alpha: 0.65),
                    child: ListeningWaveform(
                      isActive: true,
                      statusLabel: api.isStreaming ? 'Processando...' : 'Ouvindo...',
                      onCancel: () async {
                        _logDebug(
                          location: 'home_screen.dart:overlay',
                          message: 'cancel pressed',
                          hypothesisId: 'H1',
                        );
                        if (audioService.isRecording) {
                          await audioService.cancelRecording();
                        }
                      },
                      onSend: () async {
                        _logDebug(
                          location: 'home_screen.dart:overlay',
                          message: 'send pressed',
                          hypothesisId: 'H1',
                          data: {'isRecording': audioService.isRecording},
                        );
                        if (!audioService.isRecording) {
                          _logDebug(
                            location: 'home_screen.dart:overlay',
                            message: 'send ignored (not recording)',
                            hypothesisId: 'H1',
                          );
                          return;
                        }
                        try {
                          final audioBytes = await audioService.stopRecording();
                          _logDebug(
                            location: 'home_screen.dart:overlay',
                            message: 'stopRecording returned',
                            hypothesisId: 'H1',
                            data: {'bytes': audioBytes?.length},
                          );
                          if (audioBytes == null) return;
                          await api.sendAudio(audioBytes);
                        } catch (e) {
                          _logDebug(
                            location: 'home_screen.dart:overlay',
                            message: 'sendAudio error',
                            hypothesisId: 'H1',
                            data: {'error': e.toString()},
                          );
                          if (mounted) {
                            ErrorHandler.showError(
                              context,
                              ErrorHandler.getErrorMessage(e),
                            );
                          }
                        }
                      },
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ],
        ),
      ),
    );
  }
}
