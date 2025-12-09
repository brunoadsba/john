#!/usr/bin/env python3
"""
Health check geral do sistema de treinamento
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.scripts.training.utils.status_manager import StatusManager
from backend.scripts.training.utils.training_config import TrainingConfig
from backend.config import settings


def check_models_integrity() -> Dict[str, bool]:
    """Verifica integridade de modelos treinados"""
    models_status = {}
    
    # Verifica modelo fine-tunado
    if settings.sft_enabled:
        model_path = TrainingConfig.models_dir / "finetuned" / settings.finetuned_model_name
        models_status["finetuned"] = model_path.exists() and any(model_path.iterdir())
    
    # Verifica modelo de recompensa
    if settings.rlhf_enabled:
        reward_path = Path(settings.reward_model_path)
        models_status["reward_model"] = reward_path.exists() and any(reward_path.iterdir())
    
    return models_status


def check_disk_space() -> Dict[str, float]:
    """Verifica espaço em disco"""
    import shutil
    
    base_path = TrainingConfig.base_path
    stat = shutil.disk_usage(str(base_path))
    
    return {
        "total_gb": stat.total / (1024 ** 3),
        "used_gb": stat.used / (1024 ** 3),
        "free_gb": stat.free / (1024 ** 3),
        "percent_used": (stat.used / stat.total) * 100
    }


def check_status_file() -> bool:
    """Verifica se arquivo de status existe e é válido"""
    status_file = TrainingConfig.status_file
    if not status_file.exists():
        return False
    
    try:
        manager = StatusManager()
        status = manager.get_status()
        return "phases" in status
    except Exception:
        return False


def generate_health_report() -> Dict[str, Any]:
    """Gera relatório de saúde completo"""
    logger.info("Gerando relatório de saúde do sistema de treinamento...")
    
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "status_file": check_status_file(),
        "models": check_models_integrity(),
        "disk": check_disk_space(),
        "config": {
            "sft_enabled": settings.sft_enabled,
            "rlhf_enabled": settings.rlhf_enabled,
            "clustering_enabled": settings.clustering_enabled,
            "pretraining_enabled": settings.pretraining_enabled,
        }
    }
    
    # Status do treinamento
    if check_status_file():
        manager = StatusManager()
        status = manager.get_status()
        report["training_status"] = {
            "current_phase": status.get("current_phase"),
            "progress": status.get("overall_progress", 0)
        }
    
    return report


def print_report(report: Dict[str, Any]):
    """Imprime relatório formatado"""
    logger.info("=" * 60)
    logger.info("RELATÓRIO DE SAÚDE DO SISTEMA DE TREINAMENTO")
    logger.info("=" * 60)
    
    # Status file
    logger.info(f"Arquivo de status: {'✅ OK' if report['status_file'] else '❌ Não encontrado'}")
    
    # Modelos
    logger.info("Modelos:")
    for model, exists in report["models"].items():
        status = "✅ Existe" if exists else "❌ Não encontrado"
        logger.info(f"  - {model}: {status}")
    
    # Disco
    disk = report["disk"]
    logger.info(f"Disco:")
    logger.info(f"  - Total: {disk['total_gb']:.1f} GB")
    logger.info(f"  - Usado: {disk['used_gb']:.1f} GB ({disk['percent_used']:.1f}%)")
    logger.info(f"  - Livre: {disk['free_gb']:.1f} GB")
    
    # Configurações
    logger.info("Configurações:")
    for key, value in report["config"].items():
        status = "✅ Habilitado" if value else "⏸️  Desabilitado"
        logger.info(f"  - {key}: {status}")
    
    # Status de treinamento
    if "training_status" in report:
        ts = report["training_status"]
        logger.info(f"Status de treinamento:")
        logger.info(f"  - Fase atual: {ts.get('current_phase', 'N/A')}")
        logger.info(f"  - Progresso: {ts.get('progress', 0)}%")
    
    logger.info("=" * 60)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Health check do sistema de treinamento")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em JSON"
    )
    
    args = parser.parse_args()
    
    report = generate_health_report()
    
    if args.json:
        import json
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()

