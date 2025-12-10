"""
Configurações da aplicação Jonh Assistant
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict


class Settings(BaseSettings):
    """Configurações gerais da aplicação"""
    
    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # LLM Provider (ollama ou groq)
    llm_provider: str = "groq"  # Groq para desenvolvimento e produção (rápido e confiável)
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b-instruct-q4_0"  # Modelo atual do .env (funciona e está testado)
    
    # Groq
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"  # Modelo ativo e rápido (llama-3.1-70b-versatile foi descontinuado)
    
    # Configurações gerais de LLM
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    
    # Busca Web (Tool Calling)
    web_search_enabled: bool = True
    tavily_api_key: Optional[str] = None
    web_search_prefer_tavily: bool = False  # Se True, usa Tavily como primeira opção

    # Architecture Advisor
    architecture_advisor_enabled: bool = True
    
    # Sistema de Evolução de Prompts (evo/)
    evo_enabled: bool = True
    evo_judge_model: str = "llama3.1:8b"
    evo_judge_temperature: float = 0.1
    evo_population_size: int = 16  # Otimizado para 32GB RAM (era 8)
    evo_generations: int = 10  # Otimizado para melhor exploração (era 5)
    evo_mutation_rate: float = 0.3
    evo_api_url: str = "http://localhost:8000/api/process_text"
    evo_timeout: int = 60
    evo_keep_best: int = 4  # Otimizado para 32GB RAM (era 2)
    
    # Whisper
    whisper_model: str = "large-v3"  # Otimizado para 32GB RAM (melhor qualidade PT-BR)
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    
    # Piper TTS (Fase 2 - Nova geração)
    tts_engine: str = "piper"  # "piper" ou "edge" (fallback)
    tts_model_path: str = "models/tts/pt_BR-jeff-medium.onnx"
    tts_config_path: Optional[str] = "models/tts/pt_BR-jeff-medium.onnx.json"
    tts_use_cuda: bool = False  # CPU por padrão (Galaxy Book 2)
    tts_pronunciation_dict_path: str = "backend/data/tts_pronunciation_dict.json"
    tts_enable_ssml: bool = True
    tts_enable_numbers: bool = True
    tts_enable_dates: bool = True
    
    # Piper TTS (legado - manter para compatibilidade)
    piper_voice: str = "pt_BR-faber-medium"
    piper_model_path: str = "./models/piper"
    
    # Caminhos
    models_dir: str = "./models"
    temp_dir: str = "./temp"
    
    # Logging
    log_level: str = "INFO"
    
    # OpenWakeWord
    wake_word_models: List[str] = ["alexa"]  # Modelos pré-treinados disponíveis: alexa (hey_jarvis não está disponível)
    wake_word_custom_models: Dict[str, str] = {}  # Modelos customizados (ex: {"jonh": "./models/jonh.onnx"})
    wake_word_threshold: float = 0.85  # Threshold de detecção (0.0 a 1.0) - alto para evitar falsos positivos (como Alexa)
    wake_word_inference_framework: str = "onnx"  # onnx ou tf
    wake_word_debounce_seconds: float = 3.0  # Tempo mínimo entre detecções (segundos) - como Alexa
    wake_word_min_confidence: float = 0.85  # Confiança mínima adicional (além do threshold) - duplo filtro
    
    # Fine-tuning e ML
    finetuned_model_name: str = "jonh-ft-v1"
    sft_enabled: bool = True
    sft_dataset_path: str = "data/training/sft_dataset.json"
    
    # RLHF
    rlhf_enabled: bool = True
    reward_model_path: str = "models/reward_model"
    rlhf_checkpoint_dir: str = "checkpoints/rlhf"
    
    # Clustering
    clustering_enabled: bool = True
    clustering_min_samples: int = 5  # Otimizado para 32GB RAM (permite mais clusters, era 10)
    clustering_eps: float = 0.3  # Otimizado para melhor granularidade (era 0.5)
    
    # Pré-treinamento
    pretraining_enabled: bool = False
    pretraining_corpus_path: str = "data/corpus/pt_br_corpus.txt"
    
    class Config:
        # Encontra o .env na raiz do projeto (subindo 2 níveis de backend/config/)
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False


# Instância global de configurações
settings = Settings()

