"""
Módulo de modelo de recompensa para RLHF
"""
from backend.services.ml.reward_model.trainer import train_reward_model_core
from backend.services.ml.reward_model.predictor import (
    predict_reward_batch,
    load_reward_model
)

__all__ = [
    "train_reward_model_core",
    "predict_reward_batch",
    "load_reward_model"
]

