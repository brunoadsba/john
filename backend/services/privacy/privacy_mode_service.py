"""
Serviço de gerenciamento de Modo Privacidade

Gerencia alternância dinâmica entre LLM cloud (Groq) e local (Ollama),
além de filtrar plugins que requerem internet.
"""
from typing import Optional
from loguru import logger

from backend.services.llm import BaseLLMService, GroqLLMService, OllamaLLMService, create_llm_service
from backend.config import settings


class PrivacyModeService:
    """
    Gerencia modo privacidade e alternância dinâmica de LLM
    """
    
    def __init__(
        self,
        groq_service: Optional[GroqLLMService] = None,
        ollama_service: Optional[OllamaLLMService] = None
    ):
        """
        Inicializa serviço de privacidade
        
        Args:
            groq_service: Serviço Groq (opcional, cria se não fornecido)
            ollama_service: Serviço Ollama (opcional, cria se não fornecido)
        """
        self._privacy_mode_active = False
        
        # Cria serviços se não fornecidos
        if groq_service is None:
            try:
                self.groq_service = create_llm_service(
                    provider="groq",
                    api_key=settings.groq_api_key,
                    model=settings.groq_model,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens
                )
                logger.info("✅ PrivacyModeService: GroqService criado")
            except Exception as e:
                logger.warning(f"⚠️ PrivacyModeService: Erro ao criar GroqService: {e}")
                self.groq_service = None
        else:
            self.groq_service = groq_service
            
        if ollama_service is None:
            try:
                self.ollama_service = create_llm_service(
                    provider="ollama",
                    model=settings.ollama_model,
                    host=settings.ollama_host,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens
                )
                logger.info("✅ PrivacyModeService: OllamaService criado")
            except Exception as e:
                logger.warning(f"⚠️ PrivacyModeService: Erro ao criar OllamaService: {e}")
                self.ollama_service = None
        else:
            self.ollama_service = ollama_service
        
        logger.info("✅ PrivacyModeService inicializado")
    
    def set_privacy_mode(self, enabled: bool) -> dict:
        """
        Alterna modo de privacidade
        
        Args:
            enabled: True para ativar modo privacidade (local), False para cloud
            
        Returns:
            Dict com status e configuração atual
        """
        old_mode = self._privacy_mode_active
        self._privacy_mode_active = enabled
        
        mode_name = "🔒 LOCAL / PRIVADO" if enabled else "☁️ CLOUD / PADRÃO"
        logger.info(f"--- [PRIVACY MODE] Modo alterado para: {mode_name} ---")
        
        # Valida se serviço necessário está disponível
        if enabled and not self.ollama_service:
            logger.error("❌ Não é possível ativar modo privacidade: Ollama não disponível")
            self._privacy_mode_active = False
            return {
                "success": False,
                "message": "Ollama não está disponível. Instale e inicie o Ollama primeiro.",
                "privacy_mode": False,
                "provider": None
            }
        
        if not enabled and not self.groq_service:
            logger.warning("⚠️ Groq não disponível, mas modo cloud solicitado")
        
        return {
            "success": True,
            "message": f"Modo {'privacidade ativado' if enabled else 'cloud ativado'}",
            "privacy_mode": self._privacy_mode_active,
            "provider": "ollama" if enabled else "groq",
            "previous_mode": "privacy" if old_mode else "cloud"
        }
    
    def get_privacy_mode(self) -> bool:
        """Retorna se modo privacidade está ativo"""
        return self._privacy_mode_active
    
    def get_active_llm_service(self) -> Optional[BaseLLMService]:
        """
        Retorna o serviço LLM ativo baseado no modo privacidade
        
        Returns:
            Serviço LLM ativo ou None se não disponível
        """
        if self._privacy_mode_active:
            if self.ollama_service:
                return self.ollama_service
            logger.error("❌ Ollama não disponível em modo privacidade")
            return None
        else:
            if self.groq_service:
                return self.groq_service
            logger.error("❌ Groq não disponível em modo cloud")
            return None
    
    def get_status(self) -> dict:
        """
        Retorna status completo do modo privacidade
        
        Returns:
            Dict com informações de status
        """
        return {
            "privacy_mode": self._privacy_mode_active,
            "current_provider": "ollama" if self._privacy_mode_active else "groq",
            "groq_available": self.groq_service is not None,
            "ollama_available": self.ollama_service is not None,
            "active_service_available": self.get_active_llm_service() is not None
        }

