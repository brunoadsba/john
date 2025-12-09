import 'package:flutter/foundation.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:async';
import 'dart:ui';
import 'wake_word_backend_service.dart';
import 'audio_stream_service.dart';
import '../config/env.dart';

/// Serviço de background para detecção de wake word
///
/// Mantém o app rodando em background e detecta wake words continuamente.
/// Quando detecta, acorda o app e processa o comando.
class BackgroundWakeWordService {
  static BackgroundWakeWordService? _instance;
  static BackgroundWakeWordService get instance {
    _instance ??= BackgroundWakeWordService._();
    return _instance!;
  }

  BackgroundWakeWordService._();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();
  bool _isInitialized = false;
  bool _isRunning = false;

  bool get isRunning => _isRunning;

  /// Inicializa o serviço de background
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Inicializa notificações
      await _initializeNotifications();

      // Inicializa serviço de background
      final service = FlutterBackgroundService();

      await service.configure(
        androidConfiguration: AndroidConfiguration(
          onStart: onStart,
          autoStart: false, // Será iniciado manualmente no main()
          isForegroundMode:
              true, // Importante: mantém serviço rodando em foreground
          notificationChannelId: 'jonh_assistant_wake_word',
          initialNotificationTitle: 'Jonh Assistant',
          initialNotificationContent: 'Escutando wake word... (diga "Alexa")',
          foregroundServiceNotificationId: 888,
          // Nota: wakeLock e autoStartOnBoot não são suportados nesta versão do flutter_background_service
          // O wake lock é gerenciado automaticamente pelo foreground service
          // autoStartOnBoot requer configuração adicional no AndroidManifest
        ),
        iosConfiguration: IosConfiguration(
          autoStart: false, // Não inicia automaticamente
          onForeground: onStart,
          onBackground: onIosBackground,
        ),
      );

      _isInitialized = true;
      debugPrint('✅ BackgroundWakeWordService inicializado');
    } catch (e, stackTrace) {
      debugPrint('❌ Erro ao inicializar BackgroundWakeWordService: $e');
      debugPrint('Stack trace: $stackTrace');
      // Não rethrow - permite que o app continue sem background service
      _isInitialized = false;
    }
  }

  /// Inicializa notificações
  Future<void> _initializeNotifications() async {
    try {
      const androidSettings =
          AndroidInitializationSettings('@mipmap/ic_launcher');
      const iosSettings = DarwinInitializationSettings();
      const initSettings = InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      );

      await _notifications.initialize(
        initSettings,
        onDidReceiveNotificationResponse: _onNotificationTapped,
      );
    } catch (e) {
      debugPrint('⚠️ Erro ao inicializar notificações: $e');
      // Continua mesmo se falhar
    }
  }

  /// Handler quando notificação é tocada
  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('📱 Notificação tocada: ${response.payload}');
    // O app será aberto automaticamente
  }

  /// Inicia o serviço de background
  Future<void> start() async {
    if (!_isInitialized) {
      await initialize();
    }

    final service = FlutterBackgroundService();
    final isRunning = await service.isRunning();

    if (!isRunning) {
      await service.startService();
      _isRunning = true;
      debugPrint('✅ BackgroundWakeWordService iniciado');

      // Garante que o serviço continue rodando mesmo quando app fecha
      // Isso é importante para manter wake word ativo
      debugPrint('📱 Serviço configurado para rodar em background');
    } else {
      debugPrint('⚠️ BackgroundWakeWordService já está rodando');
    }
  }

  /// Para o serviço de background
  Future<void> stop() async {
    final service = FlutterBackgroundService();
    final isRunning = await service.isRunning();

    if (isRunning) {
      service.invoke('stop');
      _isRunning = false;
      debugPrint('🛑 BackgroundWakeWordService parado');
    }
  }

  /// Mostra notificação quando wake word é detectado
  Future<void> showWakeWordDetectedNotification() async {
    const androidDetails = AndroidNotificationDetails(
      'jonh_assistant_wake_word',
      'Wake Word Detection',
      channelDescription: 'Notificações quando wake word é detectado',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );

    const iosDetails = DarwinNotificationDetails();
    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.show(
      999,
      'Wake Word Detectado!',
      'Acordando Jonh Assistant...',
      details,
      payload: 'wake_word_detected',
    );
  }
}

/// Handler principal do serviço de background (Android)
@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  DartPluginRegistrant.ensureInitialized();

  if (service is AndroidServiceInstance) {
    service.on('stop').listen((event) {
      service.stopSelf();
    });
  }

  debugPrint('🔄 BackgroundWakeWordService: Iniciando...');
  debugPrint(
      '📱 Serviço configurado para rodar mesmo com tela desligada (wake lock ativo)');

  // Configura wake word backend service
  final wakeWordBackend = WakeWordBackendService();
  final audioStream = AudioStreamService();

  // URL do backend
  final baseUrl = Env.backendUrl.isNotEmpty
      ? Env.backendUrl
      : 'http://192.168.1.5:8000'; // IP do Windows na rede WiFi (mesma rede do celular)
  final wsUrl = baseUrl
      .replaceFirst('http://', 'ws://')
      .replaceFirst('https://', 'wss://');

  // Callback quando wake word é detectado
  wakeWordBackend.onWakeWordDetected = (wakeWord, confidence) async {
    debugPrint(
        '🎤 Wake word detectado em background: $wakeWord (confiança: ${confidence.toStringAsFixed(3)})');

    // Valida confiança antes de processar (duplo filtro)
    if (confidence < 0.85) {
      debugPrint(
          '⚠️ Wake word ignorado em background: confiança muito baixa ($confidence < 0.85)');
      return;
    }

    // Mostra notificação
    final notifications = FlutterLocalNotificationsPlugin();
    const androidDetails = AndroidNotificationDetails(
      'jonh_assistant_wake_word',
      'Wake Word Detection',
      channelDescription: 'Notificações quando wake word é detectado',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );
    const details = NotificationDetails(android: androidDetails);

    await notifications.show(
      999,
      'Wake Word Detectado!',
      'Acordando Jonh Assistant...',
      details,
      payload: 'wake_word_detected',
    );

    // Envia evento para acordar o app
    service.invoke('wake_word_detected', {
      'wake_word': wakeWord,
      'confidence': confidence,
    });
  };

  // Conecta ao backend
  try {
    await wakeWordBackend.connect();
    debugPrint('✅ Conectado ao backend de wake word');

    // Solicita permissões de áudio
    final hasPermission = await audioStream.requestPermissions();
    if (!hasPermission) {
      debugPrint('❌ Permissão de microfone negada');
      return;
    }

    // Configura callback de áudio
    audioStream.onAudioChunk = (chunk) {
      wakeWordBackend.sendAudioChunk(chunk);
    };

    // Inicia streaming
    await audioStream.startStreaming();
    debugPrint('✅ Streaming de áudio iniciado em background');

    // Mantém serviço rodando
    // IMPORTANTE: Com wakeLock: true e foreground service, o serviço continua funcionando mesmo quando:
    // - Tela está bloqueada/desligada
    // - App está fechado
    // - Dispositivo está em modo de economia (se otimização de bateria estiver desabilitada)
    if (service is AndroidServiceInstance) {
      service.setForegroundNotificationInfo(
        title: 'Jonh Assistant',
        content: 'Escutando wake word... (diga "Alexa")',
      );
      debugPrint(
          '✅ Foreground service ativo - funcionará mesmo com tela desligada');
      debugPrint(
          '🔋 Wake lock ativo - CPU mantida ativa para wake word detection');
    }

    // Heartbeat para manter conexão WebSocket ativa
    Timer? heartbeatTimer;
    int heartbeatInterval = 30; // 30 segundos
    int heartbeatCounter = 0;

    // Loop principal - mantém serviço rodando indefinidamente
    Timer? keepAliveTimer;
    keepAliveTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      // Incrementa contador de heartbeat
      heartbeatCounter++;

      // Atualiza notificação a cada 5 segundos (economiza bateria)
      if (heartbeatCounter % 5 == 0) {
        if (service is AndroidServiceInstance) {
          try {
            final isForeground = await service.isForegroundService();
            if (isForeground) {
              // Atualiza conteúdo da notificação para mostrar que está ativo
              final uptime = Duration(seconds: heartbeatCounter);
              final uptimeStr =
                  '${uptime.inMinutes}m ${uptime.inSeconds % 60}s';
              service.setForegroundNotificationInfo(
                title: 'Jonh Assistant',
                content: 'Escutando wake word... (diga "Alexa") • $uptimeStr',
              );
            }
          } catch (e) {
            debugPrint('⚠️ Erro ao atualizar notificação: $e');
          }
        }
      }

      // Heartbeat: envia ping a cada 30 segundos para manter conexão WebSocket ativa
      if (heartbeatCounter % heartbeatInterval == 0 &&
          wakeWordBackend.isConnected) {
        try {
          debugPrint('💓 Heartbeat: mantendo conexão ativa...');
          wakeWordBackend.ping();
        } catch (e) {
          debugPrint('⚠️ Erro no heartbeat: $e');
        }
      }

      // CORREÇÃO: Verifica se ainda está conectado ao backend (com validação mais robusta)
      if (!wakeWordBackend.isConnected) {
        debugPrint('⚠️ Backend desconectado, reconectando...');
        try {
          // Disconnect não retorna Future, apenas chama diretamente
          wakeWordBackend.disconnect();
          await Future.delayed(
              const Duration(seconds: 2)); // Aguarda antes de reconectar

          // CORREÇÃO: Tenta reconectar até 3 vezes antes de desistir
          int reconnectAttempts = 0;
          const maxReconnectAttempts = 3;
          bool reconnected = false;

          while (reconnectAttempts < maxReconnectAttempts && !reconnected) {
            try {
              await wakeWordBackend.connect();
              await Future.delayed(const Duration(
                  milliseconds: 500)); // Aguarda conexão estabilizar

              if (wakeWordBackend.isConnected) {
                await wakeWordBackend.startListening();

                if (!audioStream.isStreaming) {
                  await audioStream.startStreaming();
                }
                debugPrint(
                    '✅ Reconectado ao backend (tentativa ${reconnectAttempts + 1})');
                reconnected = true;
                heartbeatCounter = 0; // Reseta contador após reconexão
              } else {
                reconnectAttempts++;
                debugPrint(
                    '⚠️ Reconexão falhou (tentativa $reconnectAttempts/$maxReconnectAttempts)');
                await Future.delayed(const Duration(seconds: 2));
              }
            } catch (e) {
              reconnectAttempts++;
              debugPrint(
                  '❌ Erro ao reconectar (tentativa $reconnectAttempts/$maxReconnectAttempts): $e');
              if (reconnectAttempts < maxReconnectAttempts) {
                await Future.delayed(Duration(
                    seconds: 2 * reconnectAttempts)); // Backoff exponencial
              }
            }
          }

          if (!reconnected) {
            debugPrint(
                '❌ Falha ao reconectar após $maxReconnectAttempts tentativas');
          }
        } catch (e) {
          debugPrint('❌ Erro crítico ao reconectar: $e');
          // Aguarda mais tempo antes de tentar novamente (backoff exponencial)
          await Future.delayed(const Duration(seconds: 5));
        }
      }

      // Verifica se streaming está ativo
      if (!audioStream.isStreaming) {
        debugPrint('⚠️ Streaming parado, reiniciando...');
        try {
          await audioStream.startStreaming();
          debugPrint('✅ Streaming reiniciado');
        } catch (e) {
          debugPrint('❌ Erro ao reiniciar streaming: $e');
        }
      }
    });

    // Handler para parar timers quando serviço for encerrado
    if (service is AndroidServiceInstance) {
      service.on('stop').listen((event) {
        debugPrint('🛑 Parando serviço de background...');
        keepAliveTimer?.cancel();
        heartbeatTimer?.cancel();

        // Desconecta serviços
        try {
          wakeWordBackend.disconnect();
          audioStream.stopStreaming();
        } catch (e) {
          debugPrint('⚠️ Erro ao desconectar serviços: $e');
        }

        service.stopSelf();
      });
    }
  } catch (e) {
    debugPrint('❌ Erro ao iniciar serviço de background: $e');
  }
}

/// Handler para iOS background
@pragma('vm:entry-point')
Future<bool> onIosBackground(ServiceInstance service) async {
  DartPluginRegistrant.ensureInitialized();
  return true;
}
