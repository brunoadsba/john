"""
Utilitários para formatação de respostas do Architecture Advisor
"""
from typing import Dict


def format_architecture_response(data: Dict, intent: str) -> str:
    """
    Formata resultado do Architecture Advisor para exibição
    
    Args:
        data: Dados retornados pelo plugin
        intent: Intenção detectada
        
    Returns:
        String formatada
    """
    formatted = ""
    
    if intent == "analyze_requirements":
        if "functional_requirements" in data:
            formatted += "Requisitos Funcionais:\n"
            for req in data["functional_requirements"]:
                formatted += f"- {req}\n"
        
        if "non_functional_requirements" in data:
            formatted += "\nRequisitos Não-Funcionais:\n"
            for req in data["non_functional_requirements"]:
                formatted += f"- {req}\n"
        
        if "use_cases" in data:
            formatted += "\nCasos de Uso:\n"
            for uc in data["use_cases"]:
                formatted += f"- {uc}\n"
        
        if "edge_cases" in data:
            formatted += "\nCasos Extremos a Considerar:\n"
            for ec in data["edge_cases"]:
                formatted += f"- {ec}\n"
    
    elif intent == "security_checklist":
        if "items" in data:
            formatted += "Checklist de Segurança:\n"
            for item in data["items"]:
                formatted += f"- {item}\n"
    
    elif intent == "design_architecture":
        if "recommended_pattern" in data:
            formatted += f"Padrão Recomendado: {data['recommended_pattern']}\n"
        if "recommended_stack" in data:
            formatted += f"\nStack Recomendada: {', '.join(data['recommended_stack'])}\n"
        if "architecture_diagram" in data:
            formatted += f"\nDiagrama:\n{data['architecture_diagram']}\n"
    
    elif intent == "compare_solutions":
        if "comparison" in data:
            formatted += "Comparação:\n"
            for key, value in data["comparison"].items():
                formatted += f"{key}: {value}\n"
        if "recommendation" in data:
            formatted += f"\nRecomendação: {data['recommendation']}\n"
    
    elif intent == "plan_scalability":
        if "bottlenecks" in data:
            formatted += "Gargalos Identificados:\n"
            for bottleneck in data["bottlenecks"]:
                formatted += f"- {bottleneck}\n"
        if "optimizations" in data:
            formatted += "\nOtimizações Sugeridas:\n"
            for opt in data["optimizations"]:
                formatted += f"- {opt}\n"
    
    return formatted if formatted else str(data)


def create_natural_response(formatted_data: str, intent: str) -> str:
    """
    Cria resposta natural baseada no resultado do Architecture Advisor
    Sem precisar chamar LLM novamente (otimização de performance)
    
    Args:
        formatted_data: Dados formatados do plugin
        intent: Intenção detectada
        
    Returns:
        Resposta natural em português
    """
    # Respostas pré-formatadas baseadas na intenção
    responses = {
        "analyze_requirements": (
            "Analisei os requisitos do seu projeto. Aqui está o que identifiquei:\n\n"
            f"{formatted_data}\n\n"
            "Esses são os pontos principais a considerar antes de começar a implementação."
        ),
        "security_checklist": (
            "Preparei um checklist de segurança personalizado para o seu projeto:\n\n"
            f"{formatted_data}\n\n"
            "Certifique-se de implementar todos esses itens para garantir a segurança do sistema."
        ),
        "design_architecture": (
            "Sugeri uma arquitetura adequada para o seu projeto:\n\n"
            f"{formatted_data}\n\n"
            "Essa arquitetura foi escolhida considerando os requisitos e melhores práticas da indústria."
        ),
        "compare_solutions": (
            "Comparei as soluções solicitadas:\n\n"
            f"{formatted_data}\n\n"
            "Use essas informações para tomar a melhor decisão para o seu caso específico."
        ),
        "plan_scalability": (
            "Planejei a escalabilidade do seu sistema:\n\n"
            f"{formatted_data}\n\n"
            "Essas são as principais considerações para garantir que o sistema cresça adequadamente."
        ),
    }
    
    # Retorna resposta pré-formatada ou dados formatados
    base_response = responses.get(intent, formatted_data)
    
    # Limita tamanho para resposta de voz (máximo ~500 caracteres)
    if len(base_response) > 500:
        # Pega primeira parte e adiciona indicação de continuação
        lines = base_response.split('\n')
        response_parts = []
        char_count = 0
        
        for line in lines:
            if char_count + len(line) > 450:
                response_parts.append("\n\nPara mais detalhes, consulte a análise completa.")
                break
            response_parts.append(line)
            char_count += len(line) + 1
        
        return '\n'.join(response_parts)
    
    return base_response

