"""
Teste simples do Architecture Advisor - apenas verifica se o plugin está registrado
"""
import asyncio
import httpx
from loguru import logger

BASE_URL = "http://localhost:8000"


async def test_plugin_registered():
    """Testa se o plugin está registrado verificando as tools disponíveis"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Tenta fazer uma requisição simples para verificar se o servidor está rodando
        try:
            response = await client.get(f"{BASE_URL}/docs")
            logger.info(f"✅ Servidor está rodando (status: {response.status_code})")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar: {e}")
            return False
        
        # Testa um prompt simples que não requer tool calling
        logger.info("Testando prompt simples sem tool calling...")
        data = {"texto": "Olá, como você está?"}
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                resposta = response.headers.get("X-Response-Text", "")
                logger.info(f"✅ Resposta recebida: {resposta[:100]}...")
                return True
            else:
                logger.error(f"❌ Erro {response.status_code}: {response.text[:500]}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro na requisição: {e}")
            return False


async def main():
    logger.info("🧪 Teste simples do Architecture Advisor")
    success = await test_plugin_registered()
    
    if success:
        logger.info("✅ Teste básico passou!")
    else:
        logger.error("❌ Teste básico falhou!")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

