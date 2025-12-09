#!/usr/bin/env python3
"""
Coleta corpus de texto com validação de recursos
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


async def collect_corpus(
    output_path: str,
    status_manager: StatusManager
):
    """Coleta corpus com validação"""
    config = TrainingConfig.PRETRAINING_LIMITS
    
    logger.info("=" * 60)
    logger.info("COLETA DE CORPUS PARA PRÉ-TREINAMENTO")
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
    status_manager.update_phase_status("pretraining", "in_progress", etapa="collect_corpus")
    
    try:
        pretraining_service = PretrainingService()
        
        # Coleta corpus
        logger.info("Coletando corpus de conversas...")
        corpus_path = pretraining_service.collect_corpus(
            output_path=output_path,
            sources=["conversations"]
        )
        
        # Valida tamanho
        corpus_size_mb = Path(corpus_path).stat().st_size / (1024 ** 2)
        logger.info(f"Corpus coletado: {corpus_size_mb:.2f} MB")
        
        if corpus_size_mb < TrainingConfig.MIN_CORPUS_SIZE_MB:
            logger.warning(f"⚠️  Corpus pequeno: {corpus_size_mb:.2f} MB < {TrainingConfig.MIN_CORPUS_SIZE_MB} MB")
            response = input("Continuar mesmo assim? (s/N): ")
            if response.lower() != "s":
                sys.exit(0)
        
        # Atualiza status
        status_manager.update_phase_status(
            "pretraining",
            "completed",
            etapa="collect_corpus",
            corpus_path=str(corpus_path),
            corpus_size_mb=corpus_size_mb
        )
        
        logger.info("=" * 60)
        logger.info("✅ COLETA DE CORPUS CONCLUÍDA!")
        logger.info(f"Corpus salvo em: {corpus_path}")
        logger.info("=" * 60)
        
        return corpus_path
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("pretraining", "error", etapa="collect_corpus", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Coleta corpus para pré-treinamento")
    parser.add_argument(
        "--output-path",
        type=str,
        default="data/corpus/pt_br_corpus.txt",
        help="Caminho de saída do corpus"
    )
    parser.add_argument("--skip-validation", action="store_true")
    
    args = parser.parse_args()
    
    status_manager = StatusManager()
    
    try:
        if os.name != 'nt':
            os.nice(19)
        await collect_corpus(args.output_path, status_manager)
        status_manager.calculate_progress()
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

