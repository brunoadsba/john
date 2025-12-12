"""
Validador e normalizador de parâmetros de busca de vagas
"""
import re
from typing import Dict, Optional, Tuple
from loguru import logger


class JobQueryValidator:
    """
    Valida, normaliza e sanitiza parâmetros de busca de vagas
    """
    
    # Modalidades válidas
    VALID_MODALITIES = {"remoto", "presencial", "híbrido", ""}
    
    # Áreas comuns para validação
    COMMON_AREAS = {
        "ti", "tecnologia", "tecnologia da informação", "informática",
        "marketing", "vendas", "comercial", "rh", "recursos humanos",
        "financeiro", "contabilidade", "jurídico", "administração",
        "engenharia", "produção", "logística", "atendimento",
        "comunicação", "design", "educação", "saúde"
    }
    
    def __init__(self):
        """Inicializa o validador"""
        logger.debug("✅ JobQueryValidator inicializado")
    
    def validate_and_normalize(
        self,
        cargo: Optional[str] = None,
        localizacao: Optional[str] = None,
        area: Optional[str] = None,
        modalidade: Optional[str] = None
    ) -> Tuple[str, str, str, str]:
        """
        Valida e normaliza parâmetros de busca
        
        Args:
            cargo: Cargo ou título da vaga
            localizacao: Localização da vaga
            area: Área de atuação
            modalidade: Modalidade de trabalho
            
        Returns:
            Tupla com parâmetros validados e normalizados: (cargo, localizacao, area, modalidade)
        """
        # Normaliza cargo
        cargo_normalized = self._normalize_cargo(cargo or "")
        
        # Normaliza localização
        localizacao_normalized = self._normalize_localizacao(localizacao or "")
        
        # Normaliza área
        area_normalized = self._normalize_area(area or "")
        
        # Valida e normaliza modalidade
        modalidade_normalized = self._normalize_modalidade(modalidade or "")
        
        # Log de validação
        if cargo != cargo_normalized or localizacao != localizacao_normalized:
            logger.debug(f"📝 Parâmetros normalizados: cargo='{cargo}'→'{cargo_normalized}', "
                        f"localizacao='{localizacao}'→'{localizacao_normalized}'")
        
        return cargo_normalized, localizacao_normalized, area_normalized, modalidade_normalized
    
    def _normalize_cargo(self, cargo: str) -> str:
        """
        Normaliza o cargo removendo caracteres especiais e normalizando espaços
        """
        if not cargo:
            return ""
        
        # Remove caracteres especiais perigosos para query
        cargo = re.sub(r'[<>"\'\\]', '', cargo)
        
        # Normaliza espaços múltiplos
        cargo = re.sub(r'\s+', ' ', cargo).strip()
        
        # Limita tamanho
        if len(cargo) > 100:
            cargo = cargo[:100].strip()
            logger.warning(f"⚠️ Cargo truncado para 100 caracteres")
        
        return cargo
    
    def _normalize_localizacao(self, localizacao: str) -> str:
        """
        Normaliza localização detectando modalidade implícita
        """
        if not localizacao:
            return ""
        
        localizacao_lower = localizacao.lower().strip()
        
        # Detecta modalidade na localização
        if localizacao_lower in ["remoto", "remota", "home office", "homeoffice"]:
            return ""  # Retorna vazio para não duplicar com modalidade
        
        if localizacao_lower in ["presencial", "on-site", "on site"]:
            return ""  # Retorna vazio para não duplicar com modalidade
        
        if "híbrido" in localizacao_lower or "hibrido" in localizacao_lower:
            return ""  # Retorna vazio para não duplicar com modalidade
        
        # Remove caracteres especiais
        localizacao = re.sub(r'[<>"\'\\]', '', localizacao)
        
        # Normaliza espaços
        localizacao = re.sub(r'\s+', ' ', localizacao).strip()
        
        # Limita tamanho
        if len(localizacao) > 50:
            localizacao = localizacao[:50].strip()
        
        return localizacao
    
    def _normalize_area(self, area: str) -> str:
        """
        Normaliza área de atuação
        """
        if not area:
            return ""
        
        area_lower = area.lower().strip()
        
        # Normaliza variações comuns
        area_mapping = {
            "ti": "TI",
            "t.i.": "TI",
            "t.i": "TI",
            "tecnologia": "TI",
            "tecnologia da informação": "TI",
            "informática": "TI",
            "recursos humanos": "RH",
            "r.h.": "RH",
            "rh": "RH",
        }
        
        if area_lower in area_mapping:
            return area_mapping[area_lower]
        
        # Remove caracteres especiais
        area = re.sub(r'[<>"\'\\]', '', area)
        area = re.sub(r'\s+', ' ', area).strip()
        
        # Limita tamanho
        if len(area) > 30:
            area = area[:30].strip()
        
        return area
    
    def _normalize_modalidade(self, modalidade: str) -> str:
        """
        Valida e normaliza modalidade de trabalho
        """
        if not modalidade:
            return ""
        
        modalidade_lower = modalidade.lower().strip()
        
        # Normaliza variações
        if modalidade_lower in ["remoto", "remota", "remote", "home office", "homeoffice"]:
            return "remoto"
        
        if modalidade_lower in ["presencial", "on-site", "on site", "presencial"]:
            return "presencial"
        
        if modalidade_lower in ["híbrido", "hibrido", "hybrid", "híbrida", "hibrida"]:
            return "híbrido"
        
        # Se não reconheceu, retorna vazio
        logger.warning(f"⚠️ Modalidade desconhecida: '{modalidade}', usando vazio")
        return ""

