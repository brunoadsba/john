"""
Preparação de datasets para fine-tuning
"""
import json
from typing import List, Dict, Optional
from loguru import logger

try:
    from datasets import Dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    logger.warning("datasets não disponível")


def prepare_sft_dataset_core(
    dataset_path: str,
    output_path: Optional[str] = None
) -> Dataset:
    """
    Prepara dataset no formato Alpaca/Instruct para fine-tuning
    
    Args:
        dataset_path: Caminho do arquivo JSON com dataset
        output_path: Caminho opcional para salvar dataset processado
        
    Returns:
        Dataset processado no formato HuggingFace
    """
    if not DATASETS_AVAILABLE:
        raise ImportError("datasets é necessário")
    
    logger.info(f"Preparando dataset de: {dataset_path}")
    
    # Carrega dataset
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not data:
        raise ValueError("Dataset vazio")
    
    # Formata para o modelo
    formatted_data = []
    for item in data:
        instruction = item.get("instruction", "")
        input_text = item.get("input", "")
        output = item.get("output", "")
        
        # Formata prompt no estilo Llama 3.1
        if input_text:
            prompt = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                f"{instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
                f"{input_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                f"{output}<|eot_id|>"
            )
        else:
            prompt = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                f"{instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
                f"{output}<|eot_id|>"
            )
        
        formatted_data.append({"text": prompt})
    
    # Cria dataset HuggingFace
    dataset = Dataset.from_list(formatted_data)
    
    logger.info(f"Dataset preparado: {len(dataset)} exemplos")
    
    # Salva se especificado
    if output_path:
        dataset.save_to_disk(output_path)
        logger.info(f"Dataset salvo em: {output_path}")
    
    return dataset

