# 🔧 Troubleshooting - Jonh Assistant

Solução de problemas comuns do projeto.

---

## 🌐 Problemas de Rede

### ERR_CONNECTION_RESET - Celular não acessa servidor

**Sintoma:** App mobile não consegue conectar ao backend.

**Causa:** Servidor rodando no WSL2 não é acessível diretamente do dispositivo físico.

**Solução:**

1. **Configurar Port Forwarding no Windows (PowerShell como Admin):**
```powershell
# Descobrir IP do WSL2
wsl hostname -I

# Criar regra de port forwarding
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.20.240.80

# Permitir no firewall
netsh advfirewall firewall add rule name="Jonh Assistant" dir=in action=allow protocol=TCP localport=8000
```

2. **Descobrir IP do Windows na rede WiFi:**
```powershell
ipconfig | findstr IPv4
```

3. **Atualizar IP no app mobile:**
   - Editar `mobile_app/lib/config/env.dart`
   - Usar IP do Windows (ex: `192.168.1.5:8000`)

**Script automático:** `scripts/configurar_rede_windows.ps1`

---

## 📱 Problemas do App Mobile

### App não conecta ao servidor

1. Verificar se servidor está rodando:
```bash
curl http://localhost:8000/health
```

2. Verificar IP configurado no app:
```bash
grep "backendUrl" mobile_app/lib/config/env.dart
```

3. Testar conectividade do dispositivo:
```bash
# No dispositivo Android via ADB
adb shell ping -c 3 192.168.1.5
```

### Wake Word não funciona

1. Verificar se WebSocket está conectado
2. Verificar logs do backend:
```bash
tail -f /tmp/server.log | grep wake_word
```

3. Verificar logs do app:
```bash
./scripts/capturar_logs_app.sh monitor
```

---

## 🔧 Problemas do Backend

### Servidor não inicia

1. Verificar se porta 8000 está livre:
```bash
lsof -i :8000
```

2. Verificar dependências:
```bash
cd backend
pip install -r requirements.txt
```

3. Verificar variáveis de ambiente:
```bash
cat .env
```

### Serviços offline

Verificar status:
```bash
curl http://localhost:8000/health | jq
```

Se algum serviço estiver offline:
- **STT:** Verificar se Whisper está instalado
- **LLM:** Verificar se Ollama está rodando ou Groq configurado
- **TTS:** Verificar se Piper está instalado

---

## 🐛 Debug

### Capturar logs do app
```bash
./scripts/capturar_logs_app.sh monitor
```

### Capturar logs do servidor
```bash
tail -f /tmp/server.log
```

### Testar endpoints
```bash
# Health
curl http://localhost:8000/health

# Process text
curl -X POST http://localhost:8000/api/process_text \
  -F "texto=teste" \
  -F "session_id=test"
```

---

## 📚 Referências

- [WSL2 Network Fix](./WSL2_NETWORK_FIX.md) - Detalhes sobre rede WSL2
- [Mobile App Debugging](./DEBUGGING_MOBILE.md) - Debug específico do app

