"""
Configuration management for NEXUS system
Uses environment variables with sensible defaults
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "NEXUS AI System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Simulation Parameters
    SIMULATION_FPS: int = 12  # Ticks per second (10-15 recommended)
    GRID_SIZE: int = 20  # 20x20 grid
    NUM_VEHICLES: int = 8
    NUM_EMERGENCY_VEHICLES: int = 2
    
    # CSP Engine
    CSP_TICK_INTERVAL: int = 20  # Run CSP every 20 ticks
    TOTAL_POWER: int = 1000  # Total power units available
    
    # Bayesian Network
    ACCIDENT_BASE_RATE: float = 0.02  # 2% base accident probability per tick
    EMERGENCY_SPAWN_RATE: float = 0.01  # 1% fire/emergency spawn rate
    
    # XAI
    XAI_ENABLED: bool = True
    XAI_VERBOSE: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Database (for future extension)
    DATABASE_URL: str = "sqlite:///./nexus.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cache settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()