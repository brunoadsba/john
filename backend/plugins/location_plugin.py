"""
Plugin de Localização para o Jonh Assistant
Fornece informações sobre localização do usuário
"""
from typing import Dict, Any, Optional
from loguru import logger

from backend.core.plugin_manager import BasePlugin
from backend.services.geocoding_service import GeocodingService


class LocationPlugin(BasePlugin):
    """
    Plugin de informações de localização
    """
    
    def __init__(self, geocoding_service: Optional[GeocodingService] = None):
        """
        Inicializa o plugin de localização
        
        Args:
            geocoding_service: Serviço de geocodificação (cria novo se None)
        """
        self.geocoding_service = geocoding_service or GeocodingService()
        logger.info("LocationPlugin inicializado")
    
    @property
    def name(self) -> str:
        """Nome único do plugin"""
        return "location"
    
    @property
    def description(self) -> str:
        """Descrição do plugin"""
        return "Fornece informações sobre localização do usuário (cidade, estado, país)"
    
    def is_enabled(self) -> bool:
        """Sempre habilitado"""
        return True
    
    def can_handle(self, query: str) -> bool:
        """
        Verifica se a query é sobre localização
        """
        location_keywords = [
            'onde estou', 'minha localização', 'minha cidade', 'minha localização',
            'localização', 'cidade', 'estado atual', 'onde eu estou',
            'qual minha cidade', 'onde estou localizado'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in location_keywords)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna definição da ferramenta no formato OpenAI Function Calling
        """
        return {
            "type": "function",
            "function": {
                "name": "get_location_info",
                "description": "Obtém informações de localização baseado em coordenadas GPS (latitude e longitude). Retorna cidade, estado, país e endereço formatado. Use quando o usuário perguntar onde está, qual sua cidade, ou quando precisar de informações sobre localização geográfica.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude da localização (entre -90 e 90)"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude da localização (entre -180 e 180)"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            }
        }
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executa busca de informações de localização
        """
        if function_name != "get_location_info":
            raise ValueError(f"Função '{function_name}' não suportada por este plugin")
        
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")
        
        if latitude is None or longitude is None:
            return "❌ Coordenadas de localização não fornecidas."
        
        try:
            # Chama método async do geocoding service
            import asyncio
            
            try:
                # Tenta obter o loop atual
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Se já está rodando, usa run_until_complete em thread separada
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self.geocoding_service.reverse_geocode(latitude, longitude)
                        )
                        result = future.result(timeout=10)
                else:
                    result = loop.run_until_complete(
                        self.geocoding_service.reverse_geocode(latitude, longitude)
                    )
            except RuntimeError:
                # Nenhum loop, cria novo
                result = asyncio.run(
                    self.geocoding_service.reverse_geocode(latitude, longitude)
                )
            
            if not result:
                return "❌ Não foi possível determinar sua localização. Verifique se as coordenadas estão corretas."
            
            # Formata resposta
            city = result.get("city", "Desconhecida")
            state = result.get("state", "")
            country = result.get("country", "")
            address = result.get("address", "")
            
            response = f"📍 **Sua localização:**\n\n"
            response += f"**Cidade:** {city}\n"
            if state:
                response += f"**Estado:** {state}\n"
            if country:
                response += f"**País:** {country}\n"
            response += f"\n**Endereço completo:** {address}"
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao obter informações de localização: {e}")
            return f"⚠️ Erro ao obter informações de localização: {str(e)}"

