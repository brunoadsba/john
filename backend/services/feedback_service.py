"""
Serviço de coleta de feedback e preparação de dados para treinamento
"""
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from backend.database.database import Database


class FeedbackService:
    """Gerencia coleta de feedback e preparação de datasets"""
    
    def __init__(self, database: Database):
        """
        Inicializa serviço de feedback
        
        Args:
            database: Instância do banco de dados
        """
        self.db = database
        logger.info("FeedbackService inicializado")
    
    async def collect_conversation(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str,
        tokens_used: Optional[int] = None,
        processing_time: Optional[float] = None,
        used_tool: Optional[str] = None
    ) -> int:
        """
        Salva uma conversa completa automaticamente
        
        Args:
            session_id: ID da sessão
            user_input: Texto de entrada do usuário
            assistant_response: Resposta do assistente
            tokens_used: Tokens utilizados
            processing_time: Tempo de processamento
            used_tool: Ferramenta usada
            
        Returns:
            ID da conversa salva
        """
        conversation_id = await self.db.save_conversation(
            session_id=session_id,
            user_input=user_input,
            assistant_response=assistant_response,
            tokens_used=tokens_used,
            processing_time=processing_time,
            used_tool=used_tool
        )
        logger.debug(f"Conversa coletada: {conversation_id}")
        return conversation_id
    
    async def save_feedback(
        self,
        conversation_id: Optional[int],
        rating: int,
        comment: Optional[str] = None
    ) -> int:
        """
        Salva feedback explícito do usuário
        
        Args:
            conversation_id: ID da conversa (opcional)
            rating: Avaliação (-1 para negativo, 1 para positivo, ou 1-5)
            comment: Comentário opcional
            
        Returns:
            ID do feedback salvo
        """
        feedback_id = await self.db.save_feedback(
            conversation_id=conversation_id,
            rating=rating,
            comment=comment
        )
        logger.info(f"Feedback salvo: {feedback_id} (rating: {rating})")
        return feedback_id
    
    async def extract_training_pairs(
        self,
        min_quality_score: float = 0.7,
        min_feedback_rating: int = 3,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extrai pares (input, output) de conversas de alta qualidade
        
        Args:
            min_quality_score: Score mínimo de qualidade (0-1)
            min_feedback_rating: Rating mínimo de feedback (1-5)
            limit: Limite de pares a extrair
            
        Returns:
            Lista de pares de treinamento no formato Alpaca/Instruct
        """
        training_pairs = []
        
        # Busca conversas com feedback positivo
        feedback_list = await self.db.list_feedback(limit=1000)
        positive_conversation_ids = {
            f["conversation_id"]
            for f in feedback_list
            if f["conversation_id"] and f["rating"] >= min_feedback_rating
        }
        
        # Busca conversas recentes de alta qualidade
        conversations = await self.db.list_conversations(limit=limit or 1000)
        
        for conv in conversations:
            # Filtra por qualidade
            quality_score = self._calculate_quality_score(conv)
            
            if quality_score < min_quality_score:
                continue
            
            # Prioriza conversas com feedback positivo
            has_positive_feedback = conv["id"] in positive_conversation_ids
            
            # Prepara par de treinamento
            training_pair = {
                "instruction": "Você é o Jonh, um assistente de voz brasileiro extremamente educado, útil e profissional.",
                "input": conv["user_input"],
                "output": conv["assistant_response"],
                "source": "conversation",
                "quality_score": quality_score,
                "has_feedback": has_positive_feedback,
                "conversation_id": conv["id"]
            }
            
            training_pairs.append(training_pair)
        
        # Ordena por qualidade
        training_pairs.sort(key=lambda x: x["quality_score"], reverse=True)
        
        logger.info(f"Extraídos {len(training_pairs)} pares de treinamento")
        return training_pairs
    
    def _calculate_quality_score(self, conversation: Dict) -> float:
        """
        Calcula score de qualidade de uma conversa
        
        Args:
            conversation: Dados da conversa
            
        Returns:
            Score de qualidade (0-1)
        """
        score = 0.5  # Base
        
        # Bônus por tempo rápido
        if conversation.get("processing_time"):
            if conversation["processing_time"] < 2.0:
                score += 0.2
            elif conversation["processing_time"] < 4.0:
                score += 0.1
        
        # Bônus por uso adequado de ferramentas
        if conversation.get("used_tool"):
            score += 0.1
        
        # Bônus por resposta não muito curta nem muito longa
        response_len = len(conversation.get("assistant_response", ""))
        if 50 <= response_len <= 500:
            score += 0.1
        
        # Bônus por tokens razoáveis
        if conversation.get("tokens_used"):
            if 100 <= conversation["tokens_used"] <= 1000:
                score += 0.1
        
        return min(1.0, score)
    
    async def export_training_dataset(
        self,
        output_path: str,
        format: str = "alpaca",
        min_quality: float = 0.7,
        limit: Optional[int] = None
    ) -> str:
        """
        Exporta dataset para treinamento
        
        Args:
            output_path: Caminho do arquivo de saída
            format: Formato de exportação ("alpaca" ou "jsonl")
            min_quality: Score mínimo de qualidade
            limit: Limite de exemplos
            
        Returns:
            Caminho do arquivo exportado
        """
        training_pairs = await self.extract_training_pairs(
            min_quality_score=min_quality,
            limit=limit
        )
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "alpaca":
            # Formato Alpaca (comum para fine-tuning)
            dataset = [
                {
                    "instruction": pair["instruction"],
                    "input": pair["input"],
                    "output": pair["output"]
                }
                for pair in training_pairs
            ]
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        elif format == "jsonl":
            # Formato JSONL (uma linha por exemplo)
            with open(output_file, "w", encoding="utf-8") as f:
                for pair in training_pairs:
                    line = json.dumps({
                        "instruction": pair["instruction"],
                        "input": pair["input"],
                        "output": pair["output"]
                    }, ensure_ascii=False)
                    f.write(line + "\n")
        
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        logger.info(f"Dataset exportado: {output_file} ({len(training_pairs)} exemplos)")
        return str(output_file)
    
    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de feedback"""
        stats = await self.db.get_feedback_stats()
        
        # Adiciona estatísticas de conversas
        recent_conversations = await self.db.list_conversations(limit=1000)
        total_conversations = len(recent_conversations)
        
        stats["total_conversations"] = total_conversations
        stats["conversations_with_feedback"] = sum(
            1 for conv in recent_conversations
            if conv.get("id")  # Simplificado - deveria verificar se tem feedback
        )
        
        return stats
    
    async def prepare_training_data_from_conversations(
        self,
        min_quality: float = 0.7
    ) -> int:
        """
        Prepara e salva dados de treinamento a partir de conversas
        
        Args:
            min_quality: Score mínimo de qualidade
            
        Returns:
            Número de dados de treinamento salvos
        """
        training_pairs = await self.extract_training_pairs(
            min_quality_score=min_quality
        )
        
        saved_count = 0
        for pair in training_pairs:
            await self.db.save_training_data(
                instruction=pair["instruction"],
                input_text=pair["input"],
                output=pair["output"],
                source=pair["source"],
                quality_score=pair["quality_score"]
            )
            saved_count += 1
        
        logger.info(f"Preparados {saved_count} dados de treinamento")
        return saved_count

