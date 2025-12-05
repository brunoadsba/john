"""
Configurações da aplicação Jonh Assistant
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações gerais da aplicação"""
    
    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # LLM Provider (ollama ou groq)
    llm_provider: str = "ollama"
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b-instruct-q4_0"
    
    # Groq
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"
    
    # Configurações gerais de LLM
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    
    # Whisper
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    
    # Piper TTS
    piper_voice: str = "pt_BR-faber-medium"
    piper_model_path: str = "./models/piper"
    
    # Caminhos
    models_dir: str = "./models"
    temp_dir: str = "./temp"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global de configurações
settings = Settings()

