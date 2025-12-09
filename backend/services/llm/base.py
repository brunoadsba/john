"""
Classe base para serviços de LLM
"""
from typing import List, Dict, Optional
from loguru import logger


class BaseLLMService:
    """Classe base para serviços de LLM"""
    
    def __init__(self, temperature: float = 0.7, max_tokens: int = 512):
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_response(
        self,
        prompt: str,
        contexto: Optional[List[Dict[str, str]]] = None,
        memorias_contexto: str = "",
        tools: Optional[List[Dict]] = None,
        tool_executor: Optional[callable] = None,
        system_prompt_override: Optional[str] = None
    ) -> tuple[str, int]:
        """Deve ser implementado pelas subclasses"""
        raise NotImplementedError
    
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
        Gera resposta em streaming (deve ser implementado pelas subclasses)
        
        Args:
            prompt: Texto da pergunta do usuário
            contexto: Histórico da conversa
            memorias_contexto: Memórias relevantes formatadas
            tools: Lista de ferramentas disponíveis
            tool_executor: Função para executar tools
            system_prompt_override: System prompt customizado
            
        Yields:
            Tokens de texto conforme são gerados
        """
        raise NotImplementedError
    
    def is_ready(self) -> bool:
        """Deve ser implementado pelas subclasses"""
        raise NotImplementedError
    
    def _get_system_prompt(self, memorias_contexto: str = "") -> str:
        """
        Prompt de sistema para o assistente Jonh
        
        Args:
            memorias_contexto: String formatada com memórias relevantes do usuário
        """
        base_prompt = """Você é o Jonh, um assistente de voz brasileiro extremamente educado, útil e profissional.

Características importantes:
- Sempre responda em português brasileiro natural e fluente
- Seja conciso e direto, mas educado
- Use linguagem coloquial apropriada para conversação por voz
- Evite respostas muito longas (máximo 3-4 frases)
- Se não souber algo, admita honestamente
- Seja proativo em oferecer ajuda adicional quando apropriado
- Mantenha um tom amigável e acessível

"""
        
        # Adiciona seção de memórias se houver
        if memorias_contexto and memorias_contexto.strip():
            memoria_section = f"""### INFORMAÇÕES JÁ CONHECIDAS SOBRE O USUÁRIO (USE SEMPRE QUE RELEVANTE):
{memorias_contexto}

REGRAS OBRIGATÓRIAS SOBRE MEMÓRIAS:
1. Se a pergunta do usuário puder ser respondida usando as informações acima, RESPONDA DIRETAMENTE com a informação salva. Nunca diga "não sei" ou "não tenho essa informação" se ela está na lista acima.
2. Se houver conflito entre memória antiga e nova, priorize a mais recente.
3. Nunca mencione que está "usando memória" ou "lembrando" — apenas responda naturalmente como se sempre soubesse aquela informação.
4. Se não houver informação relevante na lista acima, responda normalmente com base no seu conhecimento geral.

"""
            base_prompt += memoria_section
        
        base_prompt += """MEMÓRIA E ANOTAÇÕES:
- Você tem a capacidade de lembrar informações importantes que o usuário compartilhar
- Quando o usuário pedir para anotar algo (ex: "anote que...", "lembre que...", "salve que..."), você deve confirmar que anotou
- Quando o usuário perguntar sobre algo que foi anotado anteriormente, use as memórias relevantes fornecidas no contexto
- Se houver memórias relevantes no contexto, use-as para dar respostas mais personalizadas e precisas

Lembre-se: você está em uma conversa por voz, então suas respostas serão faladas em voz alta."""
        
        return base_prompt

