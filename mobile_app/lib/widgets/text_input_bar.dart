/// Barra de input de texto para envio de mensagens
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../utils/error_handler.dart';

class TextInputBar extends StatefulWidget {
  const TextInputBar({super.key});

  @override
  State<TextInputBar> createState() => _TextInputBarState();
}

class _TextInputBarState extends State<TextInputBar> {
  final TextEditingController _controller = TextEditingController();
  bool _isSending = false;

  @override
  void dispose() {
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
    final screenWidth = MediaQuery.of(context).size.width;
    final isTablet = AppTheme.isTablet(screenWidth);
    final apiService = context.watch<ApiService>();
    final isStreaming = apiService.isStreaming;

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: AppTheme.responsiveSpacing(
          screenWidth,
          small: AppTheme.spacingM,
          medium: AppTheme.spacingM,
          large: AppTheme.spacingL,
        ),
        vertical: AppTheme.spacingS,
      ),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                enabled: !_isSending && !isStreaming,
                decoration: InputDecoration(
                  hintText: isStreaming
                      ? 'Aguardando resposta...'
                      : 'Digite sua mensagem...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusL),
                    borderSide: BorderSide(
                      color: Theme.of(context).dividerColor,
                    ),
                  ),
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: AppTheme.spacingM,
                    vertical: AppTheme.spacingS,
                  ),
                ),
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _sendText(),
              ),
            ),
            const SizedBox(width: AppTheme.spacingS),
            IconButton(
              onPressed: (_isSending || isStreaming) ? null : _sendText,
              icon: _isSending || isStreaming
                  ? SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    )
                  : const Icon(Icons.send),
              color: Theme.of(context).colorScheme.primary,
            ),
          ],
        ),
      ),
    );
  }
}

