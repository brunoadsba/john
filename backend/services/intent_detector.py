"""
Detector de intenção para Architecture Advisor
Usa LLM para classificação com fallback para regex e clusters aprendidos
"""
import re
from typing import Optional, Dict, Tuple, List
from loguru import logger

from backend.services.embedding_service import EmbeddingService

# Padrões regex para detecção rápida (fallback)
INTENT_PATTERNS = {
    "analyze_requirements": [
        r"analis[ae]r?\s+(os\s+)?requisitos",
        r"requisitos?\s+(funcionais?|não.funcionais?|não.funcionais?)",
        r"o\s+que\s+preciso\s+para",
        r"quais\s+requisitos",
        r"definir\s+requisitos",
        r"análise\s+de\s+requisitos",
        r"checklist\s+de\s+requisitos",
    ],
    "design_architecture": [
        r"arquitetura",
        r"padr[ãa]o\s+arquitetural",
        r"design\s+de\s+(sistema|arquitetura)",
        r"como\s+estruturar",
        r"estrutura\s+do\s+(projeto|sistema)",
        r"stack\s+tecnol[óo]gica",
    ],
    "security_checklist": [
        r"checklist\s+de\s+segurança",
        r"segurança\s+do\s+(sistema|app|projeto|aplicação)",
        r"vulnerabilidades?",
        r"proteção\s+de\s+dados",
        r"como\s+proteger",
        r"boas\s+práticas\s+de\s+segurança",
    ],
    "compare_solutions": [
        r"comparar\s+(soluções?|tecnologias?|ferramentas?|.*\s+vs\s+.*)",
        r"qual\s+(é|seria)\s+melhor",
        r"diferença\s+entre",
        r"prós\s+e\s+contras",
        r"trade.off",
        r".*\s+vs\s+.*",  # Padrão genérico para comparações (ex: SQL vs NoSQL)
    ],
    "plan_scalability": [
        r"escalabilidade",
        r"como\s+escalar",
        r"performance\s+e\s+crescimento",
        r"planejar\s+crescimento",
        r"infraestrutura\s+para\s+escala",
    ],
}


class IntentDetector:
    """Detector de intenção para Architecture Advisor"""
    
    def __init__(
        self,
        llm_service=None,
        embedding_service: Optional[EmbeddingService] = None,
        clustering_service=None
    ):
        """
        Inicializa o detector
        
        Args:
            llm_service: Serviço LLM para classificação (opcional)
            embedding_service: Serviço de embeddings para usar clusters
            clustering_service: Serviço de clustering (opcional)
        """
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.clustering_service = clustering_service
        self._clusters_cache: Optional[List[Dict]] = None
        logger.info("IntentDetector inicializado")
    
    def detect(self, text: str, use_llm: bool = True, use_clusters: bool = True) -> Tuple[Optional[str], float]:
        """
        Detecta a intenção do texto
        
        Args:
            text: Texto do usuário
            use_llm: Se True, usa LLM para classificação (mais preciso)
            use_clusters: Se True, usa clusters aprendidos (Fase 4)
            
        Returns:
            Tupla (intenção, confiança) ou (None, 0.0) se não detectar
        """
        text_lower = text.lower().strip()
        
        # Tenta regex primeiro (rápido)
        intent, confidence = self._detect_regex(text_lower)
        if intent:
            logger.debug(f"Intenção detectada via regex: {intent} (confiança: {confidence})")
            return intent, confidence
        
        # Tenta clusters aprendidos (Fase 4)
        if use_clusters and self.embedding_service and self.clustering_service:
            intent, confidence = self._detect_clusters(text)
            if intent and confidence > 0.6:
                logger.debug(f"Intenção detectada via clusters: {intent} (confiança: {confidence})")
                return intent, confidence
        
        # Se regex e clusters não encontraram e LLM disponível, usa LLM
        if use_llm and self.llm_service:
            intent, confidence = self._detect_llm(text)
            if intent:
                logger.debug(f"Intenção detectada via LLM: {intent} (confiança: {confidence})")
                return intent, confidence
        
        logger.debug("Nenhuma intenção detectada")
        return None, 0.0
    
    def _detect_regex(self, text: str) -> Tuple[Optional[str], float]:
        """Detecção rápida via regex"""
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Confiança baseada em quantos padrões matcham
                    matches = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
                    confidence = min(0.9, 0.6 + (matches * 0.1))
                    return intent, confidence
        
        return None, 0.0
    
    def _detect_clusters(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detecta intenção usando clusters aprendidos (Fase 4)
        Nota: Clusters são carregados de forma assíncrona, então este método
        usa cache pré-carregado
        
        Args:
            text: Texto do usuário
            
        Returns:
            Tupla (intenção, confiança) ou (None, 0.0)
        """
        if not self.embedding_service or not self.embedding_service.is_available():
            return None, 0.0
        
        if not self._clusters_cache:
            return None, 0.0
        
        try:
            # Gera embedding do texto
            query_embedding = self.embedding_service.embed_query(text)
            
            # Compara com exemplos de cada cluster
            best_match = None
            best_similarity = 0.0
            
            for cluster in self._clusters_cache:
                cluster_texts = cluster.get("texts", [])
                if not cluster_texts:
                    continue
                
                # Gera embeddings dos exemplos do cluster
                cluster_embeddings = self.embedding_service.embed(cluster_texts[:5])  # Top 5 exemplos
                
                # Calcula similaridade média
                similarities = [
                    self.embedding_service.cosine_similarity(query_embedding, emb)
                    for emb in cluster_embeddings
                ]
                
                avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
                
                if avg_similarity > best_similarity:
                    best_similarity = avg_similarity
                    # Tenta inferir intenção do cluster (simplificado)
                    # Em produção, seria necessário mapear clusters para intenções
                    best_match = "design_architecture"  # Placeholder
            
            # Retorna se similaridade for alta o suficiente
            if best_similarity > 0.7:
                return best_match, best_similarity
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao detectar intenção via clusters: {e}")
            return None, 0.0
    
    def _detect_llm(self, text: str) -> Tuple[Optional[str], float]:
        """Detecção via LLM (mais precisa)"""
        if not self.llm_service:
            return None, 0.0
        
        prompt = f"""Classifique a intenção do usuário em UMA destas categorias:
- analyze_requirements: análise de requisitos, requisitos funcionais/não-funcionais
- design_architecture: sugestões de arquitetura, padrões arquiteturais, stack tecnológica
- security_checklist: checklist de segurança, vulnerabilidades, proteção
- compare_solutions: comparar soluções técnicas, tecnologias, trade-offs
- plan_scalability: escalabilidade, performance, crescimento, infraestrutura
- none: qualquer outra coisa que não seja sobre arquitetura/requisitos/segurança

Texto do usuário: "{text}"

Responda APENAS com o nome da categoria (ex: analyze_requirements). Se não for nenhuma das categorias acima, responda "none":"""
        
        try:
            response, _ = self.llm_service.generate_response(
                prompt,
                contexto=None,
                memorias_contexto="",
                tools=None,
                tool_executor=None
            )
            
            # Limpa resposta e extrai intenção
            intent = response.strip().lower()
            
            # Remove pontuação e espaços extras
            intent = re.sub(r'[^\w]', '', intent)
            
            # Valida se é uma intenção válida
            valid_intents = list(INTENT_PATTERNS.keys()) + ["none"]
            if intent in valid_intents:
                confidence = 0.85 if intent != "none" else 0.0
                return intent if intent != "none" else None, confidence
            
            logger.warning(f"LLM retornou intenção inválida: {intent}")
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao detectar intenção via LLM: {e}")
            return None, 0.0
    
    def is_architecture_intent(self, text: str) -> bool:
        """
        Verifica se o texto é sobre arquitetura/requisitos/segurança
        
        Returns:
            True se for intenção relacionada a Architecture Advisor
        """
        intent, confidence = self.detect(text)
        return intent is not None and confidence > 0.5
    
    async def refresh_clusters_cache(self):
        """Atualiza cache de clusters (chamar após novo clustering)"""
        if self.clustering_service:
            try:
                self._clusters_cache = await self.clustering_service._load_clusters_from_db()
                logger.info(f"Cache de clusters atualizado: {len(self._clusters_cache)} clusters")
            except Exception as e:
                logger.error(f"Erro ao atualizar cache de clusters: {e}")
                self._clusters_cache = []
