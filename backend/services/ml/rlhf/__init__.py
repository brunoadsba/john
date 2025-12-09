"""
Módulo RLHF - Reinforcement Learning from Human Feedback
"""
from backend.services.ml.rlhf.ppo_trainer import train_with_ppo_core
from backend.services.ml.rlhf.candidate_generator import generate_candidates_core

__all__ = [
    "train_with_ppo_core",
    "generate_candidates_core"
]

