#!/usr/bin/env python3
"""
Treina modelo com RLHF usando PPO
"""
import sys
import os
import argparse
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.services.rlhf_service import RLHFService
from backend.services.reward_model_service import RewardModelService
from backend.database.database import Database
from backend.scripts.training.utils.training_config import TrainingConfig
from backend.scripts.training.utils.status_manager import StatusManager
from backend.scripts.training.validation.check_resources import validate_resources
import asyncio


async def train_rlhf_ppo(
    database: Database,
    reward_model_path: str,
    output_dir: str,
    status_manager: StatusManager
):
    """Treina com RLHF usando PPO"""
    config = TrainingConfig.RLHF_PPO_LIMITS
    
    logger.info("=" * 60)
    logger.info("TREINAMENTO RLHF COM PPO")
    logger.info("=" * 60)
    
    # Verifica se modelo de recompensa existe
    if not Path(reward_model_path).exists():
        logger.error(f"❌ Modelo de recompensa não encontrado: {reward_model_path}")
        logger.error("Execute primeiro: python3 backend/scripts/training/rlhf/train_reward_model.py")
        sys.exit(1)
    
    # Valida recursos
    if not validate_resources(
        min_ram=config.min_ram_gb,
        max_cpu_load=config.max_cpu_load,
        min_disk=config.min_disk_gb
    ):
        logger.error("❌ Recursos insuficientes")
        sys.exit(1)
    
    # Verifica pré-requisito
    status = status_manager.get_phase_status("rlhf")
    if status.get("reward_model", {}).get("status") != "completed":
        logger.error("❌ Modelo de recompensa deve estar treinado primeiro")
        sys.exit(1)
    
    # Atualiza status
    status_manager.update_phase_status("rlhf", "in_progress", etapa="ppo")
    
    try:
        # Carrega modelo de recompensa
        reward_service = RewardModelService()
        reward_service.load_model(reward_model_path)
        
        # Inicializa RLHF service
        rlhf_service = RLHFService(reward_model_service=reward_service)
        
        # Prepara preferências
        logger.info("Preparando preferências de feedback...")
        feedback_list = await database.list_feedback(limit=1000)
        preferences = rlhf_service.collect_preferences(feedback_list)
        
        if len(preferences) < 20:
            logger.warning(f"⚠️  Poucas preferências: {len(preferences)} (recomendado: 20+)")
            response = input("Continuar mesmo assim? (s/N): ")
            if response.lower() != "s":
                sys.exit(0)
        
        # Treina
        logger.info("Iniciando treinamento RLHF com PPO...")
        result = rlhf_service.train_with_ppo(
            training_data=preferences,
            reward_model_service=reward_service,
            output_dir=output_dir,
            batch_size=TrainingConfig.RLHF_DEFAULT_BATCH_SIZE_PPO,
            epochs=2
        )
        
        if result is None or "model_path" not in result:
            logger.error("❌ Erro durante treinamento RLHF")
            sys.exit(1)
        
        model_path = result.get("model_path", output_dir)
        
        # Atualiza status
        status_manager.update_phase_status(
            "rlhf",
            "completed",
            etapa="ppo",
            checkpoint_path=str(model_path)
        )
        
        logger.info("=" * 60)
        logger.info("✅ RLHF COM PPO CONCLUÍDO!")
        logger.info(f"Modelo salvo em: {model_path}")
        logger.info("=" * 60)
        
        return model_path
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("rlhf", "error", etapa="ppo", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Treina modelo com RLHF usando PPO")
    parser.add_argument(
        "--reward-model",
        type=str,
        default="models/reward_model",
        help="Caminho do modelo de recompensa"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="checkpoints/rlhf",
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
        await train_rlhf_ppo(
            database,
            args.reward_model,
            args.output_dir,
            status_manager
        )
        status_manager.calculate_progress()
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())

