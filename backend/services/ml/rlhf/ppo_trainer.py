"""
Lógica de treinamento PPO para RLHF
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

try:
    from transformers import TrainingArguments
    from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
    from peft import LoraConfig, get_peft_model
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.debug("trl/transformers não disponível - RLHF desabilitado (instale se necessário para treinamento)")


def train_with_ppo_core(
    model,
    tokenizer,
    reward_model,
    training_data: List[Dict[str, Any]],
    output_dir: str,
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 1e-5,
    use_lora: bool = True
) -> Dict[str, Any]:
    """
    Treina modelo usando PPO
    
    Args:
        model: Modelo base carregado
        tokenizer: Tokenizer carregado
        reward_model: Modelo de recompensa
        training_data: Dados de treinamento
        output_dir: Diretório de saída
        epochs: Número de épocas
        batch_size: Tamanho do batch
        learning_rate: Taxa de aprendizado
        use_lora: Usar LoRA para fine-tuning eficiente
        
    Returns:
        Métricas de treinamento
    """
    if not TRANSFORMERS_AVAILABLE:
        raise ImportError("trl e transformers são necessários")
    
    logger.info(f"Iniciando treinamento PPO com {len(training_data)} exemplos")
    
    # Prepara dataset
    dataset = Dataset.from_list(training_data)
    
    # Configura PPO
    ppo_config = PPOConfig(
        model_name=model.config.name_or_path if hasattr(model.config, 'name_or_path') else "base",
        learning_rate=learning_rate,
        batch_size=batch_size,
        mini_batch_size=batch_size // 2,
        gradient_accumulation_steps=1,
        optimize_cuda_cache=True,
    )
    
    # Aplica LoRA se solicitado
    if use_lora:
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM"
        )
        model = get_peft_model(model, lora_config)
        logger.info("✅ LoRA aplicado ao modelo")
    
    # Cria modelo com value head para PPO
    model = AutoModelForCausalLMWithValueHead.from_pretrained(
        model.config.name_or_path if hasattr(model.config, 'name_or_path') else model,
        torch_dtype=model.dtype
    )
    
    # Trainer PPO
    ppo_trainer = PPOTrainer(
        config=ppo_config,
        model=model,
        tokenizer=tokenizer,
        dataset=dataset,
    )
    
    # Loop de treinamento
    for epoch in range(epochs):
        logger.info(f"Época {epoch + 1}/{epochs}")
        
        for batch in dataset:
            # Gera respostas
            query_tensors = tokenizer(
                batch["instruction"],
                return_tensors="pt",
                padding=True,
                truncation=True
            )["input_ids"]
            
            # Gera resposta com modelo
            response_tensors = ppo_trainer.generate(
                query_tensors,
                return_prompt=False,
                length_sampler=None,
                batch_size=batch_size,
                temperature=0.7,
                max_new_tokens=256
            )
            
            # Calcula recompensas
            responses = tokenizer.batch_decode(response_tensors, skip_special_tokens=True)
            rewards = [
                reward_model.predict_reward(batch["instruction"], resp)
                for resp in responses
            ]
            
            # Treina com PPO
            stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
            logger.debug(f"Stats: {stats}")
    
    # Salva modelo
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ppo_trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    metrics = {
        "epochs": epochs,
        "samples": len(training_data),
        "output_dir": output_dir
    }
    
    logger.info(f"✅ Treinamento PPO concluído: {output_dir}")
    return metrics

