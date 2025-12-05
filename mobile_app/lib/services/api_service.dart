import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/message.dart';

/// Serviço de comunicação com a API do Jonh Assistant
class ApiService extends ChangeNotifier {
  // TODO: Configure o IP da sua máquina na rede local
  // Descubra com: hostname -I (Linux) ou ipconfig (Windows)
  static const String baseUrl = 'http://172.20.240.80:8000';
  static const String wsUrl = 'ws://172.20.240.80:8000/ws/listen';
  
  // Para desenvolvimento local, use:
  // static const String baseUrl = 'http://localhost:8000';
  // static const String wsUrl = 'ws://localhost:8000/ws/listen';
  
  WebSocketChannel? _channel;
  String? _sessionId;
  bool _isConnected = false;
  
  bool get isConnected => _isConnected;
  String? get sessionId => _sessionId;
  
  final List<Message> _messages = [];
  List<Message> get messages => List.unmodifiable(_messages);
  
  /// Conecta ao WebSocket
  Future<void> connect() async {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _isConnected = true;
      
      // Escuta mensagens do servidor
      _channel!.stream.listen(
        _handleWebSocketMessage,
        onError: (error) {
          debugPrint('WebSocket error: $error');
          _isConnected = false;
          notifyListeners();
        },
        onDone: () {
          debugPrint('WebSocket closed');
          _isConnected = false;
          notifyListeners();
        },
      );
      
      notifyListeners();
    } catch (e) {
      debugPrint('Erro ao conectar WebSocket: $e');
      _isConnected = false;
      notifyListeners();
    }
  }
  
  /// Desconecta do WebSocket
  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
    _sessionId = null;
    notifyListeners();
  }
  
  /// Envia áudio para processamento
  Future<void> sendAudio(List<int> audioBytes) async {
    if (!_isConnected || _channel == null) {
      throw Exception('WebSocket não conectado');
    }
    
    // Envia bytes de áudio
    _channel!.sink.add(audioBytes);
  }
  
  /// Envia mensagem de controle
  void sendControlMessage(Map<String, dynamic> message) {
    if (!_isConnected || _channel == null) return;
    _channel!.sink.add(jsonEncode(message));
  }
  
  /// Inicia nova sessão
  void startSession() {
    sendControlMessage({'type': 'start_session'});
  }
  
  /// Encerra sessão
  void endSession() {
    sendControlMessage({'type': 'end_session'});
  }
  
  /// Processa mensagens do WebSocket
  void _handleWebSocketMessage(dynamic data) {
    if (data is String) {
      // Mensagem JSON
      try {
        final json = jsonDecode(data);
        final type = json['type'];
        
        switch (type) {
          case 'session_started':
          case 'session_created':
            _sessionId = json['session_id'];
            _addSystemMessage('Sessão iniciada');
            break;
            
          case 'transcription':
            final text = json['text'];
            _addMessage(Message(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: text,
              type: MessageType.user,
            ));
            break;
            
          case 'response':
            final text = json['text'];
            _addMessage(Message(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: text,
              type: MessageType.assistant,
            ));
            break;
            
          case 'processing':
            final stage = json['stage'];
            _addSystemMessage('Processando: $stage');
            break;
            
          case 'error':
            final message = json['message'];
            _addMessage(Message(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: message,
              type: MessageType.error,
            ));
            break;
        }
      } catch (e) {
        debugPrint('Erro ao processar mensagem JSON: $e');
      }
    } else if (data is List<int>) {
      // Dados de áudio recebidos
      debugPrint('Áudio recebido: ${data.length} bytes');
      // TODO: Reproduzir áudio
    }
  }
  
  /// Adiciona mensagem à lista
  void _addMessage(Message message) {
    _messages.add(message);
    notifyListeners();
  }
  
  /// Adiciona mensagem do sistema
  void _addSystemMessage(String content) {
    _addMessage(Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      type: MessageType.system,
    ));
  }
  
  /// Limpa histórico de mensagens
  void clearMessages() {
    _messages.clear();
    notifyListeners();
  }
  
  /// Testa conexão com a API
  Future<bool> testConnection() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Erro ao testar conexão: $e');
      return false;
    }
  }
  
  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}

