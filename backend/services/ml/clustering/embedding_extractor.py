"""
Extração de embeddings para clustering de intenções
"""
from typing import List, Dict, Optional
from loguru import logger

from backend.services.embedding_service import EmbeddingService
from backend.database.database import Database


async def extract_intent_embeddings(
    database: Database,
    embedding_service: EmbeddingService,
    limit: Optional[int] = None,
    min_confidence: float = 0.0
) -> List[Dict[str, any]]:
    """
    Extrai embeddings de todas as perguntas do banco de dados
    
    Args:
        database: Instância do banco de dados
        embedding_service: Serviço de embeddings
        limit: Limite de conversas a processar
        min_confidence: Confiança mínima do feedback para incluir
        
    Returns:
        Lista de dicionários com 'text', 'embedding', 'conversation_id'
    """
    if not embedding_service.is_available():
        raise RuntimeError("Serviço de embeddings não está disponível")
    
    logger.info("Extraindo embeddings de intenções...")
    
    # Obtém conversas do banco
    conversations = await database.list_conversations(limit=limit)
    
    if not conversations:
        logger.warning("Nenhuma conversa encontrada para extrair embeddings")
        return []
    
    # Filtra por feedback se necessário
    texts_to_embed = []
    conversation_ids = []
    
    for conv in conversations:
        # Obtém feedback associado
        feedback_list = await database.list_feedback(
            conversation_id=conv["id"],
            limit=1
        )
        
        # Se min_confidence > 0, filtra por feedback
        if min_confidence > 0:
            if not feedback_list:
                continue
            feedback = feedback_list[0]
            rating = feedback.get("rating", 0)
            # Converte rating para confiança (assumindo escala 1-5)
            confidence = (rating - 1) / 4.0 if rating >= 1 else 0.0
            if confidence < min_confidence:
                continue
        
        texts_to_embed.append(conv["user_input"])
        conversation_ids.append(conv["id"])
    
    if not texts_to_embed:
        logger.warning("Nenhum texto para embeddar após filtros")
        return []
    
    logger.info(f"Gerando embeddings para {len(texts_to_embed)} textos...")
    
    # Gera embeddings
    embeddings = embedding_service.embed(texts_to_embed)
    
    # Combina resultados
    results = []
    for text, embedding, conv_id in zip(texts_to_embed, embeddings, conversation_ids):
        results.append({
            "text": text,
            "embedding": embedding,
            "conversation_id": conv_id
        })
    
    logger.info(f"✅ {len(results)} embeddings extraídos")
    return results

