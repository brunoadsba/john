"""
Serviço de LLM com suporte a Ollama e Groq
"""
import time
from typing import List, Dict, Optional
from loguru import logger

try:
    import ollama
except ImportError:
    logger.warning("ollama não disponível")
    ollama = None

try:
    from groq import Groq
except ImportError:
    logger.warning("groq não disponível")
    Groq = None


class BaseLLMService:
    """Classe base para serviços de LLM"""
    
    def __init__(self, temperature: float = 0.7, max_tokens: int = 512):
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_response(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, int]:
        """Deve ser implementado pelas subclasses"""
        raise NotImplementedError
    
    def is_ready(self) -> bool:
        """Deve ser implementado pelas subclasses"""
        raise NotImplementedError
    
    def _get_system_prompt(self) -> str:
        """Prompt de sistema para o assistente Jonh"""
        return """Você é o Jonh, um assistente de voz brasileiro extremamente educado, útil e profissional.

Características importantes:
- Sempre responda em português brasileiro natural e fluente
- Seja conciso e direto, mas educado
- Use linguagem coloquial apropriada para conversação por voz
- Evite respostas muito longas (máximo 3-4 frases)
- Se não souber algo, admita honestamente
- Seja proativo em oferecer ajuda adicional quando apropriado
- Mantenha um tom amigável e acessível

Lembre-se: você está em uma conversa por voz, então suas respostas serão faladas em voz alta."""


class OllamaLLMService(BaseLLMService):
    """Serviço de conversação usando Ollama (local)"""
    
    def __init__(
        self,
        model: str = "llama3:8b-instruct-q4_0",
        host: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Inicializa o serviço Ollama
        
        Args:
            model: Nome do modelo Ollama
            host: URL do servidor Ollama
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens na resposta
        """
        super().__init__(temperature, max_tokens)
        self.model = model
        self.host = host
        
        logger.info(f"Inicializando Ollama LLM: model={model}, host={host}")
        
        # Configura cliente Ollama
        if ollama:
            ollama.Client(host=host)
    
    def generate_response(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, int]:
        """
        Gera resposta usando Ollama
        
        Args:
            prompt: Texto da pergunta do usuário
            contexto: Histórico da conversa (lista de mensagens)
            
        Returns:
            Tupla (resposta, tokens_usados)
        """
        try:
            start_time = time.time()
            
            if ollama is None:
                raise RuntimeError("Ollama não está disponível")
            
            # Prepara mensagens
            mensagens = self._preparar_mensagens(prompt, contexto)
            
            logger.info(f"[Ollama] Gerando resposta para: '{prompt[:50]}...'")
            
            # Chama Ollama
            response = ollama.chat(
                model=self.model,
                messages=mensagens,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            
            resposta = response['message']['content']
            tokens_usados = response.get('eval_count', 0)
            
            tempo_processamento = time.time() - start_time
            logger.info(
                f"[Ollama] Resposta gerada em {tempo_processamento:.2f}s "
                f"({tokens_usados} tokens): '{resposta[:50]}...'"
            )
            
            return resposta, tokens_usados
            
        except Exception as e:
            logger.error(f"[Ollama] Erro ao gerar resposta: {e}")
            raise
    
    def _preparar_mensagens(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Prepara lista de mensagens para o Ollama"""
        mensagens = []
        
        # Adiciona system prompt
        mensagens.append({
            "role": "system",
            "content": self._get_system_prompt()
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
    
    def is_ready(self) -> bool:
        """Verifica se o serviço Ollama está pronto"""
        try:
            if ollama is None:
                return False
            
            # Tenta listar modelos para verificar conexão
            models = ollama.list()
            
            # Verifica se o modelo está disponível
            model_names = [m['name'] for m in models.get('models', [])]
            model_available = any(self.model in name for name in model_names)
            
            if not model_available:
                logger.warning(
                    f"[Ollama] Modelo {self.model} não encontrado. "
                    f"Modelos disponíveis: {model_names}"
                )
            
            return model_available
            
        except Exception as e:
            logger.error(f"[Ollama] Serviço não está pronto: {e}")
            return False


class GroqLLMService(BaseLLMService):
    """Serviço de conversação usando Groq (cloud)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
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
        contexto: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, int]:
        """
        Gera resposta usando Groq
        
        Args:
            prompt: Texto da pergunta do usuário
            contexto: Histórico da conversa (lista de mensagens)
            
        Returns:
            Tupla (resposta, tokens_usados)
        """
        try:
            start_time = time.time()
            
            # Prepara mensagens
            mensagens = self._preparar_mensagens(prompt, contexto)
            
            logger.info(f"[Groq] Gerando resposta para: '{prompt[:50]}...'")
            
            # Chama Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=mensagens,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            resposta = response.choices[0].message.content
            tokens_usados = response.usage.total_tokens
            
            tempo_processamento = time.time() - start_time
            logger.info(
                f"[Groq] Resposta gerada em {tempo_processamento:.2f}s "
                f"({tokens_usados} tokens): '{resposta[:50]}...'"
            )
            
            return resposta, tokens_usados
            
        except Exception as e:
            logger.error(f"[Groq] Erro ao gerar resposta: {e}")
            raise
    
    def _preparar_mensagens(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Prepara lista de mensagens para o Groq"""
        mensagens = []
        
        # Adiciona system prompt
        mensagens.append({
            "role": "system",
            "content": self._get_system_prompt()
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


def create_llm_service(
    provider: str,
    **kwargs
) -> BaseLLMService:
    """
    Factory para criar serviço de LLM apropriado
    
    Args:
        provider: "ollama" ou "groq"
        **kwargs: Argumentos específicos do provider
        
    Returns:
        Instância do serviço de LLM
    """
    if provider.lower() == "ollama":
        return OllamaLLMService(**kwargs)
    elif provider.lower() == "groq":
        return GroqLLMService(**kwargs)
    else:
        raise ValueError(f"Provider desconhecido: {provider}. Use 'ollama' ou 'groq'")
