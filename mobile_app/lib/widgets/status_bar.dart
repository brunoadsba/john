import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../services/wake_word_backend_service.dart';
import '../theme/app_theme.dart';

/// Barra de status do app
/// 
/// Exibe status dos serviços (API, Microfone, Wake Word, Gravação)
class StatusBar extends StatelessWidget {
  const StatusBar({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isSmallScreen = AppTheme.isSmallScreen(screenWidth);
    final isTablet = AppTheme.isTablet(screenWidth);

    return Consumer3<ApiService, AudioService, WakeWordBackendService>(
      builder: (context, apiService, audioService, wakeWordBackend, _) {
        return Container(
          padding: EdgeInsets.symmetric(
            horizontal:
                isSmallScreen ? AppTheme.spacingXS : AppTheme.spacingS,
            vertical: isSmallScreen ? AppTheme.spacingS : AppTheme.spacingS,
          ),
          color: AppTheme.surfaceVariant,
          child: isSmallScreen
              ? _CompactStatusBar(
                  apiService: apiService,
                  audioService: audioService,
                  wakeWordBackend: wakeWordBackend,
                )
              : _FullStatusBar(
                  apiService: apiService,
                  audioService: audioService,
                  wakeWordBackend: wakeWordBackend,
                  isTablet: isTablet,
                ),
        );
      },
    );
  }
}

/// Status bar completa (telas maiores)
class _FullStatusBar extends StatelessWidget {
  final ApiService apiService;
  final AudioService audioService;
  final WakeWordBackendService wakeWordBackend;
  final bool isTablet;

  const _FullStatusBar({
    required this.apiService,
    required this.audioService,
    required this.wakeWordBackend,
    required this.isTablet,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: isTablet ? AppTheme.spacingM : AppTheme.spacingS,
      runSpacing: AppTheme.spacingXS,
      children: [
        StatusChip(
          label: 'API',
          isActive: apiService.isConnected,
          compact: false,
        ),
        StatusChip(
          label: 'Microfone',
          isActive: audioService.hasPermission,
          compact: false,
        ),
        StatusChip(
          label: 'Wake Word',
          isActive: wakeWordBackend.isListening,
          compact: false,
        ),
        StatusChip(
          label: 'Gravando',
          isActive: audioService.isRecording,
          compact: false,
        ),
      ],
    );
  }
}

/// Status bar compacta (telas pequenas)
class _CompactStatusBar extends StatelessWidget {
  final ApiService apiService;
  final AudioService audioService;
  final WakeWordBackendService wakeWordBackend;

  const _CompactStatusBar({
    required this.apiService,
    required this.audioService,
    required this.wakeWordBackend,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: AppTheme.spacingS,
      runSpacing: AppTheme.spacingXS,
      children: [
        StatusChip(
          label: 'API',
          isActive: apiService.isConnected,
          compact: true,
        ),
        StatusChip(
          label: 'Mic',
          isActive: audioService.hasPermission,
          compact: true,
        ),
        StatusChip(
          label: 'Wake',
          isActive: wakeWordBackend.isListening,
          compact: true,
        ),
        StatusChip(
          label: 'Rec',
          isActive: audioService.isRecording,
          compact: true,
        ),
      ],
    );
  }
}

/// Chip de status individual
class StatusChip extends StatelessWidget {
  final String label;
  final bool isActive;
  final bool compact;

  const StatusChip({
    super.key,
    required this.label,
    required this.isActive,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(
        label,
        style: TextStyle(
          fontSize: compact ? AppTheme.fontSizeS - 1 : AppTheme.fontSizeS,
          fontWeight: FontWeight.w500,
        ),
      ),
      avatar: Icon(
        isActive ? Icons.check_circle : Icons.cancel,
        color: isActive ? AppTheme.success : AppTheme.error,
        size: compact ? AppTheme.iconSizeS : AppTheme.iconSizeS + 2,
      ),
      padding: EdgeInsets.symmetric(
        horizontal: compact ? AppTheme.spacingXS : AppTheme.spacingS,
        vertical: compact ? 0 : AppTheme.spacingXS,
      ),
      backgroundColor: isActive
          ? AppTheme.success.withOpacity(0.1)
          : AppTheme.error.withOpacity(0.1),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
}

