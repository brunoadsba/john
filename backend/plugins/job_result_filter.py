"""
Filtro robusto de resultados de busca de vagas
"""
from typing import List, Dict, Optional
from loguru import logger
from backend.plugins.job_closed_detector import JobClosedDetector
from backend.plugins.job_result_scorer import JobResultScorer


class JobSearchFilter:
    """Filtra resultados para manter apenas vagas ativas e relevantes com validação robusta"""
    
    def __init__(self, job_sites: List[str]):
        self.job_sites = job_sites
        self.closed_detector = JobClosedDetector()
        self.scorer = JobResultScorer()
    
    def filter_jobs(
        self, 
        results: List[Dict[str, str]],
        search_terms: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """
        Filtra resultados para manter apenas vagas ativas e relevantes
        
        Usa múltiplas camadas de filtragem:
        1. Remove vagas encerradas (JobClosedDetector)
        2. Valida estrutura dos resultados
        3. Filtra por relevância (sites e palavras-chave)
        4. Pontua e ordena por qualidade
        
        Args:
            results: Lista de resultados de busca
            search_terms: Termos de busca originais (opcional, para scoring)
            
        Returns:
            Lista filtrada e ordenada por relevância
        """
        if not results:
            return []
        
        # ETAPA 1: Valida estrutura básica dos resultados
        valid_results = self._validate_results_structure(results)
        
        if not valid_results:
            logger.warning("⚠️ Nenhum resultado válido após validação de estrutura")
            return []
        
        # ETAPA 2: Remove vagas encerradas usando detector avançado
        active_results = self.closed_detector.filter_closed_jobs(valid_results)
        
        if not active_results:
            logger.info("✅ Nenhuma vaga ativa encontrada após filtragem de encerradas")
            return []
        
        # ETAPA 3: Filtra por relevância (sites e palavras-chave)
        relevant_results = self._filter_by_relevance(active_results)
        
        if not relevant_results:
            logger.info("✅ Nenhuma vaga relevante encontrada após filtragem de relevância")
            return []
        
        # ETAPA 4: Pontua e ordena por qualidade
        if search_terms:
            scored_results = self.scorer.score_and_sort(relevant_results, search_terms)
        else:
            scored_results = relevant_results
        
        logger.info(f"✅ {len(scored_results)} vagas ativas e relevantes de {len(results)} resultados totais")
        
        return scored_results
    
    def _validate_results_structure(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Valida estrutura básica dos resultados
        
        Args:
            results: Lista de resultados
            
        Returns:
            Lista de resultados válidos
        """
        valid_results = []
        
        for i, result in enumerate(results):
            if not isinstance(result, dict):
                logger.warning(f"⚠️ Resultado {i} não é um dicionário, ignorando")
                continue
            
            # Valida campos obrigatórios
            title = result.get("title", "").strip()
            url = result.get("url", "").strip()
            snippet = result.get("snippet", "").strip()
            
            # Resultado deve ter pelo menos título OU URL
            if not title and not url:
                logger.debug(f"⚠️ Resultado {i} sem título e URL, ignorando")
                continue
            
            # Valida URL se presente
            if url and not self._is_valid_url(url):
                logger.debug(f"⚠️ Resultado {i} com URL inválida: {url[:50]}...")
                continue
            
            # Adiciona resultado válido
            valid_results.append({
                "title": title or "Sem título",
                "url": url,
                "snippet": snippet
            })
        
        return valid_results
    
    def _filter_by_relevance(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filtra resultados por relevância (sites e palavras-chave)
        
        Args:
            results: Lista de resultados ativos
            
        Returns:
            Lista de resultados relevantes
        """
        relevant_results = []
        
        job_keywords = [
            "vaga", "vagas", "emprego", "trabalho", "oportunidade",
            "oportunidades", "recrutamento", "contratação", "job", "position"
        ]
        
        for result in results:
            title = (result.get("title", "") or "").lower()
            snippet = (result.get("snippet", "") or "").lower()
            url = (result.get("url", "") or "").lower()
            
            # Verifica se é de site de vagas conhecido
            is_job_site = any(site in url for site in self.job_sites)
            
            # Verifica se contém palavras-chave de vagas
            text_content = f"{title} {snippet}"
            has_job_keywords = any(
                keyword in text_content
                for keyword in job_keywords
            )
            
            # Aceita se for de site conhecido OU tiver palavras-chave
            if is_job_site or has_job_keywords:
                relevant_results.append(result)
        
        return relevant_results
    
    def _is_valid_url(self, url: str) -> bool:
        """Verifica se URL é válida"""
        if not url:
            return False
        
        # Verifica se começa com http:// ou https://
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Verifica se tem pelo menos um ponto (domínio)
        if '.' not in url:
            return False
        
        return True

