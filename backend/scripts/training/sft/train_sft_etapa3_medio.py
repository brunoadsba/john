#!/usr/bin/env python3
"""
SFT Etapa 3: Médio (2000 exemplos, 3 épocas)
"""
import sys
import os
import argparse
import json
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.services.finetuning_service import FinetuningService
from backend.services.feedback_service import FeedbackService
from backend.database.database import Database
from backend.scripts.training.utils.training_config import TrainingConfig
from backend.scripts.training.utils.status_manager import StatusManager
from backend.scripts.training.validation.check_resources import validate_resources
from backend.scripts.training.validation.validate_dataset import validate_dataset
import asyncio


async def prepare_dataset_from_db(
    database: Database,
    output_path: str,
    limit: int = 2000,
    min_quality: float = 0.7
) -> str:
    """Prepara dataset do banco de dados"""
    feedback_service = FeedbackService(database)
    return await feedback_service.export_training_dataset(
        output_path=output_path,
        format="alpaca",
        min_quality=min_quality,
        limit=limit
    )


def train_with_validation(
    dataset_path: str,
    output_dir: str,
    status_manager: StatusManager
):
    """Treina modelo"""
    config = TrainingConfig.get_sft_config_for_etapa(3)
    
    logger.info("=" * 60)
    logger.info("SFT ETAPA 3: MÉDIO")
    logger.info("=" * 60)
    
    # Verifica pré-requisito
    status = status_manager.get_phase_status("sft")
    if status.get("etapas", {}).get("2", {}).get("status") != "completed":
        logger.error("❌ Etapa 2 deve estar completa")
        sys.exit(1)
    
    status_manager.update_phase_status("sft", "in_progress", etapa="3")
    
    try:
        finetuning_service = FinetuningService(base_model=config["base_model"])
        dataset = finetuning_service.prepare_sft_dataset(dataset_path)
        
        model_path = finetuning_service.train_with_lora(
            dataset=dataset,
            output_dir=output_dir,
            num_epochs=config["epochs"],
            batch_size=config["batch_size"],
            learning_rate=config["learning_rate"]
        )
        
        status_manager.update_phase_status("sft", "completed", etapa="3", checkpoint_path=str(model_path))
        logger.info("✅ ETAPA 3 CONCLUÍDA!")
        return model_path
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("sft", "error", etapa="3", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="SFT Etapa 3: Médio")
    parser.add_argument("--dataset", type=str)
    parser.add_argument("--output-dir", type=str, default="models/finetuned/jonh-ft-v1-etapa3")
    parser.add_argument("--skip-validation", action="store_true")
    
    args = parser.parse_args()
    
    if not args.skip_validation:
        config = TrainingConfig.get_limits_for_etapa(3)
        if not validate_resources(config.min_ram_gb, config.max_cpu_load, config.min_disk_gb):
            sys.exit(1)
    
    status_manager = StatusManager()
    
    if args.dataset:
        dataset_path = args.dataset
    else:
        db_path = Path(__file__).parent.parent.parent.parent / "data" / "jonh_assistant.db"
        database = Database(db_path=str(db_path))
        await database.connect()
        dataset_path = await prepare_dataset_from_db(database, "data/training/sft_dataset_etapa3.json", limit=2000)
        await database.close()
    
    if not args.skip_validation:
        if not validate_dataset(dataset_path, min_samples=2000, min_quality=0.7):
            sys.exit(1)
    
    try:
        if os.name != 'nt':
            os.nice(19)
        train_with_validation(dataset_path, args.output_dir, status_manager)
        status_manager.calculate_progress()
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

