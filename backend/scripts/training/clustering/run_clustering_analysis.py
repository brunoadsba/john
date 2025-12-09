#!/usr/bin/env python3
"""
Executa clustering incremental de intenções
"""
import sys
import os
import argparse
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.services.intent_clustering_service import IntentClusteringService
from backend.services.embedding_service import EmbeddingService
from backend.database.database import Database
from backend.scripts.training.utils.training_config import TrainingConfig
from backend.scripts.training.utils.status_manager import StatusManager
from backend.scripts.training.validation.check_resources import validate_resources
import asyncio


async def run_clustering(
    database: Database,
    status_manager: StatusManager,
    batch_size: int = 1000
):
    """Executa clustering incremental"""
    config = TrainingConfig.CLUSTERING_LIMITS
    
    logger.info("=" * 60)
    logger.info("CLUSTERING DE INTENÇÕES")
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
    status_manager.update_phase_status("clustering", "in_progress")
    
    try:
        # Inicializa serviços
        embedding_service = EmbeddingService()
        clustering_service = IntentClusteringService(
            database=database,
            embedding_service=embedding_service
        )
        
        # Busca conversas
        logger.info("Buscando conversas do banco de dados...")
        conversations = await database.list_conversations(limit=None)
        
        if len(conversations) < 100:
            logger.warning(f"⚠️  Poucas conversas: {len(conversations)} (recomendado: 100+)")
            response = input("Continuar mesmo assim? (s/N): ")
            if response.lower() != "s":
                sys.exit(0)
        
        # Processa em batches
        logger.info(f"Processando {len(conversations)} conversas em batches de {batch_size}...")
        
        total_clusters = 0
        for i in range(0, len(conversations), batch_size):
            batch = conversations[i:i + batch_size]
            logger.info(f"Processando batch {i // batch_size + 1} ({len(batch)} conversas)...")
            
            clusters = await clustering_service.cluster_intents(
                conversations=batch,
                min_samples=5,
                eps=0.3
            )
            
            total_clusters += len(clusters)
            logger.info(f"  → {len(clusters)} clusters identificados")
        
        # Identifica padrões
        logger.info("Identificando padrões nos clusters...")
        patterns = await clustering_service.identify_intent_patterns()
        
        # Atualiza status
        status_manager.update_phase_status(
            "clustering",
            "completed",
            total_clusters=total_clusters,
            total_conversations=len(conversations)
        )
        
        logger.info("=" * 60)
        logger.info("✅ CLUSTERING CONCLUÍDO!")
        logger.info(f"Total de clusters: {total_clusters}")
        logger.info(f"Total de conversas processadas: {len(conversations)}")
        logger.info("=" * 60)
        
        return total_clusters
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        status_manager.update_phase_status("clustering", "error", error=str(e))
        raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executa clustering de intenções")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Tamanho do batch para processamento (padrão: 1000)"
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
        await run_clustering(database, status_manager, args.batch_size)
        status_manager.calculate_progress()
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())

