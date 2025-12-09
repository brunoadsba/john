"""
Lógica de treinamento LoRA para fine-tuning
"""
from pathlib import Path
from typing import Dict
from loguru import logger

try:
    from transformers import (
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers/peft não disponível")


def train_with_lora_core(
    model,
    tokenizer,
    dataset: Dataset,
    output_dir: str,
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
        model: Modelo carregado
        tokenizer: Tokenizer carregado
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
    if not TRANSFORMERS_AVAILABLE:
        raise ImportError("transformers e peft são necessários")
    
    logger.info("Iniciando fine-tuning com LoRA...")
    
    # Tokeniza dataset
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Configura LoRA
    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Aplica LoRA ao modelo
    try:
        model = prepare_model_for_kbit_training(model)
    except Exception:
        # Modelo não está quantizado, continua normalmente
        pass
    
    model = get_peft_model(model, lora_config)
    
    # Configura argumentos de treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        save_total_limit=3,
        load_best_model_at_end=False,
        report_to="none"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator
    )
    
    # Treina
    logger.info("Iniciando treinamento...")
    trainer.train()
    
    # Salva modelo
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    logger.info(f"✅ Fine-tuning concluído! Modelo salvo em: {output_dir}")
    return str(output_path)

