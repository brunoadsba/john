"""
Serviço de Modelo de Recompensa para RLHF
Treina e utiliza modelo que avalia qualidade de respostas
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from loguru import logger

try:
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.debug("transformers não disponível - RLHF desabilitado (instale com: pip install transformers accelerate datasets torch se necessário)")

from backend.services.ml.reward_model import (
    train_reward_model_core,
    load_reward_model as load_reward_model_core
)


class RewardModelService:
    """Gerencia modelo de recompensa para RLHF"""
    
    def __init__(
        self,
        base_model: str = "distilbert-base-multilingual-cased",
        model_path: Optional[str] = None
    ):
        """
        Inicializa serviço de modelo de recompensa
        
        Args:
            base_model: Modelo base para classificação (HuggingFace)
            model_path: Caminho para modelo treinado (opcional)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers é necessário para modelo de recompensa")
        
        self.base_model = base_model
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        logger.info(f"RewardModelService inicializado (base: {base_model})")
    
    def _load_model(self):
        """Carrega modelo e tokenizer"""
        if self.is_loaded:
            return
        
        try:
            if self.model_path and Path(self.model_path).exists():
                logger.info(f"Carregando modelo de recompensa de: {self.model_path}")
                self.model, self.tokenizer = load_reward_model_core(self.model_path)
            else:
                logger.info(f"Carregando modelo base: {self.base_model}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.base_model,
                    num_labels=1
                )
            
            self.is_loaded = True
            logger.info("✅ Modelo de recompensa carregado")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    def train_reward_model(
        self,
        training_data: List[Dict[str, Any]],
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 2e-5,
        validation_split: float = 0.1
    ) -> Dict[str, Any]:
        """
        Treina modelo de recompensa
        
        Args:
            training_data: Lista de exemplos no formato:
                [
                    {
                        "instruction": "Pergunta do usuário",
                        "response": "Resposta do assistente",
                        "reward": 0.8  # Score de 0.0 a 1.0
                    },
                    ...
                ]
            output_dir: Diretório para salvar modelo treinado
            epochs: Número de épocas
            batch_size: Tamanho do batch
            learning_rate: Taxa de aprendizado
            validation_split: Proporção para validação
            
        Returns:
            Métricas de treinamento
        """
        logger.info(f"Iniciando treinamento do modelo de recompensa ({len(training_data)} exemplos)")
        
        if not training_data:
            raise ValueError("Dataset de treinamento vazio")
        
        # Prepara dados
        def prepare_examples(examples):
            """Prepara exemplos para treinamento"""
            texts = []
            labels = []
            
            for item in examples:
                instruction = item.get("instruction", "")
                response = item.get("response", "")
                reward = float(item.get("reward", 0.5))
                
                # Concatena instrução + resposta
                text = f"{instruction} [SEP] {response}"
                texts.append(text)
                labels.append(reward)
            
            return {"text": texts, "labels": labels}
        
        # Cria dataset
        dataset = Dataset.from_list(training_data)
        dataset = dataset.map(
            prepare_examples,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        # Split treino/validação
        dataset = dataset.train_test_split(test_size=validation_split)
        train_dataset = dataset["train"]
        eval_dataset = dataset["test"]
        
        # Carrega modelo base
        self._load_model()
        
        # Prepara textos e scores
        train_texts = train_dataset["text"]
        train_scores = train_dataset["labels"]
        val_texts = eval_dataset["text"]
        val_scores = eval_dataset["labels"]
        
        # Treina usando módulo core
        model_path, metrics = train_reward_model_core(
            model=self.model,
            tokenizer=self.tokenizer,
            train_texts=train_texts,
            train_scores=train_scores,
            val_texts=val_texts,
            val_scores=val_scores,
            output_dir=output_dir,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate
        )
        
        # Atualiza caminho do modelo
        self.model_path = model_path
        self.is_loaded = False  # Força recarregar modelo treinado
        
        return metrics
    
    def predict_reward(
        self,
        instruction: str,
        response: str
    ) -> float:
        """
        Prediz recompensa (score) de uma resposta
        
        Args:
            instruction: Pergunta/instrução do usuário
            response: Resposta do assistente
            
        Returns:
            Score de recompensa (0.0 a 1.0)
        """
        if not self.is_loaded:
            self._load_model()
        
        # Prepara texto
        text = f"{instruction} [SEP] {response}"
        
        # Tokeniza
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Predição
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            score = outputs.logits.item()
        
        # Normaliza para 0-1 (assumindo que modelo retorna score bruto)
        reward = max(0.0, min(1.0, (score + 1) / 2))  # Normaliza de [-1, 1] para [0, 1]
        
        return reward
    
    def evaluate_responses(
        self,
        instruction: str,
        responses: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Avalia múltiplas respostas e rankeia
        
        Args:
            instruction: Pergunta/instrução do usuário
            responses: Lista de respostas candidatas
            
        Returns:
            Lista de tuplas (resposta, score) ordenada por score decrescente
        """
        if not responses:
            return []
        
        scores = []
        for response in responses:
            score = self.predict_reward(instruction, response)
            scores.append((response, score))
        
        # Ordena por score (maior primeiro)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores
    
    def load_model(self, model_path: str):
        """
        Carrega modelo treinado
        
        Args:
            model_path: Caminho para modelo
        """
        self.model_path = model_path
        self.is_loaded = False
        self._load_model()
        logger.info(f"✅ Modelo carregado de: {model_path}")
