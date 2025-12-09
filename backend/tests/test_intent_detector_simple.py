"""
Teste simples do IntentDetector - verifica se detecta intenções corretamente
"""
import asyncio
import httpx
from loguru import logger

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


async def test_intent_detection():
    """Testa se o IntentDetector está funcionando"""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Teste 1: Prompt que deve detectar analyze_requirements
        logger.info("Teste 1: Análise de requisitos...")
        prompt1 = "Analise os requisitos de um sistema de notificações push"
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": prompt1},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                intent = response.headers.get("X-Architecture-Intent", "")
                resposta = response.headers.get("X-Response-Text", "")
                
                logger.info(f"✅ Status: {response.status_code}")
                logger.info(f"🏗️ Intenção detectada: {intent}")
                logger.info(f"📝 Resposta: {resposta[:200]}...")
                
                if intent:
                    logger.info("✅ IntentDetector funcionando!")
                    return True
                else:
                    logger.warning("⚠️ Nenhuma intenção detectada no header")
                    return False
            else:
                logger.error(f"❌ Erro {response.status_code}: {response.text[:500]}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False


async def main():
    logger.info("🧪 Testando IntentDetector...")
    success = await test_intent_detection()
    
    if success:
        logger.info("✅ Teste passou!")
    else:
        logger.error("❌ Teste falhou!")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

