"""
Base de conhecimento estática para o Architecture Advisor.
Mantém padrões, trade-offs, checklists e recomendações de escala.
"""

from typing import Dict, List

ARCHITECTURE_PATTERNS: Dict[str, Dict] = {
    "monolith": {
        "quando_usar": [
            "MVPs e times pequenos",
            "Domínio coeso e baixa complexidade",
            "Necessidade de entrega rápida",
        ],
        "beneficios": ["Menor complexidade operacional", "Deploy simplificado", "Debug mais fácil"],
        "riscos": ["Escala limitada", "Deploy único aumenta blast radius"],
        "stack_sugerida": ["FastAPI", "Postgres", "Redis", "Celery/RQ"],
    },
    "microservices": {
        "quando_usar": [
            "Domínio com bounded contexts claros",
            "Escala e autonomia de times",
            "Requisitos de deploy independente",
        ],
        "beneficios": ["Escala por serviço", "Isolamento de falhas", "Autonomia de equipe"],
        "riscos": ["Complexidade operacional", "Observabilidade e contratos exigentes"],
        "stack_sugerida": ["FastAPI", "gRPC/REST", "Postgres + Redis", "Kafka/Redpanda"],
    },
    "serverless": {
        "quando_usar": [
            "Cargas variáveis/rápidas",
            "Baixo overhead de operação",
            "Eventos e automações pontuais",
        ],
        "beneficios": ["Escala automática", "Custo sob uso", "Menos infra para gerenciar"],
        "riscos": ["Frio de start", "Limites de execução", "Vendor lock-in"],
        "stack_sugerida": ["Vercel Functions", "Supabase/Neon", "Edge cache"],
    },
}

TRADEOFFS: Dict[str, Dict[str, List[str]]] = {
    "sql_vs_nosql": {
        "sql_pros": ["ACID", "joins fortes", "maturidade", "reporting fácil"],
        "sql_contras": ["Escala horizontal requer sharding", "Schema rígido"],
        "nosql_pros": ["Escala horizontal simples", "Schema flexível", "Alta disponibilidade"],
        "nosql_contras": ["Sem joins fortes", "Consistência eventual em muitos casos"],
    },
    "rest_vs_graphql": {
        "rest_pros": ["Cache HTTP simples", "Ferramentas maduras", "Curva baixa"],
        "rest_contras": ["Over/under-fetch", "Versão por endpoint"],
        "graphql_pros": ["Schema único", "Query sob demanda", "Evolução sem versionar"],
        "graphql_contras": ["Complexidade de gateway", "Cache mais difícil", "Custo de segurança (N+1)"],
    },
}

SECURITY_CHECKLISTS: Dict[str, List[str]] = {
    "web": [
        "Autenticação robusta (MFA onde fizer sentido)",
        "Autorização por recurso/ação (RBAC/ABAC)",
        "Proteção CSRF e XSS",
        "TLS em todos os endpoints",
        "Rate limiting em auth e APIs sensíveis",
        "Logs sem dados sensíveis; mascarar PII",
        "Backups testados e restore validado",
    ],
    "mobile": [
        "Armazenar tokens com proteção do SO (Keychain/Keystore)",
        "Pinning de certificado se possível",
        "Canal seguro para analytics/telemetria",
        "Ofuscação básica para segredos",
        "Rate limiting no backend para chamadas mobile",
    ],
    "api": [
        "Auth e autorização por rota (scopes/claims)",
        "Validação de input com schema (Zod/Pydantic)",
        "Rate limiting e quotas",
        "Auditoria de chamadas sensíveis",
        "CORS restrito a domínios confiáveis",
    ],
}

SCALABILITY_PATTERNS: Dict[str, List[str]] = {
    "rapido": ["Cache em borda/CDN", "Pooling de conexões", "Reduzir N+1", "Paginação em todas as listas"],
    "crescimento": ["Auto-scaling", "Sharding/particionamento", "Fila para workloads pesados", "Circuit breaker"],
    "custo": ["Armazenar frio em tiers baratos", "Compressão de payloads", "Evitar overprovisioning"],
}


def get_directory_suggestion(project_type: str) -> List[str]:
    base = ["backend/", "backend/api/", "backend/plugins/"]
    if project_type.lower() == "mobile":
        base.append("mobile_app/lib/")
    return base

