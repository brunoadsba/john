#!/usr/bin/env python3
"""
Valida qualidade e tamanho do dataset antes de treinar
"""
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger


def validate_dataset_format(dataset_path: str) -> bool:
    """Valida formato do dataset"""
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error("Dataset deve ser uma lista de exemplos")
            return False
        
        if len(data) == 0:
            logger.error("Dataset vazio")
            return False
        
        # Valida estrutura do primeiro exemplo
        first = data[0]
        required_fields = ["instruction", "output"]
        for field in required_fields:
            if field not in first:
                logger.error(f"Campo obrigatório ausente: {field}")
                return False
        
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao validar formato: {e}")
        return False


def calculate_statistics(dataset_path: str) -> Dict[str, Any]:
    """Calcula estatísticas do dataset"""
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    stats = {
        "total_samples": len(data),
        "avg_instruction_length": 0,
        "avg_output_length": 0,
        "min_quality": 1.0,
        "max_quality": 0.0,
        "avg_quality": 0.0,
        "samples_with_feedback": 0,
    }
    
    total_instruction_len = 0
    total_output_len = 0
    total_quality = 0.0
    quality_count = 0
    
    for item in data:
        # Tamanhos
        instruction_len = len(item.get("instruction", ""))
        output_len = len(item.get("output", ""))
        total_instruction_len += instruction_len
        total_output_len += output_len
        
        # Qualidade
        quality = item.get("quality_score", 0.0)
        if quality > 0:
            total_quality += quality
            quality_count += 1
            stats["min_quality"] = min(stats["min_quality"], quality)
            stats["max_quality"] = max(stats["max_quality"], quality)
        
        # Feedback
        if item.get("has_feedback", False):
            stats["samples_with_feedback"] += 1
    
    if stats["total_samples"] > 0:
        stats["avg_instruction_length"] = total_instruction_len / stats["total_samples"]
        stats["avg_output_length"] = total_output_len / stats["total_samples"]
    
    if quality_count > 0:
        stats["avg_quality"] = total_quality / quality_count
    
    return stats


def validate_dataset(
    dataset_path: str,
    min_samples: int = 10,
    min_quality: float = 0.7
) -> bool:
    """
    Valida dataset completo
    
    Args:
        dataset_path: Caminho do dataset
        min_samples: Mínimo de exemplos
        min_quality: Score mínimo de qualidade
        
    Returns:
        True se válido, False caso contrário
    """
    logger.info(f"Validando dataset: {dataset_path}")
    
    # Verifica se arquivo existe
    if not Path(dataset_path).exists():
        logger.error(f"❌ Dataset não encontrado: {dataset_path}")
        return False
    
    # Valida formato
    if not validate_dataset_format(dataset_path):
        logger.error("❌ Formato do dataset inválido")
        return False
    
    # Calcula estatísticas
    stats = calculate_statistics(dataset_path)
    
    logger.info("Estatísticas do dataset:")
    logger.info(f"  - Total de exemplos: {stats['total_samples']}")
    logger.info(f"  - Tamanho médio (instruction): {stats['avg_instruction_length']:.0f} caracteres")
    logger.info(f"  - Tamanho médio (output): {stats['avg_output_length']:.0f} caracteres")
    logger.info(f"  - Qualidade média: {stats['avg_quality']:.2f}")
    logger.info(f"  - Com feedback: {stats['samples_with_feedback']}")
    
    # Valida tamanho mínimo
    if stats["total_samples"] < min_samples:
        logger.error(f"❌ Dataset muito pequeno: {stats['total_samples']} < {min_samples}")
        return False
    
    # Valida qualidade média
    if stats["avg_quality"] > 0 and stats["avg_quality"] < min_quality:
        logger.warning(f"⚠️  Qualidade média baixa: {stats['avg_quality']:.2f} < {min_quality}")
        response = input("Continuar mesmo assim? (s/N): ")
        if response.lower() != "s":
            return False
    
    logger.info("✅ Dataset validado com sucesso")
    return True


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Valida dataset de treinamento")
    parser.add_argument(
        "--dataset-path",
        type=str,
        required=True,
        help="Caminho do dataset JSON"
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=10,
        help="Mínimo de exemplos (padrão: 10)"
    )
    parser.add_argument(
        "--min-quality",
        type=float,
        default=0.7,
        help="Score mínimo de qualidade (padrão: 0.7)"
    )
    
    args = parser.parse_args()
    
    success = validate_dataset(
        dataset_path=args.dataset_path,
        min_samples=args.min_samples,
        min_quality=args.min_quality
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

