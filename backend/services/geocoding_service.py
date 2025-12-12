"""
Serviço de geocodificação reversa usando Nominatim (OpenStreetMap)
"""
import aiohttp
import asyncio
from typing import Optional, Dict
from functools import lru_cache
from loguru import logger
import time


class GeocodingService:
    """Serviço de geocodificação usando Nominatim"""
    
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
    CACHE_TTL = 3600  # 1 hora
    RATE_LIMIT_DELAY = 1.0  # 1 segundo entre requisições (respeitando rate limit)
    
    def __init__(self):
        """Inicializa o serviço de geocodificação"""
        self._last_request_time = 0
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamps: Dict[str, float] = {}
        logger.info("GeocodingService inicializado (Nominatim)")
    
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        language: str = "pt"
    ) -> Optional[Dict[str, str]]:
        """
        Realiza geocodificação reversa (coordenadas → endereço)
        
        Args:
            latitude: Latitude
            longitude: Longitude
            language: Idioma do resultado (pt, en, etc)
            
        Returns:
            Dict com informações de localização ou None se erro
        """
        # Valida coordenadas
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(f"Coordenadas inválidas: lat={latitude}, lon={longitude}")
            return None
        
        # Verifica cache
        cache_key = f"{latitude:.6f},{longitude:.6f}"
        if cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.CACHE_TTL:
                logger.debug(f"Retornando do cache: {cache_key}")
                return self._cache[cache_key]
        
        # Rate limiting (Nominatim permite 1 req/s)
        await self._respect_rate_limit()
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "lat": str(latitude),
                    "lon": str(longitude),
                    "format": "json",
                    "accept-language": language,
                    "addressdetails": "1"
                }
                
                headers = {
                    "User-Agent": "Jonh Assistant/1.0"  # Nominatim requer User-Agent
                }
                
                logger.debug(f"Buscando geocodificação: {cache_key}")
                
                async with session.get(
                    self.NOMINATIM_URL,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and "address" in data:
                            result = self._parse_address(data)
                            
                            # Salva no cache
                            self._cache[cache_key] = result
                            self._cache_timestamps[cache_key] = time.time()
                            
                            logger.info(f"Geocodificação encontrada: {result.get('city', 'N/A')}")
                            return result
                        else:
                            logger.warning(f"Nenhum endereço encontrado para {cache_key}")
                            return None
                    elif response.status == 429:
                        logger.warning("Rate limit excedido no Nominatim, aguardando...")
                        await asyncio.sleep(2)
                        return await self.reverse_geocode(latitude, longitude, language)
                    else:
                        logger.error(f"Erro na geocodificação: status {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("Timeout na geocodificação")
            return None
        except Exception as e:
            logger.error(f"Erro ao fazer geocodificação: {e}")
            return None
    
    def _parse_address(self, data: Dict) -> Dict[str, str]:
        """
        Parse do resultado do Nominatim para formato padronizado
        
        Args:
            data: Dados retornados pelo Nominatim
            
        Returns:
            Dict com informações padronizadas
        """
        address = data.get("address", {})
        
        # Extrai componentes do endereço
        city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("municipality") or
            ""
        )
        
        state = (
            address.get("state") or
            address.get("region") or
            ""
        )
        
        country = address.get("country", "")
        
        # Formata endereço completo
        parts = []
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if country:
            parts.append(country)
        
        address_str = ", ".join(parts) if parts else "Localização desconhecida"
        
        return {
            "city": city,
            "state": state,
            "country": country,
            "address": address_str,
            "latitude": str(data.get("lat", "")),
            "longitude": str(data.get("lon", ""))
        }
    
    async def _respect_rate_limit(self):
        """Respeita rate limit do Nominatim (1 req/s)"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - elapsed
            await asyncio.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def clear_cache(self):
        """Limpa cache de geocodificação"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache de geocodificação limpo")

