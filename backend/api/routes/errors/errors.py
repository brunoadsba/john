"""Rotas para monitoramento e análise de erros do mobile"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from backend.services.error_analysis import ErrorAnalysisService
from backend.database.database import Database
from .models import ErrorReportRequest
from .handlers import (
    handle_report_error,
    handle_get_analytics,
    handle_get_error,
    handle_resolve_error,
    handle_get_stats,
    handle_list_errors
)

router = APIRouter(prefix="/api/errors", tags=["errors"])

# Instâncias dos serviços (serão inicializadas no main.py)
database: Optional[Database] = None
error_analysis_service: Optional[ErrorAnalysisService] = None


def init_error_services(db: Database):
    """Inicializa serviços de erro"""
    global database, error_analysis_service
    database = db
    error_analysis_service = ErrorAnalysisService()


@router.post("/report")
async def report_error(request: ErrorReportRequest):
    """Recebe e processa erro reportado pelo mobile"""
    if not database or not error_analysis_service:
        raise HTTPException(status_code=503, detail="Error services não inicializados")
    
    try:
        return await handle_report_error(request, database, error_analysis_service)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar reporte de erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_error_analytics(
    error_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    level: Optional[str] = Query(None, description="Filtrar por nível"),
    resolved: Optional[bool] = Query(None, description="Filtrar por status"),
    limit: int = Query(100, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação")
):
    """Obtém analytics e estatísticas de erros"""
    if not database or not error_analysis_service:
        raise HTTPException(status_code=503, detail="Error services não inicializados")
    
    try:
        return await handle_get_analytics(
            database,
            error_analysis_service,
            error_type,
            level,
            resolved,
            limit,
            offset
        )
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_error_stats():
    """Obtém estatísticas de erros"""
    if not database:
        raise HTTPException(status_code=503, detail="Database não inicializado")
    
    try:
        return await handle_get_stats(database)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_errors(
    error_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    level: Optional[str] = Query(None, description="Filtrar por nível"),
    resolved: Optional[bool] = Query(None, description="Filtrar por status"),
    limit: int = Query(100, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação")
):
    """Lista erros com filtros"""
    if not database:
        raise HTTPException(status_code=503, detail="Database não inicializado")
    
    try:
        return await handle_list_errors(
            database,
            error_type,
            level,
            resolved,
            limit,
            offset
        )
    except Exception as e:
        logger.error(f"Erro ao listar erros: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{error_id}")
async def get_error(error_id: str):
    """Obtém detalhes de um erro específico"""
    if not database:
        raise HTTPException(status_code=503, detail="Database não inicializado")
    
    try:
        return await handle_get_error(error_id, database)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{error_id}/resolve")
async def resolve_error(
    error_id: str,
    resolution_notes: Optional[str] = None
):
    """Marca erro como resolvido"""
    if not database:
        raise HTTPException(status_code=503, detail="Database não inicializado")
    
    try:
        return await handle_resolve_error(error_id, database, resolution_notes)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao marcar erro como resolvido: {e}")
        raise HTTPException(status_code=500, detail=str(e))

