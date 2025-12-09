#!/usr/bin/env python3
"""
Pré-treinamento com proteções de recursos
"""
import sys
import os
import argparse
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.services.pretraining_service import PretrainingService
from backend.scripts.training.utils.training_config import TrainingConfig
from backend.scripts.training.utils.status_manager import StatusManager
from backend.scripts.training.validation.check_resources import validate_resources
import asyncio


async def pretrain_model(
    corpus_path: str,
    output_dir: str,
    status_manager: StatusManager,
    max_steps: int = 1000
):
    """Pré-treina modelo com proteções"""
    config = TrainingConfig.PRETRAINING_LIMITS
    
    logger.info("=" * 60)
    logger.info("PRÉ-TREINAMENTO DO MODELO")
    logger.info("=" * 60)
    logger.warning("⚠️  ATENÇÃO: Este processo pode levar DIAS para completar!")
    logger.warning("⚠️  Certifique-se de ter recursos suficientes e tempo disponível.")
    
    response = input("Continuar com pré-treinamento? (s/N): ")
    if response.lower() != "s":
        logger.info("Pré-treinamento cancelado.")
        sys.exit(0)
    
    # Valida recursos extensivamente
    if not validate_resources(
        min_ram=config.min_ram_gb,
        max_cpu_load=config.max_cpu_load,
        min_disk=config.min_disk_gb
    ):
        logger.error("❌ Recursos insuficientes")
        sys.exit(1)
    
    # Verifica se corpus existe
    if not Path(corpus_path).exists():
        logger.error(f"❌ Corpus não encontrado: {corpus_path}")
        logger.error("Execute primeiro: python3 backend/scripts/training/pretraining/collect_corpus_safe.py")
        sys.exit(1)
    
    # Atualiza status
    status_manager.update_phase_status("pretraining", "in_progress", etapa="pretrain")
    
    try:
        pretraining_service = PretrainingService()
        
        # Prepara dados
        logger.info("Preparando dados de pré-treinamento...")
        prepared_dataset = pretraining_service.prepare_pretraining_data(corpus_path)
        
        if prepared_dataset is None:
            logger.error("❌ Erro ao preparar dados de pré-treinamento")
            sys.exit(1)
        
        # Treina
        logger.info(f"Iniciando pré-treinamento (max_steps: {max_steps})...")
        logger.info("⚠️  Este processo salvará checkpoints a cada 500 steps")
        
        result = pretraining_service.continue_pretraining(
            dataset=prepared_dataset,
            output_dir=output_dir,
            max_steps=max_steps,
            batch_size=1,
            num_epochs=1
        )
        
        if result is None:
            logger.error("❌ Erro durante pré-treinamento")
            sys.exit(1)
        
        model_path = output_dir
        
        # Atualiza status
        status_manager.update_phase_status(
            "pretraining",
            "completed",
            etapa="pretrain",
            checkpoint_path=str(model_path)
        )
        
        logger.info("=" * 60)
        logger.info("✅ PRÉ-TREINAMENTO CONCLUÍDO!")
        logger.info(f"Modelo salvo em: {model_path}")
        logger.info("=" * 60)
        
        return model_path
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("pretraining", "error", etapa="pretrain", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Pré-treina modelo com proteções")
    parser.add_argument(
        "--corpus-path",
        type=str,
        default="data/corpus/pt_br_corpus.txt",
        help="Caminho do corpus"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/pretrained",
        help="Diretório de saída"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Número máximo de steps (padrão: 1000)"
    )
    parser.add_argument("--skip-validation", action="store_true")
    
    args = parser.parse_args()
    
    status_manager = StatusManager()
    
    try:
        if os.name != 'nt':
            os.nice(19)
        await pretrain_model(
            args.corpus_path,
            args.output_dir,
            status_manager,
            args.max_steps
        )
        status_manager.calculate_progress()
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

