"""
Identificação de padrões em clusters de intenções
"""
from typing import List, Dict, Set, Tuple
from collections import Counter
from loguru import logger
import re


def identify_intent_patterns(
    clusters: List[Dict[str, any]]
) -> List[Dict[str, any]]:
    """
    Identifica padrões comuns por cluster
    
    Args:
        clusters: Lista de clusters retornados por cluster_intents()
        
    Returns:
        Lista de dicionários com padrões identificados por cluster
    """
    logger.info("Identificando padrões nos clusters...")
    
    patterns = []
    
    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        texts = cluster["texts"]
        
        if not texts:
            continue
        
        # Encontra palavras-chave comuns
        keywords = _extract_keywords(texts)
        
        # Encontra frases comuns
        common_phrases = _find_common_phrases(texts)
        
        # Identifica estrutura de pergunta
        question_types = _identify_question_types(texts)
        
        patterns.append({
            "cluster_id": cluster_id,
            "size": len(texts),
            "keywords": keywords[:10],  # Top 10
            "common_phrases": common_phrases[:5],  # Top 5
            "question_types": question_types,
            "examples": texts[:3]  # Primeiros 3 exemplos
        })
    
    logger.info(f"✅ Padrões identificados para {len(patterns)} clusters")
    return patterns


def _extract_keywords(texts: List[str], min_frequency: int = 2) -> List[Tuple[str, int]]:
    """
    Extrai palavras-chave mais frequentes
    
    Args:
        texts: Lista de textos
        min_frequency: Frequência mínima para incluir
        
    Returns:
        Lista de tuplas (palavra, frequência) ordenada por frequência
    """
    # Palavras de parada em português (básico)
    stopwords = {
        "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
        "em", "no", "na", "nos", "nas", "para", "com", "por", "que", "qual",
        "quais", "como", "quando", "onde", "porque", "é", "são", "ser", "estar",
        "ter", "tem", "foi", "fazer", "faz", "pode", "pode", "poder", "você",
        "seu", "sua", "seus", "suas", "me", "te", "nos", "vos", "lhe", "lhes"
    }
    
    # Tokeniza e conta palavras
    word_counter = Counter()
    
    for text in texts:
        # Remove pontuação e converte para minúsculas
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtra stopwords e palavras muito curtas
        filtered_words = [
            w for w in words 
            if len(w) > 2 and w not in stopwords
        ]
        
        word_counter.update(filtered_words)
    
    # Filtra por frequência mínima
    keywords = [
        (word, count) 
        for word, count in word_counter.items() 
        if count >= min_frequency
    ]
    
    # Ordena por frequência
    keywords.sort(key=lambda x: x[1], reverse=True)
    
    return keywords


def _find_common_phrases(texts: List[str], min_length: int = 2, max_length: int = 4) -> List[Tuple[str, int]]:
    """
    Encontra frases comuns (n-grams)
    
    Args:
        texts: Lista de textos
        min_length: Tamanho mínimo do n-gram
        max_length: Tamanho máximo do n-gram
        
    Returns:
        Lista de tuplas (frase, frequência) ordenada por frequência
    """
    phrase_counter = Counter()
    
    for text in texts:
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Gera n-grams
        for n in range(min_length, min(max_length + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i+n])
                if len(phrase) > 5:  # Filtra frases muito curtas
                    phrase_counter[phrase] += 1
    
    # Filtra por frequência mínima
    common_phrases = [
        (phrase, count)
        for phrase, count in phrase_counter.items()
        if count >= 2
    ]
    
    # Ordena por frequência
    common_phrases.sort(key=lambda x: x[1], reverse=True)
    
    return common_phrases


def _identify_question_types(texts: List[str]) -> Dict[str, int]:
    """
    Identifica tipos de pergunta (quem, o que, como, etc.)
    
    Args:
        texts: Lista de textos
        
    Returns:
        Dicionário com contagem de cada tipo
    """
    question_patterns = {
        "o_que": [r"o\s+que", r"que\s+é", r"o\s+que\s+é"],
        "como": [r"como\s+", r"como\s+fazer", r"como\s+funciona"],
        "qual": [r"qual\s+", r"quais\s+", r"qual\s+é"],
        "quando": [r"quando\s+", r"em\s+que\s+momento"],
        "onde": [r"onde\s+", r"em\s+que\s+lugar"],
        "porque": [r"por\s+que", r"porquê", r"por\s+quê", r"por\s+qual\s+motivo"],
        "quem": [r"quem\s+", r"qual\s+pessoa"],
        "imperativo": [r"^[a-záàâãéêíóôõúç]+\s+", r"^faça", r"^crie", r"^mostre"]
    }
    
    type_counts = {key: 0 for key in question_patterns.keys()}
    
    for text in texts:
        text_lower = text.lower()
        for q_type, patterns in question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    type_counts[q_type] += 1
                    break
    
    return type_counts

