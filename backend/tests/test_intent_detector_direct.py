"""
Teste direto do IntentDetector - sem passar pelo servidor
"""
import sys
sys.path.insert(0, '/home/brunoadsba/john')

from backend.services.intent_detector import IntentDetector
from loguru import logger

def test_regex_only():
    """Testa apenas regex (sem LLM)"""
    logger.info("🧪 Testando IntentDetector (regex apenas)...")
    
    detector = IntentDetector(llm_service=None)
    
    test_cases = [
        ("Analise os requisitos de um sistema de notificações push", "analyze_requirements"),
        ("Me dê um checklist de segurança para app web", "security_checklist"),
        ("Sugira uma arquitetura para e-commerce", "design_architecture"),
        ("Comparar SQL vs NoSQL", "compare_solutions"),
        ("Como escalar meu sistema?", "plan_scalability"),
        ("Olá, como você está?", None),  # Não deve detectar
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_intent in test_cases:
        intent, confidence = detector.detect(text, use_llm=False)
        
        if expected_intent is None:
            if intent is None:
                logger.info(f"✅ '{text[:50]}...' → Nenhuma intenção (correto)")
                passed += 1
            else:
                logger.error(f"❌ '{text[:50]}...' → Detectou {intent} (esperava None)")
                failed += 1
        else:
            if intent == expected_intent:
                logger.info(f"✅ '{text[:50]}...' → {intent} (confiança: {confidence:.2f})")
                passed += 1
            else:
                logger.error(f"❌ '{text[:50]}...' → {intent} (esperava {expected_intent})")
                failed += 1
    
    logger.info(f"\n📊 Resultados: {passed} passaram, {failed} falharam")
    return failed == 0

if __name__ == "__main__":
    try:
        success = test_regex_only()
        if success:
            print("\n✅ Todos os testes passaram!")
            exit(0)
        else:
            print("\n❌ Alguns testes falharam!")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        logger.error(traceback.format_exc())
        exit(1)

