import requests
import random
from typing import Dict, List, Tuple, Optional
from app.core.config import settings


class WeatherService:
    """Weather data integration service"""
    
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get current weather for coordinates"""
        try:
            if self.api_key == "your-openweather-api-key":
                return self.generate_mock_weather(latitude, longitude)
            
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(self.OPENWEATHER_URL, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "wind_speed": data["wind"]["speed"] * 1.94384,  # m/s to knots
                    "wind_direction": data["wind"].get("deg", 0),
                    "wave_height": self.estimate_wave_height(data["wind"]["speed"]),
                    "current_speed": 0.5
                }
        except:
            pass
        
        return self.generate_mock_weather(latitude, longitude)
    
    def get_route_weather(self, start_lat: float, start_lon: float,
                         end_lat: float, end_lon: float, num_points: int = 5) -> List[Dict]:
        """Get weather along route"""
        weather_points = []
        
        for i in range(num_points):
            ratio = i / (num_points - 1) if num_points > 1 else 0
            lat = start_lat + (end_lat - start_lat) * ratio
            lon = start_lon + (end_lon - start_lon) * ratio
            
            weather = self.get_current_weather(lat, lon)
            if weather:
                weather["latitude"] = lat
                weather["longitude"] = lon
                weather_points.append(weather)
        
        return weather_points
    
    def generate_mock_weather(self, latitude: float, longitude: float) -> Dict:
        """Generate realistic mock weather for testing"""
        # Vary based on location
        lat_factor = (latitude + 60) / 120  # Normalize to 0-1
        
        base_wind = 8 + (lat_factor * 15)
        wind_speed = base_wind + random.uniform(-3, 3)
        
        wave_height = 1.0 + (lat_factor * 2) + random.uniform(-0.5, 0.5)
        
        current_speed = 0.3 + (lat_factor * 0.7) + random.uniform(-0.1, 0.1)
        
        return {
            "temperature": 20 + (lat_factor * 8),
            "wind_speed": max(0, wind_speed),
            "wind_direction": random.uniform(0, 360),
            "wave_height": max(0.5, wave_height),
            "current_speed": max(0, current_speed)
        }
    
    @staticmethod
    def estimate_wave_height(wind_speed_ms: float) -> float:
        """Estimate wave height from wind speed (simplified)"""
        # Beaufort scale approximation
        if wind_speed_ms < 2:
            return 0.1
        elif wind_speed_ms < 4:
            return 0.5
        elif wind_speed_ms < 7:
            return 1.0
        elif wind_speed_ms < 11:
            return 2.0
        elif wind_speed_ms < 16:
            return 3.0
        elif wind_speed_ms < 21:
            return 4.0
        else:
            return min(wind_speed_ms * 0.2, 8.0)
