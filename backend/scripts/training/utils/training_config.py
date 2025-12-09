"""
Configurações centralizadas para scripts de treinamento
"""
from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path


@dataclass
class ResourceLimits:
    """Limites de recursos por tipo de treinamento"""
    min_ram_gb: float
    max_cpu_load: float
    min_disk_gb: float


@dataclass
class TrainingConfig:
    """Configurações centralizadas para treinamento"""
    
    # Paths padrão
    base_path: Path = Path(__file__).parent.parent.parent.parent
    status_file: Path = base_path / "training_status.json"
    plan_file: Path = base_path / "training_plan.md"
    models_dir: Path = base_path / "models"
    checkpoints_dir: Path = base_path / "checkpoints"
    data_dir: Path = base_path / "data"
    
    # Limites de recursos por tipo de treinamento
    SFT_ETAPA1_LIMITS = ResourceLimits(min_ram_gb=8.0, max_cpu_load=4.0, min_disk_gb=10.0)
    SFT_ETAPA2_LIMITS = ResourceLimits(min_ram_gb=12.0, max_cpu_load=4.0, min_disk_gb=15.0)
    SFT_ETAPA3_LIMITS = ResourceLimits(min_ram_gb=16.0, max_cpu_load=4.5, min_disk_gb=20.0)
    SFT_ETAPA4_LIMITS = ResourceLimits(min_ram_gb=20.0, max_cpu_load=5.0, min_disk_gb=30.0)
    
    RLHF_REWARD_LIMITS = ResourceLimits(min_ram_gb=4.0, max_cpu_load=3.0, min_disk_gb=5.0)
    RLHF_PPO_LIMITS = ResourceLimits(min_ram_gb=18.0, max_cpu_load=4.5, min_disk_gb=25.0)
    
    CLUSTERING_LIMITS = ResourceLimits(min_ram_gb=8.0, max_cpu_load=3.0, min_disk_gb=10.0)
    PRETRAINING_LIMITS = ResourceLimits(min_ram_gb=24.0, max_cpu_load=5.0, min_disk_gb=50.0)
    
    # Configurações padrão SFT
    SFT_DEFAULT_BASE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
    SFT_DEFAULT_LEARNING_RATE = 2e-4
    SFT_DEFAULT_LORA_R = 16
    SFT_DEFAULT_LORA_ALPHA = 32
    SFT_DEFAULT_LORA_DROPOUT = 0.1
    
    # Configurações padrão RLHF
    RLHF_DEFAULT_LEARNING_RATE = 2e-5
    RLHF_DEFAULT_BATCH_SIZE_REWARD = 16
    RLHF_DEFAULT_BATCH_SIZE_PPO = 2
    
    # Thresholds de validação
    MIN_DATASET_SAMPLES = 10
    MIN_DATASET_QUALITY = 0.7
    MIN_CORPUS_SIZE_MB = 1.0
    
    # Configurações de monitoramento
    MONITORING_INTERVAL_SECONDS = 5
    ALERT_RAM_THRESHOLD_GB = 28.0
    ALERT_CPU_THRESHOLD_PERCENT = 90.0
    
    # Configurações de checkpoints
    CHECKPOINT_SAVE_STEPS = 500
    CHECKPOINT_SAVE_TOTAL_LIMIT = 3
    
    @classmethod
    def get_limits_for_etapa(cls, etapa: int) -> ResourceLimits:
        """Retorna limites de recursos para etapa SFT"""
        limits_map = {
            1: cls.SFT_ETAPA1_LIMITS,
            2: cls.SFT_ETAPA2_LIMITS,
            3: cls.SFT_ETAPA3_LIMITS,
            4: cls.SFT_ETAPA4_LIMITS,
        }
        return limits_map.get(etapa, cls.SFT_ETAPA1_LIMITS)
    
    @classmethod
    def get_sft_config_for_etapa(cls, etapa: int) -> Dict[str, Any]:
        """Retorna configuração SFT para etapa"""
        configs = {
            1: {
                "dataset_limit": 100,
                "epochs": 1,
                "batch_size": 2,
                "gradient_accumulation_steps": 1,
            },
            2: {
                "dataset_limit": 500,
                "epochs": 2,
                "batch_size": 4,
                "gradient_accumulation_steps": 2,
            },
            3: {
                "dataset_limit": 2000,
                "epochs": 3,
                "batch_size": 4,
                "gradient_accumulation_steps": 4,
            },
            4: {
                "dataset_limit": 5000,
                "epochs": 3,
                "batch_size": 4,
                "gradient_accumulation_steps": 4,
            },
        }
        base_config = {
            "base_model": cls.SFT_DEFAULT_BASE_MODEL,
            "learning_rate": cls.SFT_DEFAULT_LEARNING_RATE,
            "lora_r": cls.SFT_DEFAULT_LORA_R,
            "lora_alpha": cls.SFT_DEFAULT_LORA_ALPHA,
            "lora_dropout": cls.SFT_DEFAULT_LORA_DROPOUT,
        }
        base_config.update(configs.get(etapa, configs[1]))
        return base_config

