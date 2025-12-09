"""
Gera checklists de segurança por tipo de projeto.
"""

from typing import Dict, List

from backend.plugins.architecture_advisor.knowledge_base import SECURITY_CHECKLISTS


def generate_security_checklist(project_type: str, features: List[str]) -> Dict:
    base = SECURITY_CHECKLISTS.get(project_type.lower(), SECURITY_CHECKLISTS.get("api", []))
    extras = []
    if any(f.lower() in ["pagamento", "billing", "checkout"] for f in features):
        extras.append("PCI-DSS e tokenização de cartão; Webhook com assinatura e replay protection")
    if any(f.lower() in ["voz", "áudio", "transcrição"] for f in features):
        extras.append("Privacidade de áudio, retenção mínima e criptografia em repouso")
    return {"project_type": project_type, "items": base + extras}

