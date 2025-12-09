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
import '../widgets/voice_button.dart';
import '../widgets/text_input_bar.dart';
import '../widgets/status_bar.dart';
import '../widgets/app_bar_actions.dart';
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
        title: const Text('Jonh Assistant'),
        centerTitle: false,
        actions: [
          AppBarActions(
            onRefresh: () => _refreshApp(context),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Status bar - responsivo
            const StatusBar(),

            // Lista de mensagens
            const Expanded(
              child: MessageList(),
            ),

            // Barra de input de texto (com streaming)
            const TextInputBar(),

            // Botão de voz - responsivo
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: AppTheme.responsiveSpacing(
                  screenWidth,
                  small: AppTheme.spacingM,
                  medium: AppTheme.spacingM,
                  large: AppTheme.spacingXL,
                ),
                vertical: AppTheme.responsiveSpacing(
                  screenWidth,
                  small: AppTheme.spacingS,
                  medium: AppTheme.spacingM,
                  large: AppTheme.spacingM,
                ),
              ),
              child: const VoiceButton(),
            ),
          ],
        ),
      ),
    );
  }
}
