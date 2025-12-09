"""Handlers para rotas de erros"""
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from loguru import logger
import uuid

from backend.services.error_analysis import ErrorAnalysisService
from backend.database.database import Database
from .models import ErrorReportRequest


async def handle_report_error(
    request: ErrorReportRequest,
    database: Database,
    error_analysis_service: ErrorAnalysisService
) -> JSONResponse:
    """
    Processa reporte de erro
    
    Args:
        request: Dados do erro
        database: Instância do banco de dados
        error_analysis_service: Serviço de análise
        
    Returns:
        Resposta JSON com error_id e soluções
    """
    # Valida nível
    if request.level not in ["error", "warning", "critical"]:
        raise HTTPException(
            status_code=400,
            detail="Level deve ser 'error', 'warning' ou 'critical'"
        )
    
    # Valida tipo
    valid_types = ["network", "audio", "permission", "crash", "other"]
    if request.type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Type deve ser um de: {', '.join(valid_types)}"
        )
    
    # Gera ID único
    error_id = str(uuid.uuid4())
    
    # Analisa erro e gera soluções
    solutions = error_analysis_service.analyze_error(
        error_type=request.type,
        message=request.message,
        stack_trace=request.stack_trace,
        context=request.context
    )
    
    suggested_solution = "\n".join(solutions) if solutions else None
    
    # Salva no banco
    error_row_id = await database.save_error(
        error_id=error_id,
        level=request.level,
        error_type=request.type,
        message=request.message,
        stack_trace=request.stack_trace,
        device_info=request.device_info,
        context=request.context,
        suggested_solution=suggested_solution
    )
    
    logger.info(f"Erro reportado: {error_id} ({request.type}) - {request.message[:50]}")
    
    return JSONResponse({
        "success": True,
        "error_id": error_id,
        "error_row_id": error_row_id,
        "suggested_solutions": solutions,
        "severity": error_analysis_service.get_error_severity(
            request.type,
            request.level
        )
    })


async def handle_get_analytics(
    database: Database,
    error_analysis_service: ErrorAnalysisService,
    error_type: Optional[str] = None,
    level: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> JSONResponse:
    """
    Obtém analytics de erros
    
    Args:
        database: Instância do banco de dados
        error_analysis_service: Serviço de análise
        error_type: Filtrar por tipo
        level: Filtrar por nível
        resolved: Filtrar por status
        limit: Limite de resultados
        offset: Offset para paginação
        
    Returns:
        Resposta JSON com estatísticas e erros
    """
    # Obtém estatísticas
    stats = await database.get_error_stats()
    
    # Lista erros
    errors = await database.list_errors(
        error_type=error_type,
        level=level,
        resolved=resolved,
        limit=limit,
        offset=offset
    )
    
    # Agrupa erros similares
    grouped_errors = error_analysis_service.group_similar_errors(errors)
    
    # Analisa tendências
    trends = error_analysis_service.get_error_trends(errors)
    
    return JSONResponse({
        "success": True,
        "stats": stats,
        "trends": trends,
        "errors": errors,
        "grouped_errors": {
            key: len(group) for key, group in grouped_errors.items()
        },
        "total": len(errors)
    })


async def handle_get_error(
    error_id: str,
    database: Database
) -> JSONResponse:
    """
    Obtém detalhes de um erro específico
    
    Args:
        error_id: ID do erro
        database: Instância do banco de dados
        
    Returns:
        Resposta JSON com detalhes do erro
    """
    error = await database.get_error(error_id)
    
    if not error:
        raise HTTPException(status_code=404, detail="Erro não encontrado")
    
    return JSONResponse({
        "success": True,
        "error": error
    })


async def handle_resolve_error(
    error_id: str,
    database: Database,
    resolution_notes: Optional[str] = None
) -> JSONResponse:
    """
    Marca erro como resolvido
    
    Args:
        error_id: ID do erro
        database: Instância do banco de dados
        resolution_notes: Notas sobre a resolução
        
    Returns:
        Resposta JSON de confirmação
    """
    success = await database.mark_error_resolved(error_id, resolution_notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Erro não encontrado")
    
    return JSONResponse({
        "success": True,
        "message": "Erro marcado como resolvido"
    })


async def handle_get_stats(
    database: Database
) -> JSONResponse:
    """
    Obtém estatísticas de erros
    
    Args:
        database: Instância do banco de dados
        
    Returns:
        Resposta JSON com estatísticas
    """
    stats = await database.get_error_stats()
    
    return JSONResponse({
        "success": True,
        "stats": stats
    })


async def handle_list_errors(
    database: Database,
    error_type: Optional[str] = None,
    level: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> JSONResponse:
    """
    Lista erros com filtros
    
    Args:
        database: Instância do banco de dados
        error_type: Filtrar por tipo
        level: Filtrar por nível
        resolved: Filtrar por status
        limit: Limite de resultados
        offset: Offset para paginação
        
    Returns:
        Resposta JSON com lista de erros
    """
    errors = await database.list_errors(
        error_type=error_type,
        level=level,
        resolved=resolved,
        limit=limit,
        offset=offset
    )
    
    return JSONResponse({
        "success": True,
        "errors": errors,
        "total": len(errors),
        "limit": limit,
        "offset": offset
    })

