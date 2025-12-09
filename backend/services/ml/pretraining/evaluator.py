"""
Avaliação de melhorias em português após pré-treinamento
"""
from pathlib import Path
from typing import Dict, Optional, List, Any
from loguru import logger

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers não disponível")


def evaluate_improvements_core(
    base_model_path: str,
    pretrained_model_path: str,
    test_prompts: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Avalia melhorias do modelo pré-treinado vs. base
    
    Args:
        base_model_path: Caminho do modelo base
        pretrained_model_path: Caminho do modelo pré-treinado
        test_prompts: Lista de prompts de teste (opcional)
        
    Returns:
        Métricas de avaliação ou None se erro
    """
    if not TRANSFORMERS_AVAILABLE:
        logger.error("transformers não disponível")
        return None
    
    if test_prompts is None:
        test_prompts = [
            "Olá, como você está?",
            "Explique o que é inteligência artificial.",
            "Conte uma piada em português.",
            "Qual é a capital do Brasil?",
        ]
    
    logger.info("Avaliando melhorias do modelo pré-treinado...")
    
    try:
        # Carrega modelos
        base_model = AutoModelForCausalLM.from_pretrained(base_model_path)
        base_tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        
        pretrained_model = AutoModelForCausalLM.from_pretrained(pretrained_model_path)
        pretrained_tokenizer = AutoTokenizer.from_pretrained(pretrained_model_path)
        
        results = {
            "test_prompts": len(test_prompts),
            "base_responses": [],
            "pretrained_responses": [],
        }
        
        # Gera respostas para cada prompt
        for prompt in test_prompts:
            # Modelo base
            base_inputs = base_tokenizer(prompt, return_tensors="pt")
            base_outputs = base_model.generate(
                **base_inputs,
                max_length=100,
                do_sample=True,
                temperature=0.7
            )
            base_response = base_tokenizer.decode(base_outputs[0], skip_special_tokens=True)
            results["base_responses"].append(base_response)
            
            # Modelo pré-treinado
            pretrained_inputs = pretrained_tokenizer(prompt, return_tensors="pt")
            pretrained_outputs = pretrained_model.generate(
                **pretrained_inputs,
                max_length=100,
                do_sample=True,
                temperature=0.7
            )
            pretrained_response = pretrained_tokenizer.decode(pretrained_outputs[0], skip_special_tokens=True)
            results["pretrained_responses"].append(pretrained_response)
        
        logger.info("Avaliação concluída")
        return results
    
    except Exception as e:
        logger.error(f"Erro ao avaliar melhorias: {e}")
        return None

