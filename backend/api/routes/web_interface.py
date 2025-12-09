"""
Interface Web para Testar Funcionalidades do Jonh Assistant
Permite testar sem precisar do app mobile
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from loguru import logger

router = APIRouter(prefix="/web", tags=["web_interface"])

# Instâncias dos serviços (serão inicializadas)
stt_service = None
llm_service = None
tts_service = None
context_manager = None
memory_service = None


def init_services(stt, llm, tts, ctx, memory=None):
    """Inicializa os serviços"""
    global stt_service, llm_service, tts_service, context_manager, memory_service
    stt_service = stt
    llm_service = llm
    tts_service = tts
    context_manager = ctx
    memory_service = memory


@router.get("/", response_class=HTMLResponse)
async def web_interface():
    """Interface web para testar funcionalidades"""
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jonh Assistant - Teste Web</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 30px; }
        .status {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .status-item {
            flex: 1;
            min-width: 150px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
            text-align: center;
        }
        .status-item.active { background: #4caf50; color: white; }
        .status-item.inactive { background: #f44336; color: white; }
        .status-item h3 { font-size: 0.9em; margin-bottom: 5px; }
        .status-item p { font-size: 0.8em; opacity: 0.8; }
        .input-section {
            margin-bottom: 30px;
        }
        .input-section label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #333;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn-secondary {
            background: #f5f5f5;
            color: #333;
        }
        .btn-secondary:hover { background: #e0e0e0; }
        .response-section {
            margin-top: 30px;
        }
        .response-box {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            min-height: 100px;
            border-left: 4px solid #667eea;
        }
        .response-box.loading {
            border-left-color: #ff9800;
        }
        .response-box.error {
            border-left-color: #f44336;
        }
        .response-box h3 {
            margin-bottom: 10px;
            color: #333;
        }
        .response-text {
            color: #666;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .audio-player {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
        }
        .audio-player audio {
            width: 100%;
        }
        .memories-section {
            margin-top: 30px;
            padding: 20px;
            background: #f0f4ff;
            border-radius: 10px;
        }
        .memories-section h3 {
            margin-bottom: 15px;
            color: #333;
        }
        .memory-item {
            padding: 10px;
            background: white;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        .log {
            margin-top: 20px;
            padding: 15px;
            background: #1e1e1e;
            color: #0f0;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        .log-entry {
            margin-bottom: 5px;
        }
        .log-entry.error { color: #f44; }
        .log-entry.success { color: #4f4; }
        .log-entry.info { color: #4af; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Jonh Assistant</h1>
            <p>Interface Web para Testes - Teste todas as funcionalidades sem precisar do app mobile</p>
        </div>
        <div class="content">
            <div class="status">
                <div class="status-item" id="status-backend">
                    <h3>Backend</h3>
                    <p>Verificando...</p>
                </div>
                <div class="status-item" id="status-llm">
                    <h3>LLM</h3>
                    <p>Verificando...</p>
                </div>
                <div class="status-item" id="status-tts">
                    <h3>TTS</h3>
                    <p>Verificando...</p>
                </div>
            </div>

            <div class="input-section">
                <label for="user-input">Digite sua mensagem ou comando:</label>
                <textarea id="user-input" placeholder="Ex: Olá, como você está?&#10;Ou: Anote que meu nome é Bruno&#10;Ou: Qual é a capital do Brasil?"></textarea>
            </div>

            <div class="buttons">
                <button class="btn-primary" onclick="sendMessage()">📤 Enviar Mensagem</button>
                <button class="btn-secondary" onclick="clearResponse()">🗑️ Limpar</button>
                <button class="btn-secondary" onclick="testMemory()">💾 Testar Memória</button>
            </div>

            <div class="response-section">
                <div class="response-box" id="response-box">
                    <h3>Resposta:</h3>
                    <div class="response-text" id="response-text">Aguardando sua mensagem...</div>
                    <div class="audio-player" id="audio-player" style="display: none;">
                        <audio id="audio-element" controls></audio>
                    </div>
                </div>
            </div>

            <div class="memories-section">
                <h3>💭 Memórias Relevantes Encontradas:</h3>
                <div id="memories-list">Nenhuma memória encontrada ainda.</div>
            </div>

            <div class="log">
                <div class="log-entry info">Sistema iniciado. Pronto para receber comandos.</div>
            </div>
        </div>
    </div>

    <script>
        let sessionId = null;
        const logDiv = document.querySelector('.log');

        function addLog(message, type = 'info') {
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        async function checkStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                document.getElementById('status-backend').className = 'status-item active';
                document.getElementById('status-backend').querySelector('p').textContent = 'Online';
                
                if (data.servicos.llm === 'online') {
                    document.getElementById('status-llm').className = 'status-item active';
                    document.getElementById('status-llm').querySelector('p').textContent = 'Online';
                }
                
                if (data.servicos.tts === 'online') {
                    document.getElementById('status-tts').className = 'status-item active';
                    document.getElementById('status-tts').querySelector('p').textContent = 'Online';
                }
                
                addLog('Status verificado: todos os serviços online', 'success');
            } catch (error) {
                document.getElementById('status-backend').className = 'status-item inactive';
                document.getElementById('status-backend').querySelector('p').textContent = 'Offline';
                addLog('Erro ao verificar status: ' + error.message, 'error');
            }
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            
            if (!text) {
                alert('Digite uma mensagem primeiro!');
                return;
            }

            const responseBox = document.getElementById('response-box');
            const responseText = document.getElementById('response-text');
            const audioPlayer = document.getElementById('audio-player');
            
            responseBox.className = 'response-box loading';
            responseText.textContent = 'Processando...';
            audioPlayer.style.display = 'none';
            addLog(`Enviando: "${text}"`, 'info');

            try {
                const formData = new FormData();
                formData.append('texto', text);
                if (sessionId) {
                    formData.append('session_id', sessionId);
                }

                const response = await fetch('/api/process_text', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                // Obter resposta do header
                const responseTextHeader = response.headers.get('X-Response-Text');
                const newSessionId = response.headers.get('X-Session-ID');
                const tokens = response.headers.get('X-Tokens-Used');
                const time = response.headers.get('X-Processing-Time');

                if (newSessionId) {
                    sessionId = newSessionId;
                }

                // Obter áudio
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Atualizar UI
                responseBox.className = 'response-box';
                responseText.textContent = responseTextHeader || 'Resposta recebida';
                
                if (audioBlob.size > 0) {
                    const audioElement = document.getElementById('audio-element');
                    audioElement.src = audioUrl;
                    audioPlayer.style.display = 'block';
                    addLog(`Áudio recebido: ${(audioBlob.size / 1024).toFixed(2)} KB`, 'success');
                }

                addLog(`Resposta recebida (${tokens} tokens, ${parseFloat(time).toFixed(2)}s)`, 'success');

                // Buscar memórias relevantes
                await updateMemories(text);

            } catch (error) {
                responseBox.className = 'response-box error';
                responseText.textContent = `Erro: ${error.message}`;
                addLog(`Erro: ${error.message}`, 'error');
            }
        }

        async function updateMemories(query) {
            try {
                // Simular busca de memórias (endpoint pode ser criado)
                const memoriesList = document.getElementById('memories-list');
                memoriesList.textContent = 'Buscando memórias relevantes...';
                
                // Por enquanto, apenas mostra que está buscando
                // Em produção, criar endpoint /api/memories/search?query=...
                setTimeout(() => {
                    memoriesList.textContent = 'Memórias serão exibidas aqui quando endpoint for criado.';
                }, 500);
            } catch (error) {
                addLog(`Erro ao buscar memórias: ${error.message}`, 'error');
            }
        }

        async function testMemory() {
            const testMessages = [
                'Anote que meu nome é Bruno',
                'Lembre que minha cor favorita é azul',
                'Salve que eu trabalho como desenvolvedor'
            ];
            
            for (const msg of testMessages) {
                document.getElementById('user-input').value = msg;
                await sendMessage();
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }

        function clearResponse() {
            document.getElementById('response-text').textContent = 'Aguardando sua mensagem...';
            document.getElementById('audio-player').style.display = 'none';
            document.getElementById('response-box').className = 'response-box';
            addLog('Resposta limpa', 'info');
        }

        // Verificar status ao carregar
        checkStatus();
        
        // Permitir Enter para enviar
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                sendMessage();
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@router.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {
        "status": "ok",
        "message": "Interface web funcionando",
        "endpoints": {
            "interface": "/web/",
            "process_text": "/api/process_text",
            "health": "/health"
        }
    }

