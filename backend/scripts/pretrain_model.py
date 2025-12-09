#!/usr/bin/env python3
"""
Script para executar continuação de pré-treinamento do Llama 3.1
"""
import sys
import argparse
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from backend.services.pretraining_service import PretrainingService
from backend.config.settings import settings


def main():
    """Executa pré-treinamento do modelo"""
    parser = argparse.ArgumentParser(description="Pré-treina modelo Llama 3.1 com corpus PT-BR")
    parser.add_argument(
        "--corpus",
        type=str,
        default=settings.pretraining_corpus_path,
        help="Caminho do corpus de texto"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/pretrained_llama3.1",
        help="Diretório de saída para o modelo pré-treinado"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
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
        default=5e-5,
        help="Taxa de aprendizado"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Número máximo de steps (opcional)"
    )
    parser.add_argument(
        "--skip-prepare",
        action="store_true",
        help="Pula preparação de dados (usa dataset já preparado)"
    )
    
    args = parser.parse_args()
    
    logger.info("Iniciando pré-treinamento do modelo...")
    logger.info(f"Corpus: {args.corpus}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Épocas: {args.epochs}, Batch: {args.batch_size}, LR: {args.learning_rate}")
    
    try:
        # Inicializa serviço
        service = PretrainingService()
        
        # Prepara dados (se necessário)
        if not args.skip_prepare:
            logger.info("Preparando dados de pré-treinamento...")
            dataset = service.prepare_pretraining_data(
                corpus_path=args.corpus,
                chunk_size=2048
            )
            
            if dataset is None:
                logger.error("❌ Falha ao preparar dados")
                return 1
            
            logger.info(f"✅ Dataset preparado: {len(dataset)} exemplos")
        else:
            # Carrega dataset já preparado
            from datasets import load_from_disk
            dataset_path = Path(args.corpus).parent / "pretraining_dataset"
            if not dataset_path.exists():
                logger.error(f"❌ Dataset não encontrado: {dataset_path}")
                return 1
            dataset = load_from_disk(str(dataset_path))
            logger.info(f"✅ Dataset carregado: {len(dataset)} exemplos")
        
        # Executa pré-treinamento
        logger.info("Iniciando treinamento...")
        metrics = service.continue_pretraining(
            dataset=dataset,
            output_dir=args.output,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            max_steps=args.max_steps
        )
        
        if metrics is None:
            logger.error("❌ Falha durante pré-treinamento")
            return 1
        
        logger.info("✅ Pré-treinamento concluído!")
        logger.info(f"Métricas: {metrics}")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Erro durante pré-treinamento: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

