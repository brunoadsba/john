"""
Módulo de Pré-treinamento (Auto-Supervisionado)
"""
from backend.services.ml.pretraining.corpus_collector import collect_corpus_core
from backend.services.ml.pretraining.data_preparer import prepare_pretraining_data_core
from backend.services.ml.pretraining.trainer import continue_pretraining_core
from backend.services.ml.pretraining.evaluator import evaluate_improvements_core

__all__ = [
    "collect_corpus_core",
    "prepare_pretraining_data_core",
    "continue_pretraining_core",
    "evaluate_improvements_core"
]

