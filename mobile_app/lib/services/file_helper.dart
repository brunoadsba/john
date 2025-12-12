// Helper para criação de File com suporte web/mobile
import 'package:flutter/foundation.dart' show kIsWeb;

// Import condicional - File só disponível em mobile
import 'dart:io' if (dart.library.html) 'file_helper_stub.dart' as file_io;

/// Cria um File apenas quando não for web
/// Retorna null no web para evitar erros de compilação
dynamic createFileForStream(String path) {
  if (kIsWeb) {
    return null;
  }
  // No web, este código nunca será executado
  // No mobile, file_io.File funciona normalmente
  // ignore: avoid_web_libraries_in_flutter
  return file_io.File(path);
}

