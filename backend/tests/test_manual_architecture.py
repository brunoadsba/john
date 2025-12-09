"""
Teste manual do Architecture Advisor via API REST
Testa com prompts reais e verifica se funciona end-to-end
"""
import asyncio
import httpx
import time
from loguru import logger

BASE_URL = "http://localhost:8000"
TIMEOUT = 120.0  # 2 minutos para processar


async def test_prompt(prompt: str, expected_intent: str = None):
    """Testa um prompt específico"""
    logger.info("=" * 80)
    logger.info(f"📤 Testando: '{prompt}'")
    logger.info("=" * 80)
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/process_text",
                data={"texto": prompt},
                timeout=TIMEOUT
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                intent = response.headers.get("X-Architecture-Intent", "")
                resposta = response.headers.get("X-Response-Text", "")
                processing_time = response.headers.get("X-Processing-Time", "0")
                tokens = response.headers.get("X-Tokens-Used", "0")
                
                logger.info(f"✅ Status: {response.status_code}")
                logger.info(f"⏱️  Tempo total: {elapsed:.2f}s")
                logger.info(f"⏱️  Tempo de processamento: {processing_time}s")
                logger.info(f"🎯 Tokens usados: {tokens}")
                logger.info(f"🏗️ Intenção detectada: {intent if intent else 'Nenhuma'}")
                logger.info(f"📝 Resposta ({len(resposta)} chars):")
                logger.info(f"   {resposta[:300]}...")
                
                if expected_intent:
                    if intent == expected_intent:
                        logger.info(f"✅ Intenção correta: {intent}")
                        return True
                    else:
                        logger.warning(f"⚠️ Intenção esperada: {expected_intent}, detectada: {intent}")
                        return False
                
                return True
            else:
                logger.error(f"❌ Erro {response.status_code}: {response.text[:500]}")
                return False
                
        except httpx.TimeoutException:
            logger.error(f"❌ Timeout após {elapsed:.2f}s")
            return False
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


async def main():
    """Executa testes manuais"""
    logger.info("🚀 Iniciando testes manuais do Architecture Advisor")
    logger.info(f"🌐 Conectando em: {BASE_URL}")
    
    test_cases = [
        ("Analise os requisitos de um sistema de notificações push para app mobile", "analyze_requirements"),
        ("Me dê um checklist de segurança para aplicação web com pagamentos", "security_checklist"),
        ("Sugira uma arquitetura para sistema de e-commerce", "design_architecture"),
    ]
    
    results = []
    
    for prompt, expected_intent in test_cases:
        logger.info("\n")
        success = await test_prompt(prompt, expected_intent)
        results.append((prompt[:50], success))
        
        # Aguarda entre testes
        await asyncio.sleep(2)
    
    # Resumo
    logger.info("\n" + "=" * 80)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 80)
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    for prompt, success in results:
        status = "✅" if success else "❌"
        logger.info(f"{status} {prompt}...")
    
    logger.info(f"\n✅ {passed}/{total} testes passaram")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

