/// Reprodução de áudio via streaming (Time to First Byte)
/// Começa a tocar assim que o primeiro chunk chegar
import 'package:flutter/foundation.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'dart:async';
import 'dart:io' as io;

class AudioStreamingPlayback {
  final AudioPlayer _player = AudioPlayer();
  bool _isPlaying = false;
  File? _tempFile;
  io.IOSink? _fileSink;
  bool _hasStartedPlaying = false;
  static const int _minChunkSize = 1024; // 1KB mínimo antes de começar a tocar

  bool get isPlaying => _isPlaying;

  /// Reproduz áudio recebido via stream (chunks)
  /// Começa a tocar assim que primeiro chunk significativo chegar
  Future<void> playStreamedAudio(Stream<Uint8List> audioStream) async {
    final playbackCompleter = Completer<void>();
    StreamSubscription? streamSubscription;
    StreamSubscription? playerStateSubscription;

    try {
      debugPrint('🔊 Iniciando reprodução de áudio via streaming');
      _isPlaying = true;
      _hasStartedPlaying = false;

      // Cria arquivo temporário
      final tempPath = await _getTempPath();
      _tempFile = File(
          '$tempPath/audio_stream_${DateTime.now().millisecondsSinceEpoch}.wav');
      _fileSink = _tempFile!.openWrite();

      // Monitora estado do player
      playerStateSubscription = _player.playerStateStream.listen((state) {
        if (state.processingState == ProcessingState.completed) {
          if (!playbackCompleter.isCompleted) {
            playbackCompleter.complete();
            debugPrint('✅ Reprodução via streaming concluída');
          }
        }
      });

      // Processa chunks do stream
      streamSubscription = audioStream.listen(
        (chunk) async {
          try {
            // Escreve chunk no arquivo
            final sink = _fileSink;
            if (sink != null) {
              sink.add(chunk);
              await sink.flush();
            }

            // Começa a tocar quando primeiro chunk significativo chegar
            if (!_hasStartedPlaying && chunk.length >= _minChunkSize) {
              debugPrint(
                  '🎵 Primeiro chunk significativo recebido (${chunk.length} bytes), iniciando reprodução...');
              await _startPlayback();
              _hasStartedPlaying = true;
            }
          } catch (e) {
            debugPrint('❌ Erro ao processar chunk: $e');
            if (!playbackCompleter.isCompleted) {
              playbackCompleter.completeError(e);
            }
          }
        },
        onDone: () async {
          try {
            if (_fileSink != null) {
              await _fileSink!.close();
              _fileSink = null;
            }

            // Se ainda não começou a tocar, começa agora
            if (!_hasStartedPlaying) {
              debugPrint('⚠️ Stream terminou sem chunk significativo, iniciando reprodução...');
              await _startPlayback();
            }

            // Aguarda reprodução terminar (com timeout)
            if (_hasStartedPlaying) {
              await playbackCompleter.future.timeout(
                const Duration(seconds: 60),
                onTimeout: () {
                  debugPrint('⏱️ Timeout de reprodução via streaming');
                  _player.stop();
                },
              );
            } else {
              playbackCompleter.complete();
            }
          } catch (e) {
            if (!playbackCompleter.isCompleted) {
              playbackCompleter.completeError(e);
            }
          }
        },
        onError: (error) {
          debugPrint('❌ Erro no stream de áudio: $error');
          if (!playbackCompleter.isCompleted) {
            playbackCompleter.completeError(error);
          }
        },
        cancelOnError: false,
      );

      await playbackCompleter.future;
    } catch (e, stackTrace) {
      debugPrint('❌ Erro ao reproduzir áudio via streaming: $e');
      debugPrint('   Stack trace: $stackTrace');
      try {
        await _player.stop();
      } catch (e2) {
        debugPrint('⚠️ Erro ao parar player após erro: $e2');
      }
      rethrow;
    } finally {
      await streamSubscription?.cancel();
      await playerStateSubscription?.cancel();
      await _fileSink?.close();
      _fileSink = null;

      try {
        if (_player.playing) {
          await _player.stop();
        }
      } catch (e) {
        debugPrint('⚠️ Erro ao parar player no finally: $e');
      }

      // Limpa arquivo temporário após delay
      if (_tempFile != null) {
        _scheduleFileCleanup(_tempFile!);
      }

      _isPlaying = false;
      _hasStartedPlaying = false;
      debugPrint('✅ Reprodução via streaming finalizada');
    }
  }

  /// Inicia reprodução do arquivo temporário
  Future<void> _startPlayback() async {
    if (_tempFile == null || !await _tempFile!.exists()) {
      throw Exception('Arquivo temporário não existe');
    }

    try {
      await _player.setFilePath(_tempFile!.path);
      await _player.play();
      debugPrint('✅ Reprodução iniciada: ${_tempFile!.path}');
    } catch (e) {
      debugPrint('❌ Erro ao iniciar reprodução: $e');
      rethrow;
    }
  }

  /// Para reprodução
  Future<void> stopPlaying() async {
    await _player.stop();
    await _fileSink?.close();
    _fileSink = null;
    _isPlaying = false;
    _hasStartedPlaying = false;
  }

  /// Agenda limpeza de arquivo temporário
  void _scheduleFileCleanup(File file) {
    Future.delayed(const Duration(seconds: 5), () async {
      try {
        if (await file.exists()) {
          await file.delete();
          debugPrint('🗑️ Arquivo temporário de streaming removido');
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
    _fileSink?.close();
  }
}

