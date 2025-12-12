"""
Testes unitários para JobSearchPlugin
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.plugins.job_search_plugin import JobSearchPlugin


@pytest.fixture
def mock_web_search_plugin():
    """Cria um mock do WebSearchPlugin"""
    mock = Mock()
    mock.is_enabled.return_value = True
    mock.search.return_value = [
        {
            "title": "Desenvolvedor Python - Vaga Ativa",
            "url": "https://linkedin.com/jobs/123",
            "snippet": "Empresa X está contratando desenvolvedor Python remoto. Salário competitivo."
        },
        {
            "title": "Vaga Encerrada - Analista de Dados",
            "url": "https://indeed.com/jobs/456",
            "snippet": "Esta vaga foi encerrada e não aceita mais candidaturas."
        },
        {
            "title": "Engenheiro de Software - Remoto",
            "url": "https://glassdoor.com/jobs/789",
            "snippet": "Oportunidade para engenheiro de software trabalhando remotamente."
        }
    ]
    return mock


@pytest.fixture
def job_plugin(mock_web_search_plugin):
    """Cria uma instância do JobSearchPlugin para testes"""
    return JobSearchPlugin(web_search_plugin=mock_web_search_plugin)


class TestJobSearchPlugin:
    """Testes para JobSearchPlugin"""
    
    def test_plugin_initialization(self, mock_web_search_plugin):
        """Testa inicialização do plugin"""
        plugin = JobSearchPlugin(web_search_plugin=mock_web_search_plugin)
        assert plugin.name == "job_search"
        assert plugin.description == "Busca vagas de emprego ativas e recentes com filtros inteligentes"
        assert plugin.max_results == 10
        assert plugin.days_back == 30
    
    def test_is_enabled_with_web_search(self, mock_web_search_plugin):
        """Testa se plugin está habilitado quando web_search está disponível"""
        plugin = JobSearchPlugin(web_search_plugin=mock_web_search_plugin)
        assert plugin.is_enabled() is True
    
    def test_is_enabled_without_web_search(self):
        """Testa se plugin está desabilitado quando web_search não está disponível"""
        plugin = JobSearchPlugin(web_search_plugin=None)
        assert plugin.is_enabled() is False
    
    def test_can_handle_job_query(self, job_plugin):
        """Testa detecção de queries sobre vagas"""
        assert job_plugin.can_handle("Quero procurar vagas de emprego")
        assert job_plugin.can_handle("Tem oportunidade de trabalho?")
        assert job_plugin.can_handle("Buscar cargo de desenvolvedor")
        assert job_plugin.can_handle("Oportunidades de carreira")
        assert job_plugin.can_handle("Preciso de um emprego")
    
    def test_can_handle_non_job_query(self, job_plugin):
        """Testa que queries não relacionadas a vagas retornam False"""
        assert job_plugin.can_handle("Qual é a capital do Brasil?") is False
        assert job_plugin.can_handle("Calcule 2 + 2") is False
        assert job_plugin.can_handle("Como está o tempo hoje?") is False
    
    def test_get_tool_definition(self, job_plugin):
        """Testa definição da tool"""
        tool_def = job_plugin.get_tool_definition()
        
        assert tool_def["type"] == "function"
        assert tool_def["function"]["name"] == "job_search"
        assert "vagas" in tool_def["function"]["description"].lower()
        
        params = tool_def["function"]["parameters"]["properties"]
        assert "cargo" in params
        assert "localizacao" in params
        assert "area" in params
        assert "modalidade" in params
    
    def test_execute_basic_search(self, job_plugin, mock_web_search_plugin):
        """Testa busca básica de vagas"""
        result = job_plugin.execute(
            "job_search",
            {"cargo": "desenvolvedor Python"}
        )
        
        assert isinstance(result, str)
        assert "vagas encontradas" in result.lower()
        assert "desenvolvedor" in result.lower()
        mock_web_search_plugin.search.assert_called_once()
    
    def test_execute_with_all_filters(self, job_plugin, mock_web_search_plugin):
        """Testa busca com todos os filtros"""
        result = job_plugin.execute(
            "job_search",
            {
                "cargo": "analista de dados",
                "localizacao": "São Paulo",
                "area": "TI",
                "modalidade": "remoto"
            }
        )
        
        assert isinstance(result, str)
        assert "vagas encontradas" in result.lower()
        # Verifica que a query foi construída corretamente
        call_args = mock_web_search_plugin.search.call_args
        assert call_args is not None
        query = call_args[0][0]
        assert "analista de dados" in query.lower()
        assert "remoto" in query.lower()
    
    def test_execute_filters_closed_jobs(self, job_plugin, mock_web_search_plugin):
        """Testa que vagas encerradas são filtradas"""
        result = job_plugin.execute(
            "job_search",
            {"cargo": "analista"}
        )
        
        # Verifica que a vaga encerrada não aparece no resultado
        assert "encerrada" not in result.lower()
        assert "desenvolvedor python" in result.lower()
    
    def test_execute_no_results(self, mock_web_search_plugin):
        """Testa comportamento quando não há resultados"""
        mock_web_search_plugin.search.return_value = []
        plugin = JobSearchPlugin(web_search_plugin=mock_web_search_plugin)
        
        result = plugin.execute("job_search", {"cargo": "teste"})
        assert "nenhuma vaga encontrada" in result.lower()
    
    def test_execute_no_web_search(self):
        """Testa comportamento quando web_search não está disponível"""
        plugin = JobSearchPlugin(web_search_plugin=None)
        
        result = plugin.execute("job_search", {"cargo": "teste"})
        assert "não disponível" in result.lower()
    
    def test_execute_invalid_function(self, job_plugin):
        """Testa erro ao executar função inválida"""
        with pytest.raises(ValueError, match="Função 'invalid' não suportada"):
            job_plugin.execute("invalid", {})
    
    def test_build_search_query(self, job_plugin):
        """Testa construção de query de busca"""
        query = job_plugin.query_builder.build_query(
            cargo="desenvolvedor Python",
            localizacao="São Paulo",
            area="TI",
            modalidade="remoto"
        )
        
        assert "desenvolvedor python" in query.lower()
        assert "remoto" in query.lower()
        assert "site:" in query.lower()
        assert "-encerrada" in query.lower() or "-expired" in query.lower()
    
    def test_build_search_query_minimal(self, job_plugin):
        """Testa construção de query com parâmetros mínimos"""
        query = job_plugin.query_builder.build_query("", "", "", "")
        
        assert "vaga" in query.lower()
        assert "emprego" in query.lower()
        assert "site:" in query.lower()
    
    def test_filter_jobs(self, job_plugin):
        """Testa filtragem de vagas"""
        results = [
            {
                "title": "Vaga Ativa",
                "url": "https://linkedin.com/jobs/1",
                "snippet": "Vaga aberta para desenvolvedor"
            },
            {
                "title": "Vaga Encerrada",
                "url": "https://indeed.com/jobs/2",
                "snippet": "Esta vaga foi encerrada"
            },
            {
                "title": "Oportunidade de Emprego",
                "url": "https://vagas.com/jobs/3",
                "snippet": "Empresa contratando"
            }
        ]
        
        filtered = job_plugin.filter.filter_jobs(results)
        
        # Vaga encerrada deve ser removida
        assert len(filtered) == 2
        assert all("encerrada" not in r["title"].lower() for r in filtered)
    
    def test_format_results(self, job_plugin):
        """Testa formatação de resultados em Markdown"""
        results = [
            {
                "title": "Desenvolvedor Python",
                "url": "https://example.com/job/1",
                "snippet": "Descrição da vaga"
            },
            {
                "title": "Analista de Dados",
                "url": "https://example.com/job/2",
                "snippet": "Outra descrição"
            }
        ]
        
        formatted = job_plugin.formatter.format_results(results, "desenvolvedor", "São Paulo")
        
        assert "##" in formatted  # Markdown heading
        assert "Desenvolvedor Python" in formatted
        assert "Analista de Dados" in formatted
        assert "https://example.com/job/1" in formatted
        assert "desenvolvedor" in formatted.lower()
        assert "são paulo" in formatted.lower()

