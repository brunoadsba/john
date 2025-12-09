/// Serviço de gravação de áudio
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:typed_data';
import 'dart:io';

class AudioRecording {
  final AudioRecorder _recorder = AudioRecorder();
  bool _isRecording = false;
  bool _hasPermission = false;

  bool get isRecording => _isRecording;
  bool get hasPermission => _hasPermission;

  /// Solicita permissões de microfone
  Future<bool> requestPermissions() async {
    final status = await Permission.microphone.request();
    _hasPermission = status.isGranted;
    return _hasPermission;
  }

  /// Verifica se tem permissão
  Future<bool> checkPermissions() async {
    final status = await Permission.microphone.status;
    _hasPermission = status.isGranted;
    return _hasPermission;
  }

  /// Inicia gravação
  Future<String> startRecording() async {
    if (_isRecording) {
      debugPrint('⚠️ AudioRecording: Já está gravando');
      throw Exception('Já está gravando');
    }

    if (!_hasPermission) {
      final granted = await requestPermissions();
      if (!granted) {
        throw Exception('Permissão de microfone negada');
      }
    }

    try {
      if (await _recorder.isRecording()) {
        debugPrint('⚠️ AudioRecording: Recorder já está em uso, aguardando...');
        await Future.delayed(const Duration(milliseconds: 500));
        if (await _recorder.isRecording()) {
          throw Exception('Recorder ainda está em uso após espera');
        }
      }

      if (await _recorder.hasPermission()) {
        final path =
            '${await _getTempPath()}/audio_${DateTime.now().millisecondsSinceEpoch}.wav';

        debugPrint('🎤 AudioRecording: Iniciando gravação em: $path');

        await _recorder.start(
          const RecordConfig(
            encoder: AudioEncoder.wav,
            sampleRate: 16000,
            numChannels: 1,
          ),
          path: path,
        );

        await Future.delayed(const Duration(milliseconds: 100));
        if (await _recorder.isRecording()) {
          _isRecording = true;
          debugPrint('✅ AudioRecording: Gravação iniciada com sucesso');
          return path;
        } else {
          throw Exception('Gravação não iniciou corretamente');
        }
      } else {
        throw Exception('Permissão de microfone não concedida');
      }
    } catch (e) {
      debugPrint('❌ Erro ao iniciar gravação: $e');
      _isRecording = false;
      rethrow;
    }
  }

  /// Para gravação e retorna bytes
  Future<Uint8List?> stopRecording() async {
    if (!_isRecording) {
      debugPrint('⚠️ AudioRecording: Não está gravando');
      return null;
    }

    try {
      final path = await _recorder.stop();
      _isRecording = false;

      if (path == null) {
        debugPrint('⚠️ AudioRecording: Caminho de gravação é null');
        return null;
      }

      final file = File(path);
      if (!await file.exists()) {
        debugPrint('❌ AudioRecording: Arquivo não existe: $path');
        return null;
      }

      final bytes = await file.readAsBytes();
      debugPrint('✅ AudioRecording: Gravação parada, ${bytes.length} bytes');

      return bytes;
    } catch (e) {
      debugPrint('❌ Erro ao parar gravação: $e');
      _isRecording = false;
      return null;
    }
  }

  /// Cancela gravação
  Future<void> cancelRecording() async {
    if (_isRecording) {
      await _recorder.stop();
      _isRecording = false;
    }
  }

  Future<String> _getTempPath() async {
    final dir = await getTemporaryDirectory();
    return dir.path;
  }

  void dispose() {
    _recorder.dispose();
  }
}

