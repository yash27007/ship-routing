from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./ship_routing.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    # Weather API
    OPENWEATHER_API_KEY: str = "your-openweather-api-key"
    
    # Indian Ocean center coordinates
    INDIAN_OCEAN_CENTER_LAT: float = 5.0
    INDIAN_OCEAN_CENTER_LON: float = 65.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
