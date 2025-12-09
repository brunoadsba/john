"""
Serviço de memória para o assistente Jonh
"""
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger

from backend.database.database import Database
from backend.services.embedding_service import EmbeddingService


class MemoryService:
    """Gerencia memórias e anotações do assistente"""
    
    def __init__(self, database: Database):
        """
        Inicializa serviço de memória
        
        Args:
            database: Instância do banco de dados
        """
        self.db = database
        self.embedder = EmbeddingService()
        logger.info("MemoryService inicializado")
    
    async def extract_and_save_memory(self, user_message: str, assistant_response: str) -> List[str]:
        """
        Extrai informações importantes da conversa e salva como memória
        
        Args:
            user_message: Mensagem do usuário
            assistant_response: Resposta do assistente
            
        Returns:
            Lista de chaves de memórias salvas
        """
        saved_keys = []
        
        # Padrões para detectar comandos de anotação
        patterns = [
            # "Anote que eu gosto de café"
            (r"anote\s+que\s+(.+?)(?:\.|$)", "anotacao"),
            # "Lembre que meu nome é João"
            (r"lembre\s+que\s+(.+?)(?:\.|$)", "anotacao"),
            # "Salve que eu trabalho na empresa X"
            (r"salve\s+que\s+(.+?)(?:\.|$)", "anotacao"),
            # "Meu nome é João"
            (r"meu\s+nome\s+é\s+(\w+)", "pessoal"),
            # "Eu gosto de X"
            (r"eu\s+gosto\s+de\s+(.+?)(?:\.|$)", "preferencias"),
            # "Eu trabalho em X"
            (r"eu\s+trabalho\s+(?:em|na|no)\s+(.+?)(?:\.|$)", "trabalho"),
        ]
        
        text = f"{user_message} {assistant_response}".lower()
        
        for pattern, category in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1).strip()
                if len(value) > 3:  # Ignora valores muito curtos
                    # Gera chave única baseada no conteúdo
                    key = f"{category}_{hash(value) % 1000000}"
                    
                    try:
                        await self.db.save_memory(
                            key=key,
                            value=value,
                            category=category
                        )
                        saved_keys.append(key)
                        logger.info(f"Memória extraída e salva: {key} = {value}")
                    except Exception as e:
                        logger.error(f"Erro ao salvar memória: {e}")
        
        return saved_keys
    
    async def get_memories_for_context(self, user_message: str, limit: int = 5) -> str:
        """
        Busca memórias relevantes para o contexto atual usando busca semântica
        
        Args:
            user_message: Mensagem do usuário
            limit: Número máximo de memórias
            
        Returns:
            String formatada com memórias relevantes
        """
        if not user_message or not user_message.strip():
            return ""
        
        # Tenta busca semântica primeiro (se embeddings disponível)
        if self.embedder.is_available():
            try:
                memories = await self._semantic_search(user_message, limit)
            except Exception as e:
                logger.warning(f"Erro na busca semântica, usando fallback: {e}")
                memories = await self.db.get_relevant_memories(user_message, limit=limit)
        else:
            # Fallback para busca por palavras-chave
            logger.debug("Embeddings não disponível, usando busca por palavras-chave")
            memories = await self._keyword_search(user_message, limit)
        
        if not memories:
            return ""
        
        # Formata memórias para o LLM (formato melhorado)
        lines = []
        for mem in memories:
            key = mem.get('key', '')
            value = mem.get('value', '')
            category = mem.get('category', '')
            
            # Limpa e formata a chave
            clean_key = key.replace('_', ' ').replace('pessoal', '').replace('anotacao', '').strip()
            
            if clean_key and len(clean_key) > 2:
                lines.append(f"- {clean_key.capitalize()}: {value}")
            else:
                # Se não tem chave clara, usa apenas o valor
                if category:
                    lines.append(f"- {value} ({category})")
                else:
                    lines.append(f"- {value}")
        
        if not lines:
            return ""
        
        return "\n".join(lines)
    
    async def _semantic_search(self, query: str, limit: int) -> List[Dict]:
        """
        Busca semântica usando embeddings
        
        Args:
            query: Texto da pergunta
            limit: Número máximo de resultados
            
        Returns:
            Lista de memórias relevantes
        """
        # 1. Busca todas as memórias (ou últimas 100 para performance)
        all_memories = await self.db.list_memories(limit=100)
        
        if not all_memories:
            return []
        
        # 2. Prepara textos para vetorização (Key + Value para contexto total)
        memory_texts = [f"{m.get('key', '')}: {m.get('value', '')}" for m in all_memories]
        
        # 3. Gera embeddings
        try:
            query_embedding = self.embedder.embed_query(query)
            memory_embeddings = self.embedder.embed(memory_texts)
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return await self._keyword_search(query, limit)
        
        # 4. Calcula similaridade de cosseno e recency score
        similarities = []
        for i, mem_emb in enumerate(memory_embeddings):
            vector_score = self.embedder.cosine_similarity(query_embedding, mem_emb)
            
            # Calcula recency score
            memory = all_memories[i]
            created_at = memory.get('created_at')
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            elif not isinstance(created_at, datetime):
                created_at = datetime.now()
            
            recency_score = self._calculate_recency_score(created_at)
            
            # Combina scores: 70% vector, 30% recency
            final_score = (vector_score * 0.7) + (recency_score * 0.3)
            
            similarities.append((i, final_score, vector_score, recency_score, memory))
        
        # 5. Filtra e ordena (Top K com threshold mínimo)
        threshold = 0.35  # Ajuste fino para evitar "alucinações" de memória
        scored_memories = sorted(similarities, key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, final_score, vector_score, recency_score, memory in scored_memories[:limit]:
            if final_score > threshold:
                results.append(memory)
                logger.debug(
                    f"🔍 Memória encontrada (Final: {final_score:.2f}, "
                    f"Vector: {vector_score:.2f}, Recency: {recency_score:.2f}): "
                    f"{memory.get('key')} = {memory.get('value')[:50]}"
                )
        
        return results
    
    def _calculate_recency_score(self, memory_timestamp: datetime, decay_days: int = 7) -> float:
        """
        Calcula score de recência com decaimento exponencial
        
        Args:
            memory_timestamp: Timestamp da memória
            decay_days: Dias antes de começar decaimento
        
        Returns:
            Score de recência (0.0 a 1.0)
        """
        now = datetime.now()
        time_difference = now - memory_timestamp
        
        if time_difference <= timedelta(days=decay_days):
            return 1.0
        else:
            days_old = (time_difference.days - decay_days)
            decay_factor = 0.95  # Perde 5% por dia após período inicial
            score = decay_factor ** days_old
            return max(0.0, min(1.0, score))
    
    async def _keyword_search(self, query: str, limit: int) -> List[Dict]:
        """
        Busca por palavras-chave (fallback)
        
        Args:
            query: Texto da pergunta
            limit: Número máximo de resultados
            
        Returns:
            Lista de memórias relevantes
        """
        # Extrai palavras-chave (remove stopwords)
        stopwords = {
            "o", "a", "e", "de", "do", "da", "em", "para", "com", "que", "meu", "minha",
            "qual", "é", "um", "uma", "os", "as", "no", "na", "por", "como", "se", "me",
            "te", "nos", "você", "vocês", "ele", "ela", "eles", "elas", "seu", "sua"
        }
        
        words = re.findall(r'\b[a-zA-ZÀ-ú]+\b', query.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        if not keywords:
            # Se não há keywords, busca todas as memórias recentes
            return await self.db.list_memories(limit=limit)
        
        # Busca por cada palavra-chave
        all_results = []
        for keyword in keywords:
            results = await self.db.search_memories(query=keyword, limit=limit * 2)
            all_results.extend(results)
        
        # Remove duplicatas e limita
        seen = set()
        unique_results = []
        for mem in all_results:
            mem_id = mem.get('id')
            if mem_id and mem_id not in seen:
                seen.add(mem_id)
                unique_results.append(mem)
                if len(unique_results) >= limit:
                    break
        
        return unique_results
    
    async def save_explicit_memory(
        self,
        key: str,
        value: str,
        category: Optional[str] = None
    ) -> bool:
        """
        Salva memória explicitamente
        
        Args:
            key: Chave da memória
            value: Valor da memória
            category: Categoria opcional
        """
        try:
            await self.db.save_memory(key=key, value=value, category=category)
            logger.info(f"Memória salva explicitamente: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
            return False
    
    async def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Busca memórias"""
        return await self.db.search_memories(query=query, category=category, limit=limit)
    
    async def get_memory(self, key: str) -> Optional[Dict]:
        """Obtém memória específica"""
        return await self.db.get_memory(key)
    
    async def delete_memory(self, key: str) -> bool:
        """Remove memória"""
        return await self.db.delete_memory(key)

