"""
Coleta de corpus de texto em português brasileiro
"""
from pathlib import Path
from typing import List, Optional
from loguru import logger


def collect_corpus_core(
    output_path: str,
    sources: Optional[List[str]] = None,
    min_length: int = 50,
    max_length: int = 2048
) -> str:
    """
    Coleta corpus de texto em português brasileiro de múltiplas fontes
    
    Args:
        output_path: Caminho para salvar o corpus
        sources: Lista de fontes (opcional, usa padrão se None)
        min_length: Tamanho mínimo de texto (caracteres)
        max_length: Tamanho máximo de texto (caracteres)
        
    Returns:
        Caminho do arquivo salvo
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    if sources is None:
        sources = [
            "conversations",  # Conversas do Jonh (anonimizadas)
            "wikipedia",      # Wikipedia PT-BR (se disponível)
            "common_crawl",   # Common Crawl PT-BR (se disponível)
        ]
    
    logger.info(f"Coletando corpus de {len(sources)} fontes...")
    
    collected_texts: List[str] = []
    
    # Coleta de conversas do Jonh (anonimizadas)
    if "conversations" in sources:
        try:
            from backend.database.database import Database
            db = Database()
            
            conversations = db.db.execute(
                "SELECT user_input, assistant_response FROM conversations "
                "WHERE timestamp > datetime('now', '-30 days') "
                "LIMIT 10000"
            ).fetchall()
            
            for user_input, assistant_response in conversations:
                # Anonimiza e combina
                text = f"{user_input}\n{assistant_response}"
                if min_length <= len(text) <= max_length:
                    collected_texts.append(text)
            
            logger.info(f"Coletadas {len(conversations)} conversas")
        except Exception as e:
            logger.warning(f"Erro ao coletar conversas: {e}")
    
    # Outras fontes podem ser adicionadas aqui
    # Por enquanto, foca em conversas do Jonh
    
    if not collected_texts:
        logger.warning("Nenhum texto coletado. Criando corpus vazio.")
        output.write_text("", encoding="utf-8")
        return str(output)
    
    # Salva corpus
    corpus_text = "\n\n".join(collected_texts)
    output.write_text(corpus_text, encoding="utf-8")
    
    logger.info(f"Corpus salvo em {output_path} ({len(collected_texts)} textos, {len(corpus_text)} caracteres)")
    
    return str(output)

