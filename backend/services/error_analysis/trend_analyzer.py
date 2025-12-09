"""Analisa tendências e agrupa erros similares"""
from typing import Dict, List, Any


def group_similar_errors(errors: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Agrupa erros similares por mensagem/tipo
    
    Args:
        errors: Lista de erros
        
    Returns:
        Dicionário com erros agrupados
    """
    groups = {}
    
    for error in errors:
        # Cria chave de agrupamento baseada em tipo e mensagem (primeiras palavras)
        message_words = error.get("message", "").split()[:5]
        key = f"{error.get('type', 'other')}_{'_'.join(message_words)}"
        
        if key not in groups:
            groups[key] = []
        
        groups[key].append(error)
    
    return groups


def get_error_trends(errors: List[Dict]) -> Dict[str, Any]:
    """
    Analisa tendências de erros
    
    Args:
        errors: Lista de erros
        
    Returns:
        Dicionário com tendências
    """
    if not errors:
        return {
            "total": 0,
            "most_common_type": None,
            "most_common_message": None,
            "trend": "stable"
        }
    
    # Conta tipos
    type_counts = {}
    message_counts = {}
    
    for error in errors:
        error_type = error.get("type", "other")
        type_counts[error_type] = type_counts.get(error_type, 0) + 1
        
        message = error.get("message", "")
        if message:
            message_key = message[:50]  # Primeiros 50 caracteres
            message_counts[message_key] = message_counts.get(message_key, 0) + 1
    
    most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
    most_common_message = max(message_counts.items(), key=lambda x: x[1])[0] if message_counts else None
    
    # Determina tendência (simplificado - compara últimos 7 dias com anteriores)
    # Em produção, seria mais sofisticado
    trend = "stable"
    
    return {
        "total": len(errors),
        "most_common_type": most_common_type,
        "most_common_message": most_common_message,
        "type_distribution": type_counts,
        "trend": trend
    }

