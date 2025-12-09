#!/usr/bin/env python3
"""
Valida recursos do sistema antes de iniciar treinamento
"""
import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.scripts.training.utils.training_config import TrainingConfig


def get_ram_available_gb() -> float:
    """Retorna RAM disponível em GB"""
    try:
        result = subprocess.run(
            ["free", "-g"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.split("\n")
        for line in lines:
            if line.startswith("Mem:"):
                parts = line.split()
                total = int(parts[1])
                used = int(parts[2])
                available = total - used
                return float(available)
    except Exception as e:
        logger.warning(f"Erro ao verificar RAM: {e}")
        return 0.0
    return 0.0


def get_cpu_load() -> float:
    """Retorna CPU load (1 minuto)"""
    try:
        result = subprocess.run(
            ["uptime"],
            capture_output=True,
            text=True,
            check=True
        )
        # Formato: ... load average: 1.23, 2.45, 3.67
        output = result.stdout
        if "load average:" in output:
            parts = output.split("load average:")[1].strip().split(",")
            load_1min = float(parts[0].strip())
            return load_1min
    except Exception as e:
        logger.warning(f"Erro ao verificar CPU load: {e}")
        return 0.0
    return 0.0


def get_disk_free_gb(path: str = "/") -> float:
    """Retorna espaço livre em disco em GB"""
    try:
        stat = shutil.disk_usage(path)
        free_gb = stat.free / (1024 ** 3)
        return free_gb
    except Exception as e:
        logger.warning(f"Erro ao verificar disco: {e}")
        return 0.0


def check_other_training_running() -> bool:
    """Verifica se há outros processos de treinamento rodando"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "train_.*\.py"],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().split("\n")
        # Remove nosso próprio PID
        current_pid = str(os.getpid())
        pids = [p for p in pids if p and p != current_pid]
        return len(pids) > 0
    except Exception:
        return False


def validate_resources(
    min_ram: float,
    max_cpu_load: float,
    min_disk: float
) -> bool:
    """
    Valida recursos do sistema
    
    Args:
        min_ram: RAM mínima em GB
        max_cpu_load: CPU load máximo
        min_disk: Espaço mínimo em disco em GB
        
    Returns:
        True se recursos suficientes, False caso contrário
    """
    logger.info("Validando recursos do sistema...")
    
    # Verifica RAM
    ram_available = get_ram_available_gb()
    logger.info(f"RAM disponível: {ram_available:.1f} GB (mínimo: {min_ram:.1f} GB)")
    if ram_available < min_ram:
        logger.error(f"❌ RAM insuficiente: {ram_available:.1f} GB < {min_ram:.1f} GB")
        return False
    
    # Verifica CPU load
    cpu_load = get_cpu_load()
    logger.info(f"CPU load: {cpu_load:.2f} (máximo: {max_cpu_load:.2f})")
    if cpu_load > max_cpu_load:
        logger.error(f"❌ CPU sobrecarregado: {cpu_load:.2f} > {max_cpu_load:.2f}")
        return False
    
    # Verifica disco
    disk_free = get_disk_free_gb()
    logger.info(f"Disco livre: {disk_free:.1f} GB (mínimo: {min_disk:.1f} GB)")
    if disk_free < min_disk:
        logger.error(f"❌ Espaço em disco insuficiente: {disk_free:.1f} GB < {min_disk:.1f} GB")
        return False
    
    # Verifica outros treinamentos
    if check_other_training_running():
        logger.warning("⚠️  Outros processos de treinamento detectados")
        response = input("Continuar mesmo assim? (s/N): ")
        if response.lower() != "s":
            return False
    
    logger.info("✅ Recursos validados com sucesso")
    return True


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Valida recursos do sistema")
    parser.add_argument(
        "--min-ram",
        type=float,
        default=8.0,
        help="RAM mínima em GB (padrão: 8.0)"
    )
    parser.add_argument(
        "--max-cpu-load",
        type=float,
        default=4.0,
        help="CPU load máximo (padrão: 4.0)"
    )
    parser.add_argument(
        "--min-disk",
        type=float,
        default=10.0,
        help="Espaço mínimo em disco em GB (padrão: 10.0)"
    )
    
    args = parser.parse_args()
    
    success = validate_resources(
        min_ram=args.min_ram,
        max_cpu_load=args.max_cpu_load,
        min_disk=args.min_disk
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

