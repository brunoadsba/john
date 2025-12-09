/// Serviço de streaming de áudio (para wake word)
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:typed_data';
import 'dart:io';
import 'dart:async';

class AudioStreaming {
  final AudioRecorder _recorder = AudioRecorder();
  bool _isStreaming = false;
  Timer? _streamingTimer;
  String? _streamingPath;
  int _lastChunkPosition = 0;

  bool get isStreaming => _isStreaming;

  /// Callback para enviar chunks de áudio
  Function(Uint8List chunk)? onAudioChunk;

  /// Inicia streaming contínuo de áudio
  Future<void> startStreaming() async {
    if (_isStreaming) {
      debugPrint('⚠️ AudioStreaming: Já está fazendo streaming');
      return;
    }

    final status = await Permission.microphone.status;
    if (!status.isGranted) {
      final newStatus = await Permission.microphone.request();
      if (!newStatus.isGranted) {
        throw Exception('Permissão de microfone negada');
      }
    }

    try {
      final tempPath = await _getTempPath();
      _streamingPath =
          '$tempPath/stream_${DateTime.now().millisecondsSinceEpoch}.wav';

      debugPrint('🎤 AudioStreaming: Iniciando streaming em: $_streamingPath');

      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ),
        path: _streamingPath!,
      );

      _isStreaming = true;
      _lastChunkPosition = 0;

      _streamingTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
        _sendChunk();
      });

      debugPrint('✅ AudioStreaming: Streaming iniciado');
    } catch (e) {
      debugPrint('❌ Erro ao iniciar streaming: $e');
      _isStreaming = false;
      rethrow;
    }
  }

  /// Envia chunk de áudio
  Future<void> _sendChunk() async {
    if (!_isStreaming || _streamingPath == null) return;

    try {
      final file = File(_streamingPath!);
      if (!await file.exists()) return;

      final currentSize = await file.length();
      if (currentSize <= _lastChunkPosition) return;

      final chunkSize = currentSize - _lastChunkPosition;
      final randomAccessFile = await file.open();
      await randomAccessFile.setPosition(_lastChunkPosition);

      final chunk = await randomAccessFile.read(chunkSize);
      await randomAccessFile.close();

      if (chunk.isNotEmpty && onAudioChunk != null) {
        onAudioChunk!(chunk);
      }

      _lastChunkPosition = currentSize;
    } catch (e) {
      debugPrint('⚠️ Erro ao enviar chunk: $e');
    }
  }

  /// Para streaming
  Future<void> stopStreaming() async {
    if (!_isStreaming) {
      debugPrint('⚠️ AudioStreaming: Não está fazendo streaming');
      return;
    }

    try {
      _streamingTimer?.cancel();
      _streamingTimer = null;

      await _recorder.stop();
      _isStreaming = false;

      if (_streamingPath != null) {
        try {
          final file = File(_streamingPath!);
          if (await file.exists()) {
            await file.delete();
          }
        } catch (e) {
          debugPrint('⚠️ Erro ao deletar arquivo de streaming: $e');
        }
        _streamingPath = null;
      }

      _lastChunkPosition = 0;
      debugPrint('✅ AudioStreaming: Streaming parado');
    } catch (e) {
      debugPrint('❌ Erro ao parar streaming: $e');
      _isStreaming = false;
    }
  }

  Future<String> _getTempPath() async {
    final dir = await getTemporaryDirectory();
    return dir.path;
  }

  void dispose() {
    _streamingTimer?.cancel();
    _recorder.dispose();
  }
}

