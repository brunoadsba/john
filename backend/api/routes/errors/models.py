"""Modelos Pydantic para rotas de erros"""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ErrorReportRequest(BaseModel):
    """Modelo de requisição de reporte de erro"""
    level: str  # error, warning, critical
    type: str  # network, audio, permission, crash, other
    message: str
    stack_trace: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

