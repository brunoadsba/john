"""
Serviço de histórico de conversas salvas
"""
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

from backend.database.database import Database


class ConversationHistoryService:
    """Gerencia histórico de conversas salvas"""
    
    def __init__(self, database: Database):
        """
        Inicializa o serviço de histórico
        
        Args:
            database: Instância do banco de dados
        """
        self.db = database
        logger.info("ConversationHistoryService inicializado")
    
    async def save_conversation(
        self,
        session_id: str,
        title: str,
        messages: List[Dict[str, str]],
        user_id: Optional[str] = None
    ) -> int:
        """
        Salva uma conversa no histórico
        
        Args:
            session_id: ID da sessão
            title: Título da conversa
            messages: Lista de mensagens [{role, content}]
            user_id: ID do usuário (opcional)
            
        Returns:
            ID da conversa salva
            
        Raises:
            ValueError: Se session_id ou title estiverem vazios
        """
        if not session_id or not title:
            raise ValueError("session_id e title são obrigatórios")
        
        if not messages:
            raise ValueError("messages não pode estar vazio")
        
        await self.db.connect()
        
        try:
            messages_json = json.dumps(messages, ensure_ascii=False)
            
            # Verifica se já existe conversa para esta sessão
            async with self.db._connection.execute(
                "SELECT id FROM saved_conversations WHERE session_id = ?",
                (session_id,)
            ) as cursor:
                existing = await cursor.fetchone()
            
            if existing:
                # Atualiza conversa existente
                await self.db._connection.execute(
                    """
                    UPDATE saved_conversations
                    SET title = ?, messages = ?, updated_at = CURRENT_TIMESTAMP, saved = 1
                    WHERE session_id = ?
                    """,
                    (title, messages_json, session_id)
                )
                conversation_id = existing[0]
                logger.info(f"Conversa atualizada: {conversation_id} (session: {session_id})")
            else:
                # Cria nova conversa
                cursor = await self.db._connection.execute(
                    """
                    INSERT INTO saved_conversations 
                    (session_id, title, messages, saved, user_id)
                    VALUES (?, ?, ?, 1, ?)
                    """,
                    (session_id, title, messages_json, user_id)
                )
                conversation_id = cursor.lastrowid
                logger.info(f"Conversa salva: {conversation_id} (session: {session_id})")
            
            await self.db._connection.commit()
            return conversation_id
            
        except Exception as e:
            await self.db._connection.rollback()
            logger.error(f"Erro ao salvar conversa: {e}")
            raise
    
    async def get_saved_conversations(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista conversas salvas
        
        Args:
            limit: Número máximo de resultados
            offset: Offset para paginação
            user_id: Filtrar por usuário (opcional)
            
        Returns:
            Lista de conversas salvas
        """
        await self.db.connect()
        
        try:
            if user_id:
                async with self.db._connection.execute(
                    """
                    SELECT id, session_id, title, created_at, updated_at
                    FROM saved_conversations
                    WHERE saved = 1 AND user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (user_id, limit, offset)
                ) as cursor:
                    rows = await cursor.fetchall()
            else:
                async with self.db._connection.execute(
                    """
                    SELECT id, session_id, title, created_at, updated_at
                    FROM saved_conversations
                    WHERE saved = 1
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset)
                ) as cursor:
                    rows = await cursor.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "id": row[0],
                    "session_id": row[1],
                    "title": row[2],
                    "created_at": row[3],
                    "updated_at": row[4]
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Erro ao listar conversas: {e}")
            raise
    
    async def get_conversation_by_id(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera uma conversa específica
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            Conversa completa ou None se não encontrada
        """
        await self.db.connect()
        
        try:
            async with self.db._connection.execute(
                """
                SELECT id, session_id, title, messages, created_at, updated_at, user_id
                FROM saved_conversations
                WHERE id = ? AND saved = 1
                """,
                (conversation_id,)
            ) as cursor:
                row = await cursor.fetchone()
            
            if not row:
                return None
            
            messages = json.loads(row[3]) if row[3] else []
            
            return {
                "id": row[0],
                "session_id": row[1],
                "title": row[2],
                "messages": messages,
                "created_at": row[4],
                "updated_at": row[5],
                "user_id": row[6]
            }
            
        except Exception as e:
            logger.error(f"Erro ao recuperar conversa: {e}")
            raise
    
    async def delete_conversation(self, conversation_id: int) -> bool:
        """
        Remove uma conversa salva
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            True se deletada, False se não encontrada
        """
        await self.db.connect()
        
        try:
            cursor = await self.db._connection.execute(
                "DELETE FROM saved_conversations WHERE id = ?",
                (conversation_id,)
            )
            await self.db._connection.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Conversa deletada: {conversation_id}")
            
            return deleted
            
        except Exception as e:
            await self.db._connection.rollback()
            logger.error(f"Erro ao deletar conversa: {e}")
            raise
    
    async def update_conversation_title(
        self,
        conversation_id: int,
        new_title: str
    ) -> bool:
        """
        Atualiza o título de uma conversa
        
        Args:
            conversation_id: ID da conversa
            new_title: Novo título
            
        Returns:
            True se atualizada, False se não encontrada
        """
        if not new_title:
            raise ValueError("new_title não pode estar vazio")
        
        await self.db.connect()
        
        try:
            cursor = await self.db._connection.execute(
                """
                UPDATE saved_conversations
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (new_title, conversation_id)
            )
            await self.db._connection.commit()
            
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Título da conversa atualizado: {conversation_id}")
            
            return updated
            
        except Exception as e:
            await self.db._connection.rollback()
            logger.error(f"Erro ao atualizar título: {e}")
            raise

