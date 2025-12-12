import 'package:flutter/material.dart';
import 'dart:async';

/// Widget que exibe texto caractere por caractere (streaming effect)
class StreamingText extends StatefulWidget {
  final String text;
  final TextStyle? style;
  final int maxLines;
  final TextOverflow overflow;
  final Duration characterDelay;
  final bool autoStart;

  const StreamingText({
    super.key,
    required this.text,
    this.style,
    this.maxLines = 1,
    this.overflow = TextOverflow.ellipsis,
    this.characterDelay = const Duration(milliseconds: 20),
    this.autoStart = true,
  });

  @override
  State<StreamingText> createState() => _StreamingTextState();
}

class _StreamingTextState extends State<StreamingText> {
  Timer? _timer;
  String _displayedText = '';
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    if (widget.autoStart && widget.text.isNotEmpty) {
      _startStreaming();
    }
  }

  @override
  void didUpdateWidget(StreamingText oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.text != widget.text) {
      _resetAndRestart();
    }
  }

  void _resetAndRestart() {
    _timer?.cancel();
    _displayedText = '';
    _currentIndex = 0;
    if (widget.text.isNotEmpty) {
      _startStreaming();
    } else {
      setState(() {});
    }
  }

  void _startStreaming() {
    if (widget.text.isEmpty) return;

    _timer = Timer.periodic(widget.characterDelay, (timer) {
      if (mounted) {
        setState(() {
          if (_currentIndex < widget.text.length) {
            _displayedText = widget.text.substring(0, _currentIndex + 1);
            _currentIndex++;
          } else {
            timer.cancel();
          }
        });
      } else {
        timer.cancel();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Text(
      _displayedText,
      style: widget.style,
      maxLines: widget.maxLines,
      overflow: widget.overflow,
    );
  }
}

