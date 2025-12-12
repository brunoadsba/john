"""
Detector robusto de vagas encerradas
Classe dedicada para identificar e filtrar vagas que não estão mais ativas
"""
import re
from typing import List, Dict, Set
from loguru import logger


class JobClosedDetector:
    """
    Detector avançado de vagas encerradas com múltiplas camadas de verificação
    """
    
    def __init__(self):
        """Inicializa o detector com padrões e palavras-chave expandidos"""
        
        # Palavras-chave em português (com variações)
        self.pt_keywords: Set[str] = {
            # Status encerrado
            "encerrada", "encerradas", "encerrado", "encerrados",
            "fechada", "fechadas", "fechado", "fechados",
            "finalizada", "finalizadas", "finalizado", "finalizados",
            "concluída", "concluídas", "concluído", "concluídos",
            
            # Preenchida
            "preenchida", "preenchidas", "preenchido", "preenchidos",
            "preencheu", "preencheram",
            
            # Expirada
            "expirada", "expiradas", "expirado", "expirados",
            "vencida", "vencidas", "vencido", "vencidos",
            "expirada em", "expirou em",
            
            # Cancelada
            "cancelada", "canceladas", "cancelado", "cancelados",
            "cancelou", "cancelaram",
            
            # Encerrada temporariamente/permanentemente
            "encerrada temporariamente",
            "encerrada permanentemente",
            "fechada temporariamente",
            "fechada permanentemente",
            
            # Não aceita mais
            "não aceita mais candidaturas",
            "não está mais aceitando",
            "não aceita candidatos",
            "candidaturas encerradas",
            "inscrições encerradas",
            "inscrições fechadas",
        }
        
        # Palavras-chave em inglês
        self.en_keywords: Set[str] = {
            "closed", "expired", "filled", "finished", "ended",
            "cancelled", "cancelled", "unavailable", "unpublished",
            "no longer accepting", "not accepting", "closed for applications",
            "position filled", "job filled", "hiring closed",
            "application closed", "application period ended",
        }
        
        # Padrões regex para frases comuns
        self.regex_patterns: List[re.Pattern] = [
            # "Esta vaga foi [encerrada/fechada]"
            re.compile(r'\b(esta|essa)\s+vaga\s+(foi|está)\s+(encerrada|fechada|finalizada)', re.IGNORECASE),
            
            # "Vaga [encerrada/fechada] em [data]"
            re.compile(r'\bvaga\s+(encerrada|fechada|finalizada|expirada)\s+(em|desde|até)', re.IGNORECASE),
            
            # "Não aceita mais candidaturas"
            re.compile(r'\bnão\s+(aceita|está\s+aceitando|está\s+recebendo)\s+(mais\s+)?candidaturas?', re.IGNORECASE),
            
            # "Inscrições encerradas"
            re.compile(r'\binscrições?\s+(encerradas?|fechadas?|finalizadas?)', re.IGNORECASE),
            
            # "Position filled" / "Job filled"
            re.compile(r'\b(position|job|vaga)\s+filled\b', re.IGNORECASE),
            
            # "Application closed" / "Hiring closed"
            re.compile(r'\b(application|hiring|recruitment)\s+closed\b', re.IGNORECASE),
            
            # "No longer accepting"
            re.compile(r'\bno\s+longer\s+accepting\b', re.IGNORECASE),
            
            # Padrões de URL comuns
            re.compile(r'/closed/|/expired/|/filled/|/ended/', re.IGNORECASE),
        ]
        
        # Frases que indicam que a vaga ESTÁ ATIVA (não remover)
        self.active_indicators: Set[str] = {
            "vagas abertas", "aberta para candidaturas", "aceita candidaturas",
            "inscrições abertas", "recebendo candidaturas", "hiring now",
            "open positions", "now hiring", "currently hiring",
        }
        
        logger.info(f"✅ JobClosedDetector inicializado: {len(self.pt_keywords)} palavras PT, {len(self.en_keywords)} palavras EN, {len(self.regex_patterns)} padrões regex")
    
    def is_closed(self, title: str = "", snippet: str = "", url: str = "") -> bool:
        """
        Verifica se uma vaga está encerrada usando múltiplas camadas de detecção
        
        Args:
            title: Título da vaga
            snippet: Resumo/descrição da vaga
            url: URL da vaga
            
        Returns:
            True se a vaga está encerrada, False caso contrário
        """
        # Normaliza textos (lowercase)
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        url_lower = url.lower()
        
        # Concatena todo o texto para análise
        full_text = f"{title_lower} {snippet_lower} {url_lower}"
        
        # CAMADA 1: Verifica indicadores de vaga ATIVA (prioridade alta)
        # Se encontrar indicadores de vaga ativa, retorna False imediatamente
        for indicator in self.active_indicators:
            if indicator in full_text:
                logger.debug(f"✅ Indicador de vaga ATIVA encontrado: '{indicator}'")
                return False
        
        # CAMADA 2: Verifica padrões regex (mais específicos e confiáveis)
        for pattern in self.regex_patterns:
            if pattern.search(full_text):
                logger.debug(f"🚫 Vaga ENCERRADA detectada por regex: {pattern.pattern}")
                return True
        
        # CAMADA 3: Verifica palavras-chave em português
        for keyword in self.pt_keywords:
            # Verifica se a palavra está no texto E não está em contexto de negação
            if keyword in full_text:
                # Verifica contexto para evitar falsos positivos
                if self._is_valid_match(full_text, keyword):
                    logger.debug(f"🚫 Vaga ENCERRADA detectada por palavra PT: '{keyword}'")
                    return True
        
        # CAMADA 4: Verifica palavras-chave em inglês
        for keyword in self.en_keywords:
            if keyword in full_text:
                if self._is_valid_match(full_text, keyword):
                    logger.debug(f"🚫 Vaga ENCERRADA detectada por palavra EN: '{keyword}'")
                    return True
        
        # CAMADA 5: Verifica padrões específicos na URL
        url_indicators = ['/closed/', '/expired/', '/filled/', '/ended/', '/cancelled/']
        if any(indicator in url_lower for indicator in url_indicators):
            logger.debug(f"🚫 Vaga ENCERRADA detectada por padrão na URL")
            return True
        
        # Se passou por todas as camadas, a vaga está ativa
        return False
    
    def _is_valid_match(self, text: str, keyword: str) -> bool:
        """
        Verifica se o match da palavra-chave é válido (não está em contexto de negação)
        
        Args:
            text: Texto completo
            keyword: Palavra-chave encontrada
            
        Returns:
            True se o match é válido, False caso contrário
        """
        # Busca a posição da palavra-chave no texto
        idx = text.find(keyword)
        if idx == -1:
            return False
        
        # Verifica contexto antes da palavra (negações)
        context_before = text[max(0, idx - 50):idx].lower()
        
        # Palavras de negação que invalidam o match
        negation_words = [
            "não está", "não foi", "não está encerrada", "não está fechada",
            "ainda não", "não será", "não foi encerrada", "não foi fechada",
        ]
        
        for negation in negation_words:
            if negation in context_before:
                logger.debug(f"⚠️ Match de '{keyword}' invalidado por negação: '{negation}'")
                return False
        
        return True
    
    def filter_closed_jobs(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filtra uma lista de resultados removendo vagas encerradas
        
        Args:
            results: Lista de resultados de busca
            
        Returns:
            Lista filtrada com apenas vagas ativas
        """
        if not results:
            return []
        
        filtered = []
        closed_count = 0
        
        for result in results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")
            
            if self.is_closed(title=title, snippet=snippet, url=url):
                closed_count += 1
                logger.debug(f"🚫 Vaga removida: '{title[:50]}...'")
                continue
            
            filtered.append(result)
        
        if closed_count > 0:
            logger.info(f"✅ Filtradas {closed_count} vagas encerradas de {len(results)} resultados ({len(filtered)} vagas ativas)")
        
        return filtered

