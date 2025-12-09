/// Serviço de reprodução de áudio
import 'package:flutter/foundation.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:typed_data';
import 'dart:io';
import 'dart:async';

class AudioPlayback {
  final AudioPlayer _player = AudioPlayer();
  bool _isPlaying = false;

  bool get isPlaying => _isPlaying;

  /// Estima duração do áudio WAV baseado no tamanho
  double estimateAudioDuration(Uint8List audioBytes) {
    if (audioBytes.length < 44) {
      return 0.0;
    }

    try {
      final dataSize = (audioBytes[43] << 24) |
          (audioBytes[42] << 16) |
          (audioBytes[41] << 8) |
          audioBytes[40];

      final samples = dataSize ~/ 2;
      final duration = samples / 16000.0;
      return duration;
    } catch (e) {
      final estimatedDataSize = audioBytes.length - 44;
      final samples = estimatedDataSize ~/ 2;
      return samples / 16000.0;
    }
  }

  /// Reproduz áudio de bytes com retry automático
  Future<void> playAudio(Uint8List audioBytes, {int maxRetries = 2}) async {
    int attempt = 0;

    while (attempt <= maxRetries) {
      try {
        await _playAudioInternal(audioBytes);
        return;
      } catch (e) {
        attempt++;
        if (attempt > maxRetries) {
          debugPrint('❌ Reprodução falhou após $maxRetries tentativas: $e');
          rethrow;
        }
        debugPrint('⚠️ Tentativa $attempt de $maxRetries falhou, tentando novamente...');
        await Future.delayed(Duration(milliseconds: 500 * attempt));
      }
    }
  }

  /// Implementação interna de reprodução
  Future<void> _playAudioInternal(Uint8List audioBytes) async {
    File? tempFile;
    StreamSubscription? playerStateSubscription;

    try {
      debugPrint('🔊 Iniciando reprodução de áudio: ${audioBytes.length} bytes');

      if (audioBytes.length < 44) {
        debugPrint('❌ Áudio muito pequeno: ${audioBytes.length} bytes');
        throw Exception('Áudio inválido: muito pequeno');
      }

      if (_isPlaying) {
        debugPrint('⚠️ Parando reprodução anterior...');
        try {
          await _player.stop();
          await Future.delayed(const Duration(milliseconds: 300));
        } catch (e) {
          debugPrint('⚠️ Erro ao parar reprodução anterior: $e');
        }
      }

      _isPlaying = true;
      debugPrint('✅ Estado atualizado: isPlaying=true');

      final tempPath = await _getTempPath();
      tempFile = File(
          '$tempPath/audio_response_${DateTime.now().millisecondsSinceEpoch}.wav');
      await tempFile.writeAsBytes(audioBytes);

      final estimatedDuration = estimateAudioDuration(audioBytes);
      final timeout = Duration(
          seconds: (estimatedDuration * 2).ceil() + 5);

      debugPrint(
          '⏱️ Duração estimada: ${estimatedDuration.toStringAsFixed(2)}s, timeout: ${timeout.inSeconds}s');

      final completer = Completer<void>();

      playerStateSubscription = _player.playerStateStream.listen((state) {
        if (state.processingState == ProcessingState.completed) {
          if (!completer.isCompleted) {
            completer.complete();
            debugPrint('✅ Reprodução concluída');
          }
        } else if (state.processingState == ProcessingState.idle &&
            state.playing == false &&
            _isPlaying) {
          if (!completer.isCompleted) {
            completer.complete();
            debugPrint('✅ Player em estado idle, reprodução concluída');
          }
        }
      });

      await _player.setFilePath(tempFile.path);
      await _player.play();

      await completer.future.timeout(timeout, onTimeout: () {
        debugPrint('⏱️ Timeout de reprodução atingido, forçando parada');
        _player.stop();
      });

      try {
        if (_player.playing) {
          await _player.stop();
        }
      } catch (e) {
        debugPrint('⚠️ Erro ao parar player: $e');
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Erro ao reproduzir áudio: $e');
      debugPrint('   Stack trace: $stackTrace');
      try {
        await _player.stop();
      } catch (e2) {
        debugPrint('⚠️ Erro ao parar player após erro: $e2');
      }
      if (tempFile != null) {
        try {
          if (await tempFile.exists()) {
            await tempFile.delete();
            debugPrint('🗑️ Arquivo temporário removido após erro');
          }
        } catch (e3) {
          debugPrint('⚠️ Erro ao remover arquivo após erro: $e3');
        }
      }
      rethrow;
    } finally {
      await playerStateSubscription?.cancel();

      try {
        if (_player.playing) {
          await _player.stop();
          await Future.delayed(const Duration(milliseconds: 200));
        }
      } catch (e) {
        debugPrint('⚠️ Erro ao parar player no finally: $e');
      }

      if (tempFile != null) {
        try {
          await Future.delayed(const Duration(milliseconds: 300));
          if (await tempFile.exists()) {
            await tempFile.delete();
            debugPrint('🗑️ Arquivo temporário removido após reprodução completa');
          }
        } catch (e) {
          debugPrint('⚠️ Não foi possível remover arquivo temporário: $e');
          _scheduleFileCleanup(tempFile);
        }
      }

      _isPlaying = false;
      debugPrint('✅ Estado de reprodução atualizado: isPlaying=false');
    }
  }

  /// Para reprodução
  Future<void> stopPlaying() async {
    await _player.stop();
    _isPlaying = false;
  }

  /// Agenda limpeza de arquivo temporário
  void _scheduleFileCleanup(File file) {
    Future.delayed(const Duration(seconds: 5), () async {
      try {
        if (await file.exists()) {
          await file.delete();
          debugPrint('🗑️ Arquivo temporário removido (limpeza agendada)');
        }
      } catch (e) {
        debugPrint('⚠️ Erro na limpeza agendada: $e');
      }
    });
  }

  Future<String> _getTempPath() async {
    final dir = await getTemporaryDirectory();
    return dir.path;
  }

  void dispose() {
    _player.dispose();
  }
}

