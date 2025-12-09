"""
Exportação de modelos para formato Ollama
"""
from pathlib import Path
from loguru import logger


def export_to_ollama_format_core(
    base_model: str,
    model_path: str,
    output_path: str,
    model_name: str = "jonh-ft"
) -> str:
    """
    Exporta modelo para formato Ollama (Modelfile)
    
    Args:
        base_model: Nome do modelo base
        model_path: Caminho do modelo fine-tunado
        output_path: Caminho do arquivo Modelfile
        model_name: Nome do modelo
        
    Returns:
        Caminho do Modelfile
    """
    logger.info("Exportando para formato Ollama...")
    
    modelfile_content = f"""FROM {base_model}

# Modelo fine-tunado para Jonh Assistant
# Treinado com dados de conversas em português brasileiro

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
"""
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(modelfile_content, encoding="utf-8")
    
    logger.info(f"Modelfile criado: {output_path}")
    logger.warning("⚠️  Para usar no Ollama, você precisa converter o modelo para formato GGUF")
    logger.warning("   Use ferramentas como llama.cpp ou ollama import")
    
    return str(output_file)

