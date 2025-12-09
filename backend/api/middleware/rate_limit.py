"""
Middleware de Rate Limiting
Protege endpoints críticos contra abuso
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from loguru import logger

# Cria instância do limiter
limiter = Limiter(key_func=get_remote_address)

# Configurações de rate limit por endpoint
RATE_LIMITS = {
    "auth": "10/minute",  # Login/registro
    "process": "30/minute",  # Processamento de áudio/texto
    "websocket": "60/minute",  # Conexões WebSocket
    "wake_word": "100/minute",  # Wake word (mais permissivo)
    "default": "100/hour"  # Limite padrão
}


def get_rate_limit(endpoint_type: str = "default") -> str:
    """
    Retorna o rate limit configurado para um tipo de endpoint
    
    Args:
        endpoint_type: Tipo do endpoint (auth, process, websocket, wake_word)
    
    Returns:
        String de rate limit no formato "X/minute" ou "X/hour"
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])


def setup_rate_limiting(app):
    """
    Configura rate limiting na aplicação FastAPI
    
    Args:
        app: Instância do FastAPI
    
    Returns:
        Instância do limiter
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("✅ Rate limiting configurado")
    return limiter


def get_client_ip(request: Request) -> str:
    """
    Obtém IP do cliente de forma segura
    
    Args:
        request: Request do FastAPI
    
    Returns:
        IP do cliente
    """
    # Tenta obter IP real (atrás de proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback para IP direto
    if request.client:
        return request.client.host
    
    return "unknown"

