"""
Rotas para gerenciamento de Modo Privacidade
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from backend.services.privacy.privacy_mode_service import PrivacyModeService

router = APIRouter(prefix="/api/settings", tags=["Privacy"])

# Instância global do serviço (será inicializada)
privacy_service: Optional[PrivacyModeService] = None


def init_privacy_service(service: PrivacyModeService):
    """Inicializa serviço de privacidade nas rotas"""
    global privacy_service
    privacy_service = service
    logger.info("✅ Privacy routes inicializadas")


class PrivacySettings(BaseModel):
    """Request body para toggle de modo privacidade"""
    enabled: bool


class PrivacyStatusResponse(BaseModel):
    """Response de status de privacidade"""
    privacy_mode: bool
    current_provider: str
    groq_available: bool
    ollama_available: bool
    active_service_available: bool
    message: str


@router.post("/privacy-mode", response_model=dict)
async def toggle_privacy_mode(settings: PrivacySettings):
    """
    Ativa ou desativa o modo privacidade
    
    - enabled=True: Ativa modo privacidade (LLM local/Ollama, desativa plugins de rede)
    - enabled=False: Desativa modo privacidade (LLM cloud/Groq, ativa todos plugins)
    """
    if not privacy_service:
        raise HTTPException(
            status_code=503,
            detail="Serviço de privacidade não inicializado"
        )
    
    try:
        result = privacy_service.set_privacy_mode(settings.enabled)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Erro ao alterar modo privacidade")
            )
        
        # Determina tema UI sugerido
        ui_theme = "secure_green" if settings.enabled else "default_blue"
        
        return {
            "status": "success",
            "config": {
                "privacy_mode": result["privacy_mode"],
                "provider": result["provider"],
                "previous_mode": result.get("previous_mode")
            },
            "ui_theme": ui_theme,
            "message": result["message"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar modo privacidade: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar solicitação: {str(e)}"
        )


@router.get("/privacy-status", response_model=PrivacyStatusResponse)
async def get_privacy_status():
    """Retorna status atual do modo privacidade"""
    if not privacy_service:
        raise HTTPException(
            status_code=503,
            detail="Serviço de privacidade não inicializado"
        )
    
    try:
        status = privacy_service.get_status()
        
        mode_text = "privacidade (local)" if status["privacy_mode"] else "cloud"
        message = f"Modo {mode_text} ativo. Provider: {status['current_provider']}"
        
        if status["privacy_mode"] and not status["ollama_available"]:
            message += ". ⚠️ Ollama não disponível!"
        elif not status["privacy_mode"] and not status["groq_available"]:
            message += ". ⚠️ Groq não disponível!"
        
        return PrivacyStatusResponse(
            privacy_mode=status["privacy_mode"],
            current_provider=status["current_provider"],
            groq_available=status["groq_available"],
            ollama_available=status["ollama_available"],
            active_service_available=status["active_service_available"],
            message=message
        )
    except Exception as e:
        logger.error(f"Erro ao obter status de privacidade: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

