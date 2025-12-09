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

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializa monitoramento global de erros
  ErrorMonitor.initialize();

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

  runApp(const JonhAssistantApp());
}

class JonhAssistantApp extends StatelessWidget {
  const JonhAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ApiService()),
        ChangeNotifierProvider(create: (_) => AudioService()),
        ChangeNotifierProvider(create: (_) => WakeWordService()),
        ChangeNotifierProvider(create: (_) => WakeWordBackendService()),
        ChangeNotifierProvider(create: (_) => AudioStreamService()),
      ],
      child: MaterialApp(
        title: 'Jonh Assistant',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF6366F1), // AppTheme.primary
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          // Aplica design system
          scaffoldBackgroundColor:
              const Color(0xFFF9FAFB), // AppTheme.background
        ),
        darkTheme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF6366F1), // AppTheme.primary
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
        ),
        themeMode: ThemeMode.system,
        home: const HomeScreen(),
      ),
    );
  }
}
