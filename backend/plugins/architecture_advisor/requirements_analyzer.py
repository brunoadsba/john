"""
Analisa descrição textual para extrair requisitos e lacunas.
Heurística leve para uso offline, sem depender de LLM.
"""

from typing import Dict, List, Optional

KEYWORDS_FUNCTIONAL = ["login", "autenticação", "cadastro", "pagamento", "busca", "upload", "websocket"]
KEYWORDS_NON_FUNCTIONAL = ["latência", "performance", "escala", "segurança", "compliance", "lgpd", "gdpr", "disponibilidade"]


def _split_sentences(text: str) -> List[str]:
    parts = [p.strip() for p in text.replace("\n", ". ").split(".") if p.strip()]
    return parts


def _classify(sentences: List[str], keywords: List[str]) -> List[str]:
    return [s for s in sentences if any(k.lower() in s.lower() for k in keywords)]


def _edge_cases(requirements: List[str]) -> List[str]:
    edges = []
    for req in requirements:
        if "upload" in req.lower():
            edges.append("Arquivos grandes e tipos inválidos")
        if "pagamento" in req.lower():
            edges.append("Transações duplicadas ou timeout do gateway")
        if "login" in req.lower() or "autenticação" in req.lower():
            edges.append("Tentativas de brute force e MFA ausente")
    return edges or ["Fluxos offline/erro, timeouts, idempotência em ações críticas"]


def analyze_requirements(description: str, project_type: Optional[str] = None) -> Dict:
    sentences = _split_sentences(description)
    functional = _classify(sentences, KEYWORDS_FUNCTIONAL) or sentences[:3]
    non_functional = _classify(sentences, KEYWORDS_NON_FUNCTIONAL)
    use_cases = functional[:3]
    edge_cases = _edge_cases(functional)
    gaps = []
    if not non_functional:
        gaps.append("Definir requisitos não-funcionais: latência alvo, SLO, segurança, compliance")
    if project_type and project_type.lower() == "mobile":
        gaps.append("Especificar requisitos de rede instável e modo offline")
    return {
        "functional_requirements": functional,
        "non_functional_requirements": non_functional,
        "use_cases": use_cases,
        "edge_cases": edge_cases,
        "gaps": gaps,
    }

