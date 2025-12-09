"""
Teste simples - apenas verifica se o servidor responde
"""
import asyncio
import httpx
from loguru import logger

BASE_URL = "http://localhost:8000"


async def test_simple():
    """Testa requisição simples"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info("Testando prompt simples...")
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": "Olá"}
            )
            
            logger.info(f"Status: {response.status_code}")
            if response.status_code == 200:
                resposta = response.headers.get("X-Response-Text", "")
                logger.info(f"✅ Resposta: {resposta[:100]}...")
                return True
            else:
                logger.error(f"❌ Erro {response.status_code}: {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_simple())
    exit(0 if success else 1)

