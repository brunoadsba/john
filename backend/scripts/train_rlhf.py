#!/usr/bin/env python3
"""
Script para executar treinamento RLHF (Reinforcement Learning from Human Feedback)
"""
import sys
import argparse
from pathlib import Path
from typing import Optional

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.rlhf_service import RLHFService
from backend.services.reward_model_service import RewardModelService
from backend.database.database import Database
from backend.scripts.ml.data_preparer import (
    prepare_preferences_from_feedback,
    prepare_reward_training_data
)
from backend.scripts.ml.training_runner import (
    train_reward_model_phase,
    train_rlhf_phase
)
from loguru import logger
import asyncio


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Treina modelo RLHF")
    parser.add_argument(
        "--mode",
        choices=["reward", "rlhf", "full"],
        default="full",
        help="Modo de treinamento: reward (apenas modelo de recompensa), rlhf (apenas RLHF), full (ambos)"
    )
    parser.add_argument(
        "--reward-model-path",
        type=str,
        help="Caminho para modelo de recompensa pré-treinado (para modo rlhf)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/rlhf",
        help="Diretório de saída"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Número de épocas"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Tamanho do batch"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-5,
        help="Taxa de aprendizado"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limite de exemplos do banco de dados"
    )
    
    args = parser.parse_args()
    
    # Inicializa banco de dados
    database = Database()
    await database.init_db()
    
    # Inicializa serviços
    reward_model_service = RewardModelService()
    rlhf_service = RLHFService()
    
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Modo: apenas modelo de recompensa
    if args.mode in ["reward", "full"]:
        logger.info("Preparando dados para modelo de recompensa...")
        training_data = await prepare_reward_training_data(
            database=database,
            limit=args.limit
        )
        
        if not training_data:
            logger.warning("⚠️  Nenhum dado de treinamento encontrado")
            return
        
        reward_output = output_path / "reward_model"
        await train_reward_model_phase(
            reward_model_service=reward_model_service,
            training_data=training_data,
            output_dir=str(reward_output),
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )
        
        # Carrega modelo treinado
        reward_model_service.load_model(str(reward_output))
    
    # Modo: apenas RLHF (requer modelo de recompensa)
    if args.mode in ["rlhf", "full"]:
        # Carrega modelo de recompensa se necessário
        if args.reward_model_path:
            reward_model_service.load_model(args.reward_model_path)
        elif not reward_model_service.is_loaded:
            raise ValueError("Modelo de recompensa necessário para RLHF. Use --reward-model-path ou execute modo 'full'")
        
        logger.info("Preparando preferências para RLHF...")
        preferences = await prepare_preferences_from_feedback(
            database=database,
            limit=args.limit
        )
        
        if not preferences:
            logger.warning("⚠️  Nenhuma preferência encontrada")
            return
        
        rlhf_output = output_path / "rlhf_model"
        await train_rlhf_phase(
            rlhf_service=rlhf_service,
            reward_model_service=reward_model_service,
            preferences=preferences,
            output_dir=str(rlhf_output),
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )
    
    logger.info("=" * 60)
    logger.info("✅ Treinamento concluído!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
