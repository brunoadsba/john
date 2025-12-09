"""
Serviço de clustering de intenções (aprendizado não supervisionado)
"""
from typing import List, Dict, Optional, Any
from loguru import logger

from backend.database.database import Database
from backend.services.embedding_service import EmbeddingService
from backend.services.ml.clustering import (
    extract_intent_embeddings,
    cluster_intents,
    identify_intent_patterns
)


class IntentClusteringService:
    """Gerencia clustering de intenções para otimização de respostas"""
    
    def __init__(
        self,
        database: Database,
        embedding_service: EmbeddingService
    ):
        """
        Inicializa serviço de clustering
        
        Args:
            database: Instância do banco de dados
            embedding_service: Serviço de embeddings
        """
        self.database = database
        self.embedding_service = embedding_service
        logger.info("IntentClusteringService inicializado")
    
    async def extract_intent_embeddings(
        self,
        limit: Optional[int] = None,
        min_confidence: float = 0.0
    ) -> List[Dict[str, any]]:
        """
        Extrai embeddings de todas as perguntas
        
        Args:
            limit: Limite de conversas a processar
            min_confidence: Confiança mínima do feedback para incluir
            
        Returns:
            Lista de dicionários com 'text', 'embedding', 'conversation_id'
        """
        return await extract_intent_embeddings(
            database=self.database,
            embedding_service=self.embedding_service,
            limit=limit,
            min_confidence=min_confidence
        )
    
    async def cluster_intents(
        self,
        embeddings_data: Optional[List[Dict]] = None,
        method: str = "kmeans",
        n_clusters: Optional[int] = None,
        eps: float = 0.5,
        min_samples: int = 5,
        limit: Optional[int] = None
    ) -> List[Dict[str, any]]:
        """
        Agrupa intenções similares usando K-Means ou DBSCAN
        
        Args:
            embeddings_data: Dados de embeddings (se None, extrai do banco)
            method: Método de clustering ('kmeans' ou 'dbscan')
            n_clusters: Número de clusters (apenas para K-Means)
            eps: Distância máxima para DBSCAN
            min_samples: Mínimo de amostras por cluster (DBSCAN)
            limit: Limite de conversas (se embeddings_data é None)
            
        Returns:
            Lista de clusters com 'cluster_id', 'texts', 'embeddings', 'conversation_ids'
        """
        # Extrai embeddings se não fornecidos
        if embeddings_data is None:
            embeddings_data = await self.extract_intent_embeddings(limit=limit)
        
        if not embeddings_data:
            logger.warning("Nenhum dado para clusterizar")
            return []
        
        # Executa clustering
        clusters = cluster_intents(
            embeddings_data=embeddings_data,
            method=method,
            n_clusters=n_clusters,
            eps=eps,
            min_samples=min_samples
        )
        
        # Salva clusters no banco
        await self._save_clusters_to_db(clusters)
        
        return clusters
    
    async def identify_intent_patterns(
        self,
        clusters: Optional[List[Dict]] = None
    ) -> List[Dict[str, any]]:
        """
        Identifica padrões comuns por cluster
        
        Args:
            clusters: Lista de clusters (se None, carrega do banco)
            
        Returns:
            Lista de dicionários com padrões identificados
        """
        if clusters is None:
            clusters = await self._load_clusters_from_db()
        
        if not clusters:
            logger.warning("Nenhum cluster disponível para análise")
            return []
        
        return identify_intent_patterns(clusters)
    
    async def optimize_responses_by_cluster(
        self,
        cluster_id: int,
        response_template: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Otimiza respostas para um cluster específico
        
        Args:
            cluster_id: ID do cluster
            response_template: Template de resposta (opcional)
            
        Returns:
            Dicionário com otimizações sugeridas
        """
        clusters = await self._load_clusters_from_db()
        
        # Encontra cluster
        cluster = next((c for c in clusters if c["cluster_id"] == cluster_id), None)
        
        if not cluster:
            raise ValueError(f"Cluster {cluster_id} não encontrado")
        
        # Identifica padrões do cluster
        patterns = identify_intent_patterns([cluster])
        
        if not patterns:
            return {"cluster_id": cluster_id, "optimizations": []}
        
        pattern = patterns[0]
        
        # Gera sugestões de otimização
        optimizations = []
        
        # Sugestão baseada em palavras-chave
        if pattern["keywords"]:
            top_keywords = [kw[0] for kw in pattern["keywords"][:5]]
            optimizations.append({
                "type": "keywords",
                "suggestion": f"Incluir palavras-chave: {', '.join(top_keywords)}",
                "keywords": top_keywords
            })
        
        # Sugestão baseada em tipo de pergunta
        if pattern["question_types"]:
            dominant_type = max(pattern["question_types"].items(), key=lambda x: x[1])
            if dominant_type[1] > 0:
                optimizations.append({
                    "type": "question_type",
                    "suggestion": f"Otimizar para tipo de pergunta: {dominant_type[0]}",
                    "question_type": dominant_type[0]
                })
        
        return {
            "cluster_id": cluster_id,
            "cluster_size": pattern["size"],
            "optimizations": optimizations,
            "patterns": pattern
        }
    
    async def _save_clusters_to_db(self, clusters: List[Dict]):
        """Salva clusters no banco de dados"""
        try:
            for cluster in clusters:
                cluster_id = cluster["cluster_id"]
                examples = cluster["texts"][:10]  # Primeiros 10 exemplos
                
                # Salva ou atualiza cluster (examples já é List[str])
                await self.database.save_intent_cluster(
                    cluster_id=cluster_id,
                    intent_type=f"cluster_{cluster_id}",
                    examples=examples
                )
            
            logger.info(f"✅ {len(clusters)} clusters salvos no banco")
        except Exception as e:
            logger.error(f"Erro ao salvar clusters: {e}")
    
    async def _load_clusters_from_db(self) -> List[Dict]:
        """Carrega clusters do banco de dados"""
        try:
            clusters_data = await self.database.get_intent_clusters()
            
            # Reconstrói estrutura de clusters
            clusters = []
            for cluster_data in clusters_data:
                cluster_id = cluster_data.get("cluster_id", 0)
                examples = cluster_data.get("examples", [])
                
                # Para simplificar, retorna estrutura básica
                # Em produção, seria necessário reconstruir embeddings
                clusters.append({
                    "cluster_id": cluster_id,
                    "texts": examples if isinstance(examples, list) else [],
                    "embeddings": [],
                    "conversation_ids": []
                })
            
            return clusters
        except Exception as e:
            logger.error(f"Erro ao carregar clusters: {e}")
            return []

