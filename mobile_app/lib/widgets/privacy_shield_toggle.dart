import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/privacy_service.dart';

/// Widget toggle para Modo Privacidade
/// 
/// Exibe estado atual e permite alternar entre modo cloud e local
class PrivacyShieldToggle extends StatefulWidget {
  final Function(bool)? onModeChanged;

  const PrivacyShieldToggle({
    super.key,
    this.onModeChanged,
  });

  @override
  State<PrivacyShieldToggle> createState() => _PrivacyShieldToggleState();
}

class _PrivacyShieldToggleState extends State<PrivacyShieldToggle> {
  bool _isSecureMode = false;
  bool _isLoading = false;
  final PrivacyService _service = PrivacyService();

  @override
  void initState() {
    super.initState();
    _loadStatus();
  }

  Future<void> _loadStatus() async {
    final status = await _service.getStatus();
    if (status != null && mounted) {
      setState(() {
        _isSecureMode = status['privacy_mode'] ?? false;
      });
    }
  }

  Future<void> _toggleMode() async {
    if (_isLoading) return;

    // Feedback tátil
    HapticFeedback.heavyImpact();

    setState(() {
      _isLoading = true;
    });

    // Chama o backend
    bool success = await _service.setPrivacyMode(!_isSecureMode);

    if (success && mounted) {
      setState(() {
        _isSecureMode = !_isSecureMode;
        _isLoading = false;
      });

      // Notifica o app pai
      widget.onModeChanged?.call(_isSecureMode);

      if (_isSecureMode) {
        _showSecureFeedback();
      }
    } else if (mounted) {
      setState(() {
        _isLoading = false;
      });
      _showError();
    }
  }

  void _showSecureFeedback() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: Colors.black87,
        content: Row(
          children: const [
            Icon(Icons.shield, color: Color(0xFF00FF41)),
            SizedBox(width: 10),
            Text(
              'MODO PRIVACIDADE ATIVO',
              style: TextStyle(
                color: Color(0xFF00FF41),
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showError() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Falha ao conectar ao servidor'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final backgroundColor = _isSecureMode ? Colors.black : Colors.blue.shade50;
    final borderColor = _isSecureMode
        ? const Color(0xFF00FF41)
        : Colors.blue.shade200;
    final iconColor =
        _isSecureMode ? const Color(0xFF00FF41) : Colors.blue;
    final textColor =
        _isSecureMode ? const Color(0xFF00FF41) : Colors.blue.shade900;

    return GestureDetector(
      onTap: _toggleMode,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: borderColor, width: 2),
          boxShadow: _isSecureMode
              ? [
                  BoxShadow(
                    color: const Color(0xFF00FF41).withOpacity(0.4),
                    blurRadius: 10,
                    spreadRadius: 2,
                  )
                ]
              : [],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              transitionBuilder: (child, anim) =>
                  ScaleTransition(scale: anim, child: child),
              child: _isLoading
                  ? SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: iconColor,
                      ),
                    )
                  : Icon(
                      _isSecureMode ? Icons.lock_outline : Icons.cloud_outlined,
                      key: ValueKey<bool>(_isSecureMode),
                      color: iconColor,
                    ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _isSecureMode ? 'SECURE CORE' : 'CLOUD MODE',
                  style: TextStyle(
                    color: textColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                    letterSpacing: 1.0,
                  ),
                ),
                Text(
                  _isSecureMode ? 'Offline & Privado' : 'Groq AI Ativa',
                  style: TextStyle(
                    color: textColor.withOpacity(0.7),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

