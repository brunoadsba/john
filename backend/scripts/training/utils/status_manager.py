"""
Gerenciador de status do treinamento
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from backend.scripts.training.utils.training_config import TrainingConfig


class StatusManager:
    """Gerencia status do treinamento"""
    
    def __init__(self, status_file: Optional[Path] = None):
        """
        Inicializa gerenciador de status
        
        Args:
            status_file: Caminho do arquivo de status (usa padrão se None)
        """
        self.status_file = status_file or TrainingConfig.status_file
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self._status: Dict[str, Any] = {}
        self._load_status()
    
    def _load_status(self):
        """Carrega status do arquivo"""
        if self.status_file.exists():
            try:
                with open(self.status_file, "r", encoding="utf-8") as f:
                    self._status = json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar status: {e}. Criando novo.")
                self._status = self._default_status()
        else:
            self._status = self._default_status()
            self._save_status()
    
    def _default_status(self) -> Dict[str, Any]:
        """Retorna status padrão"""
        return {
            "current_phase": "data_collection",
            "overall_progress": 0,
            "last_updated": datetime.now().isoformat(),
            "phases": {
                "data_collection": {
                    "status": "in_progress",
                    "conversations": 0,
                    "feedbacks": 0,
                },
                "sft": {
                    "status": "pending",
                    "current_etapa": None,
                    "etapas": {
                        "1": {"status": "pending", "prerequisites": []},
                        "2": {"status": "pending", "prerequisites": ["sft_etapa1"]},
                        "3": {"status": "pending", "prerequisites": ["sft_etapa2"]},
                        "4": {"status": "pending", "prerequisites": ["sft_etapa3"]},
                    }
                },
                "rlhf": {
                    "status": "pending",
                    "reward_model": {"status": "pending"},
                    "ppo": {"status": "pending", "prerequisites": ["rlhf_reward"]}
                },
                "clustering": {
                    "status": "pending"
                },
                "pretraining": {
                    "status": "pending"
                }
            },
            "resources": {
                "last_check": None,
                "ram_available_gb": 0,
                "cpu_load": 0,
                "disk_free_gb": 0
            }
        }
    
    def _save_status(self):
        """Salva status no arquivo"""
        self._status["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(self._status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar status: {e}")
    
    def update_phase_status(
        self,
        phase: str,
        status: str,
        etapa: Optional[str] = None,
        **kwargs
    ):
        """
        Atualiza status de uma fase
        
        Args:
            phase: Nome da fase (sft, rlhf, etc.)
            status: Status (pending, in_progress, completed, error)
            etapa: Etapa específica (opcional, para SFT)
            **kwargs: Dados adicionais para atualizar
        """
        if phase not in self._status["phases"]:
            self._status["phases"][phase] = {}
        
        if etapa:
            if "etapas" not in self._status["phases"][phase]:
                self._status["phases"][phase]["etapas"] = {}
            if etapa not in self._status["phases"][phase]["etapas"]:
                self._status["phases"][phase]["etapas"][etapa] = {}
            
            self._status["phases"][phase]["etapas"][etapa]["status"] = status
            self._status["phases"][phase]["etapas"][etapa].update(kwargs)
            if status == "in_progress":
                self._status["phases"][phase]["etapas"][etapa]["started_at"] = datetime.now().isoformat()
            elif status == "completed":
                self._status["phases"][phase]["etapas"][etapa]["completed_at"] = datetime.now().isoformat()
        else:
            self._status["phases"][phase]["status"] = status
            self._status["phases"][phase].update(kwargs)
        
        if status == "in_progress":
            self._status["current_phase"] = f"{phase}_{etapa}" if etapa else phase
        
        self._save_status()
    
    def update_resources(self, ram_gb: float, cpu_load: float, disk_gb: float):
        """Atualiza informações de recursos"""
        self._status["resources"] = {
            "last_check": datetime.now().isoformat(),
            "ram_available_gb": ram_gb,
            "cpu_load": cpu_load,
            "disk_free_gb": disk_gb
        }
        self._save_status()
    
    def update_data_collection(self, conversations: int, feedbacks: int):
        """Atualiza dados de coleta"""
        phase = self._status["phases"]["data_collection"]
        phase["conversations"] = conversations
        phase["feedbacks"] = feedbacks
        if conversations > 0 or feedbacks > 0:
            phase["status"] = "in_progress"
        self._save_status()
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo"""
        return self._status.copy()
    
    def get_phase_status(self, phase: str) -> Dict[str, Any]:
        """Retorna status de uma fase específica"""
        return self._status["phases"].get(phase, {})
    
    def calculate_progress(self) -> int:
        """Calcula progresso geral (0-100)"""
        total_phases = 0
        completed_phases = 0
        
        # Data collection
        if self._status["phases"]["data_collection"]["status"] == "completed":
            completed_phases += 1
        total_phases += 1
        
        # SFT (4 etapas)
        sft_etapas = self._status["phases"]["sft"]["etapas"]
        for etapa in ["1", "2", "3", "4"]:
            total_phases += 1
            if sft_etapas.get(etapa, {}).get("status") == "completed":
                completed_phases += 1
        
        # RLHF (2 partes)
        rlhf = self._status["phases"]["rlhf"]
        total_phases += 1
        if rlhf.get("reward_model", {}).get("status") == "completed":
            completed_phases += 1
        total_phases += 1
        if rlhf.get("ppo", {}).get("status") == "completed":
            completed_phases += 1
        
        # Clustering
        total_phases += 1
        if self._status["phases"]["clustering"]["status"] == "completed":
            completed_phases += 1
        
        if total_phases == 0:
            return 0
        
        progress = int((completed_phases / total_phases) * 100)
        self._status["overall_progress"] = progress
        self._save_status()
        return progress

