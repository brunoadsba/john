"""
Testes unitários para JobClosedDetector
"""
import pytest
from backend.plugins.job_closed_detector import JobClosedDetector


@pytest.fixture
def detector():
    """Cria uma instância do detector para testes"""
    return JobClosedDetector()


class TestJobClosedDetector:
    """Testes para JobClosedDetector"""
    
    def test_detector_initialization(self, detector):
        """Testa inicialização do detector"""
        assert detector is not None
        assert len(detector.pt_keywords) > 0
        assert len(detector.en_keywords) > 0
        assert len(detector.regex_patterns) > 0
    
    def test_detect_closed_portuguese(self, detector):
        """Testa detecção de vagas encerradas em português"""
        # Vaga encerrada
        assert detector.is_closed(
            title="Desenvolvedor Python",
            snippet="Esta vaga foi encerrada e não aceita mais candidaturas"
        ) is True
        
        # Vaga fechada
        assert detector.is_closed(
            title="Vaga Fechada - Analista",
            snippet="Esta posição está fechada"
        ) is True
        
        # Vaga finalizada
        assert detector.is_closed(
            title="Analista de Dados",
            snippet="Vaga finalizada em dezembro"
        ) is True
        
        # Vaga preenchida
        assert detector.is_closed(
            title="Gerente de Projetos",
            snippet="Esta vaga já foi preenchida"
        ) is True
    
    def test_detect_closed_english(self, detector):
        """Testa detecção de vagas encerradas em inglês"""
        # Position filled
        assert detector.is_closed(
            title="Python Developer",
            snippet="This position has been filled"
        ) is True
        
        # Application closed
        assert detector.is_closed(
            title="Data Analyst",
            snippet="Application period is closed"
        ) is True
        
        # Expired
        assert detector.is_closed(
            title="Software Engineer",
            snippet="This job posting has expired"
        ) is True
    
    def test_detect_closed_regex_patterns(self, detector):
        """Testa detecção usando padrões regex"""
        # Padrão "Esta vaga foi encerrada"
        assert detector.is_closed(
            snippet="Esta vaga foi encerrada no mês passado"
        ) is True
        
        # Padrão "Não aceita mais candidaturas"
        assert detector.is_closed(
            snippet="Não aceita mais candidaturas para esta posição"
        ) is True
        
        # Padrão "Inscrições encerradas"
        assert detector.is_closed(
            snippet="Inscrições encerradas desde ontem"
        ) is True
    
    def test_detect_closed_url(self, detector):
        """Testa detecção de vagas encerradas pela URL"""
        assert detector.is_closed(
            url="https://linkedin.com/jobs/closed/123"
        ) is True
        
        assert detector.is_closed(
            url="https://indeed.com/job/expired/456"
        ) is True
        
        assert detector.is_closed(
            url="https://glassdoor.com/position/filled/789"
        ) is True
    
    def test_detect_active_jobs(self, detector):
        """Testa que vagas ativas não são detectadas como encerradas"""
        # Vaga ativa
        assert detector.is_closed(
            title="Desenvolvedor Python",
            snippet="Vaga aberta para desenvolvedor Python. Aceita candidaturas."
        ) is False
        
        # Vaga com "vagas abertas"
        assert detector.is_closed(
            title="Vagas Abertas - TI",
            snippet="Temos várias vagas abertas para profissionais de TI"
        ) is False
        
        # Vaga com "inscrições abertas"
        assert detector.is_closed(
            snippet="Inscrições abertas até o final do mês"
        ) is False
        
        # Vaga normal sem indicadores
        assert detector.is_closed(
            title="Analista de Dados",
            snippet="Buscamos analista de dados para nossa equipe"
        ) is False
    
    def test_negation_context(self, detector):
        """Testa que negações não geram falsos positivos"""
        # "Não está encerrada"
        assert detector.is_closed(
            snippet="Esta vaga não está encerrada, ainda aceita candidaturas"
        ) is False
        
        # "Não foi fechada"
        assert detector.is_closed(
            snippet="A vaga não foi fechada, continuamos recebendo CVs"
        ) is False
    
    def test_filter_closed_jobs(self, detector):
        """Testa filtragem de lista de resultados"""
        results = [
            {
                "title": "Vaga Ativa",
                "snippet": "Aceitando candidaturas",
                "url": "https://linkedin.com/job/1"
            },
            {
                "title": "Vaga Encerrada",
                "snippet": "Esta vaga foi encerrada",
                "url": "https://indeed.com/job/2"
            },
            {
                "title": "Outra Vaga Ativa",
                "snippet": "Vaga aberta para desenvolvedor",
                "url": "https://glassdoor.com/job/3"
            },
            {
                "title": "Vaga Fechada",
                "snippet": "Posição fechada, não aceita mais",
                "url": "https://vagas.com/job/4"
            }
        ]
        
        filtered = detector.filter_closed_jobs(results)
        
        # Deve manter apenas 2 vagas ativas
        assert len(filtered) == 2
        assert filtered[0]["title"] == "Vaga Ativa"
        assert filtered[1]["title"] == "Outra Vaga Ativa"
    
    def test_edge_cases(self, detector):
        """Testa casos extremos"""
        # Texto vazio
        assert detector.is_closed(title="", snippet="", url="") is False
        
        # Apenas título vazio
        assert detector.is_closed(
            title="Desenvolvedor",
            snippet="",
            url=""
        ) is False
        
        # Lista vazia
        assert detector.filter_closed_jobs([]) == []
    
    def test_multiple_indicators(self, detector):
        """Testa detecção com múltiplos indicadores"""
        # Múltiplos indicadores de vaga encerrada
        assert detector.is_closed(
            title="Vaga Encerrada - Desenvolvedor",
            snippet="Esta vaga foi fechada e não aceita mais candidaturas. Inscrições encerradas.",
            url="https://site.com/closed/job/123"
        ) is True
    
    def test_active_indicators_priority(self, detector):
        """Testa que indicadores de vaga ativa têm prioridade"""
        # Mesmo tendo palavras como "encerrada", se tem "vagas abertas" deve ser ativa
        assert detector.is_closed(
            snippet="Temos várias vagas abertas, mesmo algumas anteriormente encerradas foram reabertas"
        ) is False

