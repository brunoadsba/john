#!/usr/bin/env python3
"""
Script para executar fine-tuning supervisionado (SFT)
"""
import sys
import argparse
import json
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.finetuning_service import FinetuningService
from backend.services.feedback_service import FeedbackService
from backend.database.database import Database
from loguru import logger
import asyncio


async def prepare_dataset_from_conversations(
    database: Database,
    output_path: str,
    min_quality: float = 0.7,
    limit: Optional[int] = None
) -> str:
    """
    Prepara dataset a partir de conversas do banco de dados
    
    Args:
        database: Instância do banco de dados
        output_path: Caminho de saída
        min_quality: Score mínimo de qualidade
        limit: Limite de exemplos
        
    Returns:
        Caminho do dataset preparado
    """
    logger.info("Preparando dataset a partir de conversas...")
    
    feedback_service = FeedbackService(database)
    
    # Exporta dataset
    dataset_path = await feedback_service.export_training_dataset(
        output_path=output_path,
        format="alpaca",
        min_quality=min_quality,
        limit=limit
    )
    
    logger.info(f"Dataset preparado: {dataset_path}")
    return dataset_path


def train_model(
    dataset_path: str,
    base_model: str,
    output_dir: str,
    num_epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4
):
    """
    Treina modelo com fine-tuning
    
    Args:
        dataset_path: Caminho do dataset
        base_model: Modelo base (HuggingFace)
        output_dir: Diretório de saída
        num_epochs: Número de épocas
        batch_size: Tamanho do batch
        learning_rate: Taxa de aprendizado
    """
    logger.info("=" * 60)
    logger.info("FINE-TUNING SUPERVISIONADO (SFT)")
    logger.info("=" * 60)
    
    # Inicializa serviço
    finetuning_service = FinetuningService(base_model=base_model)
    
    # Prepara dataset
    logger.info("Preparando dataset...")
    dataset = finetuning_service.prepare_sft_dataset(dataset_path)
    
    logger.info(f"Dataset: {len(dataset)} exemplos")
    
    # Treina
    logger.info("Iniciando treinamento...")
    model_path = finetuning_service.train_with_lora(
        dataset=dataset,
        output_dir=output_dir,
        num_epochs=num_epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    logger.info("=" * 60)
    logger.info("✅ TREINAMENTO CONCLUÍDO!")
    logger.info(f"Modelo salvo em: {model_path}")
    logger.info("=" * 60)
    
    return model_path


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Fine-tuning Supervisionado (SFT)")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Caminho do dataset JSON (se não fornecido, usa conversas do banco)"
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="meta-llama/Llama-3.1-8B-Instruct",
        help="Modelo base (HuggingFace)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/finetuned/jonh-ft-v1",
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
        default=2e-4,
        help="Taxa de aprendizado"
    )
    parser.add_argument(
        "--min-quality",
        type=float,
        default=0.7,
        help="Score mínimo de qualidade (quando usa banco de dados)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limite de exemplos (quando usa banco de dados)"
    )
    
    args = parser.parse_args()
    
    # Determina dataset
    if args.dataset:
        dataset_path = args.dataset
        if not Path(dataset_path).exists():
            logger.error(f"Dataset não encontrado: {dataset_path}")
            return
    else:
        # Usa conversas do banco de dados
        logger.info("Usando conversas do banco de dados...")
        db_path = Path(__file__).parent.parent.parent / "data" / "jonh_assistant.db"
        database = Database(db_path=str(db_path))
        await database.connect()
        
        dataset_path = await prepare_dataset_from_conversations(
            database=database,
            output_path="data/training/sft_dataset.json",
            min_quality=args.min_quality,
            limit=args.limit
        )
        
        await database.close()
    
    # Verifica se dataset tem dados
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not data:
        logger.error("Dataset vazio! Não é possível treinar.")
        return
    
    logger.info(f"Dataset: {len(data)} exemplos")
    
    if len(data) < 10:
        logger.warning("⚠️  Dataset muito pequeno (< 10 exemplos). Treinamento pode não ser efetivo.")
        response = input("Continuar mesmo assim? (s/N): ")
        if response.lower() != "s":
            logger.info("Treinamento cancelado.")
            return
    
    # Treina
    try:
        train_model(
            dataset_path=dataset_path,
            base_model=args.base_model,
            output_dir=args.output_dir,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )
    except KeyboardInterrupt:
        logger.warning("Treinamento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante treinamento: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

