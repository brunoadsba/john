"""
Serviço de Fine-tuning Supervisionado (SFT) usando LoRA
"""
from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers/peft não disponível - instale com: pip install transformers peft accelerate datasets")

from backend.services.ml.finetuning import (
    prepare_sft_dataset_core,
    train_with_lora_core,
    evaluate_model_core,
    export_to_ollama_format_core
)


class FinetuningService:
    """Gerencia fine-tuning supervisionado de modelos LLM"""
    
    def __init__(self, base_model: str = "meta-llama/Llama-3.1-8B-Instruct"):
        """
        Inicializa serviço de fine-tuning
        
        Args:
            base_model: Nome do modelo base (HuggingFace)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers e peft são necessários para fine-tuning")
        
        self.base_model = base_model
        self.model = None
        self.tokenizer = None
        logger.info(f"FinetuningService inicializado (modelo base: {base_model})")
    
    def prepare_sft_dataset(
        self,
        dataset_path: str,
        output_path: Optional[str] = None
    ) -> Dataset:
        """
        Prepara dataset no formato Alpaca/Instruct para fine-tuning
        
        Args:
            dataset_path: Caminho do arquivo JSON com dataset
            output_path: Caminho opcional para salvar dataset processado
            
        Returns:
            Dataset processado no formato HuggingFace
        """
        return prepare_sft_dataset_core(dataset_path, output_path)
    
    def train_with_lora(
        self,
        dataset: Dataset,
        output_dir: str = "models/finetuned",
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        lora_r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.1
    ) -> str:
        """
        Executa fine-tuning usando LoRA (Low-Rank Adaptation)
        
        Args:
            dataset: Dataset preparado
            output_dir: Diretório para salvar modelo fine-tunado
            num_epochs: Número de épocas
            batch_size: Tamanho do batch
            learning_rate: Taxa de aprendizado
            lora_r: Rank de LoRA
            lora_alpha: Alpha de LoRA
            lora_dropout: Dropout de LoRA
            
        Returns:
            Caminho do modelo fine-tunado
        """
        # Carrega modelo e tokenizer
        if not self.model or not self.tokenizer:
            logger.info(f"Carregando modelo base: {self.base_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                device_map="auto",
                torch_dtype="auto"
            )
            
            # Adiciona padding token se não existir
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Treina usando módulo core
        return train_with_lora_core(
            model=self.model,
            tokenizer=self.tokenizer,
            dataset=dataset,
            output_dir=output_dir,
            num_epochs=num_epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            lora_r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout
        )
    
    def evaluate_model(
        self,
        test_dataset: Dataset,
        model_path: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Avalia modelo fine-tunado
        
        Args:
            test_dataset: Dataset de teste
            model_path: Caminho do modelo (se None, usa modelo atual)
            
        Returns:
            Métricas de avaliação
        """
        # Carrega modelo se necessário
        if model_path:
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        if not self.model or not self.tokenizer:
            raise ValueError("Modelo não carregado")
        
        return evaluate_model_core(
            model=self.model,
            tokenizer=self.tokenizer,
            test_dataset=test_dataset
        )
    
    def load_finetuned_model(self, model_path: str):
        """
        Carrega modelo fine-tunado
        
        Args:
            model_path: Caminho do modelo fine-tunado
        """
        logger.info(f"Carregando modelo fine-tunado: {model_path}")
        
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        logger.info("✅ Modelo fine-tunado carregado")
    
    def export_to_ollama_format(
        self,
        model_path: str,
        output_path: str,
        model_name: str = "jonh-ft"
    ) -> str:
        """
        Exporta modelo para formato Ollama (Modelfile)
        
        Args:
            model_path: Caminho do modelo fine-tunado
            output_path: Caminho do arquivo Modelfile
            model_name: Nome do modelo
            
        Returns:
            Caminho do Modelfile
        """
        return export_to_ollama_format_core(
            base_model=self.base_model,
            model_path=model_path,
            output_path=output_path,
            model_name=model_name
        )
