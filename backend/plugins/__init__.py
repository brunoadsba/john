"""
Plugins do sistema Jonh Assistant
"""
from backend.plugins.web_search_plugin import WebSearchPlugin
from backend.plugins.architecture_advisor_plugin import ArchitectureAdvisorPlugin
from backend.plugins.calculator_plugin import CalculatorPlugin
from backend.plugins.currency_converter_plugin import CurrencyConverterPlugin
from backend.plugins.job_search_plugin import JobSearchPlugin

__all__ = [
    "WebSearchPlugin",
    "ArchitectureAdvisorPlugin",
    "CalculatorPlugin",
    "CurrencyConverterPlugin",
    "JobSearchPlugin",
]

