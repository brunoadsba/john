"""
Formatador robusto de resultados de vagas em Markdown
"""
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
from backend.plugins.job_date_extractor import JobDateExtractor


class JobSearchFormatter:
    """Formata resultados de vagas em Markdown com validação e sanitização"""
    
    def __init__(self):
        self.date_extractor = JobDateExtractor()
    
    def format_results(
        self,
        results: List[Dict[str, str]],
        cargo: Optional[str] = None,
        localizacao: Optional[str] = None,
        area: Optional[str] = None,
        modalidade: Optional[str] = None
    ) -> str:
        """
        Formata resultados em Markdown com validação robusta
        
        Args:
            results: Lista de resultados de vagas
            cargo: Cargo procurado (opcional)
            localizacao: Localização (opcional)
            area: Área de atuação (opcional)
            modalidade: Modalidade (opcional)
            
        Returns:
            String formatada em Markdown
        """
        if not results:
            return "❌ Nenhuma vaga encontrada. Tente refinar sua busca com outros termos."
        
        try:
            lines = []
            
            # Cabeçalho
            lines.append(f"## 💼 Vagas Encontradas ({len(results)} resultado{'s' if len(results) > 1 else ''})\n")
            
            # Informações da busca (se disponíveis)
            search_info = []
            if cargo:
                search_info.append(f"**Cargo:** {self._escape_markdown(cargo)}")
            if localizacao:
                search_info.append(f"**Localização:** {self._escape_markdown(localizacao)}")
            if area:
                search_info.append(f"**Área:** {self._escape_markdown(area)}")
            if modalidade:
                search_info.append(f"**Modalidade:** {self._escape_markdown(modalidade)}")
            
            if search_info:
                lines.extend(search_info)
                lines.append("")  # Linha em branco
            
            # Lista de vagas
            for i, result in enumerate(results, 1):
                try:
                    title = self._sanitize_text(result.get("title", "Sem título") or "Sem título")
                    url = (result.get("url", "") or "").strip()
                    snippet = self._sanitize_text(result.get("snippet", "") or "")
                    
                    # Valida título
                    if not title or title == "Sem título":
                        if url:
                            # Tenta extrair título da URL
                            title = self._extract_title_from_url(url) or "Vaga sem título"
                        else:
                            title = "Vaga sem título"
                    
                    # Extrai datas e site
                    dates = self.date_extractor.extract_dates(title, snippet, url)
                    site_name = self.date_extractor.extract_site_name(url)
                    
                    # Formata título (escapa Markdown)
                    title_escaped = self._escape_markdown(title)
                    lines.append(f"### {i}. {title_escaped}")
                    
                    # Informações da vaga
                    info_parts = []
                    
                    # Site de origem
                    if site_name and site_name != "Site desconhecido":
                        info_parts.append(f"**Site:** {site_name}")
                    
                    # Data de publicação
                    if dates.get('posted_date'):
                        info_parts.append(f"**Postada em:** {dates['posted_date']}")
                    
                    # Data de encerramento
                    if dates.get('closing_date'):
                        info_parts.append(f"**Encerra em:** {dates['closing_date']}")
                    
                    if info_parts:
                        lines.append(" | ".join(info_parts))
                        lines.append("")
                    
                    # Formata snippet
                    if snippet:
                        snippet_clean = self._truncate_text(snippet, max_length=200)
                        snippet_escaped = self._escape_markdown(snippet_clean)
                        lines.append(f"{snippet_escaped}")
                    
                    # Formata URL
                    if url and self._is_valid_url(url):
                        lines.append(f"🔗 [Ver vaga completa]({self._escape_url(url)})")
                    elif url:
                        # URL inválida, mostra apenas como texto
                        lines.append(f"🔗 URL: {self._escape_markdown(url[:50])}...")
                    
                    lines.append("")  # Linha em branco
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao formatar resultado {i}: {e}")
                    continue
            
            # Rodapé
            lines.append("---")
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
            lines.append(f"*Última atualização: {timestamp}*")
            
            formatted = "\n".join(lines)
            
            # Valida tamanho final
            if len(formatted) > 5000:
                logger.warning(f"⚠️ Resultado formatado muito grande ({len(formatted)} chars)")
                # Trunca mantendo estrutura
                formatted = formatted[:4900] + "\n\n*... (resultado truncado)*"
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar resultados: {e}")
            return f"⚠️ Erro ao formatar resultados: {str(e)}"
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitiza texto removendo caracteres problemáticos"""
        if not text:
            return ""
        
        # Remove caracteres de controle
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Normaliza espaços
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _escape_markdown(self, text: str) -> str:
        """Escapa caracteres especiais do Markdown"""
        if not text:
            return ""
        
        # Escapa caracteres especiais
        replacements = {
            '#': '\\#',
            '*': '\\*',
            '_': '\\_',
            '[': '\\[',
            ']': '\\]',
            '(': '\\(',
            ')': '\\)',
        }
        
        result = text
        for char, escaped in replacements.items():
            result = result.replace(char, escaped)
        
        return result
    
    def _escape_url(self, url: str) -> str:
        """Escapa URL para Markdown (remove caracteres perigosos)"""
        if not url:
            return ""
        
        # Remove caracteres perigosos
        url = url.replace(' ', '%20')
        return url
    
    def _truncate_text(self, text: str, max_length: int = 200) -> str:
        """Trunca texto mantendo palavras completas"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        # Tenta truncar em palavra completa
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:  # Se encontrar espaço em 70% do texto
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _extract_title_from_url(self, url: str) -> Optional[str]:
        """Tenta extrair título da URL"""
        try:
            # Remove protocolo
            url = url.replace('https://', '').replace('http://', '')
            # Pega última parte do path
            parts = url.split('/')
            if parts:
                last_part = parts[-1]
                # Remove query string
                if '?' in last_part:
                    last_part = last_part.split('?')[0]
                # Decodifica e limpa
                last_part = last_part.replace('-', ' ').replace('_', ' ')
                if last_part and len(last_part) > 3:
                    return last_part.title()
        except Exception:
            pass
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Verifica se URL é válida"""
        if not url:
            return False
        return url.startswith(('http://', 'https://')) and '.' in url

