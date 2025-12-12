"""
Extrator de datas de vagas a partir de snippets e títulos
Extrai data de publicação e data de encerramento quando disponíveis
"""
import re
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from loguru import logger


class JobDateExtractor:
    """Extrai datas de publicação e encerramento de vagas"""
    
    # Padrões de data em português
    DATE_PATTERNS = [
        # Formato: "postado em 15/12/2024" ou "publicado em 15/12/2024"
        (r'(?:postado|publicado|criado|inserido).*?(\d{1,2})/(\d{1,2})/(\d{4})', 'pt_br_dmy'),
        # Formato: "encerra em 30/12/2024" ou "válido até 30/12/2024"
        (r'(?:encerra|expira|válido até|válida até|até|finaliza).*?(\d{1,2})/(\d{1,2})/(\d{4})', 'pt_br_dmy'),
        # Formato: "postado há 5 dias"
        (r'(?:postado|publicado|há|criado|inserido).*?(\d+).*?(?:dia|dias|semana|semanas)', 'relative'),
        # Formato: "aberta até 31/12/2024"
        (r'(?:aberta|aberto|disponível).*?até.*?(\d{1,2})/(\d{1,2})/(\d{4})', 'pt_br_dmy'),
        # Formato ISO: "2024-12-15"
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'iso'),
    ]
    
    def extract_dates(self, title: str, snippet: str, url: str = "") -> Dict[str, Optional[str]]:
        """
        Extrai datas de publicação e encerramento
        
        Args:
            title: Título da vaga
            snippet: Descrição/snippet da vaga
            url: URL da vaga (opcional)
            
        Returns:
            Dicionário com 'posted_date' e 'closing_date' (ou None se não encontrado)
        """
        text = f"{title} {snippet}".lower()
        
        posted_date = None
        closing_date = None
        
        # Procura data de postagem
        for pattern, format_type in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if format_type == 'relative':
                    # Data relativa: "há X dias"
                    days_ago = int(match.group(1))
                    if 'semana' in match.group(0):
                        days_ago *= 7
                    date = datetime.now() - timedelta(days=days_ago)
                    posted_date = date.strftime("%d/%m/%Y")
                    break
                elif format_type in ['pt_br_dmy', 'iso']:
                    try:
                        if format_type == 'pt_br_dmy':
                            day, month, year = match.groups()
                        else:  # iso
                            year, month, day = match.groups()
                        
                        date = datetime(int(year), int(month), int(day))
                        date_str = date.strftime("%d/%m/%Y")
                        
                        # Verifica se é data de encerramento (palavras-chave)
                        if any(keyword in match.group(0) for keyword in ['encerra', 'expira', 'até', 'válido', 'finaliza']):
                            closing_date = date_str
                        else:
                            posted_date = date_str
                        
                        break
                    except (ValueError, OverflowError):
                        continue
        
        # Procura data de encerramento separadamente
        if not closing_date:
            closing_patterns = [
                r'(?:encerra|expira|válido até|válida até|até|finaliza).*?(\d{1,2})/(\d{1,2})/(\d{4})',
                r'(\d{1,2})/(\d{1,2})/(\d{4}).*?(?:encerra|expira|válido até|finaliza)',
            ]
            
            for pattern in closing_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        day, month, year = match.groups()
                        date = datetime(int(year), int(month), int(day))
                        closing_date = date.strftime("%d/%m/%Y")
                        break
                    except (ValueError, OverflowError):
                        continue
        
        return {
            'posted_date': posted_date,
            'closing_date': closing_date
        }
    
    def extract_site_name(self, url: str) -> str:
        """
        Extrai nome do site da URL
        
        Args:
            url: URL da vaga
            
        Returns:
            Nome do site formatado
        """
        if not url:
            return "Site desconhecido"
        
        try:
            # Remove protocolo
            url = url.replace('https://', '').replace('http://', '')
            # Pega domínio
            domain = url.split('/')[0]
            # Remove www.
            domain = domain.replace('www.', '')
            # Capitaliza
            return domain.split('.')[0].capitalize()
        except Exception:
            return "Site desconhecido"

