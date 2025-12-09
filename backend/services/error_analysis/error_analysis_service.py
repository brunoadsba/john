"""Serviço de análise de erros e sugestão de soluções"""
from typing import Dict, Optional, List
from loguru import logger

from .solution_analyzer import analyze_error, get_error_severity
from .trend_analyzer import group_similar_errors, get_error_trends


class ErrorAnalysisService:
    """Analisa erros e sugere soluções automaticamente"""
    
    def analyze_error(
        self,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> List[str]:
        """
        Analisa erro e retorna soluções sugeridas
        
        Args:
            error_type: Tipo do erro (network, audio, permission, crash, other)
            message: Mensagem do erro
            stack_trace: Stack trace (opcional)
            context: Contexto adicional (opcional)
            
        Returns:
            Lista de soluções sugeridas
        """
        return analyze_error(error_type, message, stack_trace, context)
    
    def get_error_severity(self, error_type: str, level: str) -> str:
        """
        Determina severidade do erro
        
        Args:
            error_type: Tipo do erro
            level: Nível (error, warning, critical)
            
        Returns:
            Severidade (low, medium, high, critical)
        """
        return get_error_severity(error_type, level)
    
    def group_similar_errors(
        self,
        errors: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Agrupa erros similares por mensagem/tipo
        
        Args:
            errors: Lista de erros
            
        Returns:
            Dicionário com erros agrupados
        """
        return group_similar_errors(errors)
    
    def get_error_trends(self, errors: List[Dict]) -> Dict[str, any]:
        """
        Analisa tendências de erros
        
        Args:
            errors: Lista de erros
            
        Returns:
            Dicionário com tendências
        """
        return get_error_trends(errors)

