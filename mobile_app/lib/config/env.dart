/// Configurações de ambiente para o app
///
/// Para usar variáveis de ambiente, execute:
/// flutter run --dart-define=PICOVOICE_ACCESS_KEY=pv_sua_key_aqui
class Env {
  /// URL do backend (API do Jonh Assistant)
  ///
  /// Pode ser definida via:
  /// 1. Variável de ambiente: --dart-define=BACKEND_URL=http://172.20.240.80:8000
  /// 2. Hardcoded (para desenvolvimento)
  static const String backendUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue:
        'http://192.168.1.5:8000', // IP do Windows na rede WiFi (mesma rede do celular)
  );

  /// Access Key do Picovoice (obter em https://console.picovoice.ai/)
  ///
  /// Pode ser definida via:
  /// 1. Variável de ambiente: --dart-define=PICOVOICE_ACCESS_KEY=...
  /// 2. SharedPreferences (salva pelo app)
  /// 3. Hardcoded (apenas para desenvolvimento)
  static const String picovoiceAccessKey = String.fromEnvironment(
    'PICOVOICE_ACCESS_KEY',
    defaultValue:
        '', // Deixe vazio para usar SharedPreferences ou configurar no app
  );

  /// Caminho para modelo customizado de wake word (.ppn)
  ///
  /// Se vazio, usa palavra padrão do Porcupine
  static const String wakeWordModelPath = String.fromEnvironment(
    'WAKE_WORD_MODEL_PATH',
    defaultValue: '', // Ex: 'assets/wake_words/jonh.ppn'
  );

  /// Sensibilidade de detecção do wake word (0.0 a 1.0)
  static double get wakeWordSensitivity {
    const value =
        String.fromEnvironment('WAKE_WORD_SENSITIVITY', defaultValue: '');
    if (value.isEmpty) return 0.5;
    return double.tryParse(value) ?? 0.5;
  }
}
