"""Analisa erros e gera soluções sugeridas"""
from typing import Dict, Optional, List
from .error_patterns import ERROR_PATTERNS


def analyze_error(
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
    message_lower = message.lower()
    stack_trace_lower = (stack_trace or "").lower()
    combined_text = f"{message_lower} {stack_trace_lower}"
    
    solutions = []
    
    # Busca padrões específicos do tipo de erro
    if error_type in ERROR_PATTERNS:
        for pattern_name, pattern_data in ERROR_PATTERNS[error_type].items():
            keywords = pattern_data["keywords"]
            if any(keyword in combined_text for keyword in keywords):
                solutions.extend(pattern_data["solutions"])
                break
    
    # Se não encontrou padrão específico, usa soluções genéricas
    if not solutions:
        if error_type == "network":
            solutions = [
                "Verifique a conexão com o servidor",
                "Confirme que o backend está rodando",
                "Teste a conectividade de rede"
            ]
        elif error_type == "audio":
            solutions = [
                "Verifique as permissões de áudio",
                "Confirme que o microfone está funcionando",
                "Reinicie o app e tente novamente"
            ]
        elif error_type == "permission":
            solutions = [
                "Verifique as permissões do app nas configurações",
                "Permita todas as permissões necessárias",
                "Reinicie o app após conceder permissões"
            ]
        elif error_type == "crash":
            solutions = [
                "Reinicie o app",
                "Atualize para a versão mais recente",
                "Reporte o erro se persistir"
            ]
        else:
            solutions = [
                "Tente novamente",
                "Reinicie o app",
                "Verifique as configurações",
                "Reporte o erro se persistir"
            ]
    
    # Remove duplicatas mantendo ordem
    seen = set()
    unique_solutions = []
    for solution in solutions:
        if solution not in seen:
            seen.add(solution)
            unique_solutions.append(solution)
    
    return unique_solutions[:5]  # Limita a 5 soluções


def get_error_severity(error_type: str, level: str) -> str:
    """
    Determina severidade do erro
    
    Args:
        error_type: Tipo do erro
        level: Nível (error, warning, critical)
        
    Returns:
        Severidade (low, medium, high, critical)
    """
    if level == "critical" or error_type == "crash":
        return "critical"
    elif level == "error" and error_type in ["network", "audio"]:
        return "high"
    elif level == "warning":
        return "medium"
    else:
        return "low"

