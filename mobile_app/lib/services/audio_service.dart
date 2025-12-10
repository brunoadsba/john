/// Serviço de gravação e reprodução de áudio
/// Orquestra os serviços de gravação, reprodução e streaming
import 'package:flutter/foundation.dart';
import 'dart:typed_data';

import 'audio/audio_recording.dart';
import 'audio/audio_playback.dart';
import 'audio/audio_streaming.dart';
import 'audio/audio_streaming_playback.dart';
import 'audio/audio_cleanup.dart';
import 'dart:async';

class AudioService extends ChangeNotifier {
  final AudioRecording _recording = AudioRecording();
  final AudioPlayback _playback = AudioPlayback();
  final AudioStreaming _streaming = AudioStreaming();
  final AudioStreamingPlayback _streamingPlayback = AudioStreamingPlayback();

  bool get isRecording => _recording.isRecording;
  bool get isPlaying => _playback.isPlaying;
  bool get hasPermission => _recording.hasPermission;
  bool get isStreaming => _streaming.isStreaming;

  /// Callback para enviar chunks de áudio (usado para wake word)
  Function(Uint8List chunk)? onAudioChunk;

  AudioService() {
    _streaming.onAudioChunk = (chunk) {
      if (onAudioChunk != null) {
        onAudioChunk!(chunk);
      }
    };
  }

  /// Solicita permissões de microfone
  Future<bool> requestPermissions() async {
    final granted = await _recording.requestPermissions();
    notifyListeners();
    return granted;
  }

  /// Verifica se tem permissão
  Future<bool> checkPermissions() async {
    final granted = await _recording.checkPermissions();
    notifyListeners();
    return granted;
  }

  /// Inicia gravação
  Future<void> startRecording() async {
    await _recording.startRecording();
    notifyListeners();
  }

  /// Para gravação e retorna bytes
  Future<Uint8List?> stopRecording() async {
    final bytes = await _recording.stopRecording();
    notifyListeners();
    return bytes;
  }

  /// Cancela gravação
  Future<void> cancelRecording() async {
    await _recording.cancelRecording();
    notifyListeners();
  }

  /// Reproduz áudio de bytes com retry automático
  Future<void> playAudio(Uint8List audioBytes, {int maxRetries = 2}) async {
    await _playback.playAudio(audioBytes, maxRetries: maxRetries);
    notifyListeners();
  }
  
  /// Reproduz áudio via streaming (Time to First Byte)
  /// Começa a tocar assim que primeiro chunk significativo chegar
  Future<void> playStreamedAudio(Stream<Uint8List> audioStream) async {
    await _streamingPlayback.playStreamedAudio(audioStream);
    notifyListeners();
  }

  /// Para reprodução
  Future<void> stopPlaying() async {
    await _playback.stopPlaying();
    notifyListeners();
  }

  /// Inicia streaming contínuo de áudio
  Future<void> startStreaming() async {
    await _streaming.startStreaming();
    notifyListeners();
  }

  /// Para streaming
  Future<void> stopStreaming() async {
    await _streaming.stopStreaming();
    notifyListeners();
  }

  /// Limpa arquivos temporários antigos
  Future<void> cleanupOldTempFiles() async {
    await AudioCleanup.cleanupOldTempFiles();
  }

  @override
  void dispose() {
    _recording.dispose();
    _playback.dispose();
    _streaming.dispose();
    _streamingPlayback.dispose();
    super.dispose();
  }
}
