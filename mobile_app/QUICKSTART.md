# Quick Start - App Mobile Jonh Assistant

Guia rápido para executar o app Flutter.

## ⚡ Início Rápido

### 1. Verificar Flutter

```bash
flutter --version
flutter doctor
```

### 2. Instalar Dependências

```bash
cd mobile_app
flutter pub get
```

### 3. Configurar IP do Servidor (AUTOMÁTICO!)

**Opção 1: Script Automático (Recomendado)**
```bash
# Verifica configuração antes de rodar (opcional)
./scripts/check_mobile_config.sh
cd mobile_app && flutter run

# OU use o wrapper que faz tudo:
./scripts/run_mobile_app.sh
```

**Opção 2: Manual**
1. Descubra seu IP: `hostname -I` (Linux) ou `ipconfig` (Windows)
2. Edite `lib/services/api_service.dart`:
   ```dart
   static const String baseUrl = 'http://SEU_IP:8000';
   static const String wsUrl = 'ws://SEU_IP:8000/ws/listen';
   ```

**O script detecta e atualiza o IP automaticamente!** 🎉

### 4. Verificar Servidor Backend

```bash
# Servidor deve estar rodando
curl http://localhost:8000/health

# E acessível via IP da rede
curl http://172.20.240.80:8000/health
```

### 5. Verificar Dispositivos

```bash
flutter devices
```

**Opções:**
- Dispositivo físico conectado via USB
- Emulador Android (AVD)
- Chrome (para testes web)

### 6. Executar App

**Método 1: Script Automático (Recomendado)**
```bash
# Atualiza IP e executa automaticamente
./scripts/run_mobile_app.sh

# Ou especificar dispositivo
./scripts/run_mobile_app.sh -d <device-id>
```

**Método 2: Manual**
```bash
# Verificar configuração primeiro (opcional)
./scripts/check_mobile_config.sh

# Depois executar
cd mobile_app
flutter run
```

## 🔧 Troubleshooting

### Erro: "Servidor não acessível"

**Solução:**
1. Verifique se servidor está rodando: `ps aux | grep "python3 backend/api/main.py"`
2. Confirme que servidor está em `0.0.0.0:8000` (não `127.0.0.1`)
3. Verifique firewall: `sudo ufw allow 8000/tcp`
4. Teste conectividade: `ping 172.20.240.80`

### Erro: "No devices found"

**Solução:**
1. Conecte dispositivo via USB e ative "Depuração USB"
2. Ou inicie emulador Android
3. Ou use Chrome: `flutter run -d chrome`

### Erro: "WebSocket connection failed"

**Solução:**
1. Verifique IP correto no código
2. Confirme que servidor aceita conexões externas
3. Verifique logs do servidor

## 📱 Funcionalidades

- ✅ Interface de chat
- ✅ Gravação de áudio
- ✅ WebSocket em tempo real
- ✅ Reprodução de respostas
- 🔄 Wake word (em desenvolvimento)

## 🎯 Teste Rápido

1. Execute o app: `flutter run`
2. Toque no botão do microfone
3. Fale uma pergunta
4. Aguarde a resposta do assistente

---

## 📦 Build de APK

### Gerar APK para Android

```bash
cd mobile_app
flutter build apk --release
```

**APK gerado em:** `build/app/outputs/flutter-apk/app-release.apk`

### Instalar no Dispositivo

```bash
# Via USB (ADB)
adb install build/app/outputs/flutter-apk/app-release.apk

# Ou transfira manualmente e instale
```

## 🌐 Teste no Navegador

O app também funciona no navegador para testes rápidos:

```bash
flutter run -d chrome
```

**Funcionalidades testadas no web:**
- ✅ Gravação de áudio (blob URLs)
- ✅ Permissão de microfone automática
- ✅ WebSocket em tempo real
- ✅ Reprodução de áudio
- ✅ Interface completa

---

**Última atualização:** 05/12/2024  
**Status:** ✅ App 100% funcional (web e mobile)

