# Como Conectar App Mobile ao Servidor WSL

## 🔍 Problema

O servidor está rodando no **WSL2** (rede `172.20.240.x`), mas o **celular** está na rede **Wi-Fi** (`192.168.1.x`). São redes diferentes, então o celular não consegue acessar diretamente o IP do WSL.

## ✅ Solução: Port Forwarding

Configure port forwarding no Windows para redirecionar conexões de `192.168.1.5:8000` para `172.20.240.80:8000`.

### Método 1: Script PowerShell (Recomendado)

**No PowerShell do Windows (como Administrador):**

```powershell
cd C:\Users\danyp\john\scripts
.\port_forward_wsl.ps1
```

Ou execute diretamente:

```powershell
# Como Administrador
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.20.240.80
```

### Método 2: Manual

1. Abra PowerShell **como Administrador**
2. Execute:
   ```powershell
   netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.20.240.80
   ```
3. Verifique:
   ```powershell
   netsh interface portproxy show v4tov4
   ```

### Método 3: Firewall do Windows

Se ainda não funcionar, pode ser necessário liberar a porta no firewall:

```powershell
# Adiciona regra de entrada
New-NetFirewallRule -DisplayName "John Assistant API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

## 🔧 Verificação

### 1. Teste no Windows

```powershell
# No PowerShell do Windows
curl http://192.168.1.5:8000/health
```

Deve retornar: `{"status": "ok"}`

### 2. Teste no Celular

No navegador do celular, acesse:
```
http://192.168.1.5:8000/health
```

Deve retornar: `{"status": "ok"}`

### 3. Configuração do App

O app já está configurado com o IP correto no `env.dart`:
```dart
defaultValue: 'http://192.168.1.5:8000'
```

Se você gerou o APK com `--dart-define=BACKEND_URL=http://172.20.240.80:8000`, precisa **regenerar** o APK:

```bash
cd mobile_app
flutter build apk --release --dart-define=BACKEND_URL=http://192.168.1.5:8000
```

## 🛠️ Troubleshooting

### Port forwarding não persiste após reiniciar?

Adicione ao `~/.bashrc` do WSL ou crie um script de inicialização no Windows.

### Firewall bloqueando?

Verifique se a porta está liberada:
```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*8000*"}
```

### WSL IP mudou?

Verifique o IP atual do WSL:
```bash
# No WSL
ip addr show eth0 | grep inet
```

Atualize o script `port_forward_wsl.ps1` com o novo IP.

## 📝 Notas

- Port forwarding é necessário porque WSL2 usa NAT networking
- O IP do WSL pode mudar após reiniciar o WSL (mas geralmente mantém)
- Se o IP mudar, execute o script novamente

