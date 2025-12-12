"""
Funções auxiliares para execução do JobSearchPlugin
"""
from typing import List, Dict
from loguru import logger


def search_with_retry(
    web_search_plugin,
    query: str,
    max_results: int,
    max_retries: int = 2
) -> List[Dict[str, str]]:
    """
    Busca com retry automático em caso de falha
    
    Args:
        web_search_plugin: Instância do WebSearchPlugin
        query: Query de busca
        max_results: Número máximo de resultados
        max_retries: Número máximo de tentativas
        
    Returns:
        Lista de resultados ou lista vazia
    """
    for attempt in range(max_retries + 1):
        try:
            results = web_search_plugin.search(
                query,
                max_results=max_results * 2
            )
            
            if results:
                return results
            
            if attempt < max_retries:
                logger.debug(f"🔄 Tentativa {attempt + 1} sem resultados, tentando novamente...")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro na tentativa {attempt + 1}: {e}")
            if attempt < max_retries:
                logger.debug(f"🔄 Tentando novamente...")
            else:
                logger.error(f"❌ Todas as tentativas falharam: {e}")
    
    return []


def get_no_results_message(
    cargo: str,
    localizacao: str,
    area: str
) -> str:
    """
    Gera mensagem personalizada quando não há resultados
    
    Args:
        cargo: Cargo procurado
        localizacao: Localização procurada
        area: Área procurada
        
    Returns:
        Mensagem de erro com sugestões
    """
    suggestions = []
    
    if cargo:
        suggestions.append(f"tente buscar por termos relacionados a '{cargo}'")
    if localizacao:
        suggestions.append(f"tente uma busca sem especificar '{localizacao}'")
    if area:
        suggestions.append(f"tente buscar por termos mais genéricos na área de '{area}'")
    
    if not suggestions:
        suggestions.append("tente especificar um cargo ou área de interesse")
    
    suggestion_text = " ou ".join(suggestions[:2])
    
    return f"❌ Nenhuma vaga encontrada. {suggestion_text.capitalize()}."

