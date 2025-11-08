"""
Real-time Weather Data Integration for Maritime Routing

Supports multiple weather data providers:
1. NOAA GFS (Global Forecast System) - Free, global coverage
2. OpenWeatherMap - Free tier with API key
3. ECMWF/Copernicus - European weather data
4. CMEMS - Ocean-specific data (already integrated)

Real-time data is cached locally to minimize API calls.

REQUIRED API KEYS:
- NOAA_API_KEY: Get from https://api.weather.gov/ (free, no key needed for basic access)
- OPENWEATHER_API_KEY: Get from https://openweathermap.org/api (free tier: 60 calls/min)
- ECMWF_API_KEY (optional): Get from https://cds.climate.copernicus.eu/ (research)

References:
- NOAA GFS Documentation: https://www.ncei.noaa.gov/products/weather-global-forecasting-system
- OpenWeatherMap API: https://openweathermap.org/api
- CMEMS Data Catalog: https://marine.copernicus.eu/
"""

import requests
import json
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import hashlib
from app.core.config import settings


class WeatherDataProvider:
    """Abstract base for weather data providers"""
    
    def get_weather_point(self, lat: float, lon: float, 
                         forecast_hours: int = 0) -> Optional[Dict]:
        """
        Get weather at a single point.
        
        Args:
            lat, lon: Coordinates
            forecast_hours: Hours in future (0 = current)
        
        Returns:
            Weather dict with wind, waves, current
        """
        raise NotImplementedError
    
    def get_weather_route(self, waypoints: List[Tuple[float, float]], 
                         forecast_hours: int = 0) -> List[Dict]:
        """Get weather along route waypoints"""
        raise NotImplementedError


class NOAAGFSProvider(WeatherDataProvider):
    """
    NOAA Global Forecast System provider (Free, global coverage).
    
    Coverage: Global, 0.25° resolution
    Update frequency: Every 6 hours
    Forecast range: 0-384 hours
    """
    
    BASE_URL = "https://api.weather.gov"
    POINTS_URL = f"{BASE_URL}/points"
    GRID_URL = "https://www.ncei.noaa.gov/thredds/dodsC/model-ndfd-file"
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
    
    def _get_cache_key(self, lat: float, lon: float) -> str:
        """Generate cache key"""
        return f"noaa_{round(lat, 2)}_{round(lon, 2)}"
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and fresh"""
        if key in self.cache:
            cached_time, _ = self.cache[key]
            if (datetime.utcnow() - cached_time).total_seconds() < self.cache_duration:
                return True
        return False
    
    def get_weather_point(self, lat: float, lon: float, forecast_hours: int = 0) -> Optional[Dict]:
        """Get weather from NOAA GFS"""
        try:
            cache_key = self._get_cache_key(lat, lon)
            
            if self._is_cached(cache_key):
                _, data = self.cache[cache_key]
                return data
            
            # Get grid point data
            points_response = requests.get(
                f"{self.POINTS_URL}/{lat},{lon}",
                timeout=5
            )
            
            if points_response.status_code == 200:
                points_data = points_response.json()
                
                # Get forecast URL
                if 'properties' in points_data and 'forecast' in points_data['properties']:
                    forecast_url = points_data['properties']['forecast']
                    
                    # Get actual forecast data
                    forecast_response = requests.get(forecast_url, timeout=5)
                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json()
                        
                        weather = self._parse_forecast(forecast_data, forecast_hours)
                        self.cache[cache_key] = (datetime.utcnow(), weather)
                        return weather
        
        except Exception as e:
            print(f"[NOAA] Error getting weather for {lat},{lon}: {e}")
        
        return None
    
    def _parse_forecast(self, data: Dict, forecast_hours: int) -> Dict:
        """Parse NOAA forecast data"""
        if 'properties' not in data or 'periods' not in data['properties']:
            return self._mock_weather(0, 0)
        
        periods = data['properties']['periods']
        
        # Get appropriate period based on forecast_hours
        period_idx = min(forecast_hours // 12, len(periods) - 1)  # NOAA uses 12-hour periods
        period = periods[period_idx]
        
        wind_speed = 0
        wind_direction = 0
        
        # Parse wind info
        if 'windSpeed' in period and period['windSpeed']:
            wind_str = period['windSpeed']
            # Parse format like "10 mph"
            parts = wind_str.split()
            if parts:
                wind_speed = float(parts[0]) * 0.868976  # mph to knots
        
        if 'windDirection' in period and period['windDirection']:
            wind_direction = self._parse_direction(period['windDirection'])
        
        # Estimate wave height from wind
        wave_height = self._wind_to_wave_height(wind_speed)
        
        return {
            "source": "NOAA_GFS",
            "latitude": 0,  # Added by caller
            "longitude": 0,  # Added by caller
            "timestamp": datetime.utcnow().isoformat(),
            "wind_speed_knots": wind_speed,
            "wind_direction_deg": wind_direction,
            "wave_height_m": wave_height,
            "temperature_c": 20,  # Not always available
            "current_speed_knots": 0.3  # Not available from GFS
        }
    
    def _parse_direction(self, direction_str: str) -> float:
        """Parse direction string like 'NE' to degrees"""
        directions = {
            'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
            'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
        return directions.get(direction_str.upper(), 0)
    
    def _wind_to_wave_height(self, wind_speed_knots: float) -> float:
        """Estimate wave height from wind speed (simplified Beaufort scale)"""
        # Simplified relationship between wind speed and wave height
        if wind_speed_knots < 3:
            return 0.0
        elif wind_speed_knots < 10:
            return wind_speed_knots * 0.05
        elif wind_speed_knots < 20:
            return 0.5 + (wind_speed_knots - 10) * 0.1
        else:
            return 1.5 + (wind_speed_knots - 20) * 0.15
    
    def get_weather_route(self, waypoints: List[Tuple[float, float]], 
                         forecast_hours: int = 0) -> List[Dict]:
        """Get weather for multiple waypoints"""
        weather_data = []
        for lat, lon in waypoints:
            weather = self.get_weather_point(lat, lon, forecast_hours)
            if weather:
                weather['latitude'] = lat
                weather['longitude'] = lon
                weather_data.append(weather)
        return weather_data


class OpenWeatherMapProvider(WeatherDataProvider):
    """
    OpenWeatherMap real-time weather provider.
    
    Coverage: Global
    Update frequency: Every 10 minutes
    Free tier: 60 calls/minute
    
    API Key: https://openweathermap.org/api
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.cache = {}
        self.cache_duration = 600  # 10 minutes
    
    def get_weather_point(self, lat: float, lon: float, 
                         forecast_hours: int = 0) -> Optional[Dict]:
        """Get current weather from OpenWeatherMap"""
        try:
            if not self.api_key or self.api_key == "your-openweather-api-key":
                return None
            
            cache_key = f"owm_{round(lat, 2)}_{round(lon, 2)}"
            
            # Check cache
            if cache_key in self.cache:
                cached_time, data = self.cache[cache_key]
                if (datetime.utcnow() - cached_time).total_seconds() < self.cache_duration:
                    return data
            
            # Get current weather
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(
                f"{self.BASE_URL}/weather",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                weather = {
                    "source": "OpenWeatherMap",
                    "latitude": lat,
                    "longitude": lon,
                    "timestamp": datetime.utcnow().isoformat(),
                    "wind_speed_knots": data['wind']['speed'] * 1.94384,  # m/s to knots
                    "wind_direction_deg": data['wind'].get('deg', 0),
                    "wave_height_m": self._estimate_wave_height(data['wind']['speed']),
                    "temperature_c": data['main']['temp'],
                    "humidity_percent": data['main'].get('humidity', 50),
                    "pressure_hpa": data['main'].get('pressure', 1013),
                    "current_speed_knots": 0.3
                }
                
                self.cache[cache_key] = (datetime.utcnow(), weather)
                return weather
        
        except Exception as e:
            print(f"[OpenWeatherMap] Error: {e}")
        
        return None
    
    def _estimate_wave_height(self, wind_speed_ms: float) -> float:
        """Estimate wave height from wind speed"""
        wind_knots = wind_speed_ms * 1.94384
        if wind_knots < 3:
            return 0.0
        elif wind_knots < 10:
            return wind_knots * 0.05
        elif wind_knots < 20:
            return 0.5 + (wind_knots - 10) * 0.1
        else:
            return 1.5 + (wind_knots - 20) * 0.15
    
    def get_weather_route(self, waypoints: List[Tuple[float, float]], 
                         forecast_hours: int = 0) -> List[Dict]:
        """Get weather for multiple waypoints"""
        weather_data = []
        for lat, lon in waypoints:
            weather = self.get_weather_point(lat, lon, forecast_hours)
            if weather:
                weather_data.append(weather)
        return weather_data


class RealTimeWeatherService:
    """
    Unified interface for real-time weather data.
    
    Tries multiple providers in order of preference:
    1. NOAA GFS (free, always available)
    2. OpenWeatherMap (if API key available)
    3. CMEMS (if available)
    4. Mock weather (fallback)
    """
    
    def __init__(self):
        """Initialize weather service with multiple providers"""
        self.providers = [
            NOAAGFSProvider(),
            OpenWeatherMapProvider(),
            # CMEMSWeatherService() - already integrated
        ]
    
    def get_weather_point(self, lat: float, lon: float, 
                         forecast_hours: int = 0) -> Dict:
        """
        Get weather from best available provider.
        
        Args:
            lat, lon: Coordinates
            forecast_hours: Hours in future (0 = current, 24+ = forecast)
        
        Returns:
            Weather dictionary with wind, waves, temperature
        """
        # Try each provider
        for provider in self.providers:
            try:
                weather = provider.get_weather_point(lat, lon, forecast_hours)
                if weather:
                    weather['latitude'] = lat
                    weather['longitude'] = lon
                    return weather
            except Exception as e:
                print(f"[Weather] Provider error: {e}")
                continue
        
        # Fallback to mock
        return self._mock_weather(lat, lon)
    
    def get_weather_route(self, waypoints: List[Tuple[float, float]], 
                         forecast_hours: int = 0) -> List[Dict]:
        """Get weather along route"""
        weather_data = []
        for lat, lon in waypoints:
            weather = self.get_weather_point(lat, lon, forecast_hours)
            weather_data.append(weather)
        return weather_data
    
    def _mock_weather(self, lat: float, lon: float) -> Dict:
        """Generate realistic mock weather"""
        import random
        
        # Base conditions vary by latitude
        lat_factor = (lat + 60) / 120
        
        base_wind = 8 + (lat_factor * 15)
        wind_speed = base_wind + random.uniform(-3, 3)
        
        wave_height = 1.0 + (lat_factor * 2) + random.uniform(-0.5, 0.5)
        
        return {
            "source": "MOCK",
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.utcnow().isoformat(),
            "wind_speed_knots": max(0, wind_speed),
            "wind_direction_deg": random.uniform(0, 360),
            "wave_height_m": max(0.5, wave_height),
            "temperature_c": 20 + (lat_factor * 8),
            "current_speed_knots": 0.3 + (lat_factor * 0.7)
        }
    
    def apply_weather_to_route_cost(self, waypoints: List[Tuple[float, float]], 
                                   base_costs: List[float]) -> List[float]:
        """
        Apply real weather data to route segment costs.
        
        Weather increases fuel consumption and time.
        
        Args:
            waypoints: Route waypoints
            base_costs: Base traversal costs
        
        Returns:
            Weather-adjusted costs
        """
        weather_data = self.get_weather_route(waypoints)
        adjusted_costs = []
        
        for i, cost in enumerate(base_costs):
            if i < len(weather_data):
                weather = weather_data[i]
                
                # Wind effect: head wind increases cost, tailwind decreases
                wind_factor = 1.0 + (weather['wind_speed_knots'] / 20.0) * 0.3
                
                # Wave effect: higher waves increase fuel consumption
                wave_factor = 1.0 + (weather['wave_height_m'] / 2.0) * 0.2
                
                # Combined weather multiplier
                weather_multiplier = wind_factor * wave_factor
                
                adjusted_costs.append(cost * weather_multiplier)
            else:
                adjusted_costs.append(cost)
        
        return adjusted_costs


# Singleton instance
_weather_service: Optional[RealTimeWeatherService] = None


def get_weather_service() -> RealTimeWeatherService:
    """Get or create weather service singleton"""
    global _weather_service
    if _weather_service is None:
        _weather_service = RealTimeWeatherService()
    return _weather_service
