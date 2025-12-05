import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:just_audio/just_audio.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:typed_data';

/// Serviço de gravação e reprodução de áudio
class AudioService extends ChangeNotifier {
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();
  
  bool _isRecording = false;
  bool _isPlaying = false;
  bool _hasPermission = false;
  
  bool get isRecording => _isRecording;
  bool get isPlaying => _isPlaying;
  bool get hasPermission => _hasPermission;
  
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
  
  /// Inicia gravação
  Future<void> startRecording() async {
    if (!_hasPermission) {
      final granted = await requestPermissions();
      if (!granted) {
        throw Exception('Permissão de microfone negada');
      }
    }
    
    try {
      if (await _recorder.hasPermission()) {
        await _recorder.start(
          const RecordConfig(
            encoder: AudioEncoder.wav,
            sampleRate: 16000,
            numChannels: 1,
          ),
        );
        _isRecording = true;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Erro ao iniciar gravação: $e');
      rethrow;
    }
  }
  
  /// Para gravação e retorna bytes do áudio
  Future<Uint8List?> stopRecording() async {
    if (!_isRecording) return null;
    
    try {
      final path = await _recorder.stop();
      _isRecording = false;
      notifyListeners();
      
      if (path != null) {
        // TODO: Ler arquivo e retornar bytes
        debugPrint('Áudio gravado em: $path');
        return null; // Por enquanto retorna null
      }
      return null;
    } catch (e) {
      debugPrint('Erro ao parar gravação: $e');
      _isRecording = false;
      notifyListeners();
      return null;
    }
  }
  
  /// Cancela gravação
  Future<void> cancelRecording() async {
    if (_isRecording) {
      await _recorder.stop();
      _isRecording = false;
      notifyListeners();
    }
  }
  
  /// Reproduz áudio de bytes
  Future<void> playAudio(Uint8List audioBytes) async {
    try {
      // TODO: Implementar reprodução de bytes
      // Por enquanto apenas simula
      _isPlaying = true;
      notifyListeners();
      
      await Future.delayed(const Duration(seconds: 2));
      
      _isPlaying = false;
      notifyListeners();
    } catch (e) {
      debugPrint('Erro ao reproduzir áudio: $e');
      _isPlaying = false;
      notifyListeners();
    }
  }
  
  /// Para reprodução
  Future<void> stopPlaying() async {
    await _player.stop();
    _isPlaying = false;
    notifyListeners();
  }
  
  @override
  void dispose() {
    _recorder.dispose();
    _player.dispose();
    super.dispose();
  }
}

