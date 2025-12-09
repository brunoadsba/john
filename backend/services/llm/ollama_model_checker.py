"""
Verificação de modelos e disponibilidade do Ollama
"""
from typing import Optional, List
from loguru import logger

try:
    import ollama
except ImportError:
    ollama = None


def check_finetuned_model(
    host: str,
    base_model: str,
    finetuned_model: Optional[str]
) -> str:
    """
    Verifica e retorna o modelo a ser usado (fine-tunado ou base)
    
    Args:
        host: URL do servidor Ollama
        base_model: Nome do modelo base
        finetuned_model: Nome do modelo fine-tunado (opcional)
        
    Returns:
        Nome do modelo a ser usado
    """
    if not finetuned_model:
        return base_model
    
    if not ollama:
        logger.warning(f"Ollama não disponível, usando modelo base: {base_model}")
        return base_model
    
    try:
        client = ollama.Client(host=host)
        # Tenta listar modelos para verificar se existe
        models = client.list()
        model_names = [m.get("name", "") for m in models.get("models", [])]
        
        if finetuned_model in model_names:
            logger.info(f"Usando modelo fine-tunado: {finetuned_model}")
            return finetuned_model
        else:
            logger.warning(f"Modelo fine-tunado '{finetuned_model}' não encontrado, usando base: {base_model}")
            return base_model
    except Exception as e:
        logger.warning(f"Erro ao verificar modelo fine-tunado: {e}, usando base: {base_model}")
        return base_model


def is_ollama_ready(
    client,
    model: str
) -> bool:
    """
    Verifica se o serviço Ollama está pronto e o modelo está disponível
    
    Args:
        client: Cliente Ollama configurado
        model: Nome do modelo a verificar
        
    Returns:
        True se o serviço está pronto, False caso contrário
    """
    try:
        if ollama is None:
            return False
        
        if not client:
            return False
        
        # Tenta listar modelos para verificar conexão
        models_response = client.list()
        
        # Extrai lista de modelos de forma robusta
        models_list = _extract_models_list(models_response)
        
        if not models_list:
            logger.warning(f"[Ollama] Formato de resposta inesperado: {type(models_response)}")
            return False
        
        # Extrai nomes dos modelos
        model_names = _extract_model_names(models_list)
        
        # Verifica se o modelo está disponível
        model_available = any(model in name for name in model_names)
        
        if not model_available:
            logger.warning(
                f"[Ollama] Modelo {model} não encontrado. "
                f"Modelos disponíveis: {model_names}"
            )
        
        return model_available
        
    except KeyError as e:
        logger.error(f"[Ollama] Chave não encontrada na resposta: {e}")
        return False
    except Exception as e:
        logger.error(f"[Ollama] Serviço não está pronto: {e}")
        return False


def _extract_models_list(models_response) -> List:
    """Extrai lista de modelos da resposta do Ollama"""
    if hasattr(models_response, 'models'):
        # Resposta é um objeto ListResponse
        return models_response.models
    elif isinstance(models_response, dict):
        # Resposta é um dict
        return models_response.get('models', [])
    elif isinstance(models_response, list):
        # Resposta é uma lista direta
        return models_response
    else:
        return []


def _extract_model_names(models_list: List) -> List[str]:
    """Extrai nomes dos modelos de forma robusta"""
    model_names = []
    for m in models_list:
        # Pode ser objeto Model, dict ou string
        if hasattr(m, 'model'):
            # Objeto Model do Ollama
            model_names.append(m.model)
        elif hasattr(m, 'name'):
            # Objeto com atributo 'name'
            model_names.append(m.name)
        elif isinstance(m, dict):
            # Dict - tenta diferentes chaves
            name = m.get('model') or m.get('name') or m.get('model_name')
            if name:
                model_names.append(name)
        elif isinstance(m, str):
            # String direta
            model_names.append(m)
    
    return model_names

