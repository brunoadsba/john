#!/usr/bin/env python3
"""
SFT Etapa 1: Validação (100 exemplos, 1 época)
"""
import sys
import os
import argparse
import json
import subprocess
from pathlib import Path
from typing import Optional

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
    limit: int = 100,
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
    config = TrainingConfig.get_sft_config_for_etapa(1)
    
    logger.info("=" * 60)
    logger.info("SFT ETAPA 1: VALIDAÇÃO")
    logger.info("=" * 60)
    logger.info(f"Dataset: {len(json.load(open(dataset_path)))} exemplos")
    logger.info(f"Épocas: {config['epochs']}")
    logger.info(f"Batch size: {config['batch_size']}")
    logger.info(f"Learning rate: {config['learning_rate']}")
    
    # Atualiza status
    status_manager.update_phase_status(
        "sft",
        "in_progress",
        etapa="1",
        dataset_size=len(json.load(open(dataset_path))),
        started_at=status_manager._status["last_updated"]
    )
    
    try:
        # Inicializa serviço
        finetuning_service = FinetuningService(base_model=config["base_model"])
        
        # Prepara dataset
        logger.info("Preparando dataset...")
        dataset = finetuning_service.prepare_sft_dataset(dataset_path)
        
        # Treina
        logger.info("Iniciando treinamento...")
        model_path = finetuning_service.train_with_lora(
            dataset=dataset,
            output_dir=output_dir,
            num_epochs=config["epochs"],
            batch_size=config["batch_size"],
            learning_rate=config["learning_rate"],
            lora_r=config["lora_r"],
            lora_alpha=config["lora_alpha"],
            lora_dropout=config["lora_dropout"]
        )
        
        # Atualiza status como completo
        status_manager.update_phase_status(
            "sft",
            "completed",
            etapa="1",
            checkpoint_path=str(model_path),
            completed_at=status_manager._status["last_updated"]
        )
        
        logger.info("=" * 60)
        logger.info("✅ ETAPA 1 CONCLUÍDA!")
        logger.info(f"Modelo salvo em: {model_path}")
        logger.info("=" * 60)
        
        return model_path
    
    except Exception as e:
        logger.error(f"Erro durante treinamento: {e}")
        status_manager.update_phase_status(
            "sft",
            "error",
            etapa="1",
            error=str(e)
        )
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="SFT Etapa 1: Validação")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Caminho do dataset JSON (se não fornecido, usa banco de dados)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/finetuned/jonh-ft-v1-etapa1",
        help="Diretório de saída"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Pular validação de recursos e dataset"
    )
    
    args = parser.parse_args()
    
    # Valida recursos
    if not args.skip_validation:
        config = TrainingConfig.get_limits_for_etapa(1)
        if not validate_resources(
            min_ram=config.min_ram_gb,
            max_cpu_load=config.max_cpu_load,
            min_disk=config.min_disk_gb
        ):
            logger.error("❌ Validação de recursos falhou")
            sys.exit(1)
    
    # Inicializa status manager
    status_manager = StatusManager()
    
    # Determina dataset
    if args.dataset:
        dataset_path = args.dataset
        if not Path(dataset_path).exists():
            logger.error(f"Dataset não encontrado: {dataset_path}")
            sys.exit(1)
    else:
        # Usa banco de dados
        logger.info("Preparando dataset do banco de dados...")
        db_path = Path(__file__).parent.parent.parent.parent / "data" / "jonh_assistant.db"
        database = Database(db_path=str(db_path))
        await database.connect()
        
        dataset_path = await prepare_dataset_from_db(
            database=database,
            output_path="data/training/sft_dataset_etapa1.json",
            limit=100,
            min_quality=0.7
        )
        
        await database.close()
    
    # Valida dataset
    if not args.skip_validation:
        if not validate_dataset(dataset_path, min_samples=100, min_quality=0.7):
            logger.error("❌ Validação de dataset falhou")
            sys.exit(1)
    
    # Verifica dados
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if len(data) < 100:
        logger.warning(f"⚠️  Dataset pequeno: {len(data)} exemplos (recomendado: 100+)")
        response = input("Continuar mesmo assim? (s/N): ")
        if response.lower() != "s":
            logger.info("Treinamento cancelado.")
            sys.exit(0)
    
    # Executa com prioridade baixa
    try:
        # Usa nice para prioridade baixa
        if os.name != 'nt':  # Não funciona no Windows
            os.nice(19)
        
        train_with_validation(
            dataset_path=dataset_path,
            output_dir=args.output_dir,
            status_manager=status_manager
        )
        
        # Atualiza progresso geral
        progress = status_manager.calculate_progress()
        logger.info(f"Progresso geral: {progress}%")
        
    except KeyboardInterrupt:
        logger.warning("Treinamento interrompido pelo usuário")
        status_manager.update_phase_status("sft", "error", etapa="1", error="Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro durante treinamento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

