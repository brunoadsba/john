"""
Detecção de intenção de busca de vagas
"""
from typing import Set


class JobSearchDetection:
    """Detecta se uma query é sobre busca de vagas"""
    
    JOB_KEYWORDS: Set[str] = {
        'vaga', 'vagas', 'emprego', 'trabalho', 'oportunidade',
        'oportunidades', 'cargo', 'posição', 'contratação', 'recrutamento',
        'carreira', 'profissional'
    }
    
    @staticmethod
    def is_job_query(query: str) -> bool:
        """
        Verifica se a query é sobre busca de vagas
        
        Args:
            query: Query do usuário
            
        Returns:
            True se é sobre vagas, False caso contrário
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in JobSearchDetection.JOB_KEYWORDS)

