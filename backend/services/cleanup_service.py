"""
Serviço de limpeza automática de dados antigos
"""
from datetime import datetime, timedelta
from loguru import logger
from backend.database.database import Database


class CleanupService:
    """Gerencia limpeza automática de dados antigos"""
    
    def __init__(self, database: Database):
        """
        Inicializa serviço de limpeza
        
        Args:
            database: Instância do banco de dados
        """
        self.db = database
        logger.info("CleanupService inicializado")
    
    async def cleanup_old_sessions(self, days: int = 7) -> int:
        """
        Remove sessões antigas (não utilizadas há X dias)
        
        Args:
            days: Número de dias de inatividade para considerar expirado
        
        Returns:
            Número de sessões removidas
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Busca sessões antigas
            async with self.db._connection.execute("""
                SELECT session_id FROM sessions 
                WHERE last_activity < ?
            """, (cutoff_date.isoformat(),)) as cursor:
                old_sessions = await cursor.fetchall()
            
            removed_count = 0
            for row in old_sessions:
                session_id = row["session_id"]
                await self.db.delete_session(session_id)
                removed_count += 1
            
            if removed_count > 0:
                logger.info(f"🗑️ Limpeza: {removed_count} sessão(ões) antiga(s) removida(s)")
            
            return removed_count
        except Exception as e:
            logger.error(f"Erro ao limpar sessões antigas: {e}")
            return 0
    
    async def cleanup_old_messages(self, days: int = 30) -> int:
        """
        Remove mensagens antigas (mais de X dias)
        
        Args:
            days: Idade mínima das mensagens para remover
        
        Returns:
            Número de mensagens removidas
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            async with self.db._connection.execute("""
                DELETE FROM messages 
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),)) as cursor:
                await self.db._connection.commit()
                removed_count = cursor.rowcount
            
            if removed_count > 0:
                logger.info(f"🗑️ Limpeza: {removed_count} mensagem(ns) antiga(s) removida(s)")
            
            return removed_count
        except Exception as e:
            logger.error(f"Erro ao limpar mensagens antigas: {e}")
            return 0
    
    async def cleanup_all(self, session_days: int = 7, message_days: int = 30) -> dict:
        """
        Executa todas as limpezas
        
        Args:
            session_days: Dias para considerar sessão expirada
            message_days: Dias para considerar mensagem antiga
        
        Returns:
            Dicionário com contadores de limpeza
        """
        sessions_removed = await self.cleanup_old_sessions(session_days)
        messages_removed = await self.cleanup_old_messages(message_days)
        
        return {
            "sessions_removed": sessions_removed,
            "messages_removed": messages_removed
        }

