import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:async';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

// Helper para criação de File com suporte web/mobile
import 'file_helper.dart';

/// Serviço de streaming de áudio para wake word detection
///
/// Grava pequenos segmentos de áudio continuamente e envia como chunks
class AudioStreamService extends ChangeNotifier {
  final AudioRecorder _recorder = AudioRecorder();

  bool _isStreaming = false;
  bool _hasPermission = false;
  Timer? _recordingTimer;
  String? _streamingPath;
  int _lastChunkPosition = 0;

  bool get isStreaming => _isStreaming;
  bool get hasPermission => _hasPermission;

  /// Callback para enviar chunks de áudio
  Function(Uint8List chunk)? onAudioChunk;

  /// Solicita permissões de microfone
  Future<bool> requestPermissions() async {
    final status = await Permission.microphone.request();
    _hasPermission = status.isGranted;
    notifyListeners();
    return _hasPermission;
  }

  /// Verifica se tem permissão
  Future<bool> checkPermissions() async {
    final status = await Permission.microphone.status;
    _hasPermission = status.isGranted;
    notifyListeners();
    return _hasPermission;
  }


  /// Obtém caminho temporário
  Future<String> _getTempPath() async {
    try {
      if (!kIsWeb) {
        // No mobile, usa temporary directory
        final directory = await getTemporaryDirectory();
        return directory.path;
      } else {
        // No web, não usa arquivos locais
        return '/tmp';
      }
    } catch (e) {
      return '/tmp';
    }
  }

  /// Inicia streaming de áudio
  ///
  /// Grava continuamente e lê chunks do arquivo periodicamente
  Future<void> startStreaming() async {
    if (_isStreaming) {
      debugPrint('⚠️ AudioStreamService: Já está fazendo streaming');
      return;
    }

    // No web, streaming de arquivo não é suportado
    if (kIsWeb) {
      debugPrint(
          '⚠️ AudioStreamService: Streaming de arquivo não suportado no web');
      debugPrint('   Use gravação direta via WebSocket no web');
      return;
    }

    if (!_hasPermission) {
      final granted = await requestPermissions();
      if (!granted) {
        throw Exception('Permissão de microfone negada');
      }
    }

    if (!await _recorder.hasPermission()) {
      throw Exception('Permissão de microfone não concedida');
    }

    try {
      // Verifica se recorder está disponível
      if (await _recorder.isRecording()) {
        debugPrint(
            '⚠️ AudioStreamService: Recorder já está em uso, aguardando...');
        await Future.delayed(const Duration(milliseconds: 500));
        if (await _recorder.isRecording()) {
          throw Exception('Recorder ainda está em uso');
        }
      }

      // Cria arquivo de streaming contínuo
      final tempPath = await _getTempPath();
      _streamingPath =
          '$tempPath/stream_${DateTime.now().millisecondsSinceEpoch}.wav';
      _lastChunkPosition = 0;

      debugPrint(
          '🎤 AudioStreamService: Iniciando gravação contínua em: $_streamingPath');

      // Inicia gravação contínua
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ),
        path: _streamingPath!,
      );

      // Verifica se realmente começou
      await Future.delayed(const Duration(milliseconds: 100));
      if (!await _recorder.isRecording()) {
        throw Exception('Gravação não iniciou corretamente');
      }

      _isStreaming = true;
      notifyListeners();

      debugPrint('✅ AudioStreamService: Streaming iniciado');

      // Lê chunks periodicamente do arquivo (~80ms = ~1280 bytes a 16kHz, 16-bit, mono)
      _recordingTimer =
          Timer.periodic(const Duration(milliseconds: 80), (timer) async {
        if (!_isStreaming || _streamingPath == null) {
          timer.cancel();
          return;
        }

        try {
          if (kIsWeb) {
            // No web, não podemos ler arquivos diretamente
            // O record package no web funciona diferente
            debugPrint(
                '⚠️ AudioStreamService: Streaming de arquivo não suportado no web');
            timer.cancel();
            return;
          }

          if (!kIsWeb && _streamingPath != null) {
            // File só disponível em mobile, não no web
            // Usa helper com import condicional
            final file = createFileForStream(_streamingPath!);
            if (file != null && await file.exists()) {
              final currentSize = await file.length();

              // Se há novos dados desde a última leitura
              if (currentSize > _lastChunkPosition) {
                final fileBytes = await file.readAsBytes();

                // WAV header = 44 bytes
                const headerSize = 44;
                final dataStart = headerSize;

                // Ajusta posição inicial se necessário
                if (_lastChunkPosition < dataStart) {
                  _lastChunkPosition = dataStart;
                }

                if (currentSize > _lastChunkPosition) {
                  // Calcula tamanho do chunk (~1280 bytes = 80ms)
                  final chunkSize = currentSize - _lastChunkPosition;
                  const maxChunkSize = 1280;
                  final actualChunkSize = (chunkSize > maxChunkSize 
                      ? maxChunkSize 
                      : chunkSize) as int;

                  // Extrai chunk (apenas dados PCM, sem header)
                  if (_lastChunkPosition >= dataStart &&
                      _lastChunkPosition + actualChunkSize <= fileBytes.length) {
                    final chunk = Uint8List.sublistView(
                      fileBytes,
                      _lastChunkPosition,
                      _lastChunkPosition + actualChunkSize,
                    );

                    // Envia chunk via callback
                    if (onAudioChunk != null && chunk.isNotEmpty) {
                      onAudioChunk!(chunk);
                    }

                    _lastChunkPosition = _lastChunkPosition + actualChunkSize;
                  }
                }
              }
            }
          }
        } catch (e) {
          debugPrint('❌ AudioStreamService: Erro ao ler chunk: $e');
          // No web, este erro é esperado - não tenta mais
          if (kIsWeb) {
            timer.cancel();
          }
        }
      });
    } catch (e) {
      debugPrint('❌ AudioStreamService: Erro ao iniciar streaming: $e');
      _isStreaming = false;
      _streamingPath = null;
      _lastChunkPosition = 0;
      notifyListeners();
      rethrow;
    }
  }

  /// Para streaming
  Future<void> stopStreaming() async {
    if (!_isStreaming) return;

    debugPrint('🔇 AudioStreamService: Parando streaming...');

    // Cancela timer primeiro
    _recordingTimer?.cancel();
    _recordingTimer = null;

    // Para qualquer gravação ativa
    try {
      if (await _recorder.isRecording()) {
        await _recorder.stop();
        debugPrint('✅ AudioStreamService: Gravação parada');
      }
    } catch (e) {
      debugPrint(
          '⚠️ AudioStreamService: Erro ao parar gravação (pode já estar parado): $e');
    }

    // Remove arquivo temporário (apenas se não for web)
    if (_streamingPath != null && !kIsWeb) {
      try {
        // File só disponível em mobile, não no web
        final file = createFileForStream(_streamingPath!);
        if (file != null && await file.exists()) {
          await file.delete();
        }
      } catch (e) {
        debugPrint(
            '⚠️ AudioStreamService: Não foi possível deletar arquivo de streaming: $e');
      }
      _streamingPath = null;
    } else {
      _streamingPath = null;
    }

    // Aguarda um pouco para garantir que o recorder foi liberado
    await Future.delayed(const Duration(milliseconds: 200));

    _isStreaming = false;
    _lastChunkPosition = 0;
    notifyListeners();

    debugPrint('✅ AudioStreamService: Streaming parado completamente');
  }

  @override
  void dispose() {
    stopStreaming();
    _recorder.dispose();
    // ChangeNotifier dispose
    super.dispose();
  }
}
