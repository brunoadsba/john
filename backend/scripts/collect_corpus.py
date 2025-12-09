#!/usr/bin/env python3
"""
Script para coletar e processar corpus de texto em português brasileiro
"""
import sys
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from backend.services.pretraining_service import PretrainingService
from backend.config.settings import settings


def main():
    """Coleta corpus de texto em português brasileiro"""
    logger.info("Iniciando coleta de corpus...")
    
    # Configurações
    output_path = settings.pretraining_corpus_path
    sources = ["conversations"]  # Por enquanto, apenas conversas do Jonh
    
    try:
        # Inicializa serviço
        service = PretrainingService()
        
        # Coleta corpus
        corpus_path = service.collect_corpus(
            output_path=output_path,
            sources=sources,
            min_length=50,
            max_length=2048
        )
        
        logger.info(f"✅ Corpus coletado e salvo em: {corpus_path}")
        
        # Valida qualidade
        corpus_file = Path(corpus_path)
        if corpus_file.exists():
            size = corpus_file.stat().st_size
            text = corpus_file.read_text(encoding="utf-8")
            lines = len(text.split("\n\n"))
            
            logger.info(f"Estatísticas do corpus:")
            logger.info(f"  - Tamanho: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
            logger.info(f"  - Textos: {lines:,}")
            logger.info(f"  - Caracteres: {len(text):,}")
            
            if size < 1024:  # Menos de 1KB
                logger.warning("⚠️ Corpus muito pequeno. Considere coletar mais dados.")
        else:
            logger.error("❌ Arquivo de corpus não encontrado após coleta")
            return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Erro ao coletar corpus: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

