"""
Gerenciador de contexto de conversação
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger


class ContextManager:
    """Gerencia o contexto e histórico de conversações"""
    
    def __init__(self, max_history: int = 10, session_timeout: int = 3600):
        """
        Inicializa o gerenciador de contexto
        
        Args:
            max_history: Número máximo de mensagens no histórico
            session_timeout: Tempo em segundos para expirar sessão inativa
        """
        self.max_history = max_history
        self.session_timeout = session_timeout
        self.sessions: Dict[str, dict] = {}
        
        logger.info(
            f"Context Manager inicializado: "
            f"max_history={max_history}, timeout={session_timeout}s"
        )
    
    def create_session(self) -> str:
        """
        Cria nova sessão de conversação
        
        Returns:
            ID da sessão criada
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "messages": [],
            "location": None  # {latitude, longitude, address_info}
        }
        
        logger.info(f"Nova sessão criada: {session_id}")
        return session_id
    
    def add_message(
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
        if session_id not in self.sessions:
            logger.warning(f"Sessão {session_id} não encontrada, criando nova")
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "messages": []
            }
        
        session = self.sessions[session_id]
        
        # Adiciona mensagem
        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # Atualiza última atividade
        session["last_activity"] = datetime.now()
        
        # Limita tamanho do histórico
        if len(session["messages"]) > self.max_history:
            session["messages"] = session["messages"][-self.max_history:]
        
        logger.debug(
            f"Mensagem adicionada à sessão {session_id}: "
            f"{role} - {content[:50]}..."
        )
    
    def get_context(self, session_id: str) -> List[Dict[str, str]]:
        """
        Obtém contexto da sessão para o LLM
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Lista de mensagens formatadas para o LLM
        """
        if session_id not in self.sessions:
            logger.warning(f"Sessão {session_id} não encontrada")
            return []
        
        session = self.sessions[session_id]
        
        # Retorna mensagens no formato esperado pelo LLM
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in session["messages"]
        ]
    
    def clear_session(self, session_id: str):
        """
        Limpa histórico de uma sessão
        
        Args:
            session_id: ID da sessão
        """
        if session_id in self.sessions:
            self.sessions[session_id]["messages"] = []
            logger.info(f"Histórico da sessão {session_id} limpo")
    
    def delete_session(self, session_id: str):
        """
        Remove uma sessão completamente
        
        Args:
            session_id: ID da sessão
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Sessão {session_id} removida")
    
    def cleanup_expired_sessions(self):
        """Remove sessões expiradas"""
        now = datetime.now()
        expired = []
        
        for session_id, session in self.sessions.items():
            last_activity = session["last_activity"]
            if (now - last_activity).total_seconds() > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            self.delete_session(session_id)
        
        if expired:
            logger.info(f"Removidas {len(expired)} sessões expiradas")
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        Obtém informações sobre uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dicionário com informações da sessão ou None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "message_count": len(session["messages"]),
            "is_active": (
                datetime.now() - session["last_activity"]
            ).total_seconds() < self.session_timeout
        }
    
    def get_all_sessions(self) -> List[str]:
        """
        Lista todas as sessões ativas
        
        Returns:
            Lista de IDs de sessão
        """
        return list(self.sessions.keys())
    
    def set_location(
        self,
        session_id: str,
        latitude: float,
        longitude: float,
        address_info: Optional[Dict] = None
    ):
        """
        Define localização para uma sessão
        
        Args:
            session_id: ID da sessão
            latitude: Latitude
            longitude: Longitude
            address_info: Informações de endereço (opcional)
        """
        if session_id not in self.sessions:
            logger.warning(f"Sessão {session_id} não encontrada, criando nova")
            self.create_session()
        
        self.sessions[session_id]["location"] = {
            "latitude": latitude,
            "longitude": longitude,
            "address_info": address_info,
            "updated_at": datetime.now()
        }
        logger.debug(f"Localização definida para sessão {session_id}: {latitude}, {longitude}")
    
    def get_location(self, session_id: str) -> Optional[Dict]:
        """
        Obtém localização de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dict com localização ou None
        """
        if session_id not in self.sessions:
            return None
        
        return self.sessions[session_id].get("location")

