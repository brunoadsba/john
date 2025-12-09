"""
Compara soluções técnicas com base em trade-offs pré-mapeados.
"""

from typing import Dict

from backend.plugins.architecture_advisor.knowledge_base import TRADEOFFS


def compare_solutions(solution1: str, solution2: str, context: Dict) -> Dict:
    key = None
    pair = {solution1.lower(), solution2.lower()}
    if {"sql", "nosql"}.issuperset(pair):
        key = "sql_vs_nosql"
    if {"rest", "graphql"}.issuperset(pair):
        key = "rest_vs_graphql"
    trade = TRADEOFFS.get(key or "", {})
    return {
        "solutions": [solution1, solution2],
        "pros_cons": trade,
        "context_notes": context,
        "recommendation": _recommendation(key, context),
    }


def _recommendation(key: str, context: Dict) -> str:
    if key == "sql_vs_nosql":
        if context.get("needs_reporting") or context.get("strict_consistency"):
            return "SQL para consistência e relatórios fortes"
        return "NoSQL se escala horizontal flexível for prioridade"
    if key == "rest_vs_graphql":
        if context.get("cache_heavy"):
            return "REST favorece cache simples"
        return "GraphQL se o cliente sofre de over/under-fetch"
    return "Escolha depende de requisitos mais específicos"

