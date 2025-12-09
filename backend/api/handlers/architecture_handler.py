"""
Handler para processamento de intenções de arquitetura
"""
from typing import Optional, Dict, Any, Tuple
from loguru import logger

from backend.api.utils.architecture_formatter import (
    format_architecture_response,
    create_natural_response
)


async def handle_architecture_intent(
    intent_detector: Any,
    plugin_manager: Any,
    texto: str
) -> Optional[Tuple[str, Dict]]:
    """
    Detecta e processa intenção de arquitetura
    
    Args:
        intent_detector: Detector de intenções
        plugin_manager: Gerenciador de plugins
        texto: Texto do usuário
        
    Returns:
        Tupla (intent, plugin_result) ou None se não detectar
    """
    if not intent_detector or not plugin_manager:
        return None
    
    # Detecta intenção (apenas regex, rápido)
    intent, confidence = intent_detector.detect(texto, use_llm=False)
    if not intent or confidence <= 0.5:
        return None
    
    logger.info(f"🏗️ Intenção de arquitetura detectada: {intent} (confiança: {confidence:.2f})")
    
    # Obtém plugin
    advisor_plugin = plugin_manager.get_plugin("architecture_advisor")
    if not advisor_plugin:
        return None
    
    # Prepara argumentos baseado na intenção
    args = {"action": intent}
    
    # Extrai informações adicionais do texto
    if "mobile" in texto.lower() or "app" in texto.lower():
        args["project_type"] = "mobile"
    elif "web" in texto.lower() or "site" in texto.lower():
        args["project_type"] = "web"
    elif "api" in texto.lower():
        args["project_type"] = "api"
    
    # Adiciona descrição se disponível
    if intent in ["analyze_requirements", "design_architecture"]:
        args["description"] = texto
    
    # Adiciona features se mencionadas
    if intent == "security_checklist":
        features = []
        if "pagamento" in texto.lower() or "payment" in texto.lower():
            features.append("pagamentos")
        if "autenticação" in texto.lower() or "login" in texto.lower():
            features.append("autenticação")
        if features:
            args["features"] = features
    
    try:
        # Executa plugin
        plugin_result = advisor_plugin.execute("architecture_advisor", args)
        
        if plugin_result.get("success"):
            return (intent, plugin_result)
        else:
            logger.warning(f"Plugin retornou erro: {plugin_result.get('message')}")
            return None
    except Exception as e:
        logger.error(f"Erro ao executar Architecture Advisor: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def format_architecture_plugin_result(
    plugin_result: Dict,
    intent: str
) -> str:
    """
    Formata resultado do plugin de arquitetura em resposta natural
    
    Args:
        plugin_result: Resultado do plugin
        intent: Intenção detectada
        
    Returns:
        Resposta formatada em português
    """
    data = plugin_result.get("data", {})
    
    # Formata dados estruturados
    formatted_response = format_architecture_response(data, intent)
    
    # Cria resposta natural
    return create_natural_response(formatted_response, intent)

