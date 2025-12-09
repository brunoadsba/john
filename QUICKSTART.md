# Quick Start - Jonh Assistant

Suba o backend, teste o streaming e rode o app mobile rapidamente.

## 1) Pré-requisitos
- Python 3.10+ (WSL2 Ubuntu 22.04/24.04)
- Flutter 3.35+ (opcional, para mobile)
- Ollama instalado **ou** conta no Groq (API key)

## 2) Backend em 3 passos
```bash
git clone <seu-repositorio> john
cd john

python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

cp .env.example .env
nano .env   # LLM_PROVIDER=groq ou ollama; configure GROQ_API_KEY se usar Groq
```

Subir servidor (expondo para mobile):
```bash
cd backend
source .venv/bin/activate
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Smoke tests:
```bash
curl http://127.0.0.1:8000/health
curl -N "http://127.0.0.1:8000/api/stream_text?texto=oi%20jonh"
```

## 3) Mobile (opcional)
```bash
./scripts/check_mobile_config.sh   # confere URL do backend em env.dart

cd mobile_app
flutter pub get
flutter run        # ou flutter run -d chrome
```

Build APK:
```bash
cd mobile_app
flutter build apk --release
# build/app/outputs/flutter-apk/app-release.apk
```

## 4) Documentação rápida
- Visão geral: [README.md](README.md)
- Status: [docs/STATUS_PROJETO.md](docs/STATUS_PROJETO.md)
- Arquitetura: [docs/ARQUITETURA.md](docs/ARQUITETURA.md)
- Comparação Groq vs Ollama: [docs/COMPARACAO_LLM.md](docs/COMPARACAO_LLM.md)

## 5) Problemas comuns
- Groq: confira `GROQ_API_KEY` no `.env`
- Ollama: `ollama serve &` e confirme modelo `llama3` baixado
- Porta 8000 ocupada: ajuste `PORT` no `.env` ou libere a porta
