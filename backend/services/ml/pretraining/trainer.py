"""
Continuação de pré-treinamento do Llama 3.1
"""
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers não disponível - instale com: pip install transformers accelerate")


def continue_pretraining_core(
    model_name: str,
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
        model_name: Nome do modelo base (HuggingFace)
        dataset: Dataset preparado
        output_dir: Diretório para salvar checkpoints
        num_epochs: Número de épocas
        batch_size: Tamanho do batch
        learning_rate: Taxa de aprendizado
        max_steps: Número máximo de steps (opcional)
        
    Returns:
        Métricas de treinamento ou None se erro
    """
    if not TRANSFORMERS_AVAILABLE:
        logger.error("transformers não disponível")
        return None
    
    logger.info(f"Iniciando pré-treinamento de {model_name}...")
    
    try:
        # Carrega modelo e tokenizer
        logger.info("Carregando modelo e tokenizer...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Tokeniza dataset
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=2048,
                padding="max_length"
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # Causal LM, não masked LM
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            max_steps=max_steps,
            save_steps=500,
            logging_steps=100,
            save_total_limit=3,
            prediction_loss_only=True,
            remove_unused_columns=False,
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # Treina
        logger.info("Iniciando treinamento...")
        train_result = trainer.train()
        
        # Salva modelo final
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        
        metrics = {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics.get("train_runtime", 0),
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
        }
        
        logger.info(f"Pré-treinamento concluído. Loss final: {metrics['train_loss']:.4f}")
        
        return metrics
    
    except Exception as e:
        logger.error(f"Erro durante pré-treinamento: {e}")
        return None

