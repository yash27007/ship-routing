from fastapi import APIRouter, HTTPException
from app.services.weather import WeatherService
from app.models.schemas import WeatherPoint

router = APIRouter()

@router.get("/current")
async def get_current_weather(latitude: float, longitude: float):
    """Get current weather for coordinates"""
    
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    weather_service = WeatherService()
    weather = weather_service.get_current_weather(latitude, longitude)
    
    if not weather:
        raise HTTPException(status_code=500, detail="Could not fetch weather data")
    
    return {
        "latitude": latitude,
        "longitude": longitude,
        **weather
    }

@router.get("/route")
async def get_route_weather(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    num_points: int = 5
):
    """Get weather along route"""
    
    if not (-90 <= start_lat <= 90 and -180 <= start_lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid start coordinates")
    
    if not (-90 <= end_lat <= 90 and -180 <= end_lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid end coordinates")
    
    if num_points < 2 or num_points > 50:
        num_points = 5
    
    weather_service = WeatherService()
    weather_data = weather_service.get_route_weather(
        start_lat, start_lon, end_lat, end_lon, num_points
    )
    
    return {"weather_points": weather_data}
