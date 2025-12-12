Estamos em uma era tecnológica em que quase não há privacidade. A ideia desse projeto 'John' é poder dar um pouco de privacidade aos usuários.

Atualmente o app John é híbrido Olhama + Groq

Quero criar uma opção, em que o usuário possa ativar o 'modo privacidade' ou seja, tudo no app será local, e usará a LLM local.

Ajude-me a pensar e criar algo que possa ser últil e que empolgue os usuários.




-----
Analise as propostas, e verifique o que é viável de ser implementado em nosso app

----


GROK


### Conceito do "Modo Privacidade" no App John

Entendi sua visão! O projeto John já tem uma base sólida para priorizar privacidade, com componentes como STT (Whisper) e TTS (Piper) rodando 100% local. Adicionar um "Modo Privacidade" que force tudo para execução local é uma extensão natural, alinhada com a era de preocupações com dados (como vazamentos em serviços cloud). Isso pode empolgar usuários que valorizam soberania de dados, como profissionais de TI, ativistas de privacidade ou pessoas em regiões com internet instável. Vamos pensar nisso de forma estruturada: o que seria o modo, por que empolga, como implementar e ideias para torná-lo útil e atrativo.

#### Por Que Isso Empolga os Usuários?
- **Narrativa de Empoderamento**: Posicione o modo como uma "fortaleza digital". Frases como "Seus segredos ficam em casa: ative o Modo Privacidade e corte qualquer conexão externa" podem criar um apelo emocional. Usuários se sentem no controle, evitando rastreamento de big techs (ex: Groq ou APIs de busca).
- **Benefícios Práticos**:
  - **Offline Total**: Funciona em aviões, áreas rurais ou durante quedas de rede – ideal para viajantes ou usuários em países com censura.
  - **Velocidade e Eficiência**: Sem latência de cloud, respostas podem ser mais rápidas em hardware decente (como o Galaxy Book 2 mencionado no README).
  - **Segurança**: Nada sai do dispositivo, reduzindo riscos de interceptação ou compliance com leis como LGPD/GDPR.
- **Diferencial Competitivo**: Diferente de Alexa/Siri, que dependem de cloud, John se torna um "assistente soberano". Isso pode atrair comunidades como open-source enthusiasts no Reddit ou GitHub.

Para empolgar mais, inclua gamificação: Um badge ou animação ao ativar ("Modo Privacidade Ativado: Seus Dados Estão Seguros!"), ou estatísticas como "Você evitou X chamadas de rede esta semana".

#### Definição do Modo Privacidade
Baseado no README, o modo pode ser uma configuração que:
- **Muda o LLM para Local**: Força `LLM_PROVIDER=ollama` (já suportado), usando modelos como llama3:8b-instruct-q4_0.
- **Desativa Recursos Dependentes de Rede**: 
  - Busca web (DuckDuckGo/Tavily) – desabilite `WEB_SEARCH_ENABLED=false`.
  - Plugins como Conversão de Moedas (se usar API externa) e Especialista em Vagas (que busca sites reais).
  - Qualquer ferramenta que exija internet, como atualizações de modelos ou métricas enviadas para fora.
- **Mantém Funcionalidades Locais**: STT, TTS, Calculadora (já offline), gerenciamento de memória/contexto, lembretes locais (usando SQLite), e processamento de áudio.
- **Modo Híbrido vs. Privacidade**: O padrão continua híbrido (Ollama + Groq), mas o usuário alterna via app. Ao ativar privacidade, mostre um aviso: "Recursos como busca web estarão indisponíveis, mas sua privacidade está garantida."

#### Ideias Úteis para Implementar e Enriquecer o Modo
Vamos tornar isso prático e escalável, integrando ao backend (FastAPI) e mobile (Flutter). Use o que já existe no projeto para minimizar trabalho.

1. **Implementação no Backend**:
   - **Configuração Dinâmica**: No `.env`, adicione `PRIVACY_MODE=false` como default. No `settings.py`, leia isso e use em condicionais.
   - **Endpoints Adaptados**:
     - Em rotas como `/api/stream_text` ou `/api/process_audio`, verifique o modo: Se privacidade ativada, force Ollama e ignore tools de rede. Exemplo em código:
       ```python
       if settings.PRIVACY_MODE:
           llm_provider = "ollama"
           web_search_enabled = False
       ```
     - Adicione um endpoint REST: `POST /api/toggle_privacy` que altera o modo em runtime (atualiza um DB ou cache) e retorna status.
     - **Segurança Extra**: No modo privacidade, limpe caches de respostas antigas que possam ter dados de cloud, e logue apenas localmente (sem envios externos).
   - **Integração com Plugins**: No `PluginManager`, adicione um filtro: Plugins marquem se são "network-dependent". No modo privacidade, o LLM só chama plugins locais (ex: Calculadora).

2. **Implementação no Mobile App (Flutter)**:
   - **UI/UX Empolgante**:
     - Na tela de configurações (`features/settings`), adicione um SwitchListTile: "Modo Privacidade" com ícone de escudo e descrição: "Tudo local: sem internet, máxima privacidade".
     - Ao ativar, envie uma requisição para o backend (`POST /api/toggle_privacy`) via `StreamingService` ou um novo `PrivacyService`.
     - Animação: Use `Fluttertoast` ou um dialog com confete (pacote como `confetti`) para celebrar: "Privacidade Ativada! Seus dados estão blindados."
     - Persistência: Armazene o estado localmente com `shared_preferences` para reconexão automática.
   - **Adaptação de Features**:
     - No chat, se o usuário pedir algo que exija rede (ex: "busque vagas"), responda: "No Modo Privacidade, isso não está disponível. Deseja desativar?" com botão para toggle.
     - Integre com wake word: No background service, priorize processamento local.

3. **Funcionalidades Exclusivas para Empolgar**:
   - **Lembretes e Anotações Locais Avançados**: Expanda o sistema de memória para criar "diário privado" – o usuário diz "lembre que meu aniversário é dia 10" e o app armazena/lembra localmente.
   - **Integração com Arquivos Locais**: Permita ler/gerenciar arquivos do dispositivo (ex: "leia meu documento.txt") usando permissões Flutter, mantendo tudo offline.
   - **Modos de Economia**: No privacidade, otimize para bateria baixa – reduza modelo LLM para um mais leve (ex: q2_K) automaticamente.
   - **Relatórios de Privacidade**: Gere um relatório semanal: "Esta semana, você processou X comandos localmente, evitando Y dados enviados para cloud."
   - **Customização de Modelos**: Permita download de modelos Ollama via app (antes de ativar o modo), com barra de progresso e verificação de hash para segurança.
   - **Comunidade**: Incentive usuários a compartilhar setups locais no GitHub issues, criando uma "galeria de mods privados".

4. **Testes e Troubleshooting**:
   - **Testes Automatizados**: Expanda `pytest` para cenários de modo privacidade (ex: simule Ollama sem rede). No Flutter, adicione integration tests para o toggle.
   - **Problemas Potenciais**: Modelos locais podem ser mais lentos em hardware fraco – avise no app. Solução: Recomende GPUs ou modelos otimizados no README.
   - **Métricas**: Use o sistema de performance (Feature 020) para comparar latência cloud vs. local, mostrando ao usuário: "No modo privacidade, sua resposta média é Z segundos mais rápida!"

#### Próximos Passos para Você
- **Protótipo Rápido**: Comece adicionando o toggle no mobile e o endpoint no backend. Teste com o script de métricas para validar latência.
- **Feedback de Usuários**: Adicione uma survey no app: "O que mais você quer no Modo Privacidade?" para iterar.
- **Marketing no README**: Atualize a seção "Modo Offline vs Cloud" para destacar isso, com um badge "Privacidade Primeiro".

-----

GEMINI


Essa é uma excelente iniciativa. O "John" já possui a fundação perfeita para isso (STT e TTS locais), o que coloca você muito à frente de assistentes comerciais que *precisam* enviar seu áudio para a nuvem apenas para transcrevê-lo.

Para tornar o **"Modo Privacidade"** algo que empolgue e seja útil, não devemos vendê-lo apenas como uma "chave de desligar internet", mas sim como um **"Modo de Segurança Máxima"** (ou *Bunker Mode*).

Aqui está uma proposta conceitual e técnica para transformar essa feature no grande diferencial do John:

-----

### 🚀 Conceito: "Protocolo Fortaleza" (Fortress Protocol)

A ideia é gamificar e tangibilizar a privacidade. Quando o usuário ativa esse modo, o John não apenas "corta a internet", ele entra em um estado de proteção de dados.

#### 1\. A Experiência do Usuário (UX "Uau")

  * **Visual Transformation:** Ao ativar o modo, a UI do App (Flutter) muda drasticamente.
      * **Cor:** Sai o tema padrão e entra um tema "Dark/Matrix" ou com acentos em Verde Neon (símbolo de seguro/criptografado).
      * **Ícone:** Um escudo ou cadeado se fecha na tela.
      * **Feedback Sonoro:** O John anuncia: *"Protocolo de privacidade ativo. Desconectando da nuvem. Seus dados estão restritos a este dispositivo."*
  * **Indicador de Hardware:** Se possível, piscar uma cor específica na tela quando o microfone abrir, indicando que o áudio vai morrer ali mesmo.

#### 2\. Funcionalidades Exclusivas do Modo Privado

Para ser útil, esse modo precisa permitir coisas que as pessoas têm medo de fazer na nuvem:

  * **"Diário Secreto" (Journaling):** "John, quero desabafar sobre meu trabalho/relacionamento". O usuário sabe que isso não vai treinar a IA da Groq/OpenAI.
  * **Análise de Dados Sensíveis:** "John, aqui está o resumo das minhas senhas/contas, organize para mim" (Processado localmente pelo Llama 3).
  * **Modo Amnésia (Opcional):** Uma sub-opção onde *nem o banco de dados SQLite local* guarda o histórico. Acabou a sessão, os dados são destruídos (RAM only).

-----

### 🛠️ Implementação Técnica

Baseado na sua arquitetura atual (FastAPI + Flutter + Pattern de Services), aqui está o roteiro para implementar isso sem refazer o sistema:

#### Passo 1: Backend - Runtime Provider Switching

Atualmente, o `LLM_PROVIDER` é definido no `.env` e carregado na inicialização. Precisamos mudar isso para ser dinâmico.

1.  **Novo Endpoint de Controle:**
    Crie um endpoint `POST /api/settings/privacy-mode` que aceita `{ "enabled": true }`.
2.  **Service Factory Dinâmico:**
    No seu `backend/services/llm/`, ao invés de instanciar apenas um serviço no startup, mantenha as duas instâncias (Groq e Ollama) "aquecidas" ou prontas para instanciar.
      * O `LLMService` principal vira um "Proxy" que decide para quem mandar a requisição baseado no estado atual da sessão.
3.  **Bloqueio de Tools de Rede:**
    Se `privacy_mode == true`, o `ToolManager` deve desabilitar automaticamente os plugins `web_search_plugin`, `job_search_plugin` e `currency_converter`, mantendo apenas `calculator` e `system_tools`.

#### Passo 2: Otimização do Ollama (Para não frustrar)

O modo local precisa ser rápido para não parecer "pior".

  * **Modelo Recomendado:** Garanta que o usuário tenha o `llama3:8b` (equilibrado) ou até o `phi3:mini` (extremamente rápido e leve) baixado.
  * **System Prompt "Seco":** No modo privado, altere o System Prompt para ser mais direto e conciso, economizando tokens e tempo de geração da GPU/CPU local.

#### Passo 3: Mobile App (Flutter)

1.  **Switch Global:** Adicione um toggle na AppBar ou no Menu Lateral.
2.  **Estado Persistente:** O app deve lembrar desse estado. Se eu fechar o app em "Modo Fortaleza", ele deve abrir assim (para evitar vazamento acidental).
3.  **Visual Feedback:**
    ```dart
    // Exemplo pseudo-código Flutter
    ThemeData get currentTheme => isPrivacyMode ? darkGreenTheme : standardTheme;
    ```

-----

### 💡 Exemplo de Fluxo de Uso (Storytelling)

1.  **Cenário:** O usuário está planejando uma viagem surpresa e precisa calcular gastos sensíveis.
2.  **Ação:** Ele toca no ícone de "Escudo" no app.
3.  **Reação do App:** A interface escurece, bordas ficam verdes.
      * *John (TTS Local):* "Modo seguro ativado. Estou operando 100% offline."
4.  **Interação:**
      * *Usuário:* "Quanto custa 1500 dólares em reais?"
      * *John:* "Em modo offline, não tenho acesso à cotação em tempo real. Mas se considerar a última taxa fixa de 5.0, seriam 7500 reais. Quer que eu use a calculadora para outro valor?" (O John entende a limitação e oferece a ferramenta offline `calculator`).
5.  **Interação Privada:**
      * *Usuário:* "Anote meu plano: comprar o anel dia 15 e esconder no cofre."
      * *John:* "Anotado na memória segura. Nenhuma nuvem recebeu essa informação."

### Próximo Passo Imediato

Posso ajudar você a criar o código para o **`LLMProxyService`** no Python? Isso permitiria alternar entre Groq e Ollama em tempo real sem precisar reiniciar o servidor, que é o coração dessa funcionalidade.



Aqui está a implementação técnica do **Backend** para habilitar o "Modo Privacidade".

Vamos criar um **`LLMProxyService`**. Ele funcionará como um "porteiro": o resto do sistema conversa com ele, e ele decide se encaminha o pedido para a nuvem (Groq) ou para o processamento local (Ollama) dinamicamente.

### 1\. A Nova Estrutura de Serviço (`backend/services/llm/proxy_service.py`)

Este serviço gerencia o estado (Cloud vs Local) e desativa ferramentas que requerem internet quando o modo privacidade está ativo.

```python
import os
from typing import AsyncGenerator, List, Dict, Any, Optional
from backend.services.llm.base import BaseLLMService  # Supondo que exista uma classe base
from backend.services.llm.groq_service import GroqService
from backend.services.llm.ollama_service import OllamaService

class LLMProxyService(BaseLLMService):
    def __init__(self):
        # Inicializa ambos os serviços, mas eles ficam em standby
        self.groq_service = GroqService()
        self.ollama_service = OllamaService()
        
        # Estado inicial (pode vir de config/banco)
        self.privacy_mode_active = False
        
        # Tools que são proibidas no modo privacidade (requerem internet)
        self.banned_tools_in_privacy = [
            "web_search", 
            "job_search", 
            "currency_converter",
            "weather_lookup" 
        ]

    def set_privacy_mode(self, enabled: bool):
        """Alterna o modo de operação dinamicamente"""
        self.privacy_mode_active = enabled
        mode_name = "🔒 LOCAL / PRIVADO" if enabled else "☁️ CLOUD / PADRÃO"
        print(f"--- [LLM PROXY] Modo alterado para: {mode_name} ---")
        return {
            "privacy_mode": enabled, 
            "provider": "ollama" if enabled else "groq"
        }

    def get_status(self):
        return {
            "privacy_mode": self.privacy_mode_active,
            "current_provider": "ollama" if self.privacy_mode_active else "groq",
            "offline_ready": self.ollama_service.is_available() # Método hipotético para checar se Ollama está rodando
        }

    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        
        # 1. Seleção do Provider
        active_service = self.ollama_service if self.privacy_mode_active else self.groq_service
        
        # 2. Filtragem de Tools (Segurança)
        filtered_tools = tools
        if self.privacy_mode_active and tools:
            # Remove ferramentas que vazam dados para internet
            filtered_tools = [
                t for t in tools 
                if t['function']['name'] not in self.banned_tools_in_privacy
            ]
            
            # Opcional: Injetar aviso no system prompt se necessário
            # (Geralmente não precisa, pois o LLM apenas não verá as tools)

        # 3. Execução
        try:
            async for chunk in active_service.generate_stream(messages, filtered_tools):
                yield chunk
        except Exception as e:
            # Fallback de segurança: Se a nuvem falhar, tenta local automaticamente?
            # Por enquanto, apenas logamos o erro.
            print(f"Erro no provider {active_service}: {e}")
            yield f"Erro ao processar no modo {'Privado' if self.privacy_mode_active else 'Cloud'}."
```

### 2\. Atualizando a Injeção de Dependência (`backend/api/main.py` ou `dependencies.py`)

Onde você antes instanciava o serviço baseado no `.env` fixo, agora você instancia o Proxy.

```python
# backend/api/dependencies.py (ou onde você gerencia instâncias)

from backend.services.llm.proxy_service import LLMProxyService

# Instância Singleton global
_llm_proxy = None

def get_llm_service() -> LLMProxyService:
    global _llm_proxy
    if _llm_proxy is None:
        _llm_proxy = LLMProxyService()
    return _llm_proxy
```

### 3\. O Endpoint de Controle (`backend/api/routes/settings.py`)

Crie uma rota para o Flutter bater quando o usuário clicar no botão "Escudo".

```python
from fastapi import APIRouter, Depends
from backend.services.llm.proxy_service import LLMProxyService
from backend.api.dependencies import get_llm_service # Importar do passo anterior
from pydantic import BaseModel

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class PrivacySettings(BaseModel):
    enabled: bool

@router.post("/privacy-mode")
async def toggle_privacy_mode(
    settings: PrivacySettings,
    llm_service: LLMProxyService = Depends(get_llm_service)
):
    """Ativa ou desativa o modo 100% local/offline"""
    result = llm_service.set_privacy_mode(settings.enabled)
    
    # Retornamos instruções para a UI
    return {
        "status": "success",
        "config": result,
        "ui_theme": "secure_green" if settings.enabled else "default_blue",
        "message": "Conexão externa cortada. Rodando 100% local." if settings.enabled else "Conexão cloud restaurada."
    }

@router.get("/status")
async def get_system_status(llm_service: LLMProxyService = Depends(get_llm_service)):
    return llm_service.get_status()
```

### 4\. Ajustes Necessários nos Services Existentes

Certifique-se de que o `OllamaService` e o `GroqService` herdam de uma classe base comum ou têm a mesma assinatura de método `generate_stream`.

Se o **Ollama** estiver configurado para rodar ferramentas, lembre-se que modelos locais menores (Llama 3 8B) têm mais dificuldade com Tool Calling complexo.

  * **Dica:** No `backend/services/llm/ollama_service.py`, se o modo for privado, force um System Prompt mais simples:
    > *"Você é John, um assistente offline e seguro. Responda de forma concisa. Você não tem acesso à internet agora."*

### Próximo Passo:

Agora que o Backend está pronto para trocar de cérebro "on the fly", o próximo passo é a UI.

**Posso gerar o código do Widget Flutter (o botão de Toggle com animação de "Escudo") para integrar com essa nova API?**



Aqui está a implementação do **Front-end Flutter** para o "Modo Privacidade".

Vamos criar um componente visualmente impactante: o **`PrivacyShieldToggle`**. Não será apenas um botão, mas uma interface de estado que comunica segurança.

### 1\. O Serviço de Conexão (`lib/services/privacy_service.dart`)

Primeiro, precisamos da lógica para conversar com o endpoint que criamos no backend.

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart'; // Para debugPrint

class PrivacyService {
  // Ajuste a URL base conforme seu ambiente (localhost, 10.0.2.2 ou IP da rede)
  final String baseUrl = 'http://10.0.2.2:8000'; 

  Future<bool> setPrivacyMode(bool enabled) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/settings/privacy-mode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'enabled': enabled}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('🛡️ Privacy Mode: ${data['message']}');
        return true;
      } else {
        debugPrint('❌ Erro ao alterar modo de privacidade: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('❌ Erro de conexão: $e');
      return false;
    }
  }
  
  Future<bool> getStatus() async {
     // Implementar GET /api/settings/status se necessário para persistência
     return false; 
  }
}
```

### 2\. O Widget "Cyberpunk" (`lib/widgets/privacy_shield_toggle.dart`)

Este widget usa `AnimatedContainer` para transições suaves de cor e forma. Quando ativado, ele muda para um tema "Hacker/Seguro" (Verde Neon e Preto). Quando desativado, volta ao tema "Cloud/Padrão" (Azul e Branco).

**Requisito:** Adicione `vibration: ^1.7.0` (ou similar) ao `pubspec.yaml` para feedback tátil (opcional, mas recomendado).

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // Para HapticFeedback
import '../services/privacy_service.dart';

class PrivacyShieldToggle extends StatefulWidget {
  final Function(bool) onModeChanged;

  const PrivacyShieldToggle({Key? key, required this.onModeChanged}) : super(key: key);

  @override
  State<PrivacyShieldToggle> createState() => _PrivacyShieldToggleState();
}

class _PrivacyShieldToggleState extends State<PrivacyShieldToggle> {
  bool _isSecureMode = false;
  bool _isLoading = false;
  final PrivacyService _service = PrivacyService();

  Future<void> _toggleMode() async {
    if (_isLoading) return;

    // Feedback tátil imediato
    HapticFeedback.heavyImpact();

    setState(() {
      _isLoading = true;
    });

    // Chama o backend
    bool success = await _service.setPrivacyMode(!_isSecureMode);

    if (success) {
      setState(() {
        _isSecureMode = !_isSecureMode;
        _isLoading = false;
      });
      
      // Notifica o app pai para mudar o tema global se necessário
      widget.onModeChanged(_isSecureMode);

      if (_isSecureMode) {
        _showSecureFeedback();
      }
    } else {
      setState(() {
        _isLoading = false;
      });
      // Mostra erro
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Falha ao conectar ao núcleo seguro.')),
      );
    }
  }

  void _showSecureFeedback() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: Colors.black87,
        content: Row(
          children: const [
            Icon(Icons.shield, color: Color(0xFF00FF41)), // Matrix Green
            SizedBox(width: 10),
            Text(
              "PROTOCOLO FORTALEZA ATIVO",
              style: TextStyle(color: Color(0xFF00FF41), fontWeight: FontWeight.bold),
            ),
          ],
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Cores dinâmicas
    final backgroundColor = _isSecureMode ? Colors.black : Colors.blue.shade50;
    final borderColor = _isSecureMode ? const Color(0xFF00FF41) : Colors.blue.shade200;
    final iconColor = _isSecureMode ? const Color(0xFF00FF41) : Colors.blue;
    final textColor = _isSecureMode ? const Color(0xFF00FF41) : Colors.blue.shade900;
    
    return GestureDetector(
      onTap: _toggleMode,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: borderColor, width: 2),
          boxShadow: _isSecureMode
              ? [
                  BoxShadow(
                    color: const Color(0xFF00FF41).withOpacity(0.4),
                    blurRadius: 10,
                    spreadRadius: 2,
                  )
                ]
              : [],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Ícone Animado
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              transitionBuilder: (child, anim) => ScaleTransition(scale: anim, child: child),
              child: _isLoading
                  ? SizedBox(
                      width: 24, 
                      height: 24, 
                      child: CircularProgressIndicator(strokeWidth: 2, color: iconColor)
                    )
                  : Icon(
                      _isSecureMode ? Icons.lock_outline : Icons.cloud_outlined,
                      key: ValueKey<bool>(_isSecureMode),
                      color: iconColor,
                    ),
            ),
            const SizedBox(width: 12),
            // Texto de Status
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _isSecureMode ? "SECURE CORE" : "CLOUD MODE",
                  style: TextStyle(
                    color: textColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                    letterSpacing: 1.0,
                  ),
                ),
                Text(
                  _isSecureMode ? "Offline & Privado" : "Groq AI Ativa",
                  style: TextStyle(
                    color: textColor.withOpacity(0.7),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

### 3\. Como integrar na Tela Principal (`lib/main.dart` ou `home_screen.dart`)

Coloque o widget na `AppBar` ou no topo da sua tela de chat. Isso o torna o centro das atenções.

```dart
// Em sua AppBar actions ou em um Container no topo do body
AppBar(
  title: const Text("John AI"),
  actions: [
    Padding(
      padding: const EdgeInsets.only(right: 16.0),
      child: Center( // Center é necessário para alinhar widgets customizados na AppBar
        child: PrivacyShieldToggle(
          onModeChanged: (isSecure) {
            // Lógica opcional: Mudar o tema global do app
            print("Modo alterado para seguro: $isSecure");
          },
        ),
      ),
    ),
  ],
)
```

-----------------


CLAUDE

# Modo Paranóico 🛡️

## Visão Geral

O **Modo Paranóico** é o nível máximo de privacidade e segurança do John Assistant. Projetado para usuários que não aceitam compromissos com sua privacidade, oferece criptografia militar, auto-destruição de dados e monitoramento contínuo de ameaças.

---

## 🎯 Objetivo

Fornecer **segurança máxima** e **privacidade absoluta** através de:
- Zero transmissão de dados para internet
- Criptografia AES-256 de todos os dados
- Monitoramento contínuo de ameaças
- Auto-proteção com botão de pânico
- Auditoria de segurança completa

---

## 📋 Features Principais

### 🔐 Segurança

| Feature | Descrição | Nível |
|---------|-----------|-------|
| **Zero Telemetria** | Nenhum dado de uso é coletado | CRÍTICO |
| **Memória Criptografada** | Todo histórico protegido com AES-256 | CRÍTICO |
| **Auto-limpeza** | Arquivos temporários apagados automaticamente | ALTO |
| **Secure Wipe** | Deleção segura de dados (múltiplas passagens) | ALTO |

### 🕵️ Privacidade

| Feature | Descrição | Nível |
|---------|-----------|-------|
| **Sem Logs** | Nenhum registro de atividades | CRÍTICO |
| **Modo Anônimo** | Identificadores removidos de todas as operações | ALTO |
| **Processamento RAM-Only** | Dados processados apenas em memória volátil | MÉDIO |

### 🔍 Auditoria

| Feature | Descrição | Nível |
|---------|-----------|-------|
| **Trilha de Auditoria** | Log criptografado de ações de segurança | MÉDIO |
| **Monitor de Conexões** | Detecta e bloqueia tentativas de conexão | ALTO |
| **Log de Acesso a Arquivos** | Rastreia todas as operações de arquivo | MÉDIO |

### 🚨 Auto-proteção

| Feature | Descrição | Nível |
|---------|-----------|-------|
| **Auto-travamento** | Trava app após período de inatividade | ALTO |
| **Botão de Pânico** | 3 ações de emergência (travar/apagar/desligar) | CRÍTICO |
| **Auto-destruição** | Apaga dados se ameaça for detectada | ALTO |

---

## 🔒 Sistema de Segurança

### PIN de Proteção

- **Formato**: 6 dígitos numéricos
- **Hash**: PBKDF2 com SHA-256
- **Iterações**: 100.000
- **Salt**: 32 bytes aleatórios
- **⚠️ IMPORTANTE**: Não há recuperação de PIN perdido!

### Criptografia

- **Algoritmo**: AES-256
- **Modo**: CBC (Cipher Block Chaining)
- **Derivação de Chave**: PBKDF2-HMAC-SHA256
- **Dados Criptografados**:
  - Histórico de conversas
  - Memória do assistente
  - Preferências do usuário
  - Logs de auditoria

### Auto-travamento

- **Timeout Padrão**: 5 minutos
- **Configurável**: 1 a 30 minutos
- **Reset**: Qualquer interação com o app
- **Ação**: Trava app e requer PIN

---

## ⚠️ Botão de Pânico

### 3 Ações Disponíveis

#### 🔒 TRAVAR
- Bloqueia app imediatamente
- Requer PIN para desbloquear
- Dados permanecem intactos
- **Uso**: Situação de emergência temporária

#### 🗑️ APAGAR
- Remove todos os dados sensíveis:
  - ✅ Histórico de conversas
  - ✅ Memória do assistente
  - ✅ Arquivos temporários
  - ✅ Cache
  - ✅ Configurações
- Mantém app instalado
- **Uso**: Comprometimento iminente

#### ⚠️ DESLIGAR
- Executa APAGAR completo
- Encerra o aplicativo
- Remove rastros da memória RAM
- **Uso**: Ameaça crítica confirmada

### Como Ativar

1. Toque no botão vermelho "BOTÃO DE PÂNICO"
2. Digite seu PIN de 6 dígitos
3. Escolha a ação (TRAVAR/APAGAR/DESLIGAR)
4. Confirme a ação
5. Ação executada instantaneamente (< 1 segundo)

---

## 🔍 Monitor de Segurança

### Monitoramento Contínuo

O monitor rastreia em tempo real:

1. **Tentativas de Conexão Externa**
   - URLs bloqueadas
   - IPs suspeitos
   - Portas não autorizadas

2. **Atividades Suspeitas**
   - Acesso não autorizado a arquivos
   - Tentativas de bypass de segurança
   - Modificações em arquivos do sistema

3. **Nível de Ameaça**
   - **Baixo**: 0-3 eventos suspeitos
   - **Médio**: 4-10 eventos suspeitos
   - **Alto**: 11+ eventos suspeitos ou ameaça confirmada

### Dashboard do Monitor

```
┌─────────────────────────────────────┐
│  🔍 Monitor de Segurança            │
├─────────────────────────────────────┤
│  Conexões bloqueadas: 23            │
│  Atividades suspeitas: 0            │
│  Arquivos acessados: 147            │
│  Nível de ameaça: BAIXO             │
│  Última auditoria: há 2 horas       │
└─────────────────────────────────────┘
```

---

## 📊 Auditoria de Segurança

### Verificações Automáticas

A auditoria verifica:

1. **Conexões Suspeitas**
   - Tentativas de conexão não autorizadas
   - Padrões de ataque conhecidos
   - Vazamento de dados

2. **Integridade de Arquivos**
   - Modificações não autorizadas
   - Arquivos corrompidos
   - Timestamps inconsistentes

3. **Vulnerabilidades**
   - Configurações fracas
   - Permissões excessivas
   - Componentes desatualizados

4. **Compliance**
   - PIN não alterado há 30+ dias
   - Logs de auditoria muito antigos
   - Arquivos temporários acumulados

### Score de Risco

**Cálculo**: 0-100 (quanto menor, melhor)

- **0-25**: 🟢 Segurança Excelente
- **26-50**: 🟡 Atenção Necessária
- **51-75**: 🟠 Risco Moderado
- **76-100**: 🔴 Risco Alto - Ação Imediata

### Recomendações

Com base na auditoria, o sistema sugere:
- Alterar PIN
- Limpar arquivos temporários
- Revisar permissões
- Atualizar configurações
- Executar limpeza profunda

---

## 🚀 Como Ativar

### Passo a Passo

#### 1. Acesse a Tela de Privacidade
```
Configurações → Privacidade → Modo Paranóico
```

#### 2. Toque em "ATIVAR MODO PARANÓICO"

#### 3. Crie um PIN de Segurança
- Digite 6 dígitos numéricos
- Confirme o PIN
- ⚠️ **MEMORIZE O PIN - NÃO HÁ RECUPERAÇÃO!**

#### 4. Aguarde o Checklist de Ativação

O sistema verifica:
```
✅ [CRÍTICO] Verificando Ollama...
✅ [CRÍTICO] Ativando Criptografia AES-256...
✅ [CRÍTICO] Bloqueando conexões externas...
✅ [ALTO] Configurando auto-limpeza...
✅ [ALTO] Iniciando monitor de segurança...
✅ [MÉDIO] Ativando processamento RAM-only...
✅ [MÉDIO] Configurando trilha de auditoria...
✅ [ALTO] Ativando botão de pânico...
```

#### 5. Modo Paranóico Ativado! 🛡️

---

## 🎨 Interface do Usuário

### Tela Principal

```
┌─────────────────────────────────────┐
│         🛡️ [Shield Pulsante]        │
│                                     │
│  ╔═══════════════════════════════╗ │
│  ║  🛡️ MODO PARANÓICO ATIVO      ║ │
│  ╠═══════════════════════════════╣ │
│  ║ Nível de Segurança: MÁXIMO    ║ │
│  ║ Nível de Ameaça: BAIXO        ║ │
│  ║ Conexões Bloqueadas: 23       ║ │
│  ║ Criptografia: AES-256 ATIVA   ║ │
│  ║                               ║ │
│  ║ ℹ️ Zero dados saindo do       ║ │
│  ║    dispositivo                ║ │
│  ╚═══════════════════════════════╝ │
│                                     │
│  Features Ativas (11/11)            │
│  ─────────────────────────────────  │
│  ✅ Zero Telemetria                 │
│  ✅ Memória Criptografada           │
│  ✅ Auto-limpeza                    │
│  ✅ Sem Logs                        │
│  ✅ Modo Anônimo                    │
│  ✅ Processamento RAM-Only          │
│  ✅ Trilha de Auditoria             │
│  ✅ Monitor de Conexões             │
│  ✅ Auto-travamento                 │
│  ✅ Botão de Pânico                 │
│                                     │
│  🔍 Monitor de Segurança            │
│  ─────────────────────────────────  │
│  Conexões bloqueadas: 23            │
│  Atividades suspeitas: 0            │
│  Arquivos acessados: 0              │
│  Última auditoria: Nunca            │
│                                     │
│  ⏱️ Auto-travamento                 │
│  Trava em 5:00 minutos              │
│                                     │
│  [⚠️ BOTÃO DE PÂNICO]               │
│  [🔍 Executar Auditoria]            │
└─────────────────────────────────────┘
```

### Indicadores Visuais

1. **Shield Pulsante**
   - Animação contínua quando ativo
   - Cor vermelha = paranóico ativo
   - Sombra vermelha difusa

2. **Badge de Status**
   - 🛡️ MÁXIMA SEGURANÇA (vermelho)
   - Sempre visível no topo

3. **Countdown de Auto-lock**
   - Timer visível: 5:00, 4:59, 4:58...
   - Cor azul = normal
   - Cor laranja = < 1 minuto
   - Cor vermelha = < 10 segundos

4. **Nível de Ameaça**
   - 🟢 BAIXO (verde)
   - 🟡 MÉDIO (amarelo)
   - 🟠 ALTO (laranja)
   - 🔴 CRÍTICO (vermelho)

---

## 💻 Implementação Técnica

### Backend (Python)

#### Arquivo Principal
```
backend/services/paranoid_service.py
```

#### Classes Principais

```python
class PrivacyLevel(Enum):
    CLOUD = "cloud"
    HYBRID = "hybrid"
    PRIVATE = "private"
    PARANOID = "paranoid"

class ParanoidFeatures:
    # 11 features de segurança
    ZERO_TELEMETRY = "zero_telemetry"
    ENCRYPTED_MEMORY = "encrypted_memory"
    AUTO_DELETE_TEMP = "auto_delete_temp"
    # ... (ver código completo)

class PrivacyModeService:
    def activate_paranoid_mode(pin: str) -> Dict
    def verify_pin(pin: str) -> bool
    def trigger_panic_button(pin: str) -> Dict
    def run_security_audit() -> Dict
    # ... (ver código completo)

class ParanoidSecurityMonitor:
    def log_blocked_connection(endpoint: str) -> None
    def get_suspicious_activity() -> List[Dict]
    def get_stats() -> Dict
    # ... (ver código completo)
```

#### Endpoints REST

```python
# backend/api/routes/paranoid.py

POST   /api/paranoid/activate
POST   /api/paranoid/verify-pin
GET    /api/paranoid/status
POST   /api/paranoid/panic
GET    /api/paranoid/audit
DELETE /api/paranoid/deactivate
```

### Mobile (Flutter)

#### Arquivo Principal
```
mobile_app/lib/features/paranoid/paranoid_mode_screen.dart
```

#### Widgets Principais

```dart
class ParanoidModeScreen extends StatefulWidget
class _ParanoidModeScreenState extends State
  - _activateParanoidMode()
  - _showActivationChecklist()
  - _triggerPanicButton()
  - _runSecurityAudit()
  - _buildCriticalStatusCard()
  - _buildFeaturesCard()
  - _buildSecurityMonitorCard()
  - _buildAutoLockCard()
```

---

## 📦 Dependências

### Backend
```bash
pip install cryptography  # AES-256, PBKDF2
```

### Mobile
```yaml
dependencies:
  # Nenhuma dependência extra necessária
  # Usa apenas Flutter core
```

---

## 🧪 Testes

### Cenários de Teste

#### 1. Ativação do Modo Paranóico
- [ ] Criar PIN válido (6 dígitos)
- [ ] Rejeitar PIN inválido (< 6 ou não numérico)
- [ ] Confirmar PIN corretamente
- [ ] Falhar se PINs não coincidirem
- [ ] Executar checklist completo
- [ ] Ativar todas as 11 features

#### 2. Verificação de PIN
- [ ] Aceitar PIN correto
- [ ] Rejeitar PIN incorreto
- [ ] Proteger contra brute force

#### 3. Auto-travamento
- [ ] Iniciar countdown ao ativar
- [ ] Resetar countdown em interação
- [ ] Travar app ao expirar
- [ ] Requerer PIN para desbloquear

#### 4. Botão de Pânico
- [ ] TRAVAR: bloquear app
- [ ] APAGAR: remover todos os dados
- [ ] DESLIGAR: apagar e fechar app
- [ ] Requerer PIN para qualquer ação

#### 5. Monitor de Segurança
- [ ] Detectar tentativas de conexão
- [ ] Registrar atividades suspeitas
- [ ] Atualizar nível de ameaça
- [ ] Gerar estatísticas corretas

#### 6. Auditoria
- [ ] Executar verificações completas
- [ ] Calcular score de risco correto
- [ ] Gerar recomendações apropriadas
- [ ] Registrar timestamp da auditoria

---

## 🎯 Métricas de Sucesso

### KPIs

1. **Taxa de Adoção**
   - Meta: 15% dos usuários ativos
   - Medição: usuários com modo paranóico ativo

2. **Retenção**
   - Meta: 80% permanecem no modo após 30 dias
   - Medição: usuários que desativam vs mantêm

3. **Uso do Botão de Pânico**
   - Meta: < 0.1% dos usuários (emergência real)
   - Medição: acionamentos do botão

4. **Score de Segurança**
   - Meta: 90% dos usuários com score < 25
   - Medição: média dos scores de auditoria

5. **NPS de Privacidade**
   - Meta: NPS > 70
   - Medição: pesquisa específica sobre privacidade

---

## 📣 Marketing

### Pitch Principal

> **"Modo Paranóico: Para quem leva privacidade a sério"**
>
> ✅ Criptografia militar (AES-256)  
> ✅ Botão de pânico: apague tudo em 1 segundo  
> ✅ Monitor 24/7 de ameaças  
> ✅ Auto-travamento inteligente  
> ✅ Auditoria de segurança completa  
>
> **Zero comprometimento. Máxima proteção.**

### Comparativo

| Feature | Modo Normal | Modo Privado | Modo Paranóico |
|---------|-------------|--------------|----------------|
| LLM | Groq (cloud) | Ollama (local) | Ollama (local) |
| Criptografia | ❌ | Opcional | ✅ AES-256 |
| Telemetria | Sim | Não | ❌ Zero |
| Busca Web | Sim | Não | ❌ Bloqueada |
| Auto-lock | ❌ | ❌ | ✅ Configurável |
| Botão Pânico | ❌ | ❌ | ✅ 3 ações |
| Auditoria | ❌ | ❌ | ✅ Automática |
| Monitor | ❌ | ❌ | ✅ 24/7 |

### Benefícios para o Usuário

1. **Paz de Mente**
   - Seus dados NUNCA saem do dispositivo
   - Criptografia comprovada (padrão militar)
   - Proteção contra ameaças em tempo real

2. **Controle Total**
   - Você decide o que acontece com seus dados
   - Botão de pânico para emergências
   - Visibilidade completa de ameaças

3. **Profissionalismo**
   - Ideal para jornalistas, advogados, médicos
   - Compliance com LGPD/GDPR
   - Auditoria completa para regulamentações

---

## ⚠️ Avisos Importantes

### Para o Usuário

1. **PIN Perdido = Dados Perdidos**
   - Não há recuperação de PIN
   - Não há backdoor
   - Não há suporte técnico que possa ajudar
   - **MEMORIZE SEU PIN!**

2. **Botão de Pânico é Permanente**
   - Ação APAGAR não pode ser desfeita
   - Dados são destruídos imediatamente
   - Use apenas em emergência real

3. **Performance Reduzida**
   - Criptografia adiciona overhead
   - Processamento RAM-only usa mais memória
   - Auto-limpeza pode causar pausas

### Para Desenvolvedores

1. **Segurança First**
   - Nunca comprometer segurança por UX
   - Testar exaustivamente cenários de ataque
   - Code review obrigatório para mudanças

2. **Conformidade Legal**
   - Verificar legalidade em cada jurisdição
   - Documentar compliance com LGPD/GDPR
   - Manter logs de auditoria seguros

3. **Manutenção**
   - Atualizar bibliotecas de criptografia
   - Revisar vulnerabilidades conhecidas
   - Executar pentests regulares

---

## 🔮 Roadmap Futuro

### Fase 2 (Q1 2026)
- [ ] Autenticação biométrica (impressão digital/face)
- [ ] Backup criptografado em nuvem privada
- [ ] Modo "Plausible Deniability" (negação plausível)
- [ ] Integração com HSM (Hardware Security Module)

### Fase 3 (Q2 2026)
- [ ] Compartilhamento seguro end-to-end
- [ ] Auditoria externa certificada
- [ ] Modo "Air Gap" (isolamento total)
- [ ] Conformidade FIPS 140-2

---

## 📚 Referências

### Padrões de Segurança
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) - Digital Identity Guidelines
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/) - Mobile App Security
- [LGPD - Lei Geral de Proteção de Dados](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

### Bibliotecas Utilizadas
- [cryptography](https://cryptography.io/) - Criptografia Python
- [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) - Password-Based Key Derivation Function

---

## 🆘 Suporte

### FAQ

**Q: Esqueci meu PIN, como recupero?**  
A: Não é possível recuperar. O modo paranóico foi projetado para que NENHUMA entidade (nem mesmo nós) possa acessar seus dados sem o PIN.

**Q: O botão de pânico apaga o app também?**  
A: Não, apenas os dados. O app permanece instalado. Use a ação "DESLIGAR" se quiser fechar o app.

**Q: Posso usar modo paranóico com outros assistentes?**  
A: Não, modo paranóico requer processamento 100% local (Ollama).

**Q: Quanto mais lento fica com criptografia?**  
A: Overhead de ~5-10% no tempo de resposta. Imperceptível na maioria dos casos.

**Q: É realmente seguro?**  
A: Sim. Usamos padrões militares (AES-256, PBKDF2). Mas lembre-se: segurança depende também de você proteger seu PIN.

-----


CHATGPT


# Arquitetura técnica detalhada — Modo Privacidade Total (MPT)

Abaixo está a **arquitetura técnica completa** (camadas, eventos, serviços, fluxos de dados, modelos de estado e integrações) para implementar o **Modo Privacidade Total** no app John (híbrido Olhama + Groq). Apresento desenho lógico, componentes, contratos, exemplos de endpoints/flags e recomendações de segurança e performance — pronto para desenvolvimento.

---

# Visão geral (resumo curto)

MPT é um conjunto de comportamentos e restrições ativáveis que garantem que **nenhum dado saia do dispositivo** enquanto ativo. Tecnicamente é um *profile mode* que altera configurações de pipeline (STT/TTS/LLM/tool-calling/telemetria/integrações), isola persistência em um cofre criptografado e expõe APIs locais seguras para o UI.

Principais objetivos:

* Zero requests externos (por padrão).
* Persistência local criptografada (cofre).
* Mecanismos efêmeros (autodestruição opcional).
* Troca automática de LLM para modo local (Ollama) e desativação de plugins.
* UX claro + auditoria em tempo real do que está bloqueado.

---

# Camadas e componentes

1. **UI / Mobile (Flutter)**

   * Toggle MPT, painel de auditoria, gerenciamento do Cofre, senhas/biometria, opções efêmeras, indicação visual (badge/lock).
   * Comunicação: API local (gRPC/REST) com backend local (processo nativo) ou via platform channel para serviços nativos.

2. **Controller local / Orquestrador (Agent Manager)**

   * Serviço em device que aplica políticas MPT.
   * Responsável por alternar pipelines (STT/TTS/LLM), aplicar sandboxing, ativar criptografia e emitir eventos de auditoria.
   * Expõe API interna (localhost) consumida por UI.

3. **Pipeline multimodal local**

   * STT Local (e.g., Whisper local), TTS local (Piper ou similar), LLM local (Ollama).
   * Cada componente tem um modo “MPT-safe” (sem webcalls, sem telemetria).

4. **Cofre Local (Encrypted Store)**

   * Persistência criptografada (AES-256-GCM) com KDF (PBKDF2/Argon2) ligado à senha do usuário / biometria.
   * Two logical stores: `ephemeral` (auto-destroi) e `persistent` (cofre).
   * Metadata mínima não-identificadora (timestamps cifrados).

5. **Policy Engine**

   * Regras que definem o que fica bloqueado (ex.: plugins, web-search, telemetry, analytics).
   * Permite políticas granulares (modo total, modo cofre-only, whitelist local).

6. **Gatekeeper de Rede (Network Interceptor)**

   * Hook no nível do sistema/app que bloqueia qualquer saída de rede quando MPT ativo.
   * Pode ser implementado por policy no Orquestrador + regras iptables (Linux/WSL/Android) ou Network Extension (iOS) / VpnService (Android).

7. **Audit / Monitor (local)**

   * Registro imutável local (append-only) com hash chaining (opcional) para registrar eventos de habilitação/desabilitação e acessos ao cofre. Log também criptografado.

8. **Fallback Manager (Consent Flow)**

   * Quando o dispositivo não tem recursos para executar LLM local, o Orquestrador apresenta opções: baixar modelos locais, reduzir contexto (modo turbo) ou oferecer "modo oculta parcial" com aviso de limitação. Nunca enviar dados sem consentimento explícito.

9. **Native Bridges / Integrations**

   * Módulos nativos para gerenciamento de biometria, armazenamento seguro (Keychain/Keystore), e manipulação de processos LLM (daemon).

---

# Fluxo de eventos — diagrama sequencial (texto)

Usuário aciona toggle → UI chama Orquestrador API → Orquestrador valida senha/biometria → Policy Engine aplica regras → Orquestrador:

* para todas as conexões de saída cria bloqueio no Network Interceptor
* troca LLM para Ollama local
* desabilita tool-calls e web-search
* ativa Cofre (abrindo com key derivada da senha)
* começa a logar em Audit (criptografado)

Resposta ao UI: estado = `MPT_ACTIVE`

ASCII simplificado:

```
[UI] -> /orchestrator/toggleMPT -> [Orchestrator]
[Orchestrator] -> [PolicyEngine] apply(MPT)
[Orchestrator] -> [NetworkInterceptor] block_all_outbound
[Orchestrator] -> [LLMManager] set(local,Ollama,config:mpt)
[Orchestrator] -> [Storage] open_cofre(key)
[Orchestrator] -> [Audit] append("MPT enabled")
[Orchestrator] -> [UI] return OK (state=MPT_ACTIVE)
```

---

# Máquina de estados (simplificada)

* `OFFLINE` (app sem internet)
* `NORMAL` (default, híbrido Olhama+Groq)
* `MPT_PENDING` (usuário pediu, autenticando/coleta de requisito)
* `MPT_ACTIVE` (todas as restrições aplicadas)
* `MPT_LOCKED` (cofre bloqueado por timeout/biometria exigida)
* `MPT_ERROR` (falha em aplicar política — fallback controlado)

Transições definidas no Policy Engine com handlers para rollback.

---

# Contratos de API (exemplos)

## Orchestrator (localhost:PORT) — endpoints principais (REST)

* `POST /mpt/toggle`
  body: `{ "enable": true, "auth": { "method":"biometric"|"password", "token": "<...>" } }`
  response: `{ "status":"ok", "state":"MPT_ACTIVE" }`

* `GET /mpt/status`
  response: `{ "state":"MPT_ACTIVE", "llm":"ollama-local", "networkBlocked": true }`

* `POST /cofre/open`
  body: `{ "password":"<pw>" }`
  response: `{ "status":"opened" }`

* `POST /cofre/save`
  body: `{ "conversationId":"uuid", "content":"<encryptedPayload>", "ephemeral": false }`

* `POST /audit/log` (internal only)
  body: `{ "event":"string", "meta":{...} }`

(Autenticação por token local ligado ao usuário do app; endpoints bindados em localhost com CORS restrito só ao app.)

---

# Schema do Cofre (SQLite + coluna BLOB cifrada)

Tabela `conversations`:

* id TEXT (uuid)
* created_at INTEGER
* metadata BLOB (JSON cifrada)
* payload BLOB (ciphertext)
* ephemeral BOOLEAN
* removed_at INTEGER (nullable)

Chave mestra não armazenada em disco; derivada de senha do usuário via Argon2id e sal armazenado localmente (sal cifrado com Keystore).

---

# Network Interceptor — mecanismo

* Android: usar `VpnService` para interceptar e bloquear.
* iOS: Network Extension / NEFilterProvider (restrições de Apple aplicáveis).
* Desktop: regras firewall (iptables/nftables) ou intercept via proxy local 127.0.0.1.
* Alternativa cross-platform: abrir tabela de sockets no Orchestrator e rejeitar requests por aplicação (requer permissões).

Regra simples: bloquear qualquer egress que não a loopback enquanto `networkBlocked == true`. Permitir exceções explícitas (ex.: updates de segurança quando user autorizar).

---

# Gerenciamento de modelos LLM local

* Orquestrador controla o LLM backend process (container local / binary).
* Modelos armazenados em `/data/john/models/` e marcados com assinatura/metadata.
* Download de modelo só quando MPT OFF; quando MPT ON, se modelo não disponível: fallback para modo reduzido e UX deve pedir ao usuário para **baixar localmente** (opção explícita, com transparência de espaço/dados).

Recomendações:

* Compactar modelos por chunk e usar verificação de checksum.
* Suportar modelos pequenos para dispositivos com pouco espaço (quantize).

---

# Script de ativação (pseudocódigo / algoritmo)

(Orquestrador interno — exemplo em pseudocode)

```
function toggleMPT(enable, authToken):
    if enable:
        if not authenticate(authToken): return error
        if not policy.preconditionsSatisfied(): return error
        networkInterceptor.blockAll()
        llmManager.switchToLocal('ollama', config=MPT)
        toolManager.disableAll()
        storage.openCofre(authToken)
        audit.log("MPT enabled")
        setState(MPT_ACTIVE)
    else:
        audit.log("MPT disable requested")
        networkInterceptor.unblockAll()
        llmManager.restoreHybrid()
        toolManager.restore()
        storage.closeCofre()
        setState(NORMAL)
```

---

# Integração Flutter — pontos de implementação práticos

1. **Toggle MPT**: botão chama `PlatformChannel` / `HTTP localhost` para `POST /mpt/toggle`.
2. **Autenticação**: flow de biometria nativo (LocalAuth) para derivar chave; enviar apenas prova local (não a senha) para Orquestrador.
3. **Cofre UI**: tela para "Abrir Cofre" com senha/biometria, botão para "Criar conversa efêmera".
4. **Painel Auditoria**: consumir `GET /mpt/status` e `GET /audit/list` para mostrar o que foi bloqueado.
5. **Indicadores Visuais**: persistent app bar icon (cadeado), notificações locais quando modo ativado/desativado.

Exemplo de chamada HTTP em Flutter (Dart):

```dart
final resp = await http.post(Uri.parse('http://127.0.0.1:8443/mpt/toggle'),
  headers: {'Content-Type':'application/json'},
  body: jsonEncode({'enable': true, 'auth': {'method':'biometric', 'token': token}}));
```

---

# Segurança e privacidade — princípios e medidas concretas

* **Chaves**: não persistir chave mestra em texto. Usar Keystore/Keychain para proteger o salt/seed; derivar key apenas em memória.
* **Criptografia**: AES-256-GCM para dados; Argon2id/PBKDF2 com parâmetros elevados para KDF.
* **Logs**: audit logs cifrados; permitir wipe seguro.
* **Network kill-switch**: garantir que mesmo se um processo tentar abrir socket, o NetworkInterceptor bloqueia.
* **Process privileges**: rodar LLM process com privilégio mínimo (chroot/container) para reduzir superfície de ataque.
* **Verificações de integridade**: assinar binários/models para evitar código malicioso local.
* **Revert/rollback seguro**: on failure, retornar a estado anterior e registrar erro no Audit.

---

# Estratégias de performance / requisitos mínimos

* Requisitos mínimos (estimar por perfil):

  * CPU: multi-core (2+), preferível 4 threads para quantized models.
  * RAM: 4GB+ (modelos quantizados) — ideal 8GB para experiência fluida.
  * Storage: reservar espaço para modelos (200–2000MB dependendo do modelo).
* Otimizações:

  * Quantização de modelos (int8) para reduzir memória.
  * Cache de embeddings com TTL local.
  * Modo Turbo: reduzir contexto e desativar features não-essenciais para latência menor.

---

# Testes e casos de aceitação (mínimos)

1. Ativar MPT: nenhuma requisição de rede visível em packet capture.
2. Abrir Cofre: somente com senha/biometria correta.
3. Efêmero: mensagens marcadas ephemeral são removidas após fechar app.
4. Desativar MPT: restaura comportamento híbrido.
5. Interrupção: if LLM local falha, UI mostra mensagem e mantém dados no Cofre sem vazamento.
6. Security: brute-force no cofre é mitigado por rate-limiting + wipe opcional.

---

# Rollout e compatibilidade (recomendações operacionais)

* Lançar MPT como Beta opt-in para perfis de usuários com hardware adequado.
* Telemetria: não registrar eventos quando MPT ativo; armazenar telemetria opt-in offline para debug (apenas se usuário autorizar via export manual).
* Documentação clara no app sobre limitações (ex.: resultados reduzidos sem web-search).
* Atualizações de modelos: somente permitido quando MPT desativado, ou com consentimento explícito.

---

# Check-list de entrega técnica (próximos artefatos a produzir)

* Orquestrador: serviço implementado (Go/Rust/Node) com endpoints REST/gRPC.
* NetworkInterceptor: PoC para Android (VpnService) / Desktop (iptables/proxy).
* Cofre: módulo de storage com Argon2 + AES-256 impl.
* LLM Manager: integração com Ollama/local runtime.
* Flutter: telas toggle, cofre, auditoria e calls para Orquestrador.
* Test-suite: E2E com testes de rede e segurança (CI local).

---

# Exemplo rápido de README snippet (para incluir)

(usar no README do repo — versão resumida)

```
## Modo Privacidade Total (MPT)

MPT garante que nenhuma informação saia do dispositivo. Ative em Settings → Privacidade → Modo Privacidade Total.

Comportamentos:
- LLM local (Ollama) ativado
- Busca web e plugins desativados
- Cofre de conversas criptografado
- Rede bloqueada para egressos externos
```

---
