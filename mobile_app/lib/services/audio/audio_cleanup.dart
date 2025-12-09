/// Utilitário para limpeza de arquivos temporários de áudio
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class AudioCleanup {
  /// Limpa arquivos temporários antigos (> 1 hora)
  static Future<void> cleanupOldTempFiles() async {
    try {
      final tempPath = await _getTempPath();
      final dir = Directory(tempPath);
      final now = DateTime.now();

      if (!await dir.exists()) {
        return;
      }

      int deletedCount = 0;
      await for (final entity in dir.list()) {
        if (entity is File) {
          final fileName = entity.path.split('/').last;
          if (fileName.startsWith('audio_') || fileName.startsWith('stream_')) {
            try {
              final stat = await entity.stat();
              final age = now.difference(stat.modified);

              if (age.inHours > 1) {
                await entity.delete();
                deletedCount++;
                debugPrint('🗑️ Arquivo antigo removido: ${entity.path}');
              }
            } catch (e) {
              debugPrint('⚠️ Erro ao processar arquivo ${entity.path}: $e');
            }
          }
        }
      }

      if (deletedCount > 0) {
        debugPrint('✅ Limpeza concluída: $deletedCount arquivo(s) removido(s)');
      }
    } catch (e) {
      debugPrint('❌ Erro na limpeza de arquivos temporários: $e');
    }
  }

  static Future<String> _getTempPath() async {
    final dir = await getTemporaryDirectory();
    return dir.path;
  }
}

