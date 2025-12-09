"""
Serviço de LLM usando Ollama (local)
"""
import time
from typing import List, Dict, Optional
from loguru import logger

try:
    import ollama
except ImportError:
    logger.warning("ollama não disponível")
    ollama = None

from backend.services.llm.base import BaseLLMService
from backend.services.llm.ollama_tool_caller import process_ollama_tool_calls
from backend.services.llm.ollama_model_checker import check_finetuned_model, is_ollama_ready
from backend.services.llm.streaming import stream_ollama_response


class OllamaLLMService(BaseLLMService):
    """Serviço de conversação usando Ollama (local)"""
    
    def __init__(
        self,
        model: str = "llama3:8b-instruct-q4_0",
        host: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 512,
        finetuned_model: Optional[str] = None
    ):
        """
        Inicializa o serviço Ollama
        
        Args:
            model: Nome do modelo Ollama (base)
            host: URL do servidor Ollama
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens na resposta
            finetuned_model: Nome do modelo fine-tunado (opcional, usa se disponível)
        """
        super().__init__(temperature, max_tokens)
        self.base_model = model
        self.finetuned_model = finetuned_model
        self.host = host
        
        # Verifica e seleciona modelo (fine-tunado ou base)
        self.model = check_finetuned_model(host, model, finetuned_model)
        
        logger.info(f"Inicializando Ollama LLM: model={self.model}, host={host}")
        
        # Configura cliente Ollama
        if ollama:
            self.client = ollama.Client(host=host)
        else:
            self.client = None
    
    def generate_response(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None,
        memorias_contexto: str = "",
        tools: Optional[List[Dict]] = None,
        tool_executor: Optional[callable] = None,
        system_prompt_override: Optional[str] = None
    ) -> tuple[str, int]:
        """
        Gera resposta usando Ollama com suporte a tool calling
        
        Args:
            prompt: Texto da pergunta do usuário
            contexto: Histórico da conversa (lista de mensagens)
            memorias_contexto: Memórias relevantes formatadas
            tools: Lista de ferramentas disponíveis (formato OpenAI)
            tool_executor: Função para executar tools (recebe nome e args, retorna resultado)
            system_prompt_override: System prompt customizado (opcional)
            
        Returns:
            Tupla (resposta, tokens_usados)
        """
        try:
            start_time = time.time()
            total_tokens = 0
            
            if ollama is None:
                raise RuntimeError("Ollama não está disponível")
            
            # Prepara mensagens
            mensagens = self._preparar_mensagens(prompt, contexto, memorias_contexto, system_prompt_override)
            
            logger.info(f"[Ollama] Gerando resposta para: '{prompt[:50]}...'")
            
            # Chama Ollama usando cliente configurado com host customizado
            if not self.client:
                raise RuntimeError("Cliente Ollama não está configurado")
            
            # Loop de tool calling (máximo 3 iterações para evitar loops infinitos)
            max_iterations = 3
            for iteration in range(max_iterations):
                # Prepara opções com tools se disponível
                options = {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
                
                # Ollama suporta tools via formato OpenAI
                response = self.client.chat(
                    model=self.model,
                    messages=mensagens,
                    tools=tools if tools and iteration == 0 else None,
                    options=options
                )
                
                message = response.get('message', {})
                tokens_usados = response.get('eval_count', 0)
                total_tokens += tokens_usados
                
                # Processa tool calls usando módulo dedicado
                continuar, resposta, _ = process_ollama_tool_calls(
                    message=message,
                    tool_executor=tool_executor,
                    mensagens=mensagens,
                    iteration=iteration,
                    max_iterations=max_iterations
                )
                
                if not continuar:
                    # Sem tool calls ou última iteração - retorna resposta
                    tempo_processamento = time.time() - start_time
                    logger.info(
                        f"[Ollama] Resposta gerada em {tempo_processamento:.2f}s "
                        f"({total_tokens} tokens, {iteration + 1} iterações): '{resposta[:50]}...'"
                    )
                    return resposta, total_tokens
                
                # Continua loop para gerar resposta final
                continue
            
            # Se chegou aqui, excedeu max_iterations
            logger.warning(f"⚠️ Máximo de iterações ({max_iterations}) atingido")
            return resposta, total_tokens
            
        except Exception as e:
            logger.error(f"[Ollama] Erro ao gerar resposta: {e}")
            raise
    
    def _preparar_mensagens(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None,
        memorias_contexto: str = "",
        system_prompt_override: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Prepara lista de mensagens para o Ollama"""
        mensagens = []
        
        # Adiciona system prompt com memórias (ou override se fornecido)
        system_prompt = system_prompt_override if system_prompt_override else self._get_system_prompt(memorias_contexto)
        mensagens.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Adiciona contexto se existir
        if contexto:
            mensagens.extend(contexto)
        
        # Adiciona pergunta atual
        mensagens.append({
            "role": "user",
            "content": prompt
        })
        
        return mensagens
    
    async def generate_response_stream(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None,
        memorias_contexto: str = "",
        tools: Optional[List[Dict]] = None,
        tool_executor: Optional[callable] = None,
        system_prompt_override: Optional[str] = None
    ):
        """
        Gera resposta em streaming usando Ollama
        
        Args:
            prompt: Texto da pergunta do usuário
            contexto: Histórico da conversa
            memorias_contexto: Memórias relevantes formatadas
            tools: Lista de ferramentas disponíveis (não suportado em streaming ainda)
            tool_executor: Função para executar tools (não suportado em streaming ainda)
            system_prompt_override: System prompt customizado
            
        Yields:
            Tokens de texto conforme são gerados
        """
        try:
            if ollama is None:
                raise RuntimeError("Ollama não está disponível")
            
            # Prepara mensagens
            mensagens = self._preparar_mensagens(prompt, contexto, memorias_contexto, system_prompt_override)
            
            logger.info(f"[Ollama] Streaming resposta para: '{prompt[:50]}...'")
            
            # Nota: Tool calling não é suportado em streaming ainda
            tools_for_stream = None  # Desabilita tools em streaming por enquanto
            
            # Stream de resposta
            async for token in stream_ollama_response(
                client=self.client,
                model=self.model,
                messages=mensagens,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=tools_for_stream
            ):
                yield token
                
        except Exception as e:
            logger.error(f"[Ollama] Erro no streaming: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Verifica se o serviço Ollama está pronto"""
        return is_ollama_ready(self.client, self.model)

