import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:provider/provider.dart';
import 'features/home/index.dart';
import 'services/api_service.dart';
import 'services/audio_service.dart';
import 'services/wake_word_service.dart';
import 'services/wake_word_backend_service.dart';
import 'services/audio_stream_service.dart';
import 'services/background_wake_word_service.dart';
import 'services/error_monitor.dart';
import 'services/theme_service.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializa monitoramento global de erros
  ErrorMonitor.initialize();

  // Inicializa ThemeService e carrega preferência
  final themeService = ThemeService();
  await themeService.loadThemePreference();

  // Inicializa serviço de background APENAS em Android/iOS (não funciona no web)
  if (!kIsWeb) {
    try {
      await BackgroundWakeWordService.instance.initialize();
      // Inicia o serviço imediatamente para que continue rodando mesmo quando app fecha
      await BackgroundWakeWordService.instance.start();
      debugPrint('✅ Background service iniciado no main()');
    } catch (e) {
      debugPrint('⚠️ Erro ao inicializar background service: $e');
      // Continua mesmo se falhar - app deve funcionar sem background service
    }
  } else {
    debugPrint(
        'ℹ️ Background service não disponível no web (apenas Android/iOS)');
  }

  runApp(JonhAssistantApp(themeService: themeService));
}

class JonhAssistantApp extends StatelessWidget {
  final ThemeService themeService;

  const JonhAssistantApp({
    super.key,
    required this.themeService,
  });

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: themeService),
        ChangeNotifierProvider(create: (_) => ApiService()),
        ChangeNotifierProvider(create: (_) => AudioService()),
        ChangeNotifierProvider(create: (_) => WakeWordService()),
        ChangeNotifierProvider(create: (_) => WakeWordBackendService()),
        ChangeNotifierProvider(create: (_) => AudioStreamService()),
      ],
      child: Consumer<ThemeService>(
        builder: (context, themeService, child) {
          return MaterialApp(
            title: 'Jonh Assistant',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeService.themeMode,
            home: const HomeScreen(),
          );
        },
      ),
    );
  }
}
