#!/usr/bin/env python3
"""
Verifica dependências e modelos necessários para treinamento
"""
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from backend.config import settings


def check_dependencies() -> Tuple[bool, List[str]]:
    """Verifica se dependências estão instaladas"""
    required_packages = [
        "transformers",
        "peft",
        "accelerate",
        "datasets",
        "trl",
        "torch",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} instalado")
        except ImportError:
            logger.error(f"❌ {package} não instalado")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_base_model() -> bool:
    """Verifica se modelo base está disponível"""
    try:
        from transformers import AutoTokenizer
        
        base_model = settings.finetuned_model_name or "meta-llama/Llama-3.1-8B-Instruct"
        logger.info(f"Verificando modelo base: {base_model}")
        
        # Tenta carregar tokenizer (teste rápido)
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        logger.info("✅ Modelo base acessível")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao acessar modelo base: {e}")
        return False


def check_checkpoints(checkpoint_dir: str) -> bool:
    """Verifica se há checkpoints anteriores"""
    checkpoint_path = Path(checkpoint_dir)
    if checkpoint_path.exists() and any(checkpoint_path.iterdir()):
        logger.info(f"✅ Checkpoints encontrados em: {checkpoint_dir}")
        return True
    else:
        logger.info(f"ℹ️  Nenhum checkpoint anterior em: {checkpoint_dir}")
        return False


def check_env_config() -> bool:
    """Valida configurações do .env"""
    issues = []
    
    if not settings.sft_enabled and not settings.rlhf_enabled:
        logger.warning("⚠️  SFT e RLHF desabilitados no .env")
    
    if settings.sft_enabled:
        if not settings.finetuned_model_name:
            issues.append("FINETUNED_MODEL_NAME não definido")
    
    if settings.rlhf_enabled:
        if not settings.reward_model_path:
            issues.append("REWARD_MODEL_PATH não definido")
    
    if issues:
        for issue in issues:
            logger.warning(f"⚠️  {issue}")
        return False
    
    logger.info("✅ Configurações do .env válidas")
    return True


def check_prerequisites(
    check_deps: bool = True,
    check_model: bool = True,
    check_checkpoints: bool = False,
    checkpoint_dir: str = None
) -> bool:
    """
    Verifica todos os pré-requisitos
    
    Args:
        check_deps: Verificar dependências
        check_model: Verificar modelo base
        check_checkpoints: Verificar checkpoints
        checkpoint_dir: Diretório de checkpoints
        
    Returns:
        True se todos os pré-requisitos OK
    """
    logger.info("Verificando pré-requisitos...")
    
    all_ok = True
    
    if check_deps:
        deps_ok, missing = check_dependencies()
        if not deps_ok:
            logger.error(f"Instale dependências faltantes: pip install {' '.join(missing)}")
            all_ok = False
    
    if check_model:
        if not check_base_model():
            all_ok = False
    
    if check_checkpoints and checkpoint_dir:
        check_checkpoints(checkpoint_dir)
    
    if not check_env_config():
        all_ok = False
    
    if all_ok:
        logger.info("✅ Todos os pré-requisitos OK")
    else:
        logger.error("❌ Alguns pré-requisitos não atendidos")
    
    return all_ok


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Verifica pré-requisitos para treinamento")
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Pular verificação de dependências"
    )
    parser.add_argument(
        "--skip-model",
        action="store_true",
        help="Pular verificação de modelo base"
    )
    parser.add_argument(
        "--check-checkpoints",
        action="store_true",
        help="Verificar checkpoints anteriores"
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        help="Diretório de checkpoints para verificar"
    )
    
    args = parser.parse_args()
    
    success = check_prerequisites(
        check_deps=not args.skip_deps,
        check_model=not args.skip_model,
        check_checkpoints=args.check_checkpoints,
        checkpoint_dir=args.checkpoint_dir
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

