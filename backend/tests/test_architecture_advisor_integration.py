"""
Testes de integração do Architecture Advisor no fluxo real do LLM
Valida se o LLM consegue chamar o plugin corretamente via REST API
"""
import asyncio
import httpx
import json
from typing import Dict, Any
from loguru import logger

# Configuração
BASE_URL = "http://localhost:8000"
TIMEOUT = 120.0  # 120 segundos para processar (aumentado para LLM + plugin)


async def _process_text(prompt: str, session_id: str = None) -> Dict[str, Any]:
    """
    Testa processamento de texto via REST API
    
    Args:
        prompt: Texto para processar
        session_id: ID da sessão (opcional)
        
    Returns:
        Resposta da API com headers
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        data = {"texto": prompt}
        if session_id:
            data["session_id"] = session_id
        
        logger.info(f"📤 Enviando prompt: '{prompt[:80]}...'")
        
        response = await client.post(
            f"{BASE_URL}/api/process_text",
            data=data
        )
        
        response.raise_for_status()
        
        # Extrai informações dos headers
        result = {
            "status_code": response.status_code,
            "input_text": response.headers.get("X-Input-Text", ""),
            "response_text": response.headers.get("X-Response-Text", ""),
            "session_id": response.headers.get("X-Session-ID", ""),
            "processing_time": float(response.headers.get("X-Processing-Time", "0")),
            "tokens_used": int(response.headers.get("X-Tokens-Used", "0")),
            "audio_length": len(response.content),
        }
        
        logger.info(f"✅ Resposta recebida em {result['processing_time']:.2f}s")
        logger.info(f"📝 Resposta: '{result['response_text'][:200]}...'")
        
        return result


async def test_scenario_1_requirements_analysis():
    """
    Cenário 1: Análise de requisitos de uma feature nova
    """
    logger.info("=" * 80)
    logger.info("CENÁRIO 1: Análise de Requisitos")
    logger.info("=" * 80)
    
    prompt = (
        "Preciso criar uma nova feature para meu app: um sistema de notificações push "
        "que envia alertas personalizados para usuários baseado em suas preferências. "
        "Analise os requisitos dessa feature e me dê um checklist completo."
    )
    
    result = await _process_text(prompt)
    
    # Validações
    assert result["status_code"] == 200, "Status code deve ser 200"
    assert result["response_text"], "Deve ter resposta de texto"
    assert "requisito" in result["response_text"].lower() or "checklist" in result["response_text"].lower(), \
        "Resposta deve mencionar requisitos ou checklist"
    
    logger.info("✅ Cenário 1 passou!")
    return result


async def test_scenario_2_security_checklist():
    """
    Cenário 2: Checklist de segurança para web+pagamento
    """
    logger.info("=" * 80)
    logger.info("CENÁRIO 2: Checklist de Segurança Web+Pagamento")
    logger.info("=" * 80)
    
    prompt = (
        "Estou desenvolvendo uma aplicação web que vai processar pagamentos online. "
        "Preciso de um checklist completo de segurança para garantir que está tudo protegido. "
        "Gere um checklist de segurança para esse tipo de aplicação."
    )
    
    result = await _process_text(prompt)
    
    # Validações
    assert result["status_code"] == 200, "Status code deve ser 200"
    assert result["response_text"], "Deve ter resposta de texto"
    
    # Verifica se menciona segurança
    response_lower = result["response_text"].lower()
    security_keywords = ["segurança", "autenticação", "criptografia", "ssl", "https", "token", "validação"]
    has_security = any(keyword in response_lower for keyword in security_keywords)
    
    assert has_security, f"Resposta deve mencionar segurança. Resposta: {result['response_text'][:300]}"
    
    logger.info("✅ Cenário 2 passou!")
    return result


async def test_scenario_3_architecture_design():
    """
    Cenário 3: Design de arquitetura (extra)
    """
    logger.info("=" * 80)
    logger.info("CENÁRIO 3: Design de Arquitetura")
    logger.info("=" * 80)
    
    prompt = (
        "Quero criar um sistema de e-commerce com Next.js, PostgreSQL e Stripe. "
        "Me sugira uma arquitetura adequada para esse projeto."
    )
    
    result = await _process_text(prompt)
    
    # Validações
    assert result["status_code"] == 200, "Status code deve ser 200"
    assert result["response_text"], "Deve ter resposta de texto"
    
    logger.info("✅ Cenário 3 passou!")
    return result


async def main():
    """Executa todos os testes"""
    logger.info("🚀 Iniciando testes de integração do Architecture Advisor")
    logger.info(f"🌐 Conectando em: {BASE_URL}")
    
    results = []
    
    try:
        # Teste 1: Análise de requisitos
        result1 = await test_scenario_1_requirements_analysis()
        results.append(("Cenário 1: Requisitos", result1))
        
        # Aguarda um pouco entre testes
        await asyncio.sleep(2)
        
        # Teste 2: Checklist de segurança
        result2 = await test_scenario_2_security_checklist()
        results.append(("Cenário 2: Segurança", result2))
        
        # Aguarda um pouco entre testes
        await asyncio.sleep(2)
        
        # Teste 3: Design de arquitetura (extra)
        result3 = await test_scenario_3_architecture_design()
        results.append(("Cenário 3: Arquitetura", result3))
        
        # Resumo
        logger.info("=" * 80)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("=" * 80)
        
        for name, result in results:
            logger.info(f"\n{name}:")
            logger.info(f"  ⏱️  Tempo: {result['processing_time']:.2f}s")
            logger.info(f"  🎯 Tokens: {result['tokens_used']}")
            logger.info(f"  📝 Resposta: {result['response_text'][:150]}...")
        
        logger.info("\n✅ Todos os testes passaram!")
        
    except httpx.ConnectError:
        logger.error("❌ Erro: Não foi possível conectar ao servidor.")
        logger.error("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        logger.error("   Execute: uvicorn backend.api.main:app --reload")
        return 1
    except AssertionError as e:
        logger.error(f"❌ Teste falhou: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

