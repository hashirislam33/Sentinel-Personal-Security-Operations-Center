"""
Configuration settings for Sentinel backend.

This module handles all configuration from environment variables and provides
default values for development and production settings.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Sentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # API
    API_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql://sentinel:sentinel@localhost:5432/sentinel"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    AGENT_RATE_LIMIT_PER_MINUTE: int = 1000

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Event Processing
    EVENT_BATCH_SIZE: int = 100
    EVENT_QUEUE_SIZE: int = 10000
    DETECTION_INTERVAL_SECONDS: int = 5

    # Risk Scoring
    RISK_SCORE_MIN: int = 0
    RISK_SCORE_MAX: int = 100
    SEVERITY_THRESHOLDS: dict = {
        "informational": 0,
        "low": 20,
        "medium": 40,
        "high": 60,
        "critical": 80
    }

    # Asset Management
    ASSET_HEARTBEAT_TIMEOUT_MINUTES: int = 15

    # Audit
    AUDIT_LOG_RETENTION_DAYS: int = 90

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        if not v.startswith('postgresql://'):
            raise ValueError("Database URL must start with postgresql://")
        return v

    @validator('SECRET_KEY')
    def warn_weak_secret(cls, v, values):
        if values.get('ENVIRONMENT') == 'production' and v == 'your-secret-key-change-in-production':
            import warnings
            warnings.warn("SECRET_KEY should be changed in production!")
        return v

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
