/// Serviço simples para avaliar segurança de URLs em mensagens.
/// Mantém lista de domínios suspeitos e palavras-chave comuns em golpes.
class UrlSafetyService {
  static final List<String> _blacklistDomains = [
    'docs.google.com/forms',
    'forms.gle',
    'bit.ly',
    't.ly',
    'encurtador.com.br',
    'rebrand.ly',
    'tinyurl.com',
    // Domínio gov.br: permitir apenas o oficial com https
    'gov.br',
  ];

  static final List<String> _suspiciousKeywords = [
    'gov.br',
    'banco central',
    'verificação em duas etapas',
    'código de acesso',
    'área logada',
    'meu bc',
    'ativar agora',
  ];

  /// Retorna true se a URL for suspeita considerando domínio e texto da mensagem.
  static bool isSuspicious(String url, String messageText) {
    final lowerUrl = url.toLowerCase();
    final lowerText = messageText.toLowerCase();

    final hasBlacklistedDomain =
        _blacklistDomains.any((d) => lowerUrl.contains(d));
    final hasSuspiciousKeyword =
        _suspiciousKeywords.any((k) => lowerText.contains(k));

    // Exceção: só permite gov.br oficial com https (bloqueia subdomínios suspeitos)
    if (lowerUrl.contains('gov.br')) {
      final isOfficial = lowerUrl.startsWith('https://') &&
          (lowerUrl == 'https://www.gov.br' || lowerUrl == 'https://gov.br');
      if (!isOfficial) return true;
    }

    return hasBlacklistedDomain || hasSuspiciousKeyword;
  }

  /// Extrai a primeira URL encontrada no texto, ou null se não houver.
  static String? detectFirstUrl(String text) {
    final regex = RegExp(
      r'(https?:\/\/[^\s]+)',
      caseSensitive: false,
    );
    final match = regex.firstMatch(text);
    return match?.group(0);
  }
}

