"""
Serviço de LLM usando Groq (cloud)
"""
import time
from typing import List, Dict, Optional
from loguru import logger

try:
    from groq import Groq
except ImportError:
    logger.warning("groq não disponível")
    Groq = None

from backend.services.llm.base import BaseLLMService
from backend.services.llm.groq_rate_limit import is_rate_limit_error, handle_rate_limit_error
from backend.services.llm.groq_fallback import try_ollama_fallback
from backend.services.llm.groq_tool_caller import process_tool_calls
from backend.services.llm.streaming import stream_groq_response


class GroqLLMService(BaseLLMService):
    """Serviço de conversação usando Groq (cloud)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",  # Padrão otimizado (usa settings na prática)
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Inicializa o serviço Groq
        
        Args:
            api_key: Chave de API do Groq
            model: Nome do modelo Groq
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens na resposta
        """
        super().__init__(temperature, max_tokens)
        self.model = model
        
        if not api_key:
            raise ValueError("API key do Groq é obrigatória")
        
        if Groq is None:
            raise RuntimeError("Biblioteca groq não está instalada")
        
        self.client = Groq(api_key=api_key)
        
        logger.info(f"Inicializando Groq LLM: model={model}")
    
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
        Gera resposta usando Groq com suporte a tool calling
        
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
            
            # Prepara mensagens
            mensagens = self._preparar_mensagens(prompt, contexto, memorias_contexto, system_prompt_override)
            
            logger.info(f"[Groq] Gerando resposta para: '{prompt[:50]}...'")
            
            # Loop de tool calling (máximo 3 iterações)
            max_iterations = 3
            for iteration in range(max_iterations):
                # Prepara parâmetros para Groq
                groq_params = {
                    "model": self.model,
                    "messages": mensagens,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
                
                # Adiciona tools apenas na primeira iteração
                if tools and iteration == 0:
                    groq_params["tools"] = tools
                    groq_params["tool_choice"] = "auto"
                # Não passa tool_choice quando não há tools (Groq pode rejeitar None)
                
                # Chama Groq
                try:
                    response = self.client.chat.completions.create(**groq_params)
                except Exception as e:
                    # Detecta e trata rate limit
                    if is_rate_limit_error(e):
                        fallback_result = handle_rate_limit_error(
                            error=e,
                            prompt=prompt,
                            contexto=contexto,
                            memorias_contexto=memorias_contexto,
                            tools=tools,
                            tool_executor=tool_executor,
                            system_prompt_override=system_prompt_override,
                            fallback_callback=lambda p, c, m, t, te, sp: self._try_ollama_fallback(
                                p, c, m, t, te, sp
                            )
                        )
                        if fallback_result:
                            return fallback_result
                    
                    # Detecta erro de validação de schema do Groq relacionado a features como string
                    error_str = str(e)
                    if "tool call validation failed" in error_str and "features" in error_str and "expected array" in error_str:
                        logger.warning(f"⚠️ Groq rejeitou tool call com features como string. Tentando corrigir schema...")
                    
                    raise
                
                message = response.choices[0].message
                tokens_usados = response.usage.total_tokens
                total_tokens += tokens_usados
                
                # Processa tool calls usando módulo dedicado
                continuar, resposta, _ = process_tool_calls(
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
                        f"[Groq] Resposta gerada em {tempo_processamento:.2f}s "
                        f"({total_tokens} tokens, {iteration + 1} iterações): '{resposta[:50]}...'"
                    )
                    return resposta, total_tokens
                
                # Continua loop para gerar resposta final
                continue
            
            # Se chegou aqui, excedeu max_iterations
            logger.warning(f"⚠️ Máximo de iterações ({max_iterations}) atingido")
            return resposta, total_tokens
            
        except RuntimeError:
            # Erro já tratado (rate limit com fallback)
            raise
        except Exception as e:
            # Detecta e trata rate limit no handler externo
            if is_rate_limit_error(e):
                fallback_result = handle_rate_limit_error(
                    error=e,
                    prompt=prompt,
                    contexto=contexto,
                    memorias_contexto=memorias_contexto,
                    tools=tools,
                    tool_executor=tool_executor,
                    system_prompt_override=system_prompt_override,
                    fallback_callback=lambda p, c, m, t, te, sp: self._try_ollama_fallback(
                        p, c, m, t, te, sp
                    )
                )
                if fallback_result:
                    return fallback_result
            
            logger.error(f"[Groq] Erro ao gerar resposta: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _try_ollama_fallback(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]],
        memorias_contexto: str,
        tools: Optional[List[Dict]],
        tool_executor: Optional[callable],
        system_prompt_override: Optional[str]
    ) -> Optional[tuple[str, int]]:
        """Tenta usar Ollama como fallback quando Groq atinge rate limit"""
        return try_ollama_fallback(
            prompt=prompt,
            contexto=contexto,
            memorias_contexto=memorias_contexto,
            tools=tools,
            tool_executor=tool_executor,
            system_prompt_override=system_prompt_override,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
    
    def _preparar_mensagens(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None,
        memorias_contexto: str = "",
        system_prompt_override: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Prepara lista de mensagens para o Groq"""
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
        Gera resposta em streaming usando Groq
        
        Args:
            prompt: Texto da pergunta do usuário
            contexto: Histórico da conversa
            memorias_contexto: Memórias relevantes formatadas
            tools: Lista de ferramentas disponíveis
            tool_executor: Função para executar tools (não suportado em streaming ainda)
            system_prompt_override: System prompt customizado
            
        Yields:
            Tokens de texto conforme são gerados
        """
        try:
            # Prepara mensagens
            mensagens = self._preparar_mensagens(prompt, contexto, memorias_contexto, system_prompt_override)
            
            logger.info(f"[Groq] Streaming resposta para: '{prompt[:50]}...'")
            
            # Nota: Tool calling não é suportado em streaming ainda
            # Para streaming com tools, seria necessário implementar lógica mais complexa
            tools_for_stream = None  # Desabilita tools em streaming por enquanto
            
            # Stream de resposta
            async for token in stream_groq_response(
                client=self.client,
                model=self.model,
                messages=mensagens,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=tools_for_stream
            ):
                yield token
                
        except Exception as e:
            logger.error(f"[Groq] Erro no streaming: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Verifica se o serviço Groq está pronto"""
        try:
            # Tenta fazer uma chamada simples para verificar
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
            
        except Exception as e:
            logger.error(f"[Groq] Serviço não está pronto: {e}")
            return False

