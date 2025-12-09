"""
Preparação de dados para pré-treinamento
"""
from pathlib import Path
from typing import List, Optional
from loguru import logger

try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    logger.warning("datasets não disponível - instale com: pip install datasets")


def prepare_pretraining_data_core(
    corpus_path: str,
    tokenizer_name: str = "meta-llama/Llama-3.1-8B-Instruct",
    chunk_size: int = 2048,
    output_path: Optional[str] = None
) -> Optional[Dataset]:
    """
    Prepara dados no formato de pré-treinamento (tokenização e chunking)
    
    Args:
        corpus_path: Caminho para o corpus de texto
        tokenizer_name: Nome do tokenizer (HuggingFace)
        chunk_size: Tamanho dos chunks (tokens)
        output_path: Caminho para salvar dataset preparado (opcional)
        
    Returns:
        Dataset preparado ou None se erro
    """
    if not DATASETS_AVAILABLE:
        logger.error("datasets não disponível")
        return None
    
    corpus_file = Path(corpus_path)
    if not corpus_file.exists():
        logger.error(f"Corpus não encontrado: {corpus_path}")
        return None
    
    logger.info(f"Preparando dados de pré-treinamento de {corpus_path}...")
    
    try:
        # Carrega tokenizer
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Lê corpus
        corpus_text = corpus_file.read_text(encoding="utf-8")
        
        # Divide em chunks
        texts = corpus_text.split("\n\n")
        chunks: List[str] = []
        
        for text in texts:
            if not text.strip():
                continue
            
            # Tokeniza e divide em chunks
            tokens = tokenizer.encode(text, add_special_tokens=False)
            
            for i in range(0, len(tokens), chunk_size):
                chunk_tokens = tokens[i:i + chunk_size]
                if len(chunk_tokens) >= 100:  # Mínimo de tokens
                    chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                    chunks.append(chunk_text)
        
        if not chunks:
            logger.warning("Nenhum chunk válido gerado")
            return None
        
        logger.info(f"Gerados {len(chunks)} chunks de pré-treinamento")
        
        # Cria dataset
        dataset = Dataset.from_dict({"text": chunks})
        
        # Salva se especificado
        if output_path:
            dataset.save_to_disk(output_path)
            logger.info(f"Dataset salvo em {output_path}")
        
        return dataset
    
    except Exception as e:
        logger.error(f"Erro ao preparar dados: {e}")
        return None

