# Como Criar e Configurar Logo do App

## 📋 Resumo

O app atualmente usa a logo padrão do Flutter. Para usar uma logo personalizada, você precisa:

1. Ter uma imagem de logo (PNG, JPG, SVG)
2. Gerar ícones em múltiplos tamanhos usando ferramentas
3. Substituir os arquivos `ic_launcher.png` nas pastas `mipmap-*`

## 🎨 Opções para Criar Logo

### Opção 1: Usar Flutter Launcher Icons (Recomendado)

1. **Instalar o pacote:**
```bash
cd mobile_app
flutter pub add dev:flutter_launcher_icons
```

2. **Editar `pubspec.yaml`** para adicionar configuração:
```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.13.1

flutter_launcher_icons:
  android: true
  ios: false
  image_path: "assets/icons/logo.png"  # Sua logo (mínimo 1024x1024px)
  adaptive_icon_background: "#FFFFFF"  # Cor de fundo
  adaptive_icon_foreground: "assets/icons/logo.png"
```

3. **Gerar ícones:**
```bash
flutter pub get
flutter pub run flutter_launcher_icons
```

### Opção 2: Gerar Manualmente com Online Tools

1. Acesse: https://icon.kitchen/ ou https://www.appicon.co/
2. Faça upload da sua logo (PNG, mínimo 1024x1024px)
3. Baixe os ícones gerados
4. Substitua os arquivos em:
   - `mobile_app/android/app/src/main/res/mipmap-mdpi/ic_launcher.png` (48x48)
   - `mobile_app/android/app/src/main/res/mipmap-hdpi/ic_launcher.png` (72x72)
   - `mobile_app/android/app/src/main/res/mipmap-xhdpi/ic_launcher.png` (96x96)
   - `mobile_app/android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png` (144x144)
   - `mobile_app/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` (192x192)

### Opção 3: Criar Logo Simples (Temporário)

Se você quiser que eu crie uma logo simples baseada em texto "J" ou "JONH", posso gerar um arquivo SVG que você pode converter.

## 📝 Tamanhos Necessários

- **mdpi**: 48x48px
- **hdpi**: 72x72px  
- **xhdpi**: 96x96px
- **xxhdpi**: 144x144px
- **xxxhdpi**: 192x192px

**Tamanho ideal da imagem fonte**: 1024x1024px (quadrada)

## 🎯 Logo Recomendada

Sugestão de design:
- Fundo: Gradiente azul/teal (cor do tema do app)
- Elemento: Letra "J" estilizada ou ícone de assistente
- Estilo: Moderno, minimalista

## 📍 Localização Atual

Ícones atuais: `mobile_app/android/app/src/main/res/mipmap-*/ic_launcher.png`

Se você tem uma logo pronta, coloque em: `mobile_app/assets/icons/logo.png` e eu posso configurar o `flutter_launcher_icons` para gerar automaticamente.

