"""
Sistema de pontuação para resultados de busca de vagas
Prioriza resultados mais relevantes e de maior qualidade
"""
from typing import Dict, List
from loguru import logger
import re


class JobResultScorer:
    """
    Sistema de pontuação para classificar e priorizar resultados de vagas
    """
    
    def __init__(self):
        """Inicializa o sistema de pontuação"""
        # Importa configuração centralizada de sites
        from backend.plugins.job_site_config import JobSiteConfig
        self.site_config = JobSiteConfig
        
        # Sites com maior prioridade (usando scores da configuração centralizada)
        # Mantido para compatibilidade, mas agora usa JobSiteConfig.get_site_score()
        self.site_priority = {
            "linkedin.com": 10,
            "indeed.com": 9,
            "glassdoor.com": 8,
            "vagas.com": 8,
            "catho.com": 7,
            "infojobs.com.br": 7,
            "gupy.io": 6,
            "programathor.com.br": 6,
        }
        
        # Palavras-chave que aumentam relevância
        self.relevance_keywords = {
            "vagas": 5,
            "emprego": 4,
            "oportunidade": 4,
            "contratação": 5,
            "recrutamento": 4,
            "trabalho": 3,
            "vaga": 5,
        }
        
        logger.debug("✅ JobResultScorer inicializado")
    
    def score_and_sort(self, results: List[Dict[str, str]], search_terms: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Pontua e ordena resultados por relevância
        
        Args:
            results: Lista de resultados de busca
            search_terms: Termos de busca originais (cargo, localizacao, area, modalidade)
            
        Returns:
            Lista de resultados ordenada por score (maior primeiro)
        """
        if not results:
            return []
        
        scored_results = []
        
        for result in results:
            score = self._calculate_score(result, search_terms)
            
            # Adiciona score ao resultado
            result_with_score = result.copy()
            result_with_score['_score'] = score
            scored_results.append(result_with_score)
        
        # Ordena por score (maior primeiro)
        scored_results.sort(key=lambda x: x.get('_score', 0), reverse=True)
        
        # Remove score antes de retornar
        for result in scored_results:
            if '_score' in result:
                del result['_score']
        
        logger.debug(f"✅ {len(scored_results)} resultados pontuados e ordenados")
        
        return scored_results
    
    def _calculate_score(self, result: Dict[str, str], search_terms: Dict[str, str]) -> float:
        """
        Calcula score de relevância para um resultado
        
        Args:
            result: Resultado de busca
            search_terms: Termos de busca
            
        Returns:
            Score de relevância (float)
        """
        score = 0.0
        
        title = (result.get("title", "") or "").lower()
        snippet = (result.get("snippet", "") or "").lower()
        url = (result.get("url", "") or "").lower()
        
        # Base score (todos começam com 10)
        score += 10.0
        
        # Pontuação por site (sites confiáveis ganham mais pontos)
        site_score = self._get_site_score(url)
        score += site_score
        
        # Pontuação por correspondência no título (mais importante)
        title_score = self._calculate_text_match_score(title, search_terms, weight=3.0)
        score += title_score
        
        # Pontuação por correspondência no snippet
        snippet_score = self._calculate_text_match_score(snippet, search_terms, weight=1.0)
        score += snippet_score
        
        # Pontuação por palavras-chave de relevância
        relevance_score = self._calculate_relevance_score(title + " " + snippet)
        score += relevance_score
        
        # Penaliza resultados muito curtos (pouca informação)
        if len(snippet) < 50:
            score -= 2.0
        
        # Bonus para resultados com URL válida
        if self._is_valid_url(url):
            score += 1.0
        
        return score
    
    def _get_site_score(self, url: str) -> float:
        """
        Retorna pontuação baseada no site
        Usa configuração centralizada de sites
        """
        # Usa configuração centralizada primeiro (mais completa)
        score = self.site_config.get_site_score(url)
        if score != 5.0:  # Se encontrou na config, retorna
            return score
        
        # Fallback para compatibilidade
        for site, priority in self.site_priority.items():
            if site in url:
                return float(priority)
        
        return 5.0  # Score padrão para sites desconhecidos
    
    def _calculate_text_match_score(
        self,
        text: str,
        search_terms: Dict[str, str],
        weight: float = 1.0
    ) -> float:
        """
        Calcula score baseado em correspondência de termos
        
        Args:
            text: Texto para analisar
            search_terms: Termos de busca
            weight: Peso do score (título tem peso maior que snippet)
            
        Returns:
            Score de correspondência
        """
        score = 0.0
        
        if not text:
            return 0.0
        
        # Normaliza termos de busca
        cargo = (search_terms.get("cargo", "") or "").lower()
        localizacao = (search_terms.get("localizacao", "") or "").lower()
        area = (search_terms.get("area", "") or "").lower()
        modalidade = (search_terms.get("modalidade", "") or "").lower()
        
        # Verifica correspondência exata do cargo (score alto)
        if cargo:
            cargo_words = cargo.split()
            matches = sum(1 for word in cargo_words if word in text and len(word) > 2)
            if matches > 0:
                score += (matches / max(len(cargo_words), 1)) * 10.0 * weight
        
        # Verifica correspondência de localização
        if localizacao and localizacao in text:
            score += 5.0 * weight
        
        # Verifica correspondência de área
        if area and area in text:
            score += 3.0 * weight
        
        # Verifica correspondência de modalidade
        if modalidade:
            modalidade_terms = {
                "remoto": ["remoto", "remote", "home office", "homeoffice"],
                "presencial": ["presencial", "on-site", "on site"],
                "híbrido": ["híbrido", "hibrido", "hybrid"],
            }
            if modalidade in modalidade_terms:
                for term in modalidade_terms[modalidade]:
                    if term in text:
                        score += 4.0 * weight
                        break
        
        return score
    
    def _calculate_relevance_score(self, text: str) -> float:
        """Calcula score baseado em palavras-chave de relevância"""
        score = 0.0
        
        for keyword, points in self.relevance_keywords.items():
            if keyword in text:
                score += points
        
        return min(score, 20.0)  # Limita score máximo
    
    def _is_valid_url(self, url: str) -> bool:
        """Verifica se URL é válida"""
        if not url:
            return False
        
        # Verifica padrão básico de URL
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # porta opcional
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))

