"""
Rotas para feedback e coleta de dados
"""
from fastapi import APIRouter, HTTPException, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from loguru import logger
from pydantic import BaseModel

from backend.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Instância do serviço (será inicializada no main.py)
feedback_service: Optional[FeedbackService] = None


def init_feedback_service(service: FeedbackService):
    """Inicializa o serviço de feedback"""
    global feedback_service
    feedback_service = service


class FeedbackRequest(BaseModel):
    """Modelo de requisição de feedback"""
    conversation_id: Optional[int] = None
    rating: int  # -1 para negativo, 1 para positivo, ou 1-5
    comment: Optional[str] = None


@router.post("")
async def submit_feedback(request: FeedbackRequest):
    """
    Recebe feedback do usuário
    
    Args:
        request: Dados do feedback
        
    Returns:
        ID do feedback salvo
    """
    if not feedback_service:
        raise HTTPException(status_code=503, detail="Feedback service não inicializado")
    
    try:
        # Valida rating
        if request.rating not in [-1, 1] and not (1 <= request.rating <= 5):
            raise HTTPException(
                status_code=400,
                detail="Rating deve ser -1, 1, ou um valor entre 1 e 5"
            )
        
        feedback_id = await feedback_service.save_feedback(
            conversation_id=request.conversation_id,
            rating=request.rating,
            comment=request.comment
        )
        
        return JSONResponse({
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback salvo com sucesso"
        })
    
    except Exception as e:
        logger.error(f"Erro ao salvar feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_feedback_stats():
    """
    Obtém estatísticas de feedback
    
    Returns:
        Estatísticas de feedback e conversas
    """
    if not feedback_service:
        raise HTTPException(status_code=503, detail="Feedback service não inicializado")
    
    try:
        stats = await feedback_service.get_feedback_stats()
        return JSONResponse(stats)
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_training_dataset(
    format: str = Query("alpaca", description="Formato de exportação (alpaca ou jsonl)"),
    min_quality: float = Query(0.7, description="Score mínimo de qualidade (0-1)"),
    limit: Optional[int] = Query(None, description="Limite de exemplos")
):
    """
    Exporta dataset para treinamento
    
    Args:
        format: Formato de exportação
        min_quality: Score mínimo de qualidade
        limit: Limite de exemplos
        
    Returns:
        Arquivo JSON com dataset
    """
    if not feedback_service:
        raise HTTPException(status_code=503, detail="Feedback service não inicializado")
    
    if format not in ["alpaca", "jsonl"]:
        raise HTTPException(
            status_code=400,
            detail="Formato deve ser 'alpaca' ou 'jsonl'"
        )
    
    try:
        output_path = await feedback_service.export_training_dataset(
            output_path="data/training/dataset_export.json",
            format=format,
            min_quality=min_quality,
            limit=limit
        )
        
        return FileResponse(
            output_path,
            media_type="application/json",
            filename=f"training_dataset.{format}.json"
        )
    
    except Exception as e:
        logger.error(f"Erro ao exportar dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations(
    session_id: Optional[str] = Query(None, description="Filtrar por session_id"),
    limit: int = Query(100, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação")
):
    """
    Lista conversas coletadas
    
    Args:
        session_id: Filtrar por sessão
        limit: Limite de resultados
        offset: Offset para paginação
        
    Returns:
        Lista de conversas
    """
    if not feedback_service:
        raise HTTPException(status_code=503, detail="Feedback service não inicializado")
    
    try:
        conversations = await feedback_service.db.list_conversations(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse({
            "success": True,
            "count": len(conversations),
            "conversations": conversations
        })
    
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

