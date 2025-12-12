"""
Rotas para gerenciamento de localização
"""
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from loguru import logger

from backend.services.context_manager import ContextManager
from backend.services.geocoding_service import GeocodingService


router = APIRouter(prefix="/api/location", tags=["location"])

# Instâncias dos serviços (serão inicializadas)
context_manager: Optional[ContextManager] = None
geocoding_service: Optional[GeocodingService] = None


def init_services(
    context: ContextManager,
    geocoding: GeocodingService
):
    """Inicializa serviços nas rotas"""
    global context_manager, geocoding_service
    context_manager = context
    geocoding_service = geocoding
    logger.info("Location routes inicializadas")


class LocationSubmitRequest(BaseModel):
    """Request para submeter localização"""
    session_id: str = Field(..., description="ID da sessão")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")


class LocationResponse(BaseModel):
    """Resposta de localização"""
    success: bool
    message: str
    address_info: Optional[dict] = None


@router.post("/submit", response_model=LocationResponse)
async def submit_location(request: LocationSubmitRequest):
    """
    Submete localização do usuário
    
    Args:
        request: Dados de localização
        
    Returns:
        Resposta com status e informações de endereço
    """
    if not context_manager or not geocoding_service:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    try:
        # Valida coordenadas
        if not (-90 <= request.latitude <= 90):
            raise HTTPException(
                status_code=400,
                detail="Latitude inválida (deve estar entre -90 e 90)"
            )
        
        if not (-180 <= request.longitude <= 180):
            raise HTTPException(
                status_code=400,
                detail="Longitude inválida (deve estar entre -180 e 180)"
            )
        
        # Faz geocodificação reversa
        address_info = await geocoding_service.reverse_geocode(
            request.latitude,
            request.longitude
        )
        
        # Armazena no contexto (async para ContextManagerDB)
        if hasattr(context_manager, 'set_location'):
            if asyncio.iscoroutinefunction(context_manager.set_location):
                await context_manager.set_location(
                    session_id=request.session_id,
                    latitude=request.latitude,
                    longitude=request.longitude,
                    address_info=address_info
                )
            else:
                context_manager.set_location(
                    session_id=request.session_id,
                    latitude=request.latitude,
                    longitude=request.longitude,
                    address_info=address_info
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="ContextManager não suporta localização"
            )
        
        logger.info(
            f"Localização salva para sessão {request.session_id}: "
            f"{request.latitude}, {request.longitude}"
        )
        
        return LocationResponse(
            success=True,
            message="Localização salva com sucesso",
            address_info=address_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao salvar localização: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar localização: {str(e)}"
        )


@router.get("/{session_id}")
async def get_location(session_id: str):
    """
    Obtém localização salva de uma sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        Informações de localização ou 404 se não encontrada
    """
    if not context_manager:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    # Obtém localização (async para ContextManagerDB)
    if hasattr(context_manager, 'get_location'):
        if asyncio.iscoroutinefunction(context_manager.get_location):
            location = await context_manager.get_location(session_id)
        else:
            location = context_manager.get_location(session_id)
    else:
        location = None
    
    if not location:
        raise HTTPException(
            status_code=404,
            detail="Localização não encontrada para esta sessão"
        )
    
    return {
        "success": True,
        "location": location
    }

