"""
Configuração de sites de vagas com categorização e priorização
Baseado em plataformas reais e estratégias de recrutamento
"""
from typing import Dict, List, Set
from enum import Enum


class JobSiteCategory(Enum):
    """Categorias de sites de vagas"""
    AGGREGATOR = "aggregator"  # Agregadores (Google for Jobs, Indeed)
    PROFESSIONAL_NETWORK = "professional_network"  # LinkedIn
    PORTAL_BR = "portal_br"  # Portais brasileiros (Vagas.com, Catho)
    ATS = "ats"  # Applicant Tracking Systems (Gupy, Reachr)
    NICHE = "niche"  # Sites de nicho (Trampos, CIEE)
    REVIEW_PLATFORM = "review_platform"  # Glassdoor


class JobSiteConfig:
    """
    Configuração centralizada de sites de vagas
    Baseado em plataformas reais e suas características
    """
    
    # Sites principais (usados na busca padrão)
    MAIN_SITES: List[str] = [
        # Agregadores globais (alto volume)
        "linkedin.com",
        "indeed.com",
        # Portais brasileiros (grande volume no BR)
        "vagas.com",
        "catho.com",
        "infojobs.com.br",
        # ATS brasileiro (muito popular)
        "gupy.io",
        # Agregadores/Portais adicionais
        "glassdoor.com",
        "trabalhabrasil.com.br",
        "empregos.com.br",
    ]
    
    # Sites de nicho específico
    NICHE_SITES: Dict[str, List[str]] = {
        "estagio": [
            "ciee.org.br",
            "nube.com.br",
        ],
        "tecnologia": [
            "trampos.co",
            "programathor.com.br",
            "geekhunter.com.br",
        ],
        "criacao": [
            "trampos.co",
            "behance.net",
        ],
        "freelance": [
            "workana.com.br",
            "99freelas.com.br",
        ],
    }
    
    # Scores por site (baseado em relevância e volume no Brasil)
    SITE_SCORES: Dict[str, float] = {
        # Agregadores globais
        "linkedin.com": 10.0,  # Máxima prioridade - networking profissional
        "indeed.com": 9.5,     # Alto volume global
        "google.com": 9.0,     # Google for Jobs (agregador)
        
        # Portais brasileiros principais
        "vagas.com": 9.0,      # Um dos maiores no BR
        "gupy.io": 8.5,        # Muito popular como ATS no BR
        "catho.com": 8.0,      # Tradicional no BR
        "infojobs.com.br": 7.5,
        
        # Outros portais BR
        "trabalhabrasil.com.br": 7.0,
        "empregos.com.br": 6.5,
        "bne.com.br": 6.0,     # Banco Nacional de Empregos
        
        # Plataformas globais
        "glassdoor.com": 7.5,  # Avaliações + vagas
        
        # Sites de nicho
        "trampos.co": 7.0,     # Tecnologia e criação
        "ciee.org.br": 8.0,    # Estágios (alto score para nicho)
        "programathor.com.br": 7.0,
        "geekhunter.com.br": 6.5,
        "nube.com.br": 7.5,    # Estágios
        "workana.com.br": 6.0, # Freelance
        "99freelas.com.br": 5.5,
    }
    
    # Categorização de sites
    SITE_CATEGORIES: Dict[str, JobSiteCategory] = {
        "linkedin.com": JobSiteCategory.PROFESSIONAL_NETWORK,
        "indeed.com": JobSiteCategory.AGGREGATOR,
        "google.com": JobSiteCategory.AGGREGATOR,
        "vagas.com": JobSiteCategory.PORTAL_BR,
        "catho.com": JobSiteCategory.PORTAL_BR,
        "infojobs.com.br": JobSiteCategory.PORTAL_BR,
        "gupy.io": JobSiteCategory.ATS,
        "trabalhabrasil.com.br": JobSiteCategory.PORTAL_BR,
        "empregos.com.br": JobSiteCategory.PORTAL_BR,
        "bne.com.br": JobSiteCategory.PORTAL_BR,
        "glassdoor.com": JobSiteCategory.REVIEW_PLATFORM,
        "trampos.co": JobSiteCategory.NICHE,
        "ciee.org.br": JobSiteCategory.NICHE,
        "programathor.com.br": JobSiteCategory.NICHE,
        "geekhunter.com.br": JobSiteCategory.NICHE,
        "nube.com.br": JobSiteCategory.NICHE,
        "workana.com.br": JobSiteCategory.NICHE,
        "99freelas.com.br": JobSiteCategory.NICHE,
    }
    
    # Palavras-chave para detecção de nicho
    NICHE_KEYWORDS: Dict[str, Set[str]] = {
        "estagio": {
            "estágio", "estagio", "estagiário", "estagiaria", "estagiariao",
            "trainee", "jovem aprendiz", "aprendiz", "primeiro emprego",
            "iniciante", "sem experiência"
        },
        "tecnologia": {
            "desenvolvedor", "dev", "programador", "engenheiro de software",
            "tech", "tecnologia", "ti", "t.i.", "ti", "software",
            "python", "javascript", "java", "react", "node", "backend",
            "frontend", "fullstack", "full stack"
        },
        "criacao": {
            "designer", "design", "criativo", "arte", "ilustrador",
            "ux", "ui", "marketing digital", "redator", "copywriter",
            "social media", "mídia", "publicidade"
        },
        "freelance": {
            "freelancer", "freelance", "pj", "autônomo", "autonomo",
            "remoto", "home office", "por projeto", "temporário"
        },
    }
    
    @classmethod
    def get_sites_for_query(
        cls,
        cargo: str = "",
        area: str = "",
        detect_niche: bool = True
    ) -> List[str]:
        """
        Retorna lista de sites otimizada para a busca
        
        Args:
            cargo: Cargo procurado
            area: Área de atuação
            detect_niche: Se True, adiciona sites de nicho quando detectado
            
        Returns:
            Lista de sites ordenada por prioridade
        """
        sites = cls.MAIN_SITES.copy()
        
        if detect_niche:
            detected_niche = cls._detect_niche(cargo, area)
            if detected_niche and detected_niche in cls.NICHE_SITES:
                # Adiciona sites de nicho ao início (maior prioridade)
                niche_sites = cls.NICHE_SITES[detected_niche]
                sites = niche_sites + sites
        
        return sites
    
    @classmethod
    def _detect_niche(cls, cargo: str, area: str) -> str:
        """
        Detecta nicho baseado em cargo e área
        
        Args:
            cargo: Cargo procurado
            area: Área de atuação
            
        Returns:
            Nicho detectado ou None
        """
        text = f"{cargo} {area}".lower()
        
        # Verifica palavras-chave de cada nicho
        for niche, keywords in cls.NICHE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return niche
        
        return None
    
    @classmethod
    def get_site_score(cls, url: str) -> float:
        """
        Retorna score de um site baseado na URL
        
        Args:
            url: URL do resultado
            
        Returns:
            Score do site (padrão: 5.0)
        """
        url_lower = url.lower()
        
        for site, score in cls.SITE_SCORES.items():
            if site in url_lower:
                return score
        
        return 5.0  # Score padrão para sites desconhecidos
    
    @classmethod
    def get_site_category(cls, url: str) -> JobSiteCategory:
        """
        Retorna categoria de um site
        
        Args:
            url: URL do resultado
            
        Returns:
            Categoria do site ou None
        """
        url_lower = url.lower()
        
        for site, category in cls.SITE_CATEGORIES.items():
            if site in url_lower:
                return category
        
        return None

