import 'package:flutter/material.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'dart:io';

/// Relatório de compatibilidade do dispositivo
class CompatibilityReport {
  int? apiLevel;
  bool isSupported = false;
  bool hasLowLatencyAudio = false;
  bool hasMicrophone = false;
  double? availableMemoryMB;
  bool hasEnoughMemory = false;
  int? cpuCores;
  String? cpuArchitecture;
  String? deviceModel;
  String? deviceManufacturer;
  
  Map<String, dynamic> toMap() {
    return {
      'apiLevel': apiLevel,
      'isSupported': isSupported,
      'hasLowLatencyAudio': hasLowLatencyAudio,
      'hasMicrophone': hasMicrophone,
      'availableMemoryMB': availableMemoryMB,
      'hasEnoughMemory': hasEnoughMemory,
      'cpuCores': cpuCores,
      'cpuArchitecture': cpuArchitecture,
      'deviceModel': deviceModel,
      'deviceManufacturer': deviceManufacturer,
    };
  }
  
  @override
  String toString() {
    return '''
Compatibilidade do Dispositivo:
- API Level: $apiLevel
- Suportado: $isSupported
- Áudio Low Latency: $hasLowLatencyAudio
- Microfone: $hasMicrophone
- Memória Disponível: ${availableMemoryMB?.toStringAsFixed(0)}MB
- Memória Suficiente: $hasEnoughMemory
- CPU Cores: $cpuCores
- Arquitetura: $cpuArchitecture
- Modelo: $deviceModel
- Fabricante: $deviceManufacturer
''';
  }
}

/// Utilitário para verificar compatibilidade do dispositivo
class DeviceCompatibility {
  static const int MIN_API_LEVEL = 26; // Android 8.0
  static const double MIN_MEMORY_MB = 512.0;
  
  /// Verifica compatibilidade do dispositivo
  static Future<CompatibilityReport> checkCompatibility() async {
    final report = CompatibilityReport();
    
    if (!Platform.isAndroid) {
      // Por enquanto, apenas Android é suportado
      report.isSupported = false;
      return report;
    }
    
    try {
      final deviceInfo = DeviceInfoPlugin();
      final androidInfo = await deviceInfo.androidInfo;
      
      // API Level
      report.apiLevel = androidInfo.version.sdkInt;
      report.isSupported = report.apiLevel! >= MIN_API_LEVEL;
      
      // Informações do dispositivo
      report.deviceModel = androidInfo.model;
      report.deviceManufacturer = androidInfo.manufacturer;
      
      // Recursos de hardware (verificação básica)
      // Nota: Verificação completa requer acesso a PackageManager
      // Por enquanto, assumimos que dispositivos Android têm microfone
      report.hasMicrophone = true; // Android requer microfone para este app
      
      // Low latency audio - verificação básica
      // API Level 26+ geralmente suporta low latency
      report.hasLowLatencyAudio = report.apiLevel! >= 26;
      
      // Memória - tentativa de obter via ActivityManager
      // Nota: Requer permissões ou acesso nativo
      // Por enquanto, assumimos memória suficiente se API level adequado
      report.hasEnoughMemory = report.isSupported;
      
      // CPU - informações básicas
      // Informações detalhadas requerem acesso nativo
      report.cpuCores = androidInfo.supportedAbis.length;
      report.cpuArchitecture = androidInfo.supportedAbis.isNotEmpty 
          ? androidInfo.supportedAbis.first 
          : 'unknown';
      
    } catch (e) {
      debugPrint('❌ Erro ao verificar compatibilidade: $e');
      report.isSupported = false;
    }
    
    return report;
  }
  
  /// Verifica e mostra aviso se dispositivo não for compatível
  static Future<void> warnUserIfIncompatible(BuildContext context) async {
    final report = await checkCompatibility();
    
    if (!report.isSupported) {
      if (context.mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Dispositivo não suportado'),
            content: Text(
              'Este app requer Android 8.0 (API 26) ou superior.\n\n'
              'Seu dispositivo: Android ${report.apiLevel ?? "desconhecido"}\n\n'
              'Algumas funcionalidades podem não funcionar corretamente.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Entendi'),
              ),
            ],
          ),
        );
      }
    } else if (report.availableMemoryMB != null && 
               report.availableMemoryMB! < MIN_MEMORY_MB) {
      if (context.mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Memória insuficiente'),
            content: Text(
              'O app pode ter performance degradada.\n\n'
              'Memória disponível: ${report.availableMemoryMB!.toStringAsFixed(0)}MB\n'
              'Recomendado: ${MIN_MEMORY_MB.toStringAsFixed(0)}MB ou mais',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Continuar'),
              ),
            ],
          ),
        );
      }
    }
  }
  
  /// Retorna resumo de compatibilidade para logs
  static Future<String> getCompatibilitySummary() async {
    final report = await checkCompatibility();
    return report.toString();
  }
}

