"""
Plugin de busca de vagas de emprego para o Jonh Assistant
Especialista em encontrar vagas ativas e recentes com filtros inteligentes
"""
from typing import Dict, List, Optional, Any
from loguru import logger

from backend.core.plugin_manager import BasePlugin
from backend.plugins.job_query_builder import JobSearchQueryBuilder
from backend.plugins.job_result_filter import JobSearchFilter
from backend.plugins.job_result_formatter import JobSearchFormatter
from backend.plugins.job_search_helpers_execute import (
    search_with_retry,
    get_no_results_message
)
from backend.plugins.job_search_detection import JobSearchDetection


class JobSearchPlugin(BasePlugin):
    """
    Plugin especializado em busca de vagas de emprego
    """
    
    def __init__(
        self,
        web_search_plugin: Optional[Any] = None,
        max_results: int = 10,
        days_back: int = 30
    ):
        """
        Inicializa o plugin de busca de vagas
        
        Args:
            web_search_plugin: Instância do WebSearchPlugin (opcional)
            max_results: Número máximo de vagas a retornar
            days_back: Número de dias para buscar vagas (padrão: 30)
        """
        self.web_search_plugin = web_search_plugin
        self.max_results = max_results
        self.days_back = days_back
        
        # Sites prioritários para vagas (expandido com base em plataformas reais)
        from backend.plugins.job_site_config import JobSiteConfig
        self.site_config = JobSiteConfig
        self.job_sites = self.site_config.MAIN_SITES.copy()
        
        # Inicializa helpers
        # Query builder usa sites padrão, mas pode ser ajustado dinamicamente por nicho
        self.query_builder = JobSearchQueryBuilder(self.job_sites, days_back)
        self.filter = JobSearchFilter(self.job_sites)
        self.formatter = JobSearchFormatter()
        
        logger.info("✅ JobSearchPlugin inicializado")
    
    @property
    def name(self) -> str:
        """Nome único do plugin"""
        return "job_search"
    
    @property
    def description(self) -> str:
        """Descrição do plugin"""
        return "Busca vagas de emprego ativas e recentes com filtros inteligentes"
    
    def is_enabled(self) -> bool:
        """Verifica se o plugin está habilitado"""
        if not self.web_search_plugin:
            logger.warning("⚠️ JobSearchPlugin desabilitado: WebSearchPlugin não disponível")
            return False
        return self.web_search_plugin.is_enabled()
    
    def requires_network(self) -> bool:
        """Este plugin requer conexão com internet (usa WebSearchPlugin)"""
        return True
    
    def can_handle(self, query: str) -> bool:
        """
        Verifica se a query é sobre busca de vagas
        """
        return JobSearchDetection.is_job_query(query)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna definição da ferramenta no formato OpenAI Function Calling
        """
        return {
            "type": "function",
            "function": {
                "name": "job_search",
                "description": "Busca vagas de emprego ativas e recentes. Use quando o usuário perguntar sobre vagas, empregos, oportunidades de trabalho, cargos, ou procurar trabalho. Filtra automaticamente vagas encerradas e prioriza resultados recentes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cargo": {
                            "type": "string",
                            "description": "Cargo ou título da vaga procurada (ex: 'desenvolvedor Python', 'analista de dados', 'gerente de projetos')"
                        },
                        "localizacao": {
                            "type": "string",
                            "description": "Localização da vaga (cidade, estado ou 'remoto', 'presencial', 'híbrido')"
                        },
                        "area": {
                            "type": "string",
                            "description": "Área de atuação (ex: 'TI', 'marketing', 'vendas', 'RH')"
                        },
                        "modalidade": {
                            "type": "string",
                            "description": "Modalidade de trabalho: 'remoto', 'presencial', 'híbrido' ou deixe vazio",
                            "enum": ["remoto", "presencial", "híbrido", ""]
                        }
                    },
                    "required": []
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa busca de vagas com validação robusta e tratamento de erros
        
        Args:
            function_name: Nome da função (deve ser "job_search")
            arguments: Argumentos da função (cargo, localizacao, area, modalidade)
            
        Returns:
            String formatada em Markdown com lista de vagas encontradas
        """
        if function_name != "job_search":
            raise ValueError(f"Função '{function_name}' não suportada por este plugin")
        
        # Valida se web_search está disponível
        if not self.web_search_plugin:
            logger.error("❌ WebSearchPlugin não disponível")
            return "⚠️ Serviço de busca de vagas não disponível no momento."
        
        if not self.web_search_plugin.is_enabled():
            logger.error("❌ WebSearchPlugin desabilitado")
            return "⚠️ Serviço de busca de vagas está desabilitado."
        
        try:
            # Extrai e valida parâmetros
            cargo = arguments.get("cargo") or ""
            localizacao = arguments.get("localizacao") or ""
            area = arguments.get("area") or ""
            modalidade = arguments.get("modalidade") or ""
            
            # Armazena termos originais para scoring
            search_terms = {
                "cargo": cargo,
                "localizacao": localizacao,
                "area": area,
                "modalidade": modalidade
            }
            
            # Detecta nicho e ajusta sites se necessário
            niche_detected = self.site_config._detect_niche(cargo, area)
            if niche_detected:
                logger.info(f"🎯 Nicho detectado: {niche_detected}")
                sites_for_query = self.site_config.get_sites_for_query(cargo, area, detect_niche=True)
                self.query_builder.job_sites = sites_for_query
            else:
                self.query_builder.job_sites = self.job_sites
            
            # Constrói query de busca (com validação interna)
            query = self.query_builder.build_query(cargo, localizacao, area, modalidade)
            
            if not query or len(query.strip()) < 5:
                logger.error("❌ Query de busca inválida ou muito curta")
                return "⚠️ Não foi possível construir uma busca válida. Tente especificar um cargo ou área."
            
            logger.info(f"🔍 Buscando vagas: '{query[:100]}...'")
            
            # Busca usando WebSearchPlugin com múltiplas estratégias
            # ESTRATÉGIA 1: Busca principal com todos os sites principais
            results = search_with_retry(
                self.web_search_plugin,
                query,
                self.max_results * 2,  # Busca mais resultados para ter variedade
                max_retries=2
            )
            
            # ESTRATÉGIA 2: Buscas adicionais por grupos de sites para cobertura completa
            all_results = results.copy() if results else []
            
            # Se não tiver muitos resultados, faz buscas adicionais
            if len(all_results) < self.max_results:
                logger.info(f"🔄 Apenas {len(all_results)} resultados, fazendo buscas adicionais por sites...")
                
                # Divide sites em grupos e busca cada grupo
                site_groups = [self.job_sites[i:i+5] for i in range(0, len(self.job_sites), 5)]
                
                for group_sites in site_groups[1:]:  # Pula o primeiro (já foi buscado)
                    if len(all_results) >= self.max_results * 2:
                        break  # Já tem resultados suficientes
                    
                    # Cria query específica para este grupo
                    group_query = self.query_builder.build_query(cargo, localizacao, area, modalidade)
                    # Substitui sites na query
                    sites_query_group = " OR ".join([f"site:{site}" for site in group_sites])
                    group_query = group_query.replace(
                        f"({' OR '.join([f'site:{s}' for s in self.job_sites[:8]])})",
                        f"({sites_query_group})"
                    )
                    
                    group_results = search_with_retry(
                        self.web_search_plugin,
                        group_query,
                        max(self.max_results - len(all_results), 3),
                        max_retries=1
                    )
                    
                    if group_results:
                        # Adiciona apenas resultados únicos (por URL)
                        existing_urls = {r.get('url', '') for r in all_results}
                        for r in group_results:
                            if r.get('url', '') not in existing_urls:
                                all_results.append(r)
                                existing_urls.add(r.get('url', ''))
            
            results = all_results
            
            if not results:
                # ESTRATÉGIA 3: Fallback - busca genérica sem sites específicos
                logger.info("🔄 Nenhum resultado, tentando busca genérica...")
                fallback_query_parts = []
                if cargo:
                    fallback_query_parts.append(cargo)
                if area:
                    fallback_query_parts.append(area)
                if modalidade:
                    fallback_query_parts.append(modalidade)
                fallback_query_parts.append("vaga emprego")
                
                fallback_query = " ".join(fallback_query_parts)
                results = search_with_retry(
                    self.web_search_plugin,
                    fallback_query,
                    self.max_results,
                    max_retries=1
                )
            
            if not results:
                return get_no_results_message(cargo, localizacao, area)
            
            # Filtra e processa resultados (com scoring)
            filtered_results = self.filter.filter_jobs(results, search_terms)
            
            if not filtered_results:
                return "❌ Nenhuma vaga ativa encontrada. Todas as vagas podem estar encerradas ou não correspondem aos filtros."
            
            # Limita número de resultados
            final_results = filtered_results[:self.max_results]
            
            # Formata resposta em Markdown
            formatted = self.formatter.format_results(
                final_results,
                cargo=cargo if cargo else None,
                localizacao=localizacao if localizacao else None,
                area=area if area else None,
                modalidade=modalidade if modalidade else None
            )
            
            # Informa sites encontrados
            sites_found = set()
            for result in final_results:
                url = result.get('url', '')
                if url:
                    for site in self.job_sites:
                        if site in url.lower():
                            sites_found.add(site)
                            break
            
            logger.info(f"✅ Busca concluída: {len(final_results)} vagas de {len(sites_found)} site(s): {', '.join(list(sites_found)[:5])}")
            
            return formatted
            
        except ValueError as e:
            logger.error(f"❌ Erro de validação: {e}")
            return f"⚠️ Erro nos parâmetros de busca: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao buscar vagas: {e}", exc_info=True)
            return "⚠️ Ocorreu um erro ao buscar vagas. Tente novamente ou refine sua busca."
    

