"""Padrões conhecidos de erros e suas soluções"""
from typing import Dict, Any

# Padrões conhecidos de erros e suas soluções
ERROR_PATTERNS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "network": {
        "connection": {
            "keywords": ["connection", "connect", "network", "socket", "websocket"],
            "solutions": [
                "Verifique se o servidor está rodando",
                "Confirme que o dispositivo está na mesma rede WiFi",
                "Verifique o IP do servidor nas configurações",
                "Teste a conectividade: ping [IP_DO_SERVIDOR]"
            ]
        },
        "timeout": {
            "keywords": ["timeout", "timed out", "time out"],
            "solutions": [
                "O servidor pode estar sobrecarregado",
                "Aumente o timeout nas configurações",
                "Verifique a velocidade da conexão WiFi",
                "Tente novamente em alguns segundos"
            ]
        },
        "dns": {
            "keywords": ["dns", "hostname", "resolve", "name resolution"],
            "solutions": [
                "Verifique se o IP do servidor está correto",
                "Use o IP numérico ao invés do hostname",
                "Confirme que o servidor está acessível na rede"
            ]
        }
    },
    "audio": {
        "permission": {
            "keywords": ["permission", "microphone", "mic", "audio permission"],
            "solutions": [
                "Permita acesso ao microfone nas configurações do dispositivo",
                "Vá em Configurações > Apps > Jonh Assistant > Permissões",
                "Ative a permissão de microfone"
            ]
        },
        "recording": {
            "keywords": ["recording", "record", "audio capture", "failed to record"],
            "solutions": [
                "Verifique se outro app está usando o microfone",
                "Reinicie o app",
                "Verifique se o microfone está funcionando em outros apps"
            ]
        },
        "playback": {
            "keywords": ["playback", "play", "audio playback", "speaker"],
            "solutions": [
                "Verifique o volume do dispositivo",
                "Confirme que o áudio não está em modo silencioso",
                "Teste o áudio em outros apps"
            ]
        }
    },
    "permission": {
        "microphone": {
            "keywords": ["microphone", "mic", "audio"],
            "solutions": [
                "Permita acesso ao microfone nas configurações",
                "Vá em Configurações > Apps > Permissões > Microfone"
            ]
        },
        "storage": {
            "keywords": ["storage", "file", "write", "read"],
            "solutions": [
                "Permita acesso ao armazenamento nas configurações",
                "Vá em Configurações > Apps > Permissões > Armazenamento"
            ]
        }
    },
    "crash": {
        "general": {
            "keywords": ["crash", "exception", "fatal", "unhandled"],
            "solutions": [
                "Reinicie o app",
                "Atualize para a versão mais recente",
                "Limpe o cache do app",
                "Reinstale o app se o problema persistir"
            ]
        },
        "memory": {
            "keywords": ["memory", "out of memory", "oom"],
            "solutions": [
                "Feche outros apps para liberar memória",
                "Reinicie o dispositivo",
                "O app pode precisar de mais memória disponível"
            ]
        }
    }
}

