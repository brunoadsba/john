#!/usr/bin/env python3
"""
Monitora recursos durante treinamento em tempo real
"""
import sys
import time
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.scripts.training.utils.training_config import TrainingConfig


def get_ram_usage_gb() -> float:
    """Retorna RAM usada em GB"""
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
                used = int(parts[2])
                return float(used)
    except Exception:
        return 0.0
    return 0.0


def get_cpu_percent() -> float:
    """Retorna uso de CPU em percentual"""
    try:
        result = subprocess.run(
            ["top", "-bn1"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split("\n"):
            if "%Cpu(s)" in line:
                parts = line.split(",")
                cpu_idle = float(parts[3].strip().replace("%id", ""))
                cpu_used = 100.0 - cpu_idle
                return cpu_used
    except Exception:
        return 0.0
    return 0.0


def get_disk_usage_gb(path: str = "/") -> float:
    """Retorna espaço usado em disco em GB"""
    try:
        stat = shutil.disk_usage(path)
        used_gb = stat.used / (1024 ** 3)
        return used_gb
    except Exception:
        return 0.0


def monitor_training(
    interval: int = 5,
    alert_ram: float = 28.0,
    alert_cpu: float = 90.0,
    log_file: Optional[str] = None
):
    """
    Monitora recursos durante treinamento
    
    Args:
        interval: Intervalo de monitoramento em segundos
        alert_ram: Threshold de alerta RAM em GB
        alert_cpu: Threshold de alerta CPU em %
        log_file: Arquivo para salvar logs (opcional)
    """
    logger.info(f"Iniciando monitoramento (intervalo: {interval}s)")
    logger.info(f"Alertas: RAM > {alert_ram} GB, CPU > {alert_cpu}%")
    
    log_handle = None
    if log_file:
        log_handle = open(log_file, "a", encoding="utf-8")
        logger.info(f"Logs salvos em: {log_file}")
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            ram_used = get_ram_usage_gb()
            cpu_percent = get_cpu_percent()
            disk_used = get_disk_usage_gb()
            
            # Verifica alertas
            ram_alert = ram_used > alert_ram
            cpu_alert = cpu_percent > alert_cpu
            
            status = "OK"
            if ram_alert or cpu_alert:
                status = "ALERTA"
            
            # Log
            log_line = (
                f"[{timestamp}] "
                f"RAM: {ram_used:.1f}GB | "
                f"CPU: {cpu_percent:.1f}% | "
                f"Disco: {disk_used:.1f}GB | "
                f"Status: {status}"
            )
            
            if ram_alert or cpu_alert:
                logger.warning(log_line)
            else:
                logger.info(log_line)
            
            if log_handle:
                log_handle.write(log_line + "\n")
                log_handle.flush()
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário")
    finally:
        if log_handle:
            log_handle.close()


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Monitora recursos durante treinamento")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Intervalo de monitoramento em segundos (padrão: 5)"
    )
    parser.add_argument(
        "--alert-ram",
        type=float,
        default=28.0,
        help="Threshold de alerta RAM em GB (padrão: 28.0)"
    )
    parser.add_argument(
        "--alert-cpu",
        type=float,
        default=90.0,
        help="Threshold de alerta CPU em % (padrão: 90.0)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Arquivo para salvar logs (opcional)"
    )
    
    args = parser.parse_args()
    
    monitor_training(
        interval=args.interval,
        alert_ram=args.alert_ram,
        alert_cpu=args.alert_cpu,
        log_file=args.log_file
    )


if __name__ == "__main__":
    main()

