/// Serviço de localização GPS para o app John
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import '../config/env.dart';
import 'api_service.dart';

/// Serviço de localização GPS
class LocationService {
  static const String _prefKeyEnabled = 'location_enabled';
  static const String _prefKeyLastLat = 'location_last_lat';
  static const String _prefKeyLastLon = 'location_last_lon';
  
  final ApiService apiService;
  bool _isEnabled = false;
  Position? _lastPosition;
  
  LocationService(this.apiService) {
    // Carrega preferências de forma assíncrona
    _loadPreferences().catchError((e) {
      // Ignora erros na inicialização
    });
  }
  
  /// Carrega preferências salvas
  Future<void> _loadPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    _isEnabled = prefs.getBool(_prefKeyEnabled) ?? false;
    
    final lastLat = prefs.getDouble(_prefKeyLastLat);
    final lastLon = prefs.getDouble(_prefKeyLastLon);
    if (lastLat != null && lastLon != null) {
      _lastPosition = Position(
        latitude: lastLat,
        longitude: lastLon,
        timestamp: DateTime.now(),
        accuracy: 0,
        altitude: 0,
        heading: 0,
        speed: 0,
        speedAccuracy: 0,
        altitudeAccuracy: 0,
        headingAccuracy: 0,
      );
    }
  }
  
  /// Salva preferências
  Future<void> _savePreferences() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKeyEnabled, _isEnabled);
    
    if (_lastPosition != null) {
      await prefs.setDouble(_prefKeyLastLat, _lastPosition!.latitude);
      await prefs.setDouble(_prefKeyLastLon, _lastPosition!.longitude);
    }
  }
  
  /// Verifica se localização está habilitada
  bool get isEnabled => _isEnabled;
  
  /// Obtém última posição conhecida
  Position? get lastPosition => _lastPosition;
  
  /// Verifica se permissão de localização foi concedida
  Future<bool> hasPermission() async {
    final status = await Permission.location.status;
    return status.isGranted;
  }
  
  /// Solicita permissão de localização
  Future<bool> requestPermission() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }
  
  /// Habilita/desabilita serviço de localização
  Future<void> setEnabled(bool enabled) async {
    _isEnabled = enabled;
    await _savePreferences();
    
    if (enabled) {
      // Solicita permissão se necessário
      if (!await hasPermission()) {
        final granted = await requestPermission();
        if (!granted) {
          _isEnabled = false;
          await _savePreferences();
          return;
        }
      }
      
      // Obtém localização atual e envia ao backend
      await getCurrentLocationAndSend();
    }
  }
  
  /// Obtém localização atual
  Future<Position?> getCurrentLocation() async {
    try {
      // Verifica se GPS está habilitado
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return null;
      }
      
      // Verifica permissão
      if (!await hasPermission()) {
        return null;
      }
      
      // Obtém posição
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );
      
      _lastPosition = position;
      await _savePreferences();
      
      return position;
    } catch (e) {
      return null;
    }
  }
  
  /// Obtém localização atual e envia ao backend
  Future<bool> getCurrentLocationAndSend({String? sessionId}) async {
    if (!_isEnabled) {
      return false;
    }
    
    final position = await getCurrentLocation();
    if (position == null) {
      return false;
    }
    
    // Usa sessionId fornecido ou obtém do ApiService
    final currentSessionId = sessionId ?? apiService.sessionId;
    if (currentSessionId == null) {
      return false;
    }
    
    return await sendLocationToBackend(
      position.latitude,
      position.longitude,
      currentSessionId,
    );
  }
  
  /// Envia localização ao backend
  Future<bool> sendLocationToBackend(
    double latitude,
    double longitude,
    String sessionId,
  ) async {
    try {
      final baseUrl = Env.backendUrl.isNotEmpty
          ? Env.backendUrl
          : 'http://192.168.1.5:8000';
      final url = Uri.parse('$baseUrl/api/location/submit');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'latitude': latitude,
          'longitude': longitude,
        }),
      );
      
      if (response.statusCode == 200) {
        return true;
      } else {
        return false;
      }
    } catch (e) {
      return false;
    }
  }
}

