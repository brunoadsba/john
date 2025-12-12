"""
Funções auxiliares para JobSearchPlugin
Compatibilidade: Re-exporta classes dos módulos separados
"""
# Re-exporta classes dos módulos separados para compatibilidade
from backend.plugins.job_query_builder import JobSearchQueryBuilder
from backend.plugins.job_result_filter import JobSearchFilter
from backend.plugins.job_result_formatter import JobSearchFormatter

__all__ = [
    "JobSearchQueryBuilder",
    "JobSearchFilter",
    "JobSearchFormatter",
]
