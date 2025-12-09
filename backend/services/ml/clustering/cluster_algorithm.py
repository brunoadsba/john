"""
Algoritmos de clustering para intenções
"""
from typing import List, Dict, Tuple, Optional
from loguru import logger

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.metrics import silhouette_score
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn não disponível. Clustering será desabilitado.")


def cluster_intents(
    embeddings_data: List[Dict],
    method: str = "kmeans",
    n_clusters: Optional[int] = None,
    eps: float = 0.5,
    min_samples: int = 5
) -> List[Dict[str, any]]:
    """
    Agrupa intenções similares usando K-Means ou DBSCAN
    
    Args:
        embeddings_data: Lista de dicionários com 'text', 'embedding', 'conversation_id'
        method: Método de clustering ('kmeans' ou 'dbscan')
        n_clusters: Número de clusters (apenas para K-Means, auto se None)
        eps: Distância máxima para DBSCAN
        min_samples: Mínimo de amostras por cluster (DBSCAN)
        
    Returns:
        Lista de dicionários com 'cluster_id', 'texts', 'embeddings', 'conversation_ids'
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn é necessário para clustering")
    
    if not embeddings_data:
        logger.warning("Nenhum dado para clusterizar")
        return []
    
    logger.info(f"Clusterizando {len(embeddings_data)} intenções usando {method}...")
    
    # Extrai embeddings como array numpy
    embeddings = np.array([item["embedding"] for item in embeddings_data])
    
    # Determina número de clusters automaticamente se necessário
    if method == "kmeans" and n_clusters is None:
        n_clusters = _estimate_optimal_clusters(embeddings)
        logger.info(f"Número ótimo de clusters estimado: {n_clusters}")
    
    # Executa clustering
    if method == "kmeans":
        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = clusterer.fit_predict(embeddings)
    elif method == "dbscan":
        clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        labels = clusterer.fit_predict(embeddings)
    else:
        raise ValueError(f"Método de clustering inválido: {method}")
    
    # Agrupa resultados por cluster
    clusters = {}
    for i, label in enumerate(labels):
        # DBSCAN pode retornar -1 para outliers
        cluster_id = int(label) if label >= 0 else -1
        
        if cluster_id not in clusters:
            clusters[cluster_id] = {
                "cluster_id": cluster_id,
                "texts": [],
                "embeddings": [],
                "conversation_ids": []
            }
        
        clusters[cluster_id]["texts"].append(embeddings_data[i]["text"])
        clusters[cluster_id]["embeddings"].append(embeddings_data[i]["embedding"])
        clusters[cluster_id]["conversation_ids"].append(embeddings_data[i]["conversation_id"])
    
    # Converte para lista
    cluster_list = list(clusters.values())
    
    # Calcula métricas de qualidade
    if method == "kmeans" and len(cluster_list) > 1:
        try:
            silhouette = silhouette_score(embeddings, labels)
            logger.info(f"Silhouette score: {silhouette:.3f}")
        except Exception as e:
            logger.warning(f"Erro ao calcular silhouette score: {e}")
    
    logger.info(f"✅ {len(cluster_list)} clusters criados")
    return cluster_list


def _estimate_optimal_clusters(embeddings: np.ndarray, max_k: int = 10) -> int:
    """
    Estima número ótimo de clusters usando método do cotovelo
    
    Args:
        embeddings: Array de embeddings
        max_k: Número máximo de clusters a testar
        
    Returns:
        Número estimado de clusters
    """
    if len(embeddings) < 4:
        return max(2, len(embeddings))
    
    max_k = min(max_k, len(embeddings) // 2)
    if max_k < 2:
        return 2
    
    inertias = []
    k_range = range(2, max_k + 1)
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        inertias.append(kmeans.inertia_)
    
    # Método do cotovelo simplificado: escolhe k que minimiza redução de inércia
    if len(inertias) < 2:
        return 2
    
    # Calcula reduções
    reductions = [inertias[i] - inertias[i+1] for i in range(len(inertias) - 1)]
    
    # Encontra maior redução (cotovelo)
    if reductions:
        optimal_k_idx = reductions.index(max(reductions))
        optimal_k = k_range[optimal_k_idx]
    else:
        optimal_k = 2
    
    return optimal_k

