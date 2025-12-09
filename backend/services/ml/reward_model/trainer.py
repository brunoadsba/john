"""
Lógica de treinamento do modelo de recompensa
"""
from typing import List, Tuple, Dict
import torch
from torch.utils.data import DataLoader, TensorDataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from loguru import logger


def train_reward_model_core(
    model,
    tokenizer,
    train_texts: List[str],
    train_scores: List[float],
    val_texts: List[str],
    val_scores: List[float],
    output_dir: str,
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5
) -> Tuple[str, Dict]:
    """
    Treina o modelo de recompensa
    
    Args:
        model: Modelo pré-carregado
        tokenizer: Tokenizer pré-carregado
        train_texts: Textos de treinamento
        train_scores: Scores de recompensa (0-1)
        val_texts: Textos de validação
        val_scores: Scores de validação
        output_dir: Diretório para salvar modelo
        epochs: Número de épocas
        batch_size: Tamanho do batch
        learning_rate: Taxa de aprendizado
        
    Returns:
        Tupla (caminho do modelo salvo, métricas)
    """
    # Prepara datasets
    train_dataset = _prepare_dataset(tokenizer, train_texts, train_scores, max_length=512)
    val_dataset = _prepare_dataset(tokenizer, val_texts, val_scores, max_length=512)
    
    # Configuração de treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_steps=100,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="loss",
        greater_is_better=False,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    # Treina
    logger.info("Iniciando treinamento do modelo de recompensa...")
    train_result = trainer.train()
    
    # Salva modelo
    model_path = f"{output_dir}/final"
    trainer.save_model(model_path)
    tokenizer.save_pretrained(model_path)
    
    # Métricas
    metrics = {
        "train_loss": train_result.training_loss,
        "train_runtime": train_result.metrics.get("train_runtime", 0),
    }
    
    # Avalia no conjunto de validação
    eval_results = trainer.evaluate()
    metrics.update(eval_results)
    
    logger.info(f"✅ Modelo treinado e salvo em: {model_path}")
    logger.info(f"📊 Métricas: {metrics}")
    
    return model_path, metrics


def _prepare_dataset(tokenizer, texts: List[str], scores: List[float], max_length: int = 512):
    """Prepara dataset para treinamento"""
    # Tokeniza textos
    encodings = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors="pt"
    )
    
    # Converte scores para tensores
    labels = torch.tensor(scores, dtype=torch.float32)
    
    # Cria dataset
    dataset = TensorDataset(
        encodings["input_ids"],
        encodings["attention_mask"],
        labels
    )
    
    return dataset

