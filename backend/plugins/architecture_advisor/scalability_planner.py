"""
Sugere ações de escala e custo com base na arquitetura desejada.
"""

from typing import Dict

from backend.plugins.architecture_advisor.knowledge_base import SCALABILITY_PATTERNS


def plan_scalability(architecture: Dict, expected_users: int) -> Dict:
    bucket = "rapido"
    if expected_users > 50000:
        bucket = "crescimento"
    actions = SCALABILITY_PATTERNS.get(bucket, [])
    if architecture.get("pattern") == "microservices":
        actions.append("API Gateway com rate limit e observabilidade centralizada")
    return {
        "expected_users": expected_users,
        "pattern": architecture.get("pattern"),
        "actions": actions,
    }

