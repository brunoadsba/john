import 'dart:typed_data';

/// Resultado da validação de áudio
class ValidationResult {
  final bool isValid;
  final String? errorMessage;
  final double? estimatedDuration;

  const ValidationResult({
    required this.isValid,
    this.errorMessage,
    this.estimatedDuration,
  });
}

/// Validador centralizado para áudio
/// 
/// Centraliza todas as validações de áudio para evitar duplicação
/// e garantir consistência em todo o app.
class AudioValidator {
  AudioValidator._(); // Classe utilitária, não instanciável

  /// Tamanho mínimo do header WAV (44 bytes)
  static const int minWavHeaderSize = 44;
  
  /// Tamanho mínimo esperado de áudio válido (~1000 bytes = ~0.1s a 16kHz)
  static const int minValidAudioSize = 1000;
  
  /// Duração mínima de áudio válido em segundos
  static const double minDurationSeconds = 0.5;

  /// Valida se o áudio não está vazio
  static ValidationResult validateNotEmpty(Uint8List? audioBytes) {
    if (audioBytes == null || audioBytes.isEmpty) {
      return const ValidationResult(
        isValid: false,
        errorMessage: 'Áudio vazio',
      );
    }
    return const ValidationResult(isValid: true);
  }

  /// Valida tamanho mínimo do áudio (header WAV)
  static ValidationResult validateMinSize(Uint8List audioBytes) {
    if (audioBytes.length < minWavHeaderSize) {
      return ValidationResult(
        isValid: false,
        errorMessage: 'Áudio muito pequeno: ${audioBytes.length} bytes '
            '(mínimo: $minWavHeaderSize bytes para WAV)',
      );
    }
    return const ValidationResult(isValid: true);
  }

  /// Valida formato WAV (verifica header "RIFF")
  static ValidationResult validateWavFormat(Uint8List audioBytes) {
    if (audioBytes.length < 4) {
      return const ValidationResult(
        isValid: false,
        errorMessage: 'Áudio muito pequeno para validar formato',
      );
    }

    final header = String.fromCharCodes(audioBytes.sublist(0, 4));
    if (header != 'RIFF') {
      return ValidationResult(
        isValid: false,
        errorMessage: 'Formato de áudio inválido (header: "$header", esperado: "RIFF")',
      );
    }

    return const ValidationResult(isValid: true);
  }

  /// Valida se o áudio tem duração mínima
  static ValidationResult validateMinDuration(Uint8List audioBytes) {
    final duration = estimateDuration(audioBytes);
    
    if (duration < minDurationSeconds) {
      return ValidationResult(
        isValid: false,
        errorMessage: 'Áudio muito curto (${duration.toStringAsFixed(2)}s < $minDurationSeconds)',
        estimatedDuration: duration,
      );
    }

    return ValidationResult(
      isValid: true,
      estimatedDuration: duration,
    );
  }

  /// Validação completa de áudio (todas as validações)
  static ValidationResult validateAll(Uint8List? audioBytes) {
    // 1. Verifica se não está vazio
    final emptyCheck = validateNotEmpty(audioBytes);
    if (!emptyCheck.isValid) {
      return emptyCheck;
    }

    // 2. Verifica tamanho mínimo
    final sizeCheck = validateMinSize(audioBytes!);
    if (!sizeCheck.isValid) {
      return sizeCheck;
    }

    // 3. Verifica formato WAV
    final formatCheck = validateWavFormat(audioBytes);
    if (!formatCheck.isValid) {
      // Aviso mas não bloqueia (pode ser que formato esteja correto)
      // return formatCheck;
    }

    // 4. Verifica duração mínima (apenas aviso, não bloqueia)
    final durationCheck = validateMinDuration(audioBytes);

    // Retorna sucesso mesmo se duração for curta (apenas aviso)
    return ValidationResult(
      isValid: true,
      estimatedDuration: durationCheck.estimatedDuration,
      errorMessage: durationCheck.isValid 
          ? null 
          : durationCheck.errorMessage, // Apenas aviso
    );
  }

  /// Estima duração do áudio WAV baseado no tamanho
  /// 
  /// Assumindo: 16kHz, mono, 16-bit (2 bytes por sample)
  static double estimateDuration(Uint8List audioBytes) {
    if (audioBytes.length < minWavHeaderSize) {
      return 0.0;
    }

    try {
      // WAV header tem 44 bytes
      // Data size está no offset 40-43 (little-endian)
      final dataSize = (audioBytes[43] << 24) |
                       (audioBytes[42] << 16) |
                       (audioBytes[41] << 8) |
                       audioBytes[40];

      // Assumindo 16kHz, mono, 16-bit
      // 2 bytes por sample, 16000 samples por segundo
      final samples = dataSize ~/ 2;
      final duration = samples / 16000.0;

      return duration;
    } catch (e) {
      // Fallback: estima baseado no tamanho total
      final estimatedDataSize = audioBytes.length - minWavHeaderSize;
      final samples = estimatedDataSize ~/ 2;
      return samples / 16000.0;
    }
  }

  /// Retorna mensagem de erro amigável para o usuário
  static String getUserFriendlyErrorMessage(String? technicalError) {
    if (technicalError == null) return 'Erro desconhecido';

    // Traduz erros técnicos para mensagens amigáveis
    if (technicalError.contains('vazio')) {
      return 'Nenhum áudio foi gravado. Tente novamente.';
    }
    if (technicalError.contains('muito pequeno')) {
      return 'O áudio gravado é muito curto. Tente falar mais.';
    }
    if (technicalError.contains('muito curto')) {
      return 'O áudio é muito curto. Tente falar um pouco mais.';
    }
    if (technicalError.contains('inválido')) {
      return 'O formato do áudio não é válido. Tente novamente.';
    }

    return technicalError; // Retorna erro técnico se não conseguir traduzir
  }
}

