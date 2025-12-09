"""
Serviço de análise de padrões em clusters de intenções
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from backend.services.ml.clustering.pattern_identifier import identify_intent_patterns


class PatternAnalysisService:
    """Analisa padrões em clusters para otimização"""
    
    def __init__(self):
        """Inicializa serviço de análise de padrões"""
        logger.info("PatternAnalysisService inicializado")
    
    def analyze_cluster_quality(
        self,
        clusters: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Avalia qualidade dos clusters
        
        Args:
            clusters: Lista de clusters
            
        Returns:
            Dicionário com métricas de qualidade
        """
        if not clusters:
            return {
                "total_clusters": 0,
                "average_size": 0,
                "quality_score": 0.0,
                "notes": "Nenhum cluster para analisar"
            }
        
        total_items = sum(len(c.get("texts", [])) for c in clusters)
        cluster_sizes = [len(c.get("texts", [])) for c in clusters]
        
        # Calcula métricas
        average_size = total_items / len(clusters) if clusters else 0
        min_size = min(cluster_sizes) if cluster_sizes else 0
        max_size = max(cluster_sizes) if cluster_sizes else 0
        
        # Score de qualidade baseado em distribuição
        # Clusters muito desbalanceados = qualidade menor
        size_variance = sum((s - average_size) ** 2 for s in cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0
        quality_score = max(0.0, 1.0 - (size_variance / (average_size ** 2 + 1)))
        
        return {
            "total_clusters": len(clusters),
            "total_items": total_items,
            "average_size": round(average_size, 2),
            "min_size": min_size,
            "max_size": max_size,
            "size_variance": round(size_variance, 2),
            "quality_score": round(quality_score, 3),
            "notes": "Score próximo de 1.0 indica clusters bem balanceados"
        }
    
    def find_common_phrases(
        self,
        clusters: List[Dict[str, any]],
        top_n: int = 10
    ) -> Dict[int, List[tuple]]:
        """
        Encontra frases comuns por cluster
        
        Args:
            clusters: Lista de clusters
            top_n: Número de frases mais comuns a retornar
            
        Returns:
            Dicionário {cluster_id: [(frase, frequência), ...]}
        """
        patterns = identify_intent_patterns(clusters)
        
        common_phrases_by_cluster = {}
        for pattern in patterns:
            cluster_id = pattern["cluster_id"]
            common_phrases_by_cluster[cluster_id] = pattern.get("common_phrases", [])[:top_n]
        
        return common_phrases_by_cluster
    
    def suggest_improvements(
        self,
        clusters: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Sugere melhorias baseadas em padrões identificados
        
        Args:
            clusters: Lista de clusters
            
        Returns:
            Lista de sugestões de melhoria
        """
        if not clusters:
            return []
        
        suggestions = []
        patterns = identify_intent_patterns(clusters)
        quality = self.analyze_cluster_quality(clusters)
        
        # Sugestão 1: Clusters muito pequenos
        small_clusters = [
            p for p in patterns 
            if p["size"] < 3
        ]
        if small_clusters:
            suggestions.append({
                "type": "merge_small_clusters",
                "priority": "medium",
                "message": f"{len(small_clusters)} clusters muito pequenos (< 3 itens). Considere mesclar ou aumentar min_samples.",
                "affected_clusters": [p["cluster_id"] for p in small_clusters]
            })
        
        # Sugestão 2: Clusters muito grandes
        large_clusters = [
            p for p in patterns 
            if p["size"] > quality["average_size"] * 2
        ]
        if large_clusters:
            suggestions.append({
                "type": "split_large_clusters",
                "priority": "low",
                "message": f"{len(large_clusters)} clusters muito grandes. Considere aumentar número de clusters ou usar DBSCAN.",
                "affected_clusters": [p["cluster_id"] for p in large_clusters]
            })
        
        # Sugestão 3: Baixa qualidade geral
        if quality["quality_score"] < 0.5:
            suggestions.append({
                "type": "improve_clustering",
                "priority": "high",
                "message": f"Qualidade dos clusters baixa (score: {quality['quality_score']:.2f}). Tente ajustar parâmetros de clustering.",
                "suggested_actions": [
                    "Ajustar número de clusters (n_clusters)",
                    "Experimentar DBSCAN com diferentes eps",
                    "Aumentar min_samples para DBSCAN"
                ]
            })
        
        # Sugestão 4: Palavras-chave muito genéricas
        for pattern in patterns:
            keywords = pattern.get("keywords", [])
            if keywords:
                top_keyword = keywords[0][0] if keywords else ""
                # Palavras muito genéricas
                generic_words = {"fazer", "ter", "ser", "estar", "poder", "querer"}
                if top_keyword in generic_words:
                    suggestions.append({
                        "type": "generic_keywords",
                        "priority": "low",
                        "message": f"Cluster {pattern['cluster_id']} tem palavras-chave muito genéricas. Considere filtrar stopwords mais agressivamente.",
                        "cluster_id": pattern["cluster_id"]
                    })
        
        return suggestions

