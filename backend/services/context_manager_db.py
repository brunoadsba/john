"""
Gerenciador de contexto de conversação com persistência em banco de dados
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from backend.database.database import Database


class ContextManagerDB:
    """Gerencia o contexto e histórico de conversações com persistência"""
    
    def __init__(
        self,
        database: Database,
        max_history: int = 10,
        session_timeout: int = 3600
    ):
        """
        Inicializa o gerenciador de contexto
        
        Args:
            database: Instância do banco de dados
            max_history: Número máximo de mensagens no histórico
            session_timeout: Tempo em segundos para expirar sessão inativa
        """
        self.db = database
        self.max_history = max_history
        self.session_timeout = session_timeout
        
        logger.info(
            f"Context Manager DB inicializado: "
            f"max_history={max_history}, timeout={session_timeout}s"
        )
    
    async def create_session(self, metadata: Optional[Dict] = None) -> str:
        """
        Cria nova sessão de conversação
        
        Returns:
            ID da sessão criada
        """
        session_id = str(uuid.uuid4())
        await self.db.create_session(session_id, metadata)
        logger.info(f"Nova sessão criada: {session_id}")
        return session_id
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """
        Adiciona mensagem ao histórico da sessão
        
        Args:
            session_id: ID da sessão
            role: Papel (user, assistant, system)
            content: Conteúdo da mensagem
        """
        await self.db.add_message(session_id, role, content)
        logger.debug(
            f"Mensagem adicionada à sessão {session_id}: "
            f"{role} - {content[:50]}..."
        )
    
    async def get_context(self, session_id: str) -> List[Dict[str, str]]:
        """
        Obtém contexto da sessão para o LLM
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Lista de mensagens formatadas para o LLM
        """
        return await self.db.get_context_for_llm(session_id, self.max_history)
    
    async def clear_session(self, session_id: str):
        """
        Limpa histórico de uma sessão
        
        Args:
            session_id: ID da sessão
        """
        await self.db.clear_messages(session_id)
        logger.info(f"Histórico da sessão {session_id} limpo")
    
    async def delete_session(self, session_id: str):
        """
        Remove uma sessão completamente
        
        Args:
            session_id: ID da sessão
        """
        await self.db.delete_session(session_id)
        logger.info(f"Sessão {session_id} removida")
    
    async def cleanup_expired_sessions(self):
        """Remove sessões expiradas"""
        sessions = await self.db.list_sessions(limit=1000)
        now = datetime.now()
        expired = []
        
        for session in sessions:
            last_activity = datetime.fromisoformat(session["last_activity"])
            if (now - last_activity).total_seconds() > self.session_timeout:
                expired.append(session["session_id"])
        
        for session_id in expired:
            await self.delete_session(session_id)
        
        if expired:
            logger.info(f"Removidas {len(expired)} sessões expiradas")
    
    async def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        Obtém informações sobre uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dicionário com informações da sessão ou None
        """
        session = await self.db.get_session(session_id)
        if not session:
            return None
        
        messages = await self.db.get_messages(session_id)
        
        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "message_count": len(messages),
            "is_active": (
                datetime.now() - datetime.fromisoformat(session["last_activity"])
            ).total_seconds() < self.session_timeout
        }
    
    async def get_all_sessions(self) -> List[str]:
        """
        Lista todas as sessões ativas
        
        Returns:
            Lista de IDs de sessão
        """
        sessions = await self.db.list_sessions()
        return [s["session_id"] for s in sessions]

