# Jonh Assistant - Mobile App

Aplicativo mobile Flutter para interagir com o assistente de voz Jonh.

## 🎯 Funcionalidades

- ✅ **Interface de Chat**: Conversação fluida com o assistente
- ✅ **Gravação de Áudio**: Captura otimizada (16kHz mono)
- ✅ **WebSocket**: Comunicação em tempo real
- ✅ **Reprodução de Áudio**: Respostas em voz
- 🔄 **Wake Word**: Detecção por voz "Jonh" (em desenvolvimento)

## 📋 Requisitos

- Flutter 3.0.0+
- Dart 3.0.0+
- Android 5.0+ (API 21+)
- Servidor backend rodando

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
cd mobile_app
flutter pub get
```

### 2. Configurar IP do Servidor

Edite `lib/services/api_service.dart`:

```dart
static const String baseUrl = 'http://SEU_IP:8000';
static const String wsUrl = 'ws://SEU_IP:8000/ws/listen';
```

**Descobrir seu IP:**
```bash
# Linux/WSL
hostname -I

# Windows
ipconfig
```

### 3. Executar

```bash
flutter run
```

## 📱 Como Usar

### Conversação por Toque

1. Toque e segure o botão do microfone
2. Fale sua pergunta
3. Solte o botão
4. Aguarde a resposta

### Wake Word (Futuro)

1. Diga "Jonh"
2. Fale sua pergunta
3. Aguarde a resposta

## 🏗️ Arquitetura

```
lib/
├── main.dart                 # Entry point
├── models/
│   └── message.dart          # Modelo de mensagem
├── screens/
│   └── home_screen.dart      # Tela principal
├── services/
│   ├── api_service.dart      # Comunicação backend
│   ├── audio_service.dart    # Áudio
│   └── wake_word_service.dart # Wake word (futuro)
└── widgets/
    ├── message_list.dart     # Lista de mensagens
    └── voice_button.dart     # Botão de voz
```

## 🔧 Configuração Avançada

### Permissões

Já configuradas em `AndroidManifest.xml`:
- `INTERNET`: Comunicação com backend
- `RECORD_AUDIO`: Gravação de voz
- `MODIFY_AUDIO_SETTINGS`: Configurações de áudio
- `WAKE_LOCK`: Manter app ativo

### Build Release

```bash
flutter build apk --release
```

**APK gerado em:** `build/app/outputs/flutter-apk/app-release.apk`

### Instalar APK

```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

## 🐛 Troubleshooting

### Não conecta ao servidor

1. Verifique se backend está rodando: `curl http://localhost:8000/health`
2. Confirme IP correto no código
3. Teste conectividade: `ping SEU_IP`
4. Verifique firewall: `sudo ufw allow 8000/tcp`

### Permissão de microfone negada

1. Configurações > Apps > Jonh Assistant > Permissões > Microfone
2. Desinstale e reinstale o app

### WebSocket fecha imediatamente

1. Verifique logs do servidor
2. Confirme URL (deve começar com `ws://`, não `http://`)
3. Teste WebSocket com ferramenta online

## 📚 Documentação Completa

- **[Guia Completo](../docs/MOBILE_APP.md)**: Instalação, uso, troubleshooting
- **[Arquitetura](../docs/ARQUITETURA.md)**: Detalhes técnicos
- **[Wake Word](../docs/WAKE_WORD.md)**: Implementação futura

## 🧪 Testes

```bash
# Todos os testes
flutter test

# Teste específico
flutter test test/services/api_service_test.dart
```

## 📊 Performance

**Pipeline completo (médio):**
- Gravação: Instantâneo
- Envio: ~100ms
- STT: ~800ms
- LLM: ~300ms (Groq) / ~1800ms (Ollama)
- TTS: ~400ms
- Reprodução: Instantâneo
- **Total: ~1.6s (Groq) / ~3.1s (Ollama)**

## 🛠️ Desenvolvimento

### Hot Reload

```bash
flutter run
# Pressione 'r' para hot reload
# Pressione 'R' para hot restart
```

### Logs

```bash
flutter logs
```

### Análise de Código

```bash
flutter analyze
```

### Formatação

```bash
flutter format lib/
```

## 🔮 Roadmap

- [ ] Wake word detection (Porcupine)
- [ ] Detecção de silêncio automática
- [ ] Histórico persistente (SQLite)
- [ ] Configurações de usuário
- [ ] Suporte iOS
- [ ] Temas customizáveis
- [ ] Modo offline parcial

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para detalhes.

## 📄 Licença

MIT License - veja [LICENSE](../LICENSE) para detalhes.

## 👤 Autor

Projeto Jonh Assistant

---

**Desenvolvido com ❤️ usando Flutter**
