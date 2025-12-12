"""
Construtor de queries otimizadas para busca de vagas
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
from backend.plugins.job_query_validator import JobQueryValidator


class JobSearchQueryBuilder:
    """Constrói queries otimizadas para busca de vagas com validação robusta"""
    
    def __init__(self, job_sites: List[str], days_back: int = 30):
        self.job_sites = job_sites
        self.days_back = days_back
        self.validator = JobQueryValidator()
        
        # Lista expandida de palavras-chave para excluir na query
        self.closed_keywords = [
            # Português
            "encerrada", "fechada", "finalizada", "expirada",
            "preenchida", "cancelada", "vencida",
            # Inglês
            "closed", "expired", "filled", "finished", "ended",
            "cancelled", "unavailable",
        ]
    
    def build_query(
        self,
        cargo: Optional[str] = None,
        localizacao: Optional[str] = None,
        area: Optional[str] = None,
        modalidade: Optional[str] = None
    ) -> str:
        """
        Constrói query otimizada para busca de vagas com validação
        
        Args:
            cargo: Cargo ou título da vaga
            localizacao: Localização da vaga
            area: Área de atuação
            modalidade: Modalidade de trabalho
            
        Returns:
            Query otimizada para busca
        """
        try:
            # Valida e normaliza parâmetros
            cargo_norm, localizacao_norm, area_norm, modalidade_norm = \
                self.validator.validate_and_normalize(cargo, localizacao, area, modalidade)
            
            parts = []
            
            # Adiciona cargo (sempre presente, mesmo que genérico)
            if cargo_norm:
                parts.append(self._sanitize_for_query(cargo_norm))
            else:
                parts.append("vaga")
            
            # Adiciona modalidade (se especificada)
            if modalidade_norm:
                parts.append(modalidade_norm)
            
            # Adiciona localização (apenas se não for modalidade)
            if localizacao_norm:
                parts.append(self._sanitize_for_query(localizacao_norm))
            
            # Adiciona área (se especificada)
            if area_norm:
                parts.append(self._sanitize_for_query(area_norm))
            
            # Adiciona palavras-chave de vaga (sempre)
            parts.append("emprego vagas")
            
            # Adiciona sites prioritários (usa todos os sites principais)
            # Nota: Buscas múltiplas serão feitas no plugin para cobrir todos os sites
            if self.job_sites:
                # Usa até 8 sites na query principal (máximo prático)
                sites_query = " OR ".join([
                    f"site:{site}" 
                    for site in self.job_sites[:8]
                ])
                parts.append(f"({sites_query})")
            
            # Adiciona filtro de data (vagas recentes)
            try:
                date_filter = (datetime.now() - timedelta(days=self.days_back)).strftime("%Y-%m-%d")
                parts.append(f"since:{date_filter}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao gerar filtro de data: {e}")
            
            # Remove palavras que indicam vaga encerrada (usa todas as palavras agora)
            if self.closed_keywords:
                exclude_query = " ".join([
                    f"-{keyword}" 
                    for keyword in self.closed_keywords[:10]  # Aumentado de 8 para 10
                ])
                parts.append(exclude_query)
            
            query = " ".join(parts)
            
            # Valida tamanho da query
            if len(query) > 500:
                logger.warning(f"⚠️ Query muito longa ({len(query)} chars), truncando...")
                query = query[:500].strip()
            
            logger.debug(f"✅ Query construída: {query[:100]}...")
            return query
            
        except Exception as e:
            logger.error(f"❌ Erro ao construir query: {e}")
            # Query de fallback segura
            return "vaga emprego vagas"
    
    def _sanitize_for_query(self, text: str) -> str:
        """
        Sanitiza texto para uso seguro em query de busca
        
        Args:
            text: Texto a sanitizar
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Remove caracteres especiais perigosos
        text = text.replace('"', '').replace("'", "").replace('\\', '')
        
        # Remove caracteres de controle
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Normaliza espaços
        text = ' '.join(text.split())
        
        return text.strip()

