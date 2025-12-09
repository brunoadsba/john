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

### 2. Configurar IP do Servidor (AUTOMÁTICO!)

**Opção 1: Script Automático (Recomendado)**
```bash
# Script detecta IP, atualiza configuração e gerencia servidor automaticamente
./scripts/run_mobile_app.sh
```

**Opção 2: Manual**
```bash
# Verificar configuração (opcional - IP já está configurado)
./scripts/check_mobile_config.sh

# Depois executar
cd mobile_app
flutter run
```

**O script detecta e atualiza o IP automaticamente quando você muda de rede WiFi!** 🎉

### 3. Executar

**Método Automático:**
```bash
# Atualiza IP e executa tudo automaticamente
./scripts/run_mobile_app.sh
```

**Método Manual:**
```bash
cd mobile_app
flutter run
```

**Para testar no navegador:**
```bash
flutter run -d chrome
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
cd mobile_app
flutter build apk --release
```

**APK gerado em:** `build/app/outputs/flutter-apk/app-release.apk`

**Tamanho aproximado:** ~15-20 MB

### Instalar APK

**Método 1: Via ADB (USB)**
```bash
# Conecte dispositivo via USB
adb devices

# Instale APK
adb install build/app/outputs/flutter-apk/app-release.apk
```

**Método 2: Transferência Manual**
1. Copie `app-release.apk` para o smartphone
2. Ative "Fontes desconhecidas" nas configurações
3. Abra o arquivo APK e instale

### Build para Web

```bash
flutter build web --release
```

**Arquivos gerados em:** `build/web/`

### Testar no Navegador

```bash
# Executar em modo desenvolvimento
flutter run -d chrome

# Ou build e servir
flutter build web
cd build/web
python3 -m http.server 8080
# Acesse: http://localhost:8080
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
