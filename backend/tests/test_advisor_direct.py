"""
Teste direto do Architecture Advisor - chama o plugin diretamente sem passar pelo LLM
"""
from backend.plugins.architecture_advisor_plugin import ArchitectureAdvisorPlugin
from loguru import logger

def test_direct_call():
    """Testa chamada direta ao plugin"""
    logger.info("🧪 Testando chamada direta ao Architecture Advisor")
    
    plugin = ArchitectureAdvisorPlugin()
    
    # Teste 1: analyze_requirements
    logger.info("\n1. Testando analyze_requirements...")
    result1 = plugin.execute("architecture_advisor", {
        "action": "analyze_requirements",
        "description": "Sistema de notificações push para app mobile",
        "project_type": "mobile"
    })
    logger.info(f"✅ Resultado: {result1}")
    
    # Teste 2: security_checklist
    logger.info("\n2. Testando security_checklist...")
    result2 = plugin.execute("architecture_advisor", {
        "action": "security_checklist",
        "project_type": "web",
        "features": ["pagamentos", "autenticação"]
    })
    logger.info(f"✅ Resultado: {result2}")
    
    # Verifica se os resultados estão corretos
    assert result1.get("success") == True, "analyze_requirements deve retornar success=True"
    assert result2.get("success") == True, "security_checklist deve retornar success=True"
    
    logger.info("\n✅ Todos os testes diretos passaram!")
    return True

if __name__ == "__main__":
    try:
        test_direct_call()
        print("\n✅ Plugin funcionando corretamente!")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        logger.error(traceback.format_exc())
        exit(1)

