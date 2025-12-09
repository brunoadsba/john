"""
Geração de respostas candidatas para RLHF
"""
from typing import List
from loguru import logger


def generate_candidates_core(
    model,
    tokenizer,
    instruction: str,
    num_candidates: int = 4,
    temperature: float = 0.8,
    max_length: int = 256
) -> List[str]:
    """
    Gera múltiplas respostas candidatas para uma instrução
    
    Args:
        model: Modelo carregado
        tokenizer: Tokenizer carregado
        instruction: Pergunta/instrução do usuário
        num_candidates: Número de respostas a gerar
        temperature: Temperatura para geração (maior = mais diverso)
        max_length: Comprimento máximo da resposta
        
    Returns:
        Lista de respostas candidatas
    """
    if not model or not tokenizer:
        raise ValueError("Modelo e tokenizer devem estar carregados")
    
    candidates = []
    
    # Prepara prompt
    prompt = f"Instrução: {instruction}\nResposta:"
    
    for i in range(num_candidates):
        try:
            # Tokeniza
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            # Gera resposta
            with tokenizer.device_map if hasattr(tokenizer, 'device_map') else None:
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    num_return_sequences=1,
                    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
                )
            
            # Decodifica
            response = tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            candidates.append(response.strip())
            logger.debug(f"Candidata {i+1}/{num_candidates} gerada")
            
        except Exception as e:
            logger.error(f"Erro ao gerar candidata {i+1}: {e}")
            # Adiciona resposta vazia em caso de erro
            candidates.append("")
    
    logger.info(f"✅ {len(candidates)} candidatas geradas para: '{instruction[:50]}...'")
    return candidates

