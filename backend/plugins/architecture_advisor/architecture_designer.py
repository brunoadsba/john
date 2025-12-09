"""
Sugere arquitetura, stack e diretórios com base em requisitos.
"""

from typing import Dict, Optional

from backend.plugins.architecture_advisor.knowledge_base import ARCHITECTURE_PATTERNS, get_directory_suggestion


def _choose_pattern(requirements: Dict, project_type: Optional[str]) -> str:
    if project_type and project_type.lower() == "mobile":
        return "monolith"
    if len(requirements.get("functional_requirements", [])) > 6:
        return "microservices"
    return "monolith"


def _diagram(pattern: str) -> str:
    if pattern == "microservices":
        return "\n".join(
            [
                "Client -> API Gateway -> Services (Auth, Projects, Billing) -> DB/Cache",
                "Services -> Queue -> Workers",
                "Monitoring/Logs -> Alerting",
            ]
        )
    return "\n".join(
        [
            "Client -> FastAPI (App Router) -> Service Layer -> DB/Cache",
            "Background Jobs -> Queue -> Workers",
            "Observability -> Logs/Metrics",
        ]
    )


def design_architecture(requirements: Dict, project_type: Optional[str] = None) -> Dict:
    pattern = _choose_pattern(requirements, project_type)
    info = ARCHITECTURE_PATTERNS.get(pattern, {})
    directories = get_directory_suggestion(project_type or "")
    return {
        "pattern": pattern,
        "when_to_use": info.get("quando_usar", []),
        "benefits": info.get("beneficios", []),
        "risks": info.get("riscos", []),
        "suggested_stack": info.get("stack_sugerida", []),
        "directories": directories,
        "diagram": _diagram(pattern),
    }

