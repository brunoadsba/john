"""
Orquestração de treinamento RLHF
"""
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from backend.services.rlhf_service import RLHFService
from backend.services.reward_model_service import RewardModelService


async def train_reward_model_phase(
    reward_model_service: RewardModelService,
    training_data: list,
    output_dir: str,
    epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 2e-5
) -> Dict[str, Any]:
    """
    Fase 1: Treina modelo de recompensa
    
    Args:
        reward_model_service: Serviço de modelo de recompensa
        training_data: Dados de treinamento
        output_dir: Diretório de saída
        epochs: Número de épocas
        batch_size: Tamanho do batch
        learning_rate: Taxa de aprendizado
        
    Returns:
        Métricas de treinamento
    """
    logger.info("=" * 60)
    logger.info("FASE 1: Treinamento do Modelo de Recompensa")
    logger.info("=" * 60)
    
    if not training_data:
        raise ValueError("Dados de treinamento vazios")
    
    metrics = reward_model_service.train_reward_model(
        training_data=training_data,
        output_dir=output_dir,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    logger.info(f"✅ Modelo de recompensa treinado: {output_dir}")
    return metrics


async def train_rlhf_phase(
    rlhf_service: RLHFService,
    reward_model_service: RewardModelService,
    preferences: list,
    output_dir: str,
    epochs: int = 1,
    batch_size: int = 4,
    learning_rate: float = 1e-6
) -> Dict[str, Any]:
    """
    Fase 2: Treinamento RLHF completo
    
    Args:
        rlhf_service: Serviço RLHF
        reward_model_service: Serviço de modelo de recompensa
        preferences: Lista de preferências
        output_dir: Diretório de saída
        epochs: Número de épocas
        batch_size: Tamanho do batch
        learning_rate: Taxa de aprendizado
        
    Returns:
        Métricas de treinamento
    """
    logger.info("=" * 60)
    logger.info("FASE 2: Treinamento RLHF (PPO)")
    logger.info("=" * 60)
    
    if not preferences:
        raise ValueError("Lista de preferências vazia")
    
    metrics = rlhf_service.train_with_ppo(
        training_data=preferences,
        reward_model_service=reward_model_service,
        output_dir=output_dir,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    logger.info(f"✅ Treinamento RLHF concluído: {output_dir}")
    return metrics

