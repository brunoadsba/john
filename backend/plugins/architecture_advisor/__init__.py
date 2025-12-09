"""
Módulo do plugin Architecture Advisor.
Agrupa helpers de requisitos, arquitetura, trade-offs, segurança e escala.
"""

from backend.plugins.architecture_advisor.knowledge_base import (
    ARCHITECTURE_PATTERNS,
    TRADEOFFS,
    SECURITY_CHECKLISTS,
    SCALABILITY_PATTERNS,
)
from backend.plugins.architecture_advisor.requirements_analyzer import analyze_requirements
from backend.plugins.architecture_advisor.architecture_designer import design_architecture
from backend.plugins.architecture_advisor.tradeoff_analyzer import compare_solutions
from backend.plugins.architecture_advisor.security_checklist import generate_security_checklist
from backend.plugins.architecture_advisor.scalability_planner import plan_scalability

__all__ = [
    "ARCHITECTURE_PATTERNS",
    "TRADEOFFS",
    "SECURITY_CHECKLISTS",
    "SCALABILITY_PATTERNS",
    "analyze_requirements",
    "design_architecture",
    "compare_solutions",
    "generate_security_checklist",
    "plan_scalability",
]

