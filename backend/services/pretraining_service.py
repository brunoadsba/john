"""
Serviço de Continuação de Pré-treinamento (Auto-Supervisionado)
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers/datasets não disponível - instale com: pip install transformers datasets accelerate")

from backend.services.ml.pretraining import (
    collect_corpus_core,
    prepare_pretraining_data_core,
    continue_pretraining_core,
    evaluate_improvements_core
)


class PretrainingService:
    """Gerencia continuação de pré-treinamento de modelos LLM"""
    
    def __init__(self, base_model: str = "meta-llama/Llama-3.1-8B-Instruct"):
        """
        Inicializa serviço de pré-treinamento
        
        Args:
            base_model: Nome do modelo base (HuggingFace)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers e datasets são necessários para pré-treinamento")
        
        self.base_model = base_model
        logger.info(f"PretrainingService inicializado (modelo base: {base_model})")
    
    def collect_corpus(
        self,
        output_path: str,
        sources: Optional[List[str]] = None,
        min_length: int = 50,
        max_length: int = 2048
    ) -> str:
        """
        Coleta corpus de texto em português brasileiro
        
        Args:
            output_path: Caminho para salvar o corpus
            sources: Lista de fontes (opcional)
            min_length: Tamanho mínimo de texto
            max_length: Tamanho máximo de texto
            
        Returns:
            Caminho do arquivo salvo
        """
        return collect_corpus_core(
            output_path=output_path,
            sources=sources,
            min_length=min_length,
            max_length=max_length
        )
    
    def prepare_pretraining_data(
        self,
        corpus_path: str,
        tokenizer_name: Optional[str] = None,
        chunk_size: int = 2048,
        output_path: Optional[str] = None
    ) -> Optional[Dataset]:
        """
        Prepara dados no formato de pré-treinamento
        
        Args:
            corpus_path: Caminho para o corpus
            tokenizer_name: Nome do tokenizer (usa base_model se None)
            chunk_size: Tamanho dos chunks
            output_path: Caminho para salvar dataset (opcional)
            
        Returns:
            Dataset preparado ou None se erro
        """
        if tokenizer_name is None:
            tokenizer_name = self.base_model
        
        return prepare_pretraining_data_core(
            corpus_path=corpus_path,
            tokenizer_name=tokenizer_name,
            chunk_size=chunk_size,
            output_path=output_path
        )
    
    def continue_pretraining(
        self,
        dataset: Dataset,
        output_dir: str,
        num_epochs: int = 1,
        batch_size: int = 4,
        learning_rate: float = 5e-5,
        max_steps: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Continua pré-treinamento do modelo base
        
        Args:
            dataset: Dataset preparado
            output_dir: Diretório para salvar checkpoints
            num_epochs: Número de épocas
            batch_size: Tamanho do batch
            learning_rate: Taxa de aprendizado
            max_steps: Número máximo de steps (opcional)
            
        Returns:
            Métricas de treinamento ou None se erro
        """
        return continue_pretraining_core(
            model_name=self.base_model,
            dataset=dataset,
            output_dir=output_dir,
            num_epochs=num_epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            max_steps=max_steps
        )
    
    def evaluate_improvements(
        self,
        base_model_path: str,
        pretrained_model_path: str,
        test_prompts: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Avalia melhorias do modelo pré-treinado vs. base
        
        Args:
            base_model_path: Caminho do modelo base
            pretrained_model_path: Caminho do modelo pré-treinado
            test_prompts: Lista de prompts de teste (opcional)
            
        Returns:
            Métricas de avaliação ou None se erro
        """
        return evaluate_improvements_core(
            base_model_path=base_model_path,
            pretrained_model_path=pretrained_model_path,
            test_prompts=test_prompts
        )

