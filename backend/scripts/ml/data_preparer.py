"""
Preparação de dados para treinamento RLHF
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from backend.services.feedback_service import FeedbackService
from backend.database.database import Database


async def prepare_preferences_from_feedback(
    database: Database,
    min_rating: int = 3,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Prepara preferências a partir de feedback do banco de dados
    
    Args:
        database: Instância do banco de dados
        min_rating: Rating mínimo para considerar feedback positivo
        limit: Limite de preferências
        
    Returns:
        Lista de preferências formatadas
    """
    logger.info("Preparando preferências a partir de feedback...")
    
    feedback_service = FeedbackService(database)
    
    # Obtém conversas com feedback
    conversations = await feedback_service.list_conversations(limit=limit or 1000)
    
    preferences = []
    for conv in conversations:
        # Obtém feedback associado
        feedback_list = await database.list_feedback(
            conversation_id=conv["id"],
            limit=1
        )
        
        if not feedback_list:
            continue
        
        feedback = feedback_list[0]
        rating = feedback.get("rating", 0)
        
        # Converte rating para preferência
        # Assumindo que temos múltiplas respostas ou podemos gerar candidatas
        if rating >= min_rating:
            # Para simplificar, usamos a resposta atual como "preferida"
            # Em produção, precisaríamos de comparações A/B reais
            preference = {
                "instruction": conv["user_input"],
                "response_a": conv["assistant_response"],
                "response_b": "",  # Em produção, seria outra resposta candidata
                "preferred": "a",
                "timestamp": conv["timestamp"]
            }
            preferences.append(preference)
    
    logger.info(f"Preparadas {len(preferences)} preferências")
    return preferences


async def prepare_reward_training_data(
    database: Database,
    min_rating: int = 1,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Prepara dados de treinamento para modelo de recompensa
    
    Args:
        database: Instância do banco de dados
        min_rating: Rating mínimo para incluir
        limit: Limite de exemplos
        
    Returns:
        Lista de exemplos no formato (instruction, response, reward)
    """
    logger.info("Preparando dados para modelo de recompensa...")
    
    feedback_service = FeedbackService(database)
    
    # Obtém conversas com feedback
    conversations = await feedback_service.list_conversations(limit=limit or 1000)
    
    training_data = []
    for conv in conversations:
        # Obtém feedback associado
        feedback_list = await database.list_feedback(
            conversation_id=conv["id"],
            limit=1
        )
        
        if not feedback_list:
            continue
        
        feedback = feedback_list[0]
        rating = feedback.get("rating", 0)
        
        # Converte rating para score de recompensa (0.0 a 1.0)
        # Assumindo rating de 1-5, normaliza para 0-1
        reward = (rating - 1) / 4.0 if rating >= min_rating else 0.0
        
        training_example = {
            "instruction": conv["user_input"],
            "response": conv["assistant_response"],
            "reward": reward
        }
        training_data.append(training_example)
    
    logger.info(f"Preparados {len(training_data)} exemplos para treinamento do modelo de recompensa")
    return training_data

