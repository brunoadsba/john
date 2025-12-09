"""
Rotas de analytics e análise de clusters
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.services.intent_clustering_service import IntentClusteringService
from backend.services.pattern_analysis_service import PatternAnalysisService
from backend.services.embedding_service import EmbeddingService
from backend.database.database import Database

router = APIRouter(tags=["analytics"])

# Instâncias dos serviços (serão inicializadas no startup)
clustering_service: Optional[IntentClusteringService] = None
pattern_service: Optional[PatternAnalysisService] = None


def init_analytics_services(
    database: Database,
    embedding_service: EmbeddingService
):
    """Inicializa serviços de analytics"""
    global clustering_service, pattern_service
    clustering_service = IntentClusteringService(database, embedding_service)
    pattern_service = PatternAnalysisService()
    logger.info("✅ Serviços de analytics inicializados")


@router.get("/analytics/intents")
async def get_intent_clusters(
    method: str = "kmeans",
    n_clusters: Optional[int] = None,
    limit: Optional[int] = None
):
    """
    Lista clusters de intenções
    
    Args:
        method: Método de clustering ('kmeans' ou 'dbscan')
        n_clusters: Número de clusters (apenas para K-Means)
        limit: Limite de conversas a processar
        
    Returns:
        Lista de clusters com padrões identificados
    """
    if not clustering_service:
        raise HTTPException(status_code=503, detail="Serviço de clustering não inicializado")
    
    try:
        # Executa clustering
        clusters = await clustering_service.cluster_intents(
            method=method,
            n_clusters=n_clusters,
            limit=limit
        )
        
        # Identifica padrões
        patterns = await clustering_service.identify_intent_patterns(clusters)
        
        return {
            "clusters": clusters,
            "patterns": patterns,
            "total_clusters": len(clusters)
        }
    except Exception as e:
        logger.error(f"Erro ao obter clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/patterns")
async def get_patterns():
    """
    Retorna padrões identificados nos clusters
    
    Returns:
        Padrões e sugestões de melhoria
    """
    if not clustering_service or not pattern_service:
        raise HTTPException(status_code=503, detail="Serviços de analytics não inicializados")
    
    try:
        # Carrega clusters do banco
        clusters = await clustering_service._load_clusters_from_db()
        
        if not clusters:
            return {
                "patterns": [],
                "suggestions": [],
                "note": "Nenhum cluster encontrado. Execute /analytics/intents primeiro."
            }
        
        # Identifica padrões
        patterns = await clustering_service.identify_intent_patterns(clusters)
        
        # Encontra frases comuns
        common_phrases = pattern_service.find_common_phrases(clusters)
        
        # Gera sugestões
        suggestions = pattern_service.suggest_improvements(clusters)
        
        return {
            "patterns": patterns,
            "common_phrases": common_phrases,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Erro ao obter padrões: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/stats")
async def get_analytics_stats():
    """
    Estatísticas gerais de analytics
    
    Returns:
        Estatísticas de clusters e qualidade
    """
    if not clustering_service or not pattern_service:
        raise HTTPException(status_code=503, detail="Serviços de analytics não inicializados")
    
    try:
        # Carrega clusters do banco
        clusters = await clustering_service._load_clusters_from_db()
        
        # Analisa qualidade
        quality = pattern_service.analyze_cluster_quality(clusters)
        
        # Conta tipos de pergunta
        patterns = await clustering_service.identify_intent_patterns(clusters)
        question_types_count = {}
        for pattern in patterns:
            for q_type, count in pattern.get("question_types", {}).items():
                question_types_count[q_type] = question_types_count.get(q_type, 0) + count
        
        return {
            "clusters": quality,
            "question_types": question_types_count,
            "total_patterns": len(patterns)
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/cluster/{cluster_id}/optimize")
async def optimize_cluster(cluster_id: int):
    """
    Otimiza respostas para um cluster específico
    
    Args:
        cluster_id: ID do cluster
        
    Returns:
        Sugestões de otimização
    """
    if not clustering_service:
        raise HTTPException(status_code=503, detail="Serviço de clustering não inicializado")
    
    try:
        optimizations = await clustering_service.optimize_responses_by_cluster(cluster_id)
        return optimizations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao otimizar cluster: {e}")
        raise HTTPException(status_code=500, detail=str(e))

