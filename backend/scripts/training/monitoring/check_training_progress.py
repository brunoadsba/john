#!/usr/bin/env python3
"""
Verifica progresso de treinamento ativo
"""
import sys
import argparse
import subprocess
import re
from pathlib import Path
from typing import Optional, Dict

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger


def find_training_processes() -> list:
    """Encontra processos de treinamento rodando"""
    try:
        result = subprocess.run(
            ["pgrep", "-af", "train_.*\.py"],
            capture_output=True,
            text=True
        )
        processes = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    processes.append({"pid": parts[0], "cmd": parts[1]})
        return processes
    except Exception:
        return []


def parse_training_log(log_file: str) -> Optional[Dict]:
    """Lê e parseia log de treinamento"""
    if not Path(log_file).exists():
        return None
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Procura por padrões de progresso
        progress = {
            "epoch": None,
            "step": None,
            "loss": None,
            "learning_rate": None,
        }
        
        for line in reversed(lines[-100:]):  # Últimas 100 linhas
            # Epoch
            epoch_match = re.search(r"epoch[:\s]+(\d+\.?\d*)", line, re.IGNORECASE)
            if epoch_match and not progress["epoch"]:
                progress["epoch"] = float(epoch_match.group(1))
            
            # Step
            step_match = re.search(r"step[:\s]+(\d+)", line, re.IGNORECASE)
            if step_match and not progress["step"]:
                progress["step"] = int(step_match.group(1))
            
            # Loss
            loss_match = re.search(r"loss[:\s]+(\d+\.\d+)", line, re.IGNORECASE)
            if loss_match and not progress["loss"]:
                progress["loss"] = float(loss_match.group(1))
            
            # Learning rate
            lr_match = re.search(r"learning.?rate[:\s]+([\d\.e-]+)", line, re.IGNORECASE)
            if lr_match and not progress["learning_rate"]:
                progress["learning_rate"] = float(lr_match.group(1))
        
        return progress if any(progress.values()) else None
    except Exception as e:
        logger.warning(f"Erro ao ler log: {e}")
        return None


def check_progress(log_file: Optional[str] = None):
    """Verifica progresso de treinamento"""
    logger.info("Verificando progresso de treinamento...")
    
    # Encontra processos
    processes = find_training_processes()
    if not processes:
        logger.info("ℹ️  Nenhum processo de treinamento encontrado")
        return
    
    logger.info(f"Encontrados {len(processes)} processo(s) de treinamento:")
    for proc in processes:
        logger.info(f"  PID {proc['pid']}: {proc['cmd']}")
    
    # Tenta ler log se fornecido
    if log_file:
        progress = parse_training_log(log_file)
        if progress:
            logger.info("Progresso atual:")
            if progress["epoch"] is not None:
                logger.info(f"  Epoch: {progress['epoch']:.2f}")
            if progress["step"] is not None:
                logger.info(f"  Step: {progress['step']}")
            if progress["loss"] is not None:
                logger.info(f"  Loss: {progress['loss']:.4f}")
            if progress["learning_rate"] is not None:
                logger.info(f"  Learning Rate: {progress['learning_rate']}")
        else:
            logger.warning("Não foi possível extrair progresso do log")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Verifica progresso de treinamento")
    parser.add_argument(
        "--log-file",
        type=str,
        help="Caminho do arquivo de log para analisar"
    )
    
    args = parser.parse_args()
    
    check_progress(log_file=args.log_file)


if __name__ == "__main__":
    main()

