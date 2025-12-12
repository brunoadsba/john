"""
Rotas REST para gerenciamento de histórico de conversas
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from loguru import logger

from backend.services.conversation_history_service import ConversationHistoryService
from backend.services.context_manager import ContextManager


router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Instâncias dos serviços (serão inicializadas)
history_service: Optional[ConversationHistoryService] = None
context_manager: Optional[ContextManager] = None


def init_services(
    history: ConversationHistoryService,
    context: ContextManager
):
    """Inicializa serviços nas rotas"""
    global history_service, context_manager
    history_service = history
    context_manager = context
    logger.info("Conversations routes inicializadas")


# Modelos Pydantic
class SaveConversationRequest(BaseModel):
    """Request para salvar conversa"""
    session_id: str = Field(..., description="ID da sessão")
    title: str = Field(..., min_length=1, max_length=200, description="Título da conversa")
    user_id: Optional[str] = Field(None, description="ID do usuário (opcional)")


class UpdateTitleRequest(BaseModel):
    """Request para atualizar título"""
    title: str = Field(..., min_length=1, max_length=200, description="Novo título")


@router.post("/save", response_model=Dict[str, Any])
async def save_conversation(request: SaveConversationRequest):
    """
    Salva uma conversa no histórico
    
    - **session_id**: ID da sessão a ser salva
    - **title**: Título da conversa
    - **user_id**: ID do usuário (opcional)
    """
    if not history_service or not context_manager:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    try:
        # Obtém mensagens da sessão
        session_info = context_manager.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail=f"Sessão {request.session_id} não encontrada"
            )
        
        # Obtém contexto formatado
        messages = context_manager.get_context(request.session_id)
        if not messages:
            raise HTTPException(
                status_code=400,
                detail="Sessão não possui mensagens para salvar"
            )
        
        # Salva conversa
        conversation_id = await history_service.save_conversation(
            session_id=request.session_id,
            title=request.title,
            messages=messages,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "session_id": request.session_id,
            "title": request.title
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao salvar conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar conversa")


@router.get("", response_model=Dict[str, Any])
async def list_conversations(
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuário")
):
    """
    Lista conversas salvas
    
    - **limit**: Número máximo de resultados (1-100)
    - **offset**: Offset para paginação
    - **user_id**: Filtrar por usuário (opcional)
    """
    if not history_service:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    try:
        conversations = await history_service.get_saved_conversations(
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        return {
            "success": True,
            "conversations": conversations,
            "count": len(conversations),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar conversas")


@router.get("/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(conversation_id: int):
    """
    Recupera uma conversa específica
    
    - **conversation_id**: ID da conversa
    """
    if not history_service:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    try:
        conversation = await history_service.get_conversation_by_id(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversa {conversation_id} não encontrada"
            )
        
        return {
            "success": True,
            "conversation": conversation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao recuperar conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao recuperar conversa")


@router.delete("/{conversation_id}", response_model=Dict[str, Any])
async def delete_conversation(conversation_id: int):
    """
    Remove uma conversa salva
    
    - **conversation_id**: ID da conversa a ser deletada
    """
    if not history_service:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    try:
        deleted = await history_service.delete_conversation(conversation_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Conversa {conversation_id} não encontrada"
            )
        
        return {
            "success": True,
            "message": f"Conversa {conversation_id} deletada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar conversa")


@router.patch("/{conversation_id}/title", response_model=Dict[str, Any])
async def update_conversation_title(
    conversation_id: int,
    request: UpdateTitleRequest
):
    """
    Atualiza o título de uma conversa
    
    - **conversation_id**: ID da conversa
    - **title**: Novo título
    """
    if not history_service:
        raise HTTPException(status_code=503, detail="Serviços não inicializados")
    
    try:
        updated = await history_service.update_conversation_title(
            conversation_id=conversation_id,
            new_title=request.title
        )
        
        if not updated:
            raise HTTPException(
                status_code=404,
                detail=f"Conversa {conversation_id} não encontrada"
            )
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "title": request.title
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar título: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar título")

