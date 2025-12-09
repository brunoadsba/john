// Stub file para web - Porcupine não suporta web
// Este arquivo é usado apenas quando compilando para web

class PorcupineManager {
  // Stub - nunca será usado em web pois kIsWeb é verificado antes

  static Future<PorcupineManager> fromKeywordPaths(
    String accessKey,
    List<String> keywordPaths,
    Function(int) wakeWordCallback, {
    Function(dynamic)? errorCallback,
    List<double>? sensitivities,
  }) async {
    throw UnimplementedError('Porcupine não suporta web');
  }

  static Future<PorcupineManager> fromKeywords(
    String accessKey,
    List<String> keywords,
    Function(int) wakeWordCallback, {
    Function(dynamic)? errorCallback,
    List<double>? sensitivities,
  }) async {
    throw UnimplementedError('Porcupine não suporta web');
  }

  Future<void> start() async {
    throw UnimplementedError('Porcupine não suporta web');
  }

  Future<void> stop() async {
    throw UnimplementedError('Porcupine não suporta web');
  }

  void delete() {
    // No-op em web
  }
}
