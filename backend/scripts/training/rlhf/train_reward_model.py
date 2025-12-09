#!/usr/bin/env python3
"""
Treina modelo de recompensa para RLHF
"""
import sys
import os
import argparse
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.services.reward_model_service import RewardModelService
from backend.database.database import Database
from backend.scripts.training.utils.training_config import TrainingConfig
from backend.scripts.training.utils.status_manager import StatusManager
from backend.scripts.training.validation.check_resources import validate_resources
import asyncio


async def train_reward_model(
    database: Database,
    output_dir: str,
    status_manager: StatusManager
):
    """Treina modelo de recompensa"""
    config = TrainingConfig.RLHF_REWARD_LIMITS
    
    logger.info("=" * 60)
    logger.info("TREINAMENTO DE MODELO DE RECOMPENSA")
    logger.info("=" * 60)
    
    # Valida recursos
    if not validate_resources(
        min_ram=config.min_ram_gb,
        max_cpu_load=config.max_cpu_load,
        min_disk=config.min_disk_gb
    ):
        logger.error("❌ Recursos insuficientes")
        sys.exit(1)
    
    # Atualiza status
    status_manager.update_phase_status("rlhf", "in_progress", etapa="reward_model")
    
    try:
        reward_service = RewardModelService()
        
        # Prepara dados de feedback
        logger.info("Preparando dados de feedback...")
        feedback_list = await database.list_feedback(limit=1000)
        
        if len(feedback_list) < 50:
            logger.warning(f"⚠️  Poucos feedbacks: {len(feedback_list)} (recomendado: 50+)")
            response = input("Continuar mesmo assim? (s/N): ")
            if response.lower() != "s":
                sys.exit(0)
        
        # Treina
        logger.info("Iniciando treinamento do modelo de recompensa...")
        model_path = reward_service.train_reward_model(
            feedback_data=feedback_list,
            output_dir=output_dir,
            batch_size=TrainingConfig.RLHF_DEFAULT_BATCH_SIZE_REWARD,
            num_epochs=3
        )
        
        # Atualiza status
        status_manager.update_phase_status(
            "rlhf",
            "completed",
            etapa="reward_model",
            checkpoint_path=str(model_path)
        )
        
        logger.info("=" * 60)
        logger.info("✅ MODELO DE RECOMPENSA TREINADO!")
        logger.info(f"Modelo salvo em: {model_path}")
        logger.info("=" * 60)
        
        return model_path
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("rlhf", "error", etapa="reward_model", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Treina modelo de recompensa")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/reward_model",
        help="Diretório de saída"
    )
    parser.add_argument("--skip-validation", action="store_true")
    
    args = parser.parse_args()
    
    status_manager = StatusManager()
    
    # Conecta ao banco
    db_path = Path(__file__).parent.parent.parent.parent / "data" / "jonh_assistant.db"
    database = Database(db_path=str(db_path))
    await database.connect()
    
    try:
        if os.name != 'nt':
            os.nice(19)
        await train_reward_model(database, args.output_dir, status_manager)
        status_manager.calculate_progress()
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())

