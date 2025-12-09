"""
Lógica de predição do modelo de recompensa
"""
from typing import List, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from loguru import logger


def predict_reward_batch(
    model,
    tokenizer,
    instructions: List[str],
    responses: List[str],
    batch_size: int = 32
) -> List[float]:
    """
    Prediz recompensas para um batch de pares instrução-resposta
    
    Args:
        model: Modelo de recompensa carregado
        tokenizer: Tokenizer carregado
        instructions: Lista de instruções
        responses: Lista de respostas
        batch_size: Tamanho do batch para processamento
        
    Returns:
        Lista de scores de recompensa (0-1)
    """
    model.eval()
    scores = []
    
    # Processa em batches
    for i in range(0, len(instructions), batch_size):
        batch_instructions = instructions[i:i + batch_size]
        batch_responses = responses[i:i + batch_size]
        
        # Combina instrução + resposta
        batch_texts = [
            f"{inst} {resp}" for inst, resp in zip(batch_instructions, batch_responses)
        ]
        
        # Tokeniza
        encodings = tokenizer(
            batch_texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Move para o mesmo device do modelo
        device = next(model.parameters()).device
        input_ids = encodings["input_ids"].to(device)
        attention_mask = encodings["attention_mask"].to(device)
        
        # Prediz
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            # Extrai logits e aplica sigmoid para obter scores 0-1
            logits = outputs.logits.squeeze(-1)
            batch_scores = torch.sigmoid(logits).cpu().tolist()
        
        scores.extend(batch_scores)
    
    return scores


def load_reward_model(model_path: str) -> Tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """
    Carrega modelo de recompensa e tokenizer
    
    Args:
        model_path: Caminho para o modelo
        
    Returns:
        Tupla (modelo, tokenizer)
    """
    try:
        logger.info(f"Carregando modelo de recompensa de: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.eval()
        logger.info("✅ Modelo de recompensa carregado com sucesso")
        return model, tokenizer
    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo de recompensa: {e}")
        raise

