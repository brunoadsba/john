"""
Serviço de RLHF (Reinforcement Learning from Human Feedback)
Implementa PPO para fine-tuning baseado em preferências humanas
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from loguru import logger

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("trl/transformers não disponível - instale com: pip install trl transformers peft accelerate datasets")

from backend.services.ml.rlhf import (
    train_with_ppo_core,
    generate_candidates_core
)


class RLHFService:
    """Gerencia treinamento RLHF usando PPO"""
    
    def __init__(
        self,
        base_model: str = "meta-llama/Llama-3.1-8B-Instruct",
        reward_model_path: Optional[str] = None
    ):
        """
        Inicializa serviço RLHF
        
        Args:
            base_model: Modelo base para fine-tuning
            reward_model_path: Caminho para modelo de recompensa treinado
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("trl e transformers são necessários para RLHF")
        
        self.base_model = base_model
        self.reward_model_path = reward_model_path
        self.model = None
        self.tokenizer = None
        self.reward_model = None
        logger.info(f"RLHFService inicializado (base: {base_model})")
    
    def collect_preferences(
        self,
        instruction: str,
        response_a: str,
        response_b: str,
        preferred: str  # "a" ou "b"
    ) -> Dict[str, Any]:
        """
        Coleta preferência do usuário entre duas respostas
        
        Args:
            instruction: Pergunta/instrução do usuário
            response_a: Primeira resposta candidata
            response_b: Segunda resposta candidata
            preferred: Qual resposta foi preferida ("a" ou "b")
            
        Returns:
            Dicionário com preferência formatada
        """
        preference = {
            "instruction": instruction,
            "response_a": response_a,
            "response_b": response_b,
            "preferred": preferred,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug(f"Preferência coletada: {preferred} escolhida")
        return preference
    
    def generate_candidates(
        self,
        instruction: str,
        num_candidates: int = 4,
        temperature: float = 0.8,
        max_length: int = 256
    ) -> List[str]:
        """
        Gera múltiplas respostas candidatas para uma instrução
        
        Args:
            instruction: Pergunta/instrução do usuário
            num_candidates: Número de respostas a gerar
            temperature: Temperatura para geração (maior = mais diverso)
            max_length: Comprimento máximo da resposta
            
        Returns:
            Lista de respostas candidatas
        """
        if not self.model or not self.tokenizer:
            # Carrega modelo se não estiver carregado
            self._load_model()
        
        return generate_candidates_core(
            model=self.model,
            tokenizer=self.tokenizer,
            instruction=instruction,
            num_candidates=num_candidates,
            temperature=temperature,
            max_length=max_length
        )
    
    def select_best_response(
        self,
        instruction: str,
        candidates: List[str],
        reward_model_service: Any
    ) -> Tuple[str, float]:
        """
        Seleciona melhor resposta usando modelo de recompensa
        
        Args:
            instruction: Pergunta/instrução do usuário
            candidates: Lista de respostas candidatas
            reward_model_service: Serviço de modelo de recompensa
            
        Returns:
            Tupla (melhor_resposta, score)
        """
        if not candidates:
            return "", 0.0
        
        # Avalia todas as candidatas
        scored = reward_model_service.evaluate_responses(instruction, candidates)
        
        if not scored:
            return candidates[0], 0.0
        
        # Retorna a melhor (primeira da lista ordenada)
        best_response, best_score = scored[0]
        logger.info(f"✅ Melhor resposta selecionada (score: {best_score:.3f})")
        
        return best_response, best_score
    
    def train_with_ppo(
        self,
        training_data: List[Dict[str, Any]],
        reward_model_service: Any,
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 1e-5,
        use_lora: bool = True
    ) -> Dict[str, Any]:
        """
        Treina modelo usando PPO
        
        Args:
            training_data: Lista de exemplos com preferências
            reward_model_service: Serviço de modelo de recompensa
            output_dir: Diretório para salvar modelo treinado
            epochs: Número de épocas
            batch_size: Tamanho do batch
            learning_rate: Taxa de aprendizado
            use_lora: Usar LoRA para fine-tuning eficiente
            
        Returns:
            Métricas de treinamento
        """
        logger.info(f"Iniciando treinamento RLHF com {len(training_data)} exemplos")
        
        if not training_data:
            raise ValueError("Dataset de treinamento vazio")
        
        # Carrega modelo se necessário
        if not self.model or not self.tokenizer:
            self._load_model()
        
        # Treina usando módulo core
        metrics = train_with_ppo_core(
            model=self.model,
            tokenizer=self.tokenizer,
            reward_model=reward_model_service,
            training_data=training_data,
            output_dir=output_dir,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            use_lora=use_lora
        )
        
        return metrics
    
    def _load_model(self):
        """Carrega modelo e tokenizer"""
        if self.model and self.tokenizer:
            return
        
        try:
            logger.info(f"Carregando modelo base: {self.base_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype="auto",
                device_map="auto"
            )
            
            # Configura pad token se necessário
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("✅ Modelo e tokenizer carregados")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    def load_trained_model(self, model_path: str):
        """
        Carrega modelo treinado
        
        Args:
            model_path: Caminho para modelo treinado
        """
        try:
            logger.info(f"Carregando modelo treinado de: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype="auto",
                device_map="auto"
            )
            logger.info(f"✅ Modelo treinado carregado de: {model_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo treinado: {e}")
            raise
