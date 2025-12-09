"""
Plugin Architecture & Design Advisor.
Fornece análise de requisitos, desenho de arquitetura, trade-offs,
checklist de segurança e plano de escalabilidade.
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from backend.core.plugin_manager import BasePlugin
from backend.plugins.architecture_advisor import (
    analyze_requirements,
    design_architecture,
    compare_solutions,
    generate_security_checklist,
    plan_scalability,
)


def _success(data: Any) -> Dict[str, Any]:
    return {"success": True, "data": data, "message": "ok"}


def _error(message: str) -> Dict[str, Any]:
    return {"success": False, "data": None, "message": message}


class ArchitectureAdvisorPlugin(BasePlugin):
    """Plugin de consultoria arquitetural"""

    @property
    def name(self) -> str:
        return "architecture_advisor"

    @property
    def description(self) -> str:
        return "Ajuda a definir requisitos, arquitetura, segurança e escalabilidade."

    def get_tool_definition(self) -> Dict[str, Any]:
        """Tool única com parâmetro action para escolher a função."""
        return {
            "type": "function",
            "function": {
                "name": "architecture_advisor",
                "description": (
                    "Analisa requisitos, recomenda arquitetura, compara soluções técnicas, "
                    "gera checklist de segurança ou plano de escalabilidade para projetos de software. "
                    "Use o parâmetro 'action' para escolher a função desejada."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "analyze_requirements",
                                "design_architecture",
                                "compare_solutions",
                                "security_checklist",
                                "plan_scalability",
                            ],
                            "description": "Tipo de análise a realizar: analyze_requirements (usa: description, project_type), design_architecture (usa: project_type, NÃO use features), compare_solutions (usa: solution1, solution2, context), security_checklist (usa: project_type, features como ARRAY), plan_scalability (usa: architecture, expected_users)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Descrição textual do projeto ou feature a ser analisada"
                        },
                        "project_type": {
                            "type": "string",
                            "description": "Tipo do projeto: web, mobile, api, desktop, microservices, etc."
                        },
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de features principais do projeto. OBRIGATÓRIO: deve ser um ARRAY de strings, nunca uma string simples. Usado APENAS para action 'security_checklist'. Exemplo correto: [\"pagamento\", \"notificações\", \"estoque\"]. NÃO use para outras actions."
                        },
                    },
                    "required": ["action"],
                },
            },
        }

    def _normalize_features(self, features: Any) -> List[str]:
        """Normaliza features: aceita string ou array e retorna array"""
        if features is None:
            return []
        if isinstance(features, str):
            # Se for string, tenta dividir por vírgula ou retorna como lista única
            if "," in features:
                return [f.strip() for f in features.split(",") if f.strip()]
            return [features.strip()] if features.strip() else []
        if isinstance(features, list):
            return [str(f) for f in features if f]
        return []
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        if function_name != "architecture_advisor":
            raise ValueError(f"Função '{function_name}' não suportada")
        action = arguments.get("action")
        
        # Remove features se não for necessário para esta action
        # features é usado apenas para security_checklist
        if action != "security_checklist" and "features" in arguments:
            logger.debug(f"Removendo 'features' de arguments (não necessário para action '{action}')")
            arguments.pop("features", None)
        
        # Normaliza features se presente (pode vir como string do LLM)
        if "features" in arguments:
            arguments["features"] = self._normalize_features(arguments["features"])
        
        try:
            if action == "analyze_requirements":
                desc = arguments.get("description", "")
                project_type = arguments.get("project_type")
                data = analyze_requirements(desc, project_type)
                return _success(data)
            if action == "design_architecture":
                reqs = arguments.get("requirements", {}) or {}
                project_type = arguments.get("project_type")
                data = design_architecture(reqs, project_type)
                return _success(data)
            if action == "compare_solutions":
                s1 = arguments.get("solution1") or ""
                s2 = arguments.get("solution2") or ""
                context = arguments.get("context", {}) or {}
                data = compare_solutions(s1, s2, context)
                return _success(data)
            if action == "security_checklist":
                project_type = arguments.get("project_type", "api")
                features: List[str] = arguments.get("features") or []
                data = generate_security_checklist(project_type, features)
                return _success(data)
            if action == "plan_scalability":
                architecture = arguments.get("architecture", {}) or {}
                expected_users: int = int(arguments.get("expected_users") or 0)
                data = plan_scalability(architecture, expected_users)
                return _success(data)
            return _error(f"Ação '{action}' não suportada")
        except Exception as exc:
            logger.error(f"Erro ao executar '{action}': {exc}")
            return _error(str(exc))

