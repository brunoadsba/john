/// Barra de input de texto moderna estilo WhatsApp/Grok
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../theme/app_theme.dart';
import '../theme/responsive.dart';
import '../utils/error_handler.dart';
import 'glassmorphic_container.dart';
import 'metallic_glow_button.dart';

class TextInputBar extends StatefulWidget {
  const TextInputBar({super.key});

  @override
  State<TextInputBar> createState() => _TextInputBarState();
}

class _TextInputBarState extends State<TextInputBar> {
  final TextEditingController _controller = TextEditingController();
  bool _isSending = false;
  bool _hasText = false;
  Uint8List? _recordedAudio; // Áudio gravado aguardando envio

  // #region agent log helper
  void _logDebug({
    required String location,
    required String message,
    required String hypothesisId,
    Map<String, dynamic>? data,
    String runId = 'pre-fix',
  }) {
    const sessionId = 'debug-session';
    const logPath = '/home/brunoadsba/john/.cursor/debug.log';
    final entry = {
      'sessionId': sessionId,
      'runId': runId,
      'hypothesisId': hypothesisId,
      'location': location,
      'message': message,
      'data': data ?? {},
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };
    try {
      File(logPath).writeAsStringSync(
        jsonEncode(entry) + '\n',
        mode: FileMode.append,
        flush: true,
      );
    } catch (_) {
      // silencioso para não quebrar UI
    }
  }
  // #endregion

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onTextChanged);
  }

  void _onTextChanged() {
    setState(() {
      _hasText = _controller.text.trim().isNotEmpty;
    });
  }

  @override
  void dispose() {
    _controller.removeListener(_onTextChanged);
    _controller.dispose();
    super.dispose();
  }

  Future<void> _sendText() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isSending) return;

    final apiService = context.read<ApiService>();

    // Verifica se está conectado
    if (!apiService.isConnected) {
      try {
        await apiService.connect();
      } catch (e) {
        if (mounted) {
          ErrorHandler.showConnectionError(
            context,
            onRetry: () => apiService.connect(),
          );
        }
        return;
      }
    }

    setState(() {
      _isSending = true;
    });

    try {
      await apiService.sendText(text);
      _controller.clear();
    } catch (e) {
      if (mounted) {
        ErrorHandler.showError(
          context,
          ErrorHandler.getErrorMessage(e),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSending = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final apiService = context.watch<ApiService>();
    final isStreaming = apiService.isStreaming;

    final horizontalPadding = Responsive.horizontalPadding(context).horizontal;
    
    return GlassmorphicContainer(
      margin: EdgeInsets.fromLTRB(
        horizontalPadding,
        0,
        horizontalPadding,
        Responsive.spacing(context, small: 12, medium: 16),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      borderRadius: BorderRadius.circular(24),
      blur: 10.0,
      opacity: 0.15,
      child: SafeArea(
        top: false,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // TextField expansível com estilo moderno
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: isDark
                      ? AppTheme.darkSurfaceVariant.withOpacity(0.5)
                      : Colors.white.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(21),
                ),
                child: TextField(
                  controller: _controller,
                  enabled: !_isSending && !isStreaming,
                  maxLines: 5,
                  minLines: 1,
                  textCapitalization: TextCapitalization.sentences,
                  decoration: InputDecoration(
                    hintText: isStreaming
                        ? 'Aguardando resposta...'
                        : 'Digite ou fale...',
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 10,
                    ),
                    hintStyle: TextStyle(
                      color: isDark
                          ? AppTheme.timestampDark.withOpacity(0.7)
                          : AppTheme.timestampLight.withOpacity(0.7),
                    ),
                  ),
                  style: theme.textTheme.bodyMedium,
                  onSubmitted: (_) => _sendText(),
                ),
              ),
            ),
            const SizedBox(width: 8),

            // Botão Send, Voice ou Send Audio (alterna)
            if (_hasText)
              _buildSendButton(theme)
            else if (_recordedAudio != null)
              _buildSendAudioButton(theme)
            else
              _buildVoiceButton(theme),
          ],
        ),
      ),
    );
  }

  Widget _buildSendButton(ThemeData theme) {
    return Material(
      color: theme.colorScheme.primary,
      shape: const CircleBorder(),
      child: InkWell(
        onTap: (_isSending || context.read<ApiService>().isStreaming)
            ? null
            : _sendText,
        customBorder: const CircleBorder(),
        child: Container(
          width: 48,
          height: 48,
          alignment: Alignment.center,
          child: _isSending || context.watch<ApiService>().isStreaming
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                )
              : const Icon(
                  Icons.send,
                  color: Colors.white,
                  size: 20,
                ),
        ),
      ),
    );
  }

  Future<void> _handleVoicePress() async {
    final audioService = context.read<AudioService>();
    final apiService = context.read<ApiService>();

    _logDebug(
      location: 'text_input_bar.dart:_handleVoicePress',
      message: 'pressed mic',
      hypothesisId: 'H1',
      data: {
        'isRecording': audioService.isRecording,
        'hasPermission': audioService.hasPermission,
        'hasRecordedAudio': _recordedAudio != null,
      },
    );

    if (audioService.isRecording) {
      // Para gravação e salva (não envia automaticamente)
      final audioBytes = await audioService.stopRecording();

      if (audioBytes == null) {
        _logDebug(
          location: 'text_input_bar.dart:_handleVoicePress',
          message: 'stop recording returned null',
          hypothesisId: 'H1',
        );
        if (mounted) {
          ErrorHandler.showWarning(context, 'Nenhum áudio foi gravado');
        }
        return;
      }

      // Salva o áudio gravado para envio posterior
      setState(() {
        _recordedAudio = audioBytes;
      });
      _logDebug(
        location: 'text_input_bar.dart:_handleVoicePress',
        message: 'recording stopped, audio saved',
        hypothesisId: 'H1',
        data: {'audioBytes': audioBytes.length},
      );
    } else {
      // Solicita permissão se não tiver
      if (!audioService.hasPermission) {
        final granted = await audioService.requestPermissions();
        if (!granted) {
          _logDebug(
            location: 'text_input_bar.dart:_handleVoicePress',
            message: 'permission denied',
            hypothesisId: 'H1',
          );
          if (mounted) {
            ErrorHandler.showPermissionError(
              context,
              'microfone',
              onRequest: () => audioService.requestPermissions(),
            );
          }
          return;
        }
      }

      // Conecta à API se não estiver conectado
      if (!apiService.isConnected) {
        if (mounted) {
          ErrorHandler.showInfo(context, 'Conectando ao servidor...');
        }

        try {
          await apiService.connect();
        } catch (e) {
          if (mounted) {
            ErrorHandler.showConnectionError(
              context,
              onRetry: () => apiService.connect(),
            );
          }
          return;
        }
      }

      // Marca início da gravação para métricas
      apiService.metrics.markRecordingStart();
      _logDebug(
        location: 'text_input_bar.dart:_handleVoicePress',
        message: 'start recording',
        hypothesisId: 'H1',
      );
      
      // Inicia gravação
      try {
        await audioService.startRecording();
      } catch (e) {
        _logDebug(
          location: 'text_input_bar.dart:_handleVoicePress',
          message: 'startRecording exception',
          hypothesisId: 'H1',
          data: {'error': e.toString()},
        );
        if (mounted) {
          ErrorHandler.showError(
            context,
            ErrorHandler.getErrorMessage(e),
          );
        }
      }
    }
  }

  Future<void> _sendRecordedAudio() async {
    if (_recordedAudio == null) return;

    final apiService = context.read<ApiService>();
    final audioBytes = _recordedAudio!;

    _logDebug(
      location: 'text_input_bar.dart:_sendRecordedAudio',
      message: 'sending recorded audio',
      hypothesisId: 'H2',
      data: {'audioBytes': audioBytes.length, 'isConnected': apiService.isConnected},
    );

    // Limpa o áudio gravado
    setState(() {
      _recordedAudio = null;
      _isSending = true;
    });

    // Verifica e garante conexão antes de enviar
    if (!apiService.isConnected) {
      if (mounted) {
        ErrorHandler.showInfo(context, 'Reconectando ao servidor...');
      }

      try {
        await apiService.connect();
      } catch (e) {
        _logDebug(
          location: 'text_input_bar.dart:_sendRecordedAudio',
          message: 'connect failed',
          hypothesisId: 'H2',
          data: {'error': e.toString()},
        );
        if (mounted) {
          setState(() {
            _isSending = false;
            _recordedAudio = audioBytes; // Restaura se falhar
          });
          ErrorHandler.showConnectionError(
            context,
            onRetry: () async {
              try {
                await apiService.connect();
                await apiService.sendAudio(audioBytes);
                if (mounted) {
                  setState(() {
                    _recordedAudio = null;
                  });
                }
              } catch (e) {
                // Erro já será tratado pelo ErrorHandler
              }
            },
          );
        }
        return;
      }
    }

    // Envia para API
    try {
      await apiService.sendAudio(audioBytes);
      _logDebug(
        location: 'text_input_bar.dart:_sendRecordedAudio',
        message: 'sendAudio success',
        hypothesisId: 'H2',
        data: {'audioBytes': audioBytes.length},
      );
      if (mounted) {
        setState(() {
          _recordedAudio = null;
        });
      }
    } catch (e) {
      _logDebug(
        location: 'text_input_bar.dart:_sendRecordedAudio',
        message: 'sendAudio exception',
        hypothesisId: 'H2',
        data: {'error': e.toString()},
      );
      if (mounted) {
        setState(() {
          _recordedAudio = audioBytes; // Restaura se falhar
        });
        ErrorHandler.showAudioError(
          context,
          ErrorHandler.getErrorMessage(e),
          onRetry: () async {
            try {
              await apiService.sendAudio(audioBytes);
              _logDebug(
                location: 'text_input_bar.dart:_sendRecordedAudio',
                message: 'retry sendAudio success',
                hypothesisId: 'H2',
                data: {'audioBytes': audioBytes.length},
              );
              if (mounted) {
                setState(() {
                  _recordedAudio = null;
                });
              }
            } catch (e) {
              _logDebug(
                location: 'text_input_bar.dart:_sendRecordedAudio',
                message: 'retry sendAudio failed',
                hypothesisId: 'H2',
                data: {'error': e.toString()},
              );
              // Erro já será tratado
            }
          },
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSending = false;
        });
      }
    }
  }

  void _discardRecordedAudio() {
    setState(() {
      _recordedAudio = null;
    });
  }

  Widget _buildSendAudioButton(ThemeData theme) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Botão de descartar
        Material(
          color: Colors.grey[700],
          shape: const CircleBorder(),
          child: InkWell(
            onTap: _isSending ? null : _discardRecordedAudio,
            customBorder: const CircleBorder(),
            child: Container(
              width: 48,
              height: 48,
              alignment: Alignment.center,
              child: const Icon(
                Icons.close,
                color: Colors.white,
                size: 20,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        // Botão de enviar áudio
        Material(
          color: theme.colorScheme.primary,
          shape: const CircleBorder(),
          child: InkWell(
            onTap: _isSending ? null : _sendRecordedAudio,
            customBorder: const CircleBorder(),
            child: Container(
              width: 48,
              height: 48,
              alignment: Alignment.center,
              child: _isSending
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Icon(
                      Icons.send,
                      color: Colors.white,
                      size: 20,
                    ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildVoiceButton(ThemeData theme) {
    return Consumer2<AudioService, ApiService>(
      builder: (context, audioService, apiService, _) {
        final isRecording = audioService.isRecording;
        final canRecord = audioService.hasPermission;

        return MetallicGlowButton(
          onTap: canRecord ? _handleVoicePress : null,
          onLongPress: canRecord ? _handleVoicePress : null,
          onLongPressEnd: canRecord && isRecording
              ? () => _handleVoicePress()
              : null,
          icon: isRecording ? Icons.stop : Icons.mic,
          size: 48,
          isActive: isRecording,
          glowColor: isRecording
              ? AppTheme.recording
              : canRecord
                  ? theme.colorScheme.primary
                  : AppTheme.textTertiary,
          tooltip: isRecording
              ? 'Parar gravação'
              : canRecord
                  ? 'Gravar áudio'
                  : 'Permissão de microfone necessária',
        );
      },
    );
  }
}

