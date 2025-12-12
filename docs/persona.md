### Ajustes no App Jonh

Olá! Pelo que entendi do seu README e das suas instruções, você quer implementar dois ajustes principais no assistente Jonh: (1) manter um histórico de conversas salvas e (2) transformá-lo em um especialista em busca de vagas de emprego na web, com filtros personalizados, acesso inteligente a sites como Google e LinkedIn, organização profissional dos resultados e foco em vagas ativas (evitando encerradas). Vou detalhar como implementar isso de forma prática, baseada na arquitetura atual do Jonh (backend em Python/FastAPI, LLM com tool calling via Groq/Ollama, plugins modulares e mobile em Flutter).

Estou assumindo que você é o desenvolvedor (brunoadsba, pelo repo GitHub mencionado). Se precisar de código pronto para copiar/colar, avise. Vamos passo a passo.

#### 1. Manter um Histórico de Conversas Salvas
Pela arquitetura descrita no README, o Jonh já tem gerenciamento de contexto de conversação e persistência via SQLite (para histórico e memória). Isso é ótimo como base! O que falta é uma funcionalidade explícita para "salvar" conversas manualmente ou automaticamente, com visualização no app mobile (ex.: uma tela de histórico). Isso pode ser expandido sem grandes mudanças.

**Passos para Implementar:**

- **Backend (FastAPI/Python):**
  - No `backend/services/` (provavelmente em `memory_service.py` ou um novo `history_service.py`), adicione uma tabela no SQLite para histórico de conversas. Use SQLAlchemy para gerenciar.
    - Exemplo de schema: Tabela `conversations` com colunas `id`, `session_id`, `user_id` (opcional), `timestamp`, `messages` (JSON ou string serializada), `saved` (boolean para marcar como salva).
  - No endpoint `/api/process_audio` ou `/ws/listen` (WebSocket), adicione lógica para salvar automaticamente toda conversa ou sob comando (ex.: se o usuário diz "salve esta conversa").
  - Novo endpoint REST: `POST /api/save_conversation` para salvar manualmente (recebe `session_id` e marca como saved).
  - Endpoint para listar: `GET /api/conversations?saved=true` (retorna lista de conversas salvas, com filtros por data ou usuário).

  Exemplo de código snippet para o serviço (em `history_service.py`):
  ```python
  from sqlalchemy import Column, Integer, String, Boolean, DateTime
  from sqlalchemy.orm import sessionmaker
  from datetime import datetime
  import json

  # ... (importar base do seu config/settings.py)

  class Conversation(Base):
      __tablename__ = 'conversations'
      id = Column(Integer, primary_key=True)
      session_id = Column(String, unique=True)
      timestamp = Column(DateTime, default=datetime.utcnow)
      messages = Column(String)  # JSON string de lista de mensagens
      saved = Column(Boolean, default=False)

  def save_conversation(session_id: str, messages: list):
      session = Session()
      conv = session.query(Conversation).filter_by(session_id=session_id).first()
      if not conv:
          conv = Conversation(session_id=session_id, messages=json.dumps(messages), saved=True)
          session.add(conv)
      else:
          conv.saved = True
          conv.messages = json.dumps(messages)
      session.commit()
      session.close()

  def get_saved_conversations():
      session = Session()
      return session.query(Conversation).filter_by(saved=True).all()
  ```

- **Integração com LLM (Tool Calling):**
  - Adicione um plugin simples no `PluginManager` (Feature 022) para "salvar conversa". O LLM pode chamar isso quando detectar intenções como "salve isso".
  - Exemplo de prompt no LLM: Adicione ao system prompt algo como "Se o usuário pedir para salvar a conversa, use a tool 'save_conversation'."

- **Mobile App (Flutter):**
  - Na arquitetura feature-based, crie uma nova feature em `lib/features/history/` com `HistoryScreen.dart` (uma lista de cards com resumo de conversas salvas).
  - Use `http` ou WebSocket para chamar o endpoint `/api/conversations?saved=true`.
  - Adicione um botão no chat principal (ex.: ícone de "salvar") que envia `POST /api/save_conversation`.
  - Para visualização: Liste conversas com data, resumo (primeira mensagem) e opção para carregar o histórico completo.
  - Teste: Adicione testes em widget/integration para essa tela (você já tem 33 testes, isso cabe na Fase 4).

- **Considerações:**
  - Privacidade: As conversas são locais/offline, mas avise o usuário.
  - Performance: Limite o histórico a 50 conversas por usuário para evitar sobrecarga.
  - Tempo estimado: 2-4 horas, já que o SQLite está pronto.

Isso alinha com o roadmap (gerenciamento de contexto e memória já implementados).

#### 2. Tornar Jonh o Maior Especialista em Busca de Vagas de Emprego
Isso é ambicioso e encaixa perfeitamente no sistema de plugins modulares (Feature 022) e tool calling (Feature 021). O Jonh já tem busca web via DuckDuckGo/Tavily, que pode ser usada para acessar Google, LinkedIn, Indeed, etc. Para torná-lo "inteligente":
- Use filtros do usuário (ex.: "estágio, 100% remoto, tecnologia Python").
- Busque em múltiplos sites, priorizando vagas recentes (ex.: postadas nos últimos 7-30 dias).
- Evite vagas encerradas: Adicione filtros de data no query (ex.: "since:2025-12-01") e valide browsing páginas para checar status.
- Organize resultados: Use tabelas Markdown no response do LLM, com colunas como Título, Empresa, Localização, Link, Descrição resumida.
- Profissionalismo: O LLM (Groq) pode formatar respostas como "Aqui estão 5 vagas relevantes para estágio remoto em tecnologia: [tabela]".

**Passos para Implementar:**

- **Backend (Plugin Novo):**
  - No `PluginManager`, crie um novo plugin em `backend/services/plugins/job_search_plugin.py`.
  - Use a tool de busca web existente (DuckDuckGo/Tavily) para queries inteligentes.
  - Lógica: O LLM decide chamar o plugin quando detectar intenções de busca de emprego (ex.: prompt: "Se o usuário pedir vagas de emprego, use 'job_search' com filtros").
  - Filtros: Parseie inputs do usuário (ex.: estágio, remoto, tecnologia) e construa queries como:
    - "estágio remoto python site:linkedin.com since:2025-11-01" (para evitar antigas).
    - Ou multi-sites: Busque no Google com "estágio remoto python inurl:linkedin.com OR inurl:indeed.com".
  - Para inteligência: Após busca inicial, browse páginas (se a API permitir) para filtrar "vaga encerrada" ou "expired" no texto.
  - Cache: Use o cache TTL de 1 hora (já implementado) para buscas repetidas.
  - Integre com novos tools (calculadora para salários, conversão de moedas para vagas internacionais).

  Exemplo de código para o plugin:
  ```python
  from plugins.base import BasePlugin
  from services.web_search import search_web  # Assumindo que existe

  class JobSearchPlugin(BasePlugin):
      name = "job_search"
      description = "Busca vagas de emprego na web com filtros."

      def execute(self, filters: dict):  # filters = {'type': 'estágio', 'remote': True, 'tech': 'Python'}
          query = f"{filters.get('type', '')} { '100% remoto' if filters.get('remote') else ''} {filters.get('tech', '')} vagas emprego"
          query += " since:2025-12-01 -encerrada -expired site:linkedin.com OR site:indeed.com OR site:glassdoor.com"
          results = search_web(query, num_results=20)  # Usando DuckDuckGo/Tavily
          
          # Filtrar e organizar (ex.: remova resultados antigos ou com "vaga fechada")
          filtered = [r for r in results if 'encerrada' not in r['snippet'].lower() and 'expired' not in r['snippet'].lower()]
          
          # Formatar como tabela
          organized = []
          for r in filtered[:10]:  # Top 10
              organized.append({
                  'title': r['title'],
                  'company': extract_company(r['snippet']),  # Função custom para extrair
                  'location': 'Remoto' if 'remoto' in r['snippet'] else 'N/A',
                  'link': r['url'],
                  'description': r['snippet'][:200]
              })
          return organized  # LLM formata como tabela Markdown
  ```

  - Registre no PluginManager: No `main.py` ou init, adicione `plugin_manager.register(JobSearchPlugin())`.

- **Integração com LLM:**
  - No prompt do Groq/Ollama, adicione: "Você é especialista em vagas de emprego. Use 'job_search' para buscar, filtre por datas recentes e organize em tabela com links."
  - No modo offline (Ollama), desabilite se WEB_SEARCH_ENABLED=false, ou avise "Busca requer internet".

- **Mobile App (Flutter):**
  - Na feature de chat, adicione suporte para inputs de filtros (ex.: campos de texto ou voz: "Encontre estágio remoto em Python").
  - Mostre resultados em uma lista scrollable com cards: Título, Empresa, Link (clicável para abrir browser).
  - Use Markdown renderer (pacote como `flutter_markdown`) para tabelas.
  - Métricas: Track latência da busca (Feature 020).

- **Evitar Vagas Encerradas (Inteligência):**
  - Sempre adicione "since:YYYY-MM-DD" (use data atual -7 dias).
  - Para precisão, após busca, use browsing (se Tavily suportar) para checar a página da vaga e procurar por "aplicações encerradas".
  - Sites prioritários: LinkedIn (site:linkedin.com/jobs), Indeed (site:indeed.com), Google Jobs (intitle:"vagas" site:google.com).
  - Limite: 5-10 resultados por resposta para evitar overload.

- **Testes e Performance:**
  - Adicione testes automatizados (pytest para backend, Flutter tests para app).
  - Use o script de análise de performance para medir latência (<3s).
  - Teste manual: "Jonh, encontre vagas de estágio remoto em IA".

- **Considerações:**
  - Legal: Avise que resultados são da web, não garantidos. Não colete dados pessoais sem consentimento.
  - Expansão: Futuro, integre API oficial do LinkedIn (se disponível), ou adicione filtros como salário.
  - Tempo estimado: 4-8 horas para MVP, já que plugins são modulares.

Se precisar de mais detalhes, como PR no GitHub ou exemplos de queries/testes, é só pedir. Isso vai tornar o Jonh ainda mais poderoso! 🚀

--


# Implementação: John - Especialista em Vagas e Histórico de Conversas

## 1. Plano de Implementação

Este plano detalha as etapas para adicionar as funcionalidades de Histórico de Conversas e Especialista em Vagas de Emprego ao projeto, utilizando a stack Next.js/React e o banco de dados Supabase/PostgreSQL.

### Escopo do Projeto

| Módulo | Funcionalidade | Descrição |
| :--- | :--- | :--- |
| **Histórico de Conversas** | Persistência | Armazenamento seguro no Supabase/PostgreSQL, associado ao ID do usuário. |
| **Especialista em Vagas** | Busca Inteligente | Uso de LLM (Groq) com *tool calling* para buscar vagas na web (Google Jobs, LinkedIn), aplicando filtros e validando a atividade da vaga. |

### Tecnologias Envolvidas

| Componente | Tecnologia | Uso |
| :--- | :--- | :--- |
| **Frontend** | Next.js / React / TypeScript | Interface do usuário (UI/UX). |
| **Backend (API)** | Next.js API Routes | Endpoints para Histórico e Busca de Vagas. |
| **Banco de Dados** | Supabase / PostgreSQL | Persistência e modelagem de dados. |
| **Inteligência** | Groq (LLM) | Orquestração da busca inteligente e formatação do output. |
| **Web Search** | DuckDuckGo/Tavily (via LLM Tool) | Acesso à web para buscar informações de vagas. |

---

## 2. Modelagem de Dados (SQL - Supabase/PostgreSQL)

Crie a seguinte tabela no seu banco de dados (ex: no editor SQL do Supabase):

**Arquivo:** `conversations_table.sql`

```sql
-- Tabela para armazenar o histórico de conversas
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) NOT NULL, -- Associa ao usuário logado
    title TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    messages JSONB NOT NULL -- Array de objetos {role: 'user' | 'assistant', content: '...'}
);

-- Opcional: Crie um índice para buscas rápidas por usuário
CREATE INDEX idx_conversations_user_id ON conversations (user_id);
```

---

## 3. API de Histórico (Next.js API Route)

Implemente esta rota para gerenciar o salvamento e listagem das conversas.

**Arquivo:** `src/app/api/conversations/route.ts`

```typescript
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

// GET /api/conversations - Lista conversas do usuário
export async function GET() {
  const supabase = createRouteHandlerClient({ cookies });
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
  }

  const { data, error } = await supabase
    .from('conversations')
    .select('id, title, created_at')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Erro ao buscar conversas:', error);
    return NextResponse.json({ error: 'Erro interno do servidor' }, { status: 500 });
  }

  return NextResponse.json(data);
}

// POST /api/conversations - Salva uma nova conversa
export async function POST(request: Request) {
  const supabase = createRouteHandlerClient({ cookies });
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
  }

  const { title, messages } = await request.json();

  if (!title || !messages) {
    return NextResponse.json({ error: 'Título e mensagens são obrigatórios' }, { status: 400 });
  }

  const { data, error } = await supabase
    .from('conversations')
    .insert({ user_id: user.id, title, messages })
    .select()
    .single();

  if (error) {
    console.error('Erro ao salvar conversa:', error);
    return NextResponse.json({ error: 'Erro interno do servidor' }, { status: 500 });
  }

  return NextResponse.json(data, { status: 201 });
}
```

---

## 4. Lógica de Busca Inteligente de Vagas (Serviço)

Este serviço utiliza o Groq (LLM) para orquestrar a busca na web e formatar o resultado.

**Arquivo:** `src/lib/ia/job-search-expert.ts`

```typescript
import { Groq } from 'groq-sdk';

// Inicialize o Groq SDK (certifique-se de que GROQ_API_KEY está no seu .env)
const groq = new Groq();

// Definição da Tool para busca na web (exemplo)
const webSearchTool = {
  type: 'function',
  function: {
    name: 'perform_web_search',
    description: 'Busca informações atualizadas na web, como vagas de emprego no Google Jobs ou LinkedIn.',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'A query de busca otimizada para encontrar vagas de emprego. Ex: "vagas estágio 100% remoto tecnologia"',
        },
      },
      required: ['query'],
    },
  },
};

export async function searchJobs(filters: { cargo: string, modalidade: string, area: string }) {
  const userPrompt = `Eu sou um usuário procurando vagas de emprego. Os filtros são: Cargo: ${filters.cargo}, Modalidade: ${filters.modalidade}, Área: ${filters.area}.
  
  Você é o John, o maior especialista em busca de vagas. Sua tarefa é:
  1. Usar a ferramenta \`perform_web_search\` para encontrar as vagas mais relevantes e **recentes** nos principais sites (Google Jobs, LinkedIn).
  2. Analisar os resultados da busca.
  3. Retornar APENAS as vagas que parecem estar **ativas** e organizadas profissionalmente.
  
  Formato de saída profissional (Markdown):
  
  ## Vagas Encontradas para ${filters.cargo}
  
  ### [Título da Vaga] - [Empresa]
  - **Localização/Modalidade:** [Cidade/Remoto]
  - **Resumo:** [Breve descrição da vaga e requisitos chave]
  - **Link para Aplicação:** [URL Completa]
  
  ... (Repetir para outras vagas)
  
  **Nota:** Priorize links diretos e informações claras.
  `;

  // 1. Primeira chamada ao LLM para decidir se usa a tool
  let response = await groq.chat.completions.create({
    model: 'llama3-8b-8192', // Modelo rápido para orquestração
    messages: [{ role: 'user', content: userPrompt }],
    tools: [webSearchTool],
  });

  // 2. Se o LLM decidir usar a tool, execute a busca na web
  if (response.choices[0].finish_reason === 'tool_calls') {
    const toolCall = response.choices[0].tool_calls[0];
    const { query } = JSON.parse(toolCall.function.arguments);

    // **IMPORTANTE:** Aqui você deve integrar sua biblioteca de busca na web (DuckDuckGo/Tavily/etc.)
    // Exemplo de chamada de uma função de busca simulada:
    const searchResults = await performWebSearch(query); 

    // 3. Segunda chamada ao LLM com os resultados da busca
    response = await groq.chat.completions.create({
      model: 'llama3-8b-8192',
      messages: [
        { role: 'user', content: userPrompt },
        {
          role: 'tool',
          tool_call_id: toolCall.id,
          content: JSON.stringify(searchResults), // Passa os resultados da busca para o LLM
        },
      ],
    });
  }

  // Retorna o texto formatado pelo LLM
  return response.choices[0].message.content;
}

// **Função de busca na web simulada (substitua pela sua implementação real)**
async function performWebSearch(query: string): Promise<any> {
    // Implemente aqui a chamada real à sua API de busca na web (ex: Tavily, DuckDuckGo API)
    // A busca deve retornar snippets de texto ou URLs relevantes.
    console.log(`Realizando busca na web com a query: "${query}"`);
    
    // Retorno simulado para o LLM processar
    return [
        { title: "Vaga Desenvolvedor Frontend Pleno - Empresa X", snippet: "Vaga 100% remota, React/Next.js. Publicada há 2 dias no LinkedIn. Link: https://linkedin.com/vaga/123", url: "https://linkedin.com/vaga/123" },
        { title: "Estágio em TI - Empresa Y (Encerrada)", snippet: "Vaga presencial em São Paulo. Publicada há 3 meses. Status: Encerrada.", url: "https://empresa-y.com/vaga/encerrada" },
        { title: "Vaga Analista de Dados - Empresa Z", snippet: "Vaga híbrida, Python/SQL. Publicada hoje no Google Jobs. Link: https://google.com/vaga/456", url: "https://google.com/vaga/456" },
    ];
}
```

---

## 5. API Route para Busca de Vagas

Este endpoint recebe os filtros do usuário e chama o serviço de busca inteligente.

**Arquivo:** `src/app/api/vagas/search/route.ts`

```typescript
import { NextResponse } from 'next/server';
import { searchJobs } from '@/lib/ia/job-search-expert'; // Ajuste o caminho conforme sua estrutura

// POST /api/vagas/search - Endpoint para buscar vagas
export async function POST(request: Request) {
  try {
    const { cargo, modalidade, area } = await request.json();

    if (!cargo) {
      return NextResponse.json({ error: 'O campo "cargo" é obrigatório.' }, { status: 400 });
    }

    const filters = {
      cargo: cargo || '',
      modalidade: modalidade || 'qualquer',
      area: area || 'qualquer',
    };

    // Chama a lógica de busca inteligente
    const jobResultsMarkdown = await searchJobs(filters);

    // Retorna o resultado formatado em Markdown pelo LLM
    return new NextResponse(jobResultsMarkdown, {
      status: 200,
      headers: {
        'Content-Type': 'text/markdown; charset=utf-8',
      },
    });

  } catch (error) {
    console.error('Erro na busca de vagas:', error);
    return NextResponse.json({ error: 'Erro interno ao processar a busca de vagas.' }, { status: 500 });
  }
}
```
---



# Plano de Implementação: Geolocalização Móvel para o Assistente John

## 1. Introdução

Este documento detalha o plano de implementação para a funcionalidade de **Geolocalização Móvel** no assistente John. O objetivo é permitir que o aplicativo mobile acesse o GPS do dispositivo para fornecer informações de localização precisas, que serão utilizadas pelo assistente (LLM) para contextualizar respostas e fornecer informações mais relevantes (ex: "Qual o clima na minha cidade?", "Onde fica o posto de gasolina mais próximo?").

O plano foca na integração entre o **App Mobile (Flutter)** e o **Backend (Python/FastAPI)**.

## 2. Escopo da Funcionalidade

| Item | Descrição |
| :--- | :--- |
| **Coleta de Dados** | Obter a latitude e longitude precisas do dispositivo móvel. |
| **Permissões** | Gerenciar as permissões de localização no Android e iOS. |
| **Comunicação** | Enviar os dados de localização do App Mobile para o Backend. |
| **Contextualização** | O LLM deve receber a localização (ou o endereço reverso) como parte do contexto da conversa. |
| **Privacidade** | A localização só deve ser coletada e enviada com o consentimento explícito do usuário. |

## 3. Tecnologias Envolvidas

| Componente | Tecnologia | Uso |
| :--- | :--- | :--- |
| **App Mobile** | Flutter (Dart) | Solicitar permissões e obter a localização via GPS. |
| **Pacote Flutter** | `geolocator` | Facilita a obtenção da localização e gerenciamento de permissões. |
| **Backend** | Python / FastAPI | Receber a localização e, opcionalmente, realizar a geocodificação reversa. |
| **LLM** | Groq / Ollama | Utilizar a localização no contexto da conversa. |
| **Geocodificação** | API de Geocodificação Reversa (ex: OpenCage, Google Maps API) | Converter Lat/Long em endereço legível (cidade, estado). |

## 4. Plano de Implementação Detalhado

O desenvolvimento será dividido em 3 fases principais:

### Fase 1: Implementação no App Mobile (Flutter)

| Passo | Descrição | Duração Estimada |
| :--- | :--- | :--- |
| **1.1** | **Adicionar Dependência:** Incluir o pacote `geolocator` no `pubspec.yaml`. | 0.5 dia |
| **1.2** | **Configurar Permissões:** Adicionar as permissões necessárias (`ACCESS_FINE_LOCATION`, etc.) nos arquivos de manifesto do Android e Info.plist do iOS. | 1 dia |
| **1.3** | **Serviço de Localização:** Criar um `LocationService` no Flutter para verificar permissões e obter a `Position` (latitude, longitude). | 1 dia |
| **1.4** | **Integração com a Conversa:** Modificar a lógica de envio de mensagens para incluir a localização atual (se disponível e permitida) no payload enviado ao Backend. | 1 dia |

### Fase 2: Desenvolvimento do Backend (FastAPI)

| Passo | Descrição | Duração Estimada |
| :--- | :--- | :--- |
| **2.1** | **Atualizar Modelo de Dados:** Modificar o endpoint de processamento de áudio/texto para aceitar campos opcionais de `latitude` e `longitude`. | 0.5 dia |
| **2.2** | **Serviço de Geocodificação (Opcional):** Implementar um `GeocodingService` para converter Lat/Long em um endereço legível (cidade, estado). Isso evita que o LLM precise fazer a busca na web para isso. | 2 dias |
| **2.3** | **Integração com o LLM:** Atualizar o `LLMService` para injetar a informação de localização (ex: "Localização atual do usuário: [Cidade, Estado]") no prompt do sistema (System Prompt) antes de enviar a requisição ao Groq/Ollama. | 1 dia |

### Fase 3: Testes e Validação

| Passo | Descrição | Duração Estimada |
| :--- | :--- | :--- |
| **3.1** | **Testes de Unidade:** Testar o `LocationService` no Flutter (usando mocks) e o `GeocodingService` no Python. | 1 dia |
| **3.2** | **Testes de Integração:** Validar o fluxo completo: App -> Backend -> LLM. | 1 dia |
| **3.3** | **Testes em Dispositivo Real:** Testar a funcionalidade em dispositivos Android e iOS para garantir que as permissões e a precisão do GPS funcionem corretamente. | 1 dia |

## 5. Exemplo de Código (Flutter)

Exemplo de como obter a localização no Flutter usando o pacote `geolocator`:

```dart
import 'package:geolocator/geolocator.dart';

class LocationService {
  Future<Position?> getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    // Testar se os serviços de localização estão habilitados
    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      // Serviços de localização não estão habilitados.
      return null;
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        // Permissões negadas.
        return null;
      }
    }
    
    if (permission == LocationPermission.deniedForever) {
      // Permissões negadas permanentemente.
      return null;
    }

    // Quando as permissões são concedidas, retorna a posição atual
    return await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high
    );
  }
}

// Exemplo de uso antes de enviar a mensagem ao backend:
/*
final location = await LocationService().getCurrentLocation();
if (location != null) {
  final payload = {
    'text': 'Minha pergunta',
    'latitude': location.latitude,
    'longitude': location.longitude,
  };
  // Enviar payload para o endpoint do FastAPI
}
*/
```

## 6. Exemplo de Código (FastAPI - Atualização do Endpoint)

Atualização do endpoint principal para receber a localização.

**Arquivo:** `backend/api/routes/process.py` (ou similar)

```python
from fastapi import APIRouter, File, UploadFile, Form
from typing import Optional

router = APIRouter()

@router.post("/process_audio")
async def process_audio(
    audio: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    # 1. Processar áudio (STT)
    transcribed_text = await stt_service.transcribe(audio)
    
    # 2. Preparar contexto de localização
    location_context = ""
    if latitude is not None and longitude is not None:
        # **OPCIONAL:** Chamar GeocodingService aqui para obter cidade/estado
        # location_info = await geocoding_service.reverse_geocode(latitude, longitude)
        # location_context = f"Localização do usuário: {location_info}"
        location_context = f"Coordenadas do usuário: Lat {latitude}, Long {longitude}"
        
    # 3. Chamar LLM com contexto
    full_prompt = f"{location_context}. Pergunta do usuário: {transcribed_text}"
    llm_response = await llm_service.generate_response(full_prompt)
    
    # 4. Processar resposta (TTS)
    tts_audio = await tts_service.synthesize(llm_response)
    
    return {"response_text": llm_response, "audio": tts_audio}
```
---


# Adição de Funcionalidade de GPS ao App Jonh

## Visão Geral

Este documento descreve a implementação de integração com GPS no aplicativo mobile Jonh (desenvolvido em Flutter). O objetivo é permitir que o app acesse a localização do dispositivo (via GPS) para fornecer informações precisas baseadas na localidade do usuário, como clima local, vagas de emprego próximas, rotas, ou respostas contextuais (ex.: "Onde estou?" ou "Vagas de emprego na minha cidade").

Essa feature se integra à arquitetura existente:
- **Backend**: Pode processar dados de localização enviados pelo app (ex.: via WebSocket ou API REST) e usar tool calling para buscas web baseadas em coordenadas (ex.: via geocode em queries de busca).
- **Mobile App**: Adiciona permissões, serviço de localização e envio de dados para o backend.
- **Privacidade**: Sempre peça permissão explícita e avise o usuário sobre uso de dados de localização.

**Benefícios**:
- Respostas mais personalizadas (ex.: "Vagas de estágio remoto ou em São Paulo, baseado na sua localização").
- Integração com tool calling: Use localização em queries como "geocode:-23.5505,-46.6333" no X Keyword Search ou web_search.
- Modo offline: Cache de localização recente para uso sem internet (se LLM local).

**Requisitos**:
- Flutter 3.35+ (já usado).
- Adicionar pacote `geolocator` para GPS.
- Permissões para Android/iOS.

**Data de Criação**: 11 de Dezembro de 2025.

## Arquitetura da Feature

### Backend (Python/FastAPI)
- Adicione suporte para receber coordenadas (latitude/longitude) em endpoints existentes.
- No LLM (Groq/Ollama), use localização em prompts ou tools (ex.: web_search com "vagas emprego near:lat,long").
- Novo plugin: `LocationPlugin` para geolocalização reversa (cidade a partir de coords) ou integração com APIs como OpenWeather para clima.

### Mobile App (Flutter)
- Nova feature: `lib/features/location/`.
- Serviço: `LocationService` para gerenciar GPS.
- Integração: Envie localização ao backend via WebSocket ou novo endpoint REST.

## Requisitos Adicionais

### Dependências
- Adicione ao `pubspec.yaml`:
  ```yaml
  dependencies:
    geolocator: ^12.0.0  # Versão atual em 2025; verifique pub.dev para updates
    permission_handler: ^11.3.1  # Para gerenciar permissões
  ```

### Permissões
- **Android**: Adicione ao `android/app/src/main/AndroidManifest.xml`:
  ```xml
  <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
  <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
  <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />  <!-- Opcional para background -->
  ```
- **iOS**: Adicione ao `ios/Runner/Info.plist`:
  ```xml
  <key>NSLocationWhenInUseUsageDescription</key>
  <string>Jonh precisa da sua localização para fornecer informações precisas.</string>
  <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
  <string>Jonh precisa da sua localização em background para notificações.</string>
  ```

## Instalação e Configuração

1. **Atualize Dependências**:
   ```bash
   cd mobile_app
   flutter pub get
   ```

2. **Configure Env**:
   - Em `lib/config/env.dart`, adicione flags como `ENABLE_LOCATION=true`.

3. **Teste Permissões**:
   - Rode `flutter doctor` para verificar Android/iOS setup.

## Implementação Detalhada

### 1. Backend
- **Novo Endpoint REST**: `POST /api/submit_location` para receber coords e processar.
  - Exemplo em `backend/api/routes/process.py`:
    ```python
    from fastapi import APIRouter, Body
    from pydantic import BaseModel

    router = APIRouter()

    class LocationData(BaseModel):
        latitude: float
        longitude: float
        session_id: str

    @router.post("/submit_location")
    async def submit_location(data: LocationData = Body(...)):
        # Armazene em sessão ou use em LLM
        # Ex: session_manager.update_session(data.session_id, {"location": (data.latitude, data.longitude)})
        return {"status": "received"}
    ```
- **Integração com LLM/Tool Calling**:
  - No `llm_service.py`, adicione ao context: "User location: lat,long" se disponível.
  - No `JobSearchPlugin` (do doc anterior), adicione filtro: `query += f" near:{lat},{long}"` para vagas locais.
  - Para clima ou info local: Novo tool calling com web_search (ex.: "clima em [cidade]").

- **Plugin de Localização**:
  - Em `backend/services/plugins/location_plugin.py`:
    ```python
    from plugins.base import BasePlugin
    import requests  # Para geocode reverso, se necessário

    class LocationPlugin(BasePlugin):
        name = "get_location_info"
        description = "Obtém info baseada em localização."

        def execute(self, lat: float, long: float):
            # Ex: Geocode reverso via API gratuita (ex.: Nominatim, mas respeite limites)
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={long}&format=json"
            response = requests.get(url).json()
            city = response.get('address', {}).get('city', 'Desconhecida')
            return {"city": city, "country": response.get('address', {}).get('country')}
    ```
  - Registre no PluginManager.

### 2. Mobile App (Flutter)
- **Nova Feature**: Crie `lib/features/location/`.
  - `location_service.dart`:
    ```dart
    import 'package:geolocator/geolocator.dart';
    import 'package:permission_handler/permission_handler.dart';

    class LocationService {
      Future<Position?> getCurrentLocation() async {
        // Checa e pede permissão
        var status = await Permission.location.request();
        if (status.isDenied) {
          return null;  // Ou handle erro
        }

        bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
        if (!serviceEnabled) {
          return null;  // Peça para ativar GPS
        }

        return await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
        );
      }

      // Envie para backend
      Future<void> sendLocationToBackend(double lat, double long, String sessionId) async {
        // Use http ou WebSocket service existente
        // Ex: http.post('/api/submit_location', body: {'latitude': lat, 'longitude': long, 'session_id': sessionId});
      }
    }
    ```
  - Integre no chat: No `ChatController` ou ao iniciar sessão, chame `getCurrentLocation()` se ENABLE_LOCATION.
  - UI: Adicione switch em configurações para ativar/desativar GPS.
  - Background: Para updates em background, use `Geolocator.getPositionStream()` com notificação persistente (já implementada).

- **Integração com Wake Word/Chat**:
  - Ao detectar comandos como "vagas na minha localização", chame LocationService e envie coords ao backend via StreamingService ou WebSocket.
  - Exemplo em `voice_feature`: Após STT, se contiver "localização", ative GPS.

### 3. Testes
- **Backend**: Adicione pytest para `/api/submit_location`.
- **Mobile**: Adicione testes de integração para LocationService (ex.: mock Geolocator).
  - Rode: `flutter test`.
- **E2E**: Use emulador com GPS mockado.

## Uso Exemplo
- Usuário diz: "Encontre vagas de emprego na minha cidade."
- App: Pega GPS → Envia ao backend → LLM usa tool calling com filtro de localização → Retorna vagas organizadas.

## Troubleshooting
- **Permissões Negadas**: Mostre dialog explicando necessidade.
- **GPS Desativado**: Prompt para ativar nas settings do device.
- **Precisão Baixa**: Use `LocationAccuracy.high` e fallback para coarse.
- **Privacidade**: Adicione política no app: "Dados de localização usados apenas para respostas e não armazenados permanentemente."

## Roadmap para Essa Feature
- [ ] Implementar geofencing para notificações (ex.: "Nova vaga perto de você").
- [ ] Integração com mapas (adicionar `google_maps_flutter`).
- [ ] Suporte iOS completo (testar em device real).

Essa adição mantém o app híbrido local/cloud e melhora a usabilidade. Se precisar de mais código ou ajustes, avise!

---

**Jonh Assistant** - Agora com suporte a localização precisa para experiências personalizadas.
