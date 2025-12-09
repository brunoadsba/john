"""
Script para baixar e testar o modelo Whisper large-v3
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger
from faster_whisper import WhisperModel
import time

def download_and_test_large_v3():
    """Baixa e testa o modelo Whisper large-v3"""
    
    logger.info("=" * 60)
    logger.info("Baixando modelo Whisper large-v3...")
    logger.info("=" * 60)
    
    try:
        # Modelo large-v3 com quantização int8 (recomendado para CPU)
        logger.info("Inicializando modelo large-v3 (int8)...")
        start_time = time.time()
        
        model = WhisperModel(
            "large-v3",
            device="cpu",
            compute_type="int8"
        )
        
        load_time = time.time() - start_time
        logger.info(f"✅ Modelo large-v3 carregado com sucesso em {load_time:.2f}s")
        
        # Teste rápido com áudio silencioso (apenas para verificar se carrega)
        logger.info("Testando modelo...")
        import numpy as np
        
        # Cria um áudio de teste (1 segundo de silêncio)
        sample_rate = 16000
        audio = np.zeros(sample_rate, dtype=np.float32)
        
        start_time = time.time()
        segments, info = model.transcribe(
            audio,
            language="pt",
            beam_size=5
        )
        
        # Consome o gerador
        list(segments)
        
        test_time = time.time() - start_time
        logger.info(f"✅ Teste concluído em {test_time:.2f}s")
        
        logger.info("=" * 60)
        logger.info("✅ Whisper large-v3 instalado e testado com sucesso!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📝 Próximos passos:")
        logger.info("  1. Atualize o .env com: WHISPER_MODEL=large-v3")
        logger.info("  2. Reinicie o servidor")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao baixar/testar modelo: {e}")
        logger.error("")
        logger.error("💡 Dicas:")
        logger.error("  - Verifique sua conexão com a internet")
        logger.error("  - Certifique-se de ter espaço em disco (~3GB)")
        logger.error("  - Verifique se faster-whisper está instalado: pip install faster-whisper")
        return False


if __name__ == "__main__":
    success = download_and_test_large_v3()
    sys.exit(0 if success else 1)

