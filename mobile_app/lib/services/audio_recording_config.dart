/// Configuração padronizada para gravação de áudio (Alexa-like)
///
/// Define os parâmetros de tempo para detecção de comando após wake word.
/// Valores baseados na experiência da Alexa.
class AudioRecordingConfig {
  /// Tempo inicial antes de começar a detectar silêncio (2 segundos)
  ///
  /// Dá tempo para o usuário começar a falar após o wake word ser detectado.
  /// Similar à Alexa, que aguarda um momento antes de começar a processar.
  static const Duration initialDelay = Duration(seconds: 2);

  /// Tempo mínimo de gravação (5 segundos)
  ///
  /// Garante que comandos curtos sejam capturados completamente.
  /// Mesmo que detecte silêncio, continua gravando até atingir este tempo mínimo.
  static const Duration minDuration = Duration(seconds: 5);

  /// Threshold de silêncio (3 segundos)
  ///
  /// Após o tempo mínimo, se detectar silêncio por este período,
  /// para a gravação automaticamente.
  /// Permite pausas naturais na fala, mas para quando o usuário termina.
  static const Duration silenceThreshold = Duration(seconds: 3);

  /// Tempo máximo de gravação (20 segundos)
  ///
  /// Limite absoluto de gravação para evitar comandos muito longos
  /// e economizar recursos.
  static const Duration maxDuration = Duration(seconds: 20);

  /// Intervalo de verificação de silêncio (300ms)
  ///
  /// Frequência com que verifica se há silêncio ou se deve parar.
  /// Balance entre responsividade e consumo de CPU.
  static const Duration checkInterval = Duration(milliseconds: 300);

  /// Delay após iniciar gravação antes de começar a detectar (500ms)
  ///
  /// Aguarda o recorder inicializar completamente antes de começar
  /// a detectar silêncio.
  static const Duration recorderInitDelay = Duration(milliseconds: 500);

  /// Retorna configuração padrão como mapa
  static Map<String, Duration> toMap() {
    return {
      'initialDelay': initialDelay,
      'minDuration': minDuration,
      'silenceThreshold': silenceThreshold,
      'maxDuration': maxDuration,
      'checkInterval': checkInterval,
      'recorderInitDelay': recorderInitDelay,
    };
  }

  /// Retorna string formatada para logs
  static String toDebugString() {
    return '''
AudioRecordingConfig:
  - Initial Delay: ${initialDelay.inSeconds}s
  - Min Duration: ${minDuration.inSeconds}s
  - Silence Threshold: ${silenceThreshold.inSeconds}s
  - Max Duration: ${maxDuration.inSeconds}s
  - Check Interval: ${checkInterval.inMilliseconds}ms
  - Recorder Init Delay: ${recorderInitDelay.inMilliseconds}ms
''';
  }
}
