"""
Gerenciamento de banco de dados SQLite
"""
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger


class Database:
    """Gerenciador de banco de dados SQLite"""
    
    def __init__(self, db_path: str = "data/jonh_assistant.db"):
        """
        Inicializa o banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None
        
        logger.info(f"Database inicializado: {self.db_path}")
    
    async def connect(self):
        """Conecta ao banco de dados"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(str(self.db_path))
            self._connection.row_factory = aiosqlite.Row
            await self._initialize_schema()
            logger.info("✅ Conectado ao banco de dados")
    
    async def close(self):
        """Fecha conexão com banco de dados"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("🔌 Conexão com banco de dados fechada")
    
    async def _initialize_schema(self):
        """Inicializa schema do banco de dados"""
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                metadata TEXT
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id, timestamp)
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                metadata TEXT
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_key 
            ON memories(key)
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_category 
            ON memories(category)
        """) as cursor:
            await self._connection.commit()
        
        # Tabela de conversas salvas (histórico de conversas)
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS saved_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                messages TEXT NOT NULL,
                saved BOOLEAN DEFAULT 1,
                user_id TEXT
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_saved_conversations_session 
            ON saved_conversations(session_id)
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_saved_conversations_created 
            ON saved_conversations(created_at DESC)
        """) as cursor:
            await self._connection.commit()
        
        # Tabela de conversas (para coleta de dados de treinamento)
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                tokens_used INTEGER,
                processing_time REAL,
                used_tool TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_session 
            ON conversations(session_id, created_at)
        """) as cursor:
            await self._connection.commit()
        
        # Tabela de feedback do usuário
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_conversation 
            ON feedback(conversation_id)
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_rating 
            ON feedback(rating, created_at)
        """) as cursor:
            await self._connection.commit()
        
        # Tabela de dados de treinamento (preparados para fine-tuning)
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instruction TEXT NOT NULL,
                input TEXT,
                output TEXT NOT NULL,
                source TEXT,
                quality_score REAL,
                created_at TIMESTAMP NOT NULL
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_training_data_source 
            ON training_data(source, quality_score)
        """) as cursor:
            await self._connection.commit()
        
        # Tabela de clusters de intenções
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS intent_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id INTEGER NOT NULL,
                intent_type TEXT NOT NULL,
                examples TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_intent_clusters_cluster 
            ON intent_clusters(cluster_id, intent_type)
        """) as cursor:
            await self._connection.commit()
        
        # Tabela de erros (monitoramento mobile)
        async with self._connection.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                level TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                stack_trace TEXT,
                device_info TEXT,
                context TEXT,
                suggested_solution TEXT,
                resolved BOOLEAN DEFAULT 0,
                resolution_notes TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_errors_timestamp 
            ON errors(timestamp DESC)
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_errors_type 
            ON errors(type, level)
        """) as cursor:
            await self._connection.commit()
        
        async with self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_errors_resolved 
            ON errors(resolved, timestamp DESC)
        """) as cursor:
            await self._connection.commit()
        
        logger.info("✅ Schema do banco de dados inicializado")
    
    # ========== SESSÕES ==========
    
    async def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> bool:
        """Cria nova sessão"""
        try:
            import json
            metadata_json = json.dumps(metadata) if metadata else None
            
            await self._connection.execute("""
                INSERT INTO sessions (session_id, created_at, last_activity, metadata)
                VALUES (?, ?, ?, ?)
            """, (session_id, datetime.now(), datetime.now(), metadata_json))
            
            await self._connection.commit()
            logger.debug(f"Sessão criada: {session_id}")
            return True
        except aiosqlite.IntegrityError:
            logger.warning(f"Sessão {session_id} já existe")
            return False
    
    async def update_session_activity(self, session_id: str):
        """Atualiza última atividade da sessão"""
        await self._connection.execute("""
            UPDATE sessions 
            SET last_activity = ? 
            WHERE session_id = ?
        """, (datetime.now(), session_id))
        await self._connection.commit()
    
    async def delete_session(self, session_id: str):
        """Remove sessão e todas suas mensagens"""
        await self._connection.execute("""
            DELETE FROM sessions WHERE session_id = ?
        """, (session_id,))
        await self._connection.commit()
        logger.info(f"Sessão {session_id} removida")
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Obtém informações da sessão"""
        async with self._connection.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                import json
                return {
                    "session_id": row["session_id"],
                    "created_at": row["created_at"],
                    "last_activity": row["last_activity"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
            return None
    
    async def list_sessions(self, limit: int = 100) -> List[Dict]:
        """Lista sessões"""
        async with self._connection.execute("""
            SELECT * FROM sessions 
            ORDER BY last_activity DESC 
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            import json
            return [
                {
                    "session_id": row["session_id"],
                    "created_at": row["created_at"],
                    "last_activity": row["last_activity"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
                for row in rows
            ]
    
    # ========== MENSAGENS ==========
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> int:
        """Adiciona mensagem ao histórico"""
        # Garante que sessão existe
        session = await self.get_session(session_id)
        if not session:
            await self.create_session(session_id)
        
        # Adiciona mensagem
        cursor = await self._connection.execute("""
            INSERT INTO messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, datetime.now()))
        
        await self._connection.commit()
        await self.update_session_activity(session_id)
        
        message_id = cursor.lastrowid
        logger.debug(f"Mensagem adicionada: {message_id} (sessão: {session_id})")
        return message_id
    
    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Obtém mensagens da sessão"""
        query = """
            SELECT * FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """
        params = [session_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"]
                }
                for row in rows
            ]
    
    async def clear_messages(self, session_id: str):
        """Limpa mensagens de uma sessão"""
        await self._connection.execute("""
            DELETE FROM messages WHERE session_id = ?
        """, (session_id,))
        await self._connection.commit()
        logger.info(f"Mensagens da sessão {session_id} limpas")
    
    # ========== MEMÓRIAS ==========
    
    async def save_memory(
        self,
        key: str,
        value: str,
        category: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Salva uma memória (nota/anotação)
        
        Args:
            key: Chave única da memória (ex: "nome_usuario", "preferencia_cor")
            value: Valor da memória
            category: Categoria opcional (ex: "pessoal", "trabalho", "preferencias")
            metadata: Metadados adicionais (JSON)
        """
        import json
        metadata_json = json.dumps(metadata) if metadata else None
        now = datetime.now()
        
        # Tenta atualizar se já existe
        cursor = await self._connection.execute("""
            UPDATE memories 
            SET value = ?, category = ?, updated_at = ?, metadata = ?
            WHERE key = ?
        """, (value, category, now, metadata_json, key))
        
        if cursor.rowcount == 0:
            # Se não existe, cria nova
            cursor = await self._connection.execute("""
                INSERT INTO memories (key, value, category, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (key, value, category, now, now, metadata_json))
        
        await self._connection.commit()
        memory_id = cursor.lastrowid if cursor.rowcount == 0 else None
        logger.info(f"Memória salva: {key} = {value[:50]}...")
        return memory_id or 0
    
    async def get_memory(self, key: str) -> Optional[Dict]:
        """Obtém uma memória por chave"""
        async with self._connection.execute("""
            SELECT * FROM memories WHERE key = ?
        """, (key,)) as cursor:
            row = await cursor.fetchone()
            if row:
                import json
                return {
                    "id": row["id"],
                    "key": row["key"],
                    "value": row["value"],
                    "category": row["category"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
            return None
    
    async def search_memories(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Busca memórias
        
        Args:
            query: Busca texto no key ou value
            category: Filtra por categoria
            limit: Limite de resultados
        """
        conditions = []
        params = []
        
        if query:
            conditions.append("(key LIKE ? OR value LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)
        
        async with self._connection.execute(f"""
            SELECT * FROM memories 
            WHERE {where_clause}
            ORDER BY updated_at DESC
            LIMIT ?
        """, params) as cursor:
            rows = await cursor.fetchall()
            import json
            return [
                {
                    "id": row["id"],
                    "key": row["key"],
                    "value": row["value"],
                    "category": row["category"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
                for row in rows
            ]
    
    async def delete_memory(self, key: str) -> bool:
        """Remove uma memória"""
        cursor = await self._connection.execute("""
            DELETE FROM memories WHERE key = ?
        """, (key,))
        await self._connection.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Memória removida: {key}")
        return deleted
    
    async def list_memories(self, limit: int = 100) -> List[Dict]:
        """Lista todas as memórias"""
        return await self.search_memories(limit=limit)
    
    # ========== CONTEXTO PARA LLM ==========
    
    async def get_context_for_llm(
        self,
        session_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Obtém contexto formatado para o LLM
        
        Returns:
            Lista de mensagens no formato {role, content}
        """
        messages = await self.get_messages(session_id, limit=max_messages)
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in messages
        ]
    
    async def get_relevant_memories(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Busca memórias relevantes para uma query
        
        Args:
            query: Texto da pergunta/comando
            limit: Número máximo de memórias a retornar
        """
        # Busca simples por palavras-chave
        return await self.search_memories(query=query, limit=limit)
    
    # ========== CONVERSAS ==========
    
    async def save_conversation(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str,
        tokens_used: Optional[int] = None,
        processing_time: Optional[float] = None,
        used_tool: Optional[str] = None
    ) -> int:
        """
        Salva uma conversa completa
        
        Args:
            session_id: ID da sessão
            user_input: Texto de entrada do usuário
            assistant_response: Resposta do assistente
            tokens_used: Tokens utilizados
            processing_time: Tempo de processamento em segundos
            used_tool: Ferramenta usada (se houver)
            
        Returns:
            ID da conversa salva
        """
        cursor = await self._connection.execute("""
            INSERT INTO conversations 
            (session_id, user_input, assistant_response, tokens_used, processing_time, used_tool, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_input, assistant_response, tokens_used, processing_time, used_tool, datetime.now()))
        
        await self._connection.commit()
        conversation_id = cursor.lastrowid
        logger.debug(f"Conversa salva: {conversation_id} (sessão: {session_id})")
        return conversation_id
    
    async def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """Obtém uma conversa por ID"""
        async with self._connection.execute("""
            SELECT * FROM conversations WHERE id = ?
        """, (conversation_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "user_input": row["user_input"],
                    "assistant_response": row["assistant_response"],
                    "tokens_used": row["tokens_used"],
                    "processing_time": row["processing_time"],
                    "used_tool": row["used_tool"],
                    "created_at": row["created_at"]
                }
            return None
    
    async def list_conversations(
        self,
        session_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Lista conversas"""
        if session_id:
            query = """
                SELECT * FROM conversations 
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = (session_id, limit, offset)
        else:
            query = """
                SELECT * FROM conversations 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = (limit, offset)
        
        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "user_input": row["user_input"],
                    "assistant_response": row["assistant_response"],
                    "tokens_used": row["tokens_used"],
                    "processing_time": row["processing_time"],
                    "used_tool": row["used_tool"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    # ========== FEEDBACK ==========
    
    async def save_feedback(
        self,
        conversation_id: Optional[int],
        rating: int,
        comment: Optional[str] = None
    ) -> int:
        """
        Salva feedback do usuário
        
        Args:
            conversation_id: ID da conversa (opcional)
            rating: Avaliação (1-5 ou -1/1 para negativo/positivo)
            comment: Comentário opcional
            
        Returns:
            ID do feedback salvo
        """
        cursor = await self._connection.execute("""
            INSERT INTO feedback (conversation_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, rating, comment, datetime.now()))
        
        await self._connection.commit()
        feedback_id = cursor.lastrowid
        logger.info(f"Feedback salvo: {feedback_id} (rating: {rating})")
        return feedback_id
    
    async def get_feedback(self, feedback_id: int) -> Optional[Dict]:
        """Obtém feedback por ID"""
        async with self._connection.execute("""
            SELECT * FROM feedback WHERE id = ?
        """, (feedback_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "conversation_id": row["conversation_id"],
                    "rating": row["rating"],
                    "comment": row["comment"],
                    "created_at": row["created_at"]
                }
            return None
    
    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de feedback"""
        async with self._connection.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating > 0 THEN 1 END) as positive,
                COUNT(CASE WHEN rating < 0 THEN 1 END) as negative
            FROM feedback
        """) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "total": row["total"],
                    "avg_rating": row["avg_rating"],
                    "positive": row["positive"],
                    "negative": row["negative"]
                }
            return {"total": 0, "avg_rating": 0.0, "positive": 0, "negative": 0}
    
    async def list_feedback(
        self,
        conversation_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Lista feedback"""
        if conversation_id:
            query = """
                SELECT * FROM feedback 
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            params = (conversation_id, limit)
        else:
            query = """
                SELECT * FROM feedback 
                ORDER BY created_at DESC
                LIMIT ?
            """
            params = (limit,)
        
        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "conversation_id": row["conversation_id"],
                    "rating": row["rating"],
                    "comment": row["comment"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    # ========== DADOS DE TREINAMENTO ==========
    
    async def save_training_data(
        self,
        instruction: str,
        output: str,
        input_text: Optional[str] = None,
        source: Optional[str] = None,
        quality_score: Optional[float] = None
    ) -> int:
        """
        Salva dados de treinamento preparados
        
        Args:
            instruction: Instrução/prompt
            output: Resposta esperada
            input_text: Input opcional
            source: Fonte dos dados (ex: "conversation", "feedback")
            quality_score: Score de qualidade (0-1)
            
        Returns:
            ID do dado de treinamento salvo
        """
        cursor = await self._connection.execute("""
            INSERT INTO training_data 
            (instruction, input, output, source, quality_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (instruction, input_text, output, source, quality_score, datetime.now()))
        
        await self._connection.commit()
        training_id = cursor.lastrowid
        logger.debug(f"Dado de treinamento salvo: {training_id}")
        return training_id
    
    async def list_training_data(
        self,
        source: Optional[str] = None,
        min_quality: Optional[float] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Lista dados de treinamento"""
        conditions = []
        params = []
        
        if source:
            conditions.append("source = ?")
            params.append(source)
        
        if min_quality is not None:
            conditions.append("quality_score >= ?")
            params.append(min_quality)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)
        
        async with self._connection.execute(f"""
            SELECT * FROM training_data 
            WHERE {where_clause}
            ORDER BY quality_score DESC, created_at DESC
            LIMIT ?
        """, params) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "instruction": row["instruction"],
                    "input": row["input"],
                    "output": row["output"],
                    "source": row["source"],
                    "quality_score": row["quality_score"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    # ========== CLUSTERS DE INTENÇÕES ==========
    
    async def save_intent_cluster(
        self,
        cluster_id: int,
        intent_type: str,
        examples: List[str]
    ) -> int:
        """
        Salva cluster de intenções
        
        Args:
            cluster_id: ID do cluster
            intent_type: Tipo de intenção
            examples: Lista de exemplos
            
        Returns:
            ID do cluster salvo
        """
        import json
        examples_json = json.dumps(examples)
        now = datetime.now()
        
        # Atualiza se já existe
        cursor = await self._connection.execute("""
            UPDATE intent_clusters 
            SET examples = ?, updated_at = ?
            WHERE cluster_id = ? AND intent_type = ?
        """, (examples_json, now, cluster_id, intent_type))
        
        if cursor.rowcount == 0:
            # Cria novo se não existe
            cursor = await self._connection.execute("""
                INSERT INTO intent_clusters 
                (cluster_id, intent_type, examples, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (cluster_id, intent_type, examples_json, now, now))
        
        await self._connection.commit()
        cluster_row_id = cursor.lastrowid if cursor.rowcount == 0 else None
        logger.debug(f"Cluster salvo: {cluster_id} ({intent_type})")
        return cluster_row_id or 0
    
    async def get_intent_clusters(
        self,
        intent_type: Optional[str] = None
    ) -> List[Dict]:
        """Obtém clusters de intenções"""
        if intent_type:
            query = """
                SELECT * FROM intent_clusters 
                WHERE intent_type = ?
                ORDER BY cluster_id
            """
            params = (intent_type,)
        else:
            query = """
                SELECT * FROM intent_clusters 
                ORDER BY cluster_id, intent_type
            """
            params = ()
        
        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            import json
            return [
                {
                    "id": row["id"],
                    "cluster_id": row["cluster_id"],
                    "intent_type": row["intent_type"],
                    "examples": json.loads(row["examples"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in rows
            ]
    
    # ========== ERROS (MONITORAMENTO MOBILE) ==========
    
    async def save_error(
        self,
        error_id: str,
        level: str,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        device_info: Optional[Dict] = None,
        context: Optional[Dict] = None,
        suggested_solution: Optional[str] = None
    ) -> int:
        """
        Salva erro reportado pelo mobile
        
        Args:
            error_id: ID único do erro (UUID)
            level: Nível (error, warning, critical)
            error_type: Tipo (network, audio, permission, crash, other)
            message: Mensagem do erro
            stack_trace: Stack trace completo
            device_info: Informações do dispositivo
            context: Contexto adicional (session_id, user_action, etc.)
            suggested_solution: Solução sugerida (gerada automaticamente)
            
        Returns:
            ID do erro salvo
        """
        import json
        device_info_json = json.dumps(device_info) if device_info else None
        context_json = json.dumps(context) if context else None
        
        cursor = await self._connection.execute("""
            INSERT INTO errors 
            (error_id, timestamp, level, type, message, stack_trace, 
             device_info, context, suggested_solution, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            error_id,
            datetime.now(),
            level,
            error_type,
            message,
            stack_trace,
            device_info_json,
            context_json,
            suggested_solution
        ))
        
        await self._connection.commit()
        error_row_id = cursor.lastrowid
        logger.debug(f"Erro salvo: {error_row_id} ({error_type})")
        return error_row_id
    
    async def get_error(self, error_id: str) -> Optional[Dict]:
        """Obtém erro por ID"""
        async with self._connection.execute("""
            SELECT * FROM errors WHERE error_id = ?
        """, (error_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                import json
                return {
                    "id": row["id"],
                    "error_id": row["error_id"],
                    "timestamp": row["timestamp"],
                    "level": row["level"],
                    "type": row["type"],
                    "message": row["message"],
                    "stack_trace": row["stack_trace"],
                    "device_info": json.loads(row["device_info"]) if row["device_info"] else None,
                    "context": json.loads(row["context"]) if row["context"] else None,
                    "suggested_solution": row["suggested_solution"],
                    "resolved": bool(row["resolved"]),
                    "resolution_notes": row["resolution_notes"],
                    "created_at": row["created_at"]
                }
            return None
    
    async def list_errors(
        self,
        error_type: Optional[str] = None,
        level: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Lista erros com filtros
        
        Args:
            error_type: Filtrar por tipo
            level: Filtrar por nível
            resolved: Filtrar por status de resolução
            limit: Limite de resultados
            offset: Offset para paginação
        """
        query = "SELECT * FROM errors WHERE 1=1"
        params = []
        
        if error_type:
            query += " AND type = ?"
            params.append(error_type)
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            import json
            return [
                {
                    "id": row["id"],
                    "error_id": row["error_id"],
                    "timestamp": row["timestamp"],
                    "level": row["level"],
                    "type": row["type"],
                    "message": row["message"],
                    "stack_trace": row["stack_trace"],
                    "device_info": json.loads(row["device_info"]) if row["device_info"] else None,
                    "context": json.loads(row["context"]) if row["context"] else None,
                    "suggested_solution": row["suggested_solution"],
                    "resolved": bool(row["resolved"]),
                    "resolution_notes": row["resolution_notes"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    async def mark_error_resolved(
        self,
        error_id: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Marca erro como resolvido"""
        cursor = await self._connection.execute("""
            UPDATE errors 
            SET resolved = 1, resolution_notes = ?
            WHERE error_id = ?
        """, (resolution_notes, error_id))
        
        await self._connection.commit()
        return cursor.rowcount > 0
    
    async def get_error_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de erros"""
        stats = {}
        
        # Total de erros
        async with self._connection.execute("""
            SELECT COUNT(*) as total FROM errors
        """) as cursor:
            row = await cursor.fetchone()
            stats["total"] = row["total"] if row else 0
        
        # Por nível
        async with self._connection.execute("""
            SELECT level, COUNT(*) as count 
            FROM errors 
            GROUP BY level
        """) as cursor:
            rows = await cursor.fetchall()
            stats["by_level"] = {row["level"]: row["count"] for row in rows}
        
        # Por tipo
        async with self._connection.execute("""
            SELECT type, COUNT(*) as count 
            FROM errors 
            GROUP BY type
        """) as cursor:
            rows = await cursor.fetchall()
            stats["by_type"] = {row["type"]: row["count"] for row in rows}
        
        # Resolvidos vs não resolvidos
        async with self._connection.execute("""
            SELECT resolved, COUNT(*) as count 
            FROM errors 
            GROUP BY resolved
        """) as cursor:
            rows = await cursor.fetchall()
            stats["by_resolution"] = {
                "resolved": sum(row["count"] for row in rows if row["resolved"]),
                "unresolved": sum(row["count"] for row in rows if not row["resolved"])
            }
        
        # Erros recentes (últimas 24h)
        async with self._connection.execute("""
            SELECT COUNT(*) as count 
            FROM errors 
            WHERE timestamp > datetime('now', '-1 day')
        """) as cursor:
            row = await cursor.fetchone()
            stats["recent_24h"] = row["count"] if row else 0
        
        return stats

