import 'package:flutter/foundation.dart';
import 'dart:async';

/// Sistema de métricas de performance para rastrear latência end-to-end
///
/// Rastreia tempos de cada etapa do pipeline:
/// - Gravação de áudio
/// - Envio para servidor
/// - Processamento (STT, LLM, TTS)
/// - Recebimento de resposta
/// - Reprodução de áudio
class PerformanceMetrics {
  DateTime? _recordingStart;
  DateTime? _sendStart;
  DateTime? _responseReceived;
  DateTime? _audioPlaybackStart;
  DateTime? _audioPlaybackEnd;

  // Métricas de backend (recebidas via WebSocket)
  Duration? _sttTime;
  Duration? _llmTime;
  Duration? _ttsTime;
  Duration? _networkTime;

  /// Marca início da gravação
  void markRecordingStart() {
    _recordingStart = DateTime.now();
    debugPrint('📊 Performance: Gravação iniciada');
  }

  /// Marca início do envio
  void markSendStart() {
    _sendStart = DateTime.now();
    if (_recordingStart != null) {
      final recordingTime = _sendStart!.difference(_recordingStart!);
      debugPrint('📊 Performance: Envio iniciado (gravação: ${recordingTime.inMilliseconds}ms)');
    } else {
      debugPrint('📊 Performance: Envio iniciado');
    }
  }

  /// Marca áudio enviado (alias para markSendStart)
  void markAudioSent() {
    markSendStart();
  }

  /// Marca recebimento da resposta
  void markResponseReceived() {
    _responseReceived = DateTime.now();
    if (_sendStart != null) {
      _networkTime = _responseReceived!.difference(_sendStart!);
      debugPrint('📊 Performance: Resposta recebida (rede: ${_networkTime!.inMilliseconds}ms)');
    } else {
      debugPrint('📊 Performance: Resposta recebida');
    }
  }

  /// Marca início da reprodução
  void markAudioPlaybackStart() {
    _audioPlaybackStart = DateTime.now();
    debugPrint('📊 Performance: Reprodução iniciada');
  }

  /// Marca fim da reprodução
  void markAudioPlaybackEnd() {
    _audioPlaybackEnd = DateTime.now();
    if (_audioPlaybackStart != null) {
      final playbackTime = _audioPlaybackEnd!.difference(_audioPlaybackStart!);
      debugPrint('📊 Performance: Reprodução concluída (${playbackTime.inMilliseconds}ms)');
    }
    _logAllMetrics();
  }

  /// Define métricas do backend
  void setBackendMetrics({
    Duration? sttTime,
    Duration? llmTime,
    Duration? ttsTime,
  }) {
    _sttTime = sttTime;
    _llmTime = llmTime;
    _ttsTime = ttsTime;
    
    if (sttTime != null) {
      debugPrint('📊 Performance: STT = ${sttTime.inMilliseconds}ms');
    }
    if (llmTime != null) {
      debugPrint('📊 Performance: LLM = ${llmTime.inMilliseconds}ms');
    }
    if (ttsTime != null) {
      debugPrint('📊 Performance: TTS = ${ttsTime.inMilliseconds}ms');
    }
  }

  /// Calcula tempo total (gravação → reprodução completa)
  Duration? get totalTime {
    if (_recordingStart == null || _audioPlaybackEnd == null) {
      return null;
    }
    return _audioPlaybackEnd!.difference(_recordingStart!);
  }

  /// Calcula tempo de gravação
  Duration? get recordingTime {
    if (_recordingStart == null || _sendStart == null) {
      return null;
    }
    return _sendStart!.difference(_recordingStart!);
  }

  /// Calcula tempo de rede (envio → recebimento)
  Duration? get networkTime => _networkTime;

  /// Calcula tempo de processamento (STT + LLM + TTS)
  Duration? get processingTime {
    if (_sttTime == null && _llmTime == null && _ttsTime == null) {
      return null;
    }
    int totalMs = 0;
    if (_sttTime != null) totalMs += _sttTime!.inMilliseconds;
    if (_llmTime != null) totalMs += _llmTime!.inMilliseconds;
    if (_ttsTime != null) totalMs += _ttsTime!.inMilliseconds;
    return Duration(milliseconds: totalMs);
  }

  /// Calcula tempo de reprodução
  Duration? get playbackTime {
    if (_audioPlaybackStart == null || _audioPlaybackEnd == null) {
      return null;
    }
    return _audioPlaybackEnd!.difference(_audioPlaybackStart!);
  }

  /// Loga todas as métricas
  void _logAllMetrics() {
    debugPrint('');
    debugPrint('═══════════════════════════════════════');
    debugPrint('📊 MÉTRICAS DE PERFORMANCE');
    debugPrint('═══════════════════════════════════════');
    
    if (recordingTime != null) {
      debugPrint('   Gravação:     ${recordingTime!.inMilliseconds}ms');
    }
    
    if (networkTime != null) {
      debugPrint('   Rede:         ${networkTime!.inMilliseconds}ms');
    }
    
    if (_sttTime != null) {
      debugPrint('   STT:          ${_sttTime!.inMilliseconds}ms');
    }
    
    if (_llmTime != null) {
      debugPrint('   LLM:          ${_llmTime!.inMilliseconds}ms');
    }
    
    if (_ttsTime != null) {
      debugPrint('   TTS:          ${_ttsTime!.inMilliseconds}ms');
    }
    
    if (processingTime != null) {
      debugPrint('   Processamento: ${processingTime!.inMilliseconds}ms');
    }
    
    if (playbackTime != null) {
      debugPrint('   Reprodução:   ${playbackTime!.inMilliseconds}ms');
    }
    
    if (totalTime != null) {
      final totalSeconds = totalTime!.inMilliseconds / 1000.0;
      debugPrint('   ─────────────────────────────────────');
      debugPrint('   TOTAL:        ${totalSeconds.toStringAsFixed(2)}s');
      
      // Verifica se está dentro do objetivo (< 3s)
      if (totalSeconds < 3.0) {
        debugPrint('   ✅ Objetivo atingido (< 3s)');
      } else {
        debugPrint('   ⚠️ Acima do objetivo (>= 3s)');
      }
    }
    
    debugPrint('═══════════════════════════════════════');
    debugPrint('');
  }

  /// Reseta todas as métricas
  void reset() {
    _recordingStart = null;
    _sendStart = null;
    _responseReceived = null;
    _audioPlaybackStart = null;
    _audioPlaybackEnd = null;
    _sttTime = null;
    _llmTime = null;
    _ttsTime = null;
    _networkTime = null;
  }

  /// Retorna métricas como mapa (útil para logging estruturado)
  Map<String, dynamic> toMap() {
    return {
      'recordingTime': recordingTime?.inMilliseconds,
      'networkTime': networkTime?.inMilliseconds,
      'sttTime': _sttTime?.inMilliseconds,
      'llmTime': _llmTime?.inMilliseconds,
      'ttsTime': _ttsTime?.inMilliseconds,
      'processingTime': processingTime?.inMilliseconds,
      'playbackTime': playbackTime?.inMilliseconds,
      'totalTime': totalTime?.inMilliseconds,
    };
  }
}

