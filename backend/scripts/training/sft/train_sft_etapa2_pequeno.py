#!/usr/bin/env python3
"""
SFT Etapa 2: Pequeno (500 exemplos, 2 épocas)
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
    limit: int = 500,
    min_quality: float = 0.7
) -> str:
    """Prepara dataset do banco de dados"""
    feedback_service = FeedbackService(database)
    dataset_path = await feedback_service.export_training_dataset(
        output_path=output_path,
        format="alpaca",
        min_quality=min_quality,
        limit=limit
    )
    return dataset_path


def train_with_validation(
    dataset_path: str,
    output_dir: str,
    status_manager: StatusManager
):
    """Treina modelo com validação e atualização de status"""
    config = TrainingConfig.get_sft_config_for_etapa(2)
    
    logger.info("=" * 60)
    logger.info("SFT ETAPA 2: PEQUENO")
    logger.info("=" * 60)
    logger.info(f"Dataset: {len(json.load(open(dataset_path)))} exemplos")
    logger.info(f"Épocas: {config['epochs']}")
    logger.info(f"Batch size: {config['batch_size']}")
    
    # Verifica pré-requisito (etapa 1)
    status = status_manager.get_phase_status("sft")
    etapa1 = status.get("etapas", {}).get("1", {})
    if etapa1.get("status") != "completed":
        logger.error("❌ Etapa 1 deve estar completa antes de executar Etapa 2")
        sys.exit(1)
    
    # Atualiza status
    status_manager.update_phase_status(
        "sft",
        "in_progress",
        etapa="2",
        dataset_size=len(json.load(open(dataset_path)))
    )
    
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
        
        status_manager.update_phase_status(
            "sft",
            "completed",
            etapa="2",
            checkpoint_path=str(model_path)
        )
        
        logger.info("✅ ETAPA 2 CONCLUÍDA!")
        return model_path
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("sft", "error", etapa="2", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="SFT Etapa 2: Pequeno")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Caminho do dataset JSON"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/finetuned/jonh-ft-v1-etapa2",
        help="Diretório de saída"
    )
    parser.add_argument("--skip-validation", action="store_true")
    
    args = parser.parse_args()
    
    if not args.skip_validation:
        config = TrainingConfig.get_limits_for_etapa(2)
        if not validate_resources(
            min_ram=config.min_ram_gb,
            max_cpu_load=config.max_cpu_load,
            min_disk=config.min_disk_gb
        ):
            sys.exit(1)
    
    status_manager = StatusManager()
    
    if args.dataset:
        dataset_path = args.dataset
    else:
        db_path = Path(__file__).parent.parent.parent.parent / "data" / "jonh_assistant.db"
        database = Database(db_path=str(db_path))
        await database.connect()
        dataset_path = await prepare_dataset_from_db(
            database=database,
            output_path="data/training/sft_dataset_etapa2.json",
            limit=500
        )
        await database.close()
    
    if not args.skip_validation:
        if not validate_dataset(dataset_path, min_samples=500, min_quality=0.7):
            sys.exit(1)
    
    try:
        if os.name != 'nt':
            os.nice(19)
        train_with_validation(dataset_path, args.output_dir, status_manager)
        status_manager.calculate_progress()
    except KeyboardInterrupt:
        logger.warning("Interrompido")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

