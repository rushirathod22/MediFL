"""
Application configuration - loads settings from YAML and environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    """Central config class. Values come from .env or environment variables."""
    # App
    APP_NAME: str = "MediFL"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://medifl:medifl_pass@localhost:5432/medifl_db"
    DB_POOL_SIZE: int = 10
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Federated Learning
    MIN_NODES: int = 2
    MAX_ROUNDS: int = 100
    DEFAULT_STRATEGY: str = "fedavg"
    DP_ENABLED: bool = True
    CLIP_NORM: float = 1.0
    NOISE_MULTIPLIER: float = 0.1
    TARGET_EPSILON: float = 8.0
    TARGET_DELTA: float = 1e-5
    class Config:
        env_file = ".env"
        case_sensitive = True
# Singleton instance - import this everywhere
settings = Settings()
