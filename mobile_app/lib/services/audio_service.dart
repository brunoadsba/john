import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:just_audio/just_audio.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'dart:io';

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
        // Gera caminho temporário para o arquivo de áudio
        final path = '${await _getTempPath()}/audio_${DateTime.now().millisecondsSinceEpoch}.wav';
        
        await _recorder.start(
          const RecordConfig(
            encoder: AudioEncoder.wav,
            sampleRate: 16000,
            numChannels: 1,
          ),
          path: path,
        );
        _isRecording = true;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Erro ao iniciar gravação: $e');
      rethrow;
    }
  }
  
  /// Obtém caminho temporário
  Future<String> _getTempPath() async {
    try {
      if (Platform.isAndroid || Platform.isIOS) {
        final directory = await getTemporaryDirectory();
        return directory.path;
      } else {
        // Para web/desktop, usa /tmp
        return '/tmp';
      }
    } catch (e) {
      // Fallback para web
      return '/tmp';
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
        debugPrint('Áudio gravado em: $path');
        
        // No web, path é um blob URL, não um arquivo
        if (kIsWeb) {
          // Para web, precisa fazer fetch do blob
          try {
            final response = await http.get(Uri.parse(path));
            if (response.statusCode == 200) {
              final bytes = response.bodyBytes;
              debugPrint('Áudio lido do blob: ${bytes.length} bytes');
              return Uint8List.fromList(bytes);
            } else {
              debugPrint('Erro ao ler blob: status ${response.statusCode}');
              return null;
            }
          } catch (e) {
            debugPrint('Erro ao fazer fetch do blob: $e');
            return null;
          }
        } else {
          // Para mobile/desktop, lê arquivo normalmente
          final file = File(path);
          if (await file.exists()) {
            final bytes = await file.readAsBytes();
            debugPrint('Áudio lido: ${bytes.length} bytes');
            
            // Remove arquivo temporário após ler
            try {
              await file.delete();
            } catch (e) {
              debugPrint('Aviso: Não foi possível deletar arquivo temporário: $e');
            }
            
            return Uint8List.fromList(bytes);
          } else {
            debugPrint('Erro: Arquivo de áudio não encontrado: $path');
            return null;
          }
        }
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

