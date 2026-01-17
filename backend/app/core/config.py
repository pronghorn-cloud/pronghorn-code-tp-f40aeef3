"""Application Configuration Settings

Manages all configuration using Pydantic Settings with environment variable support.
Supports HIPAA-compliant configuration management.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    PROJECT_NAME: str = "Claims Processing Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "RS256"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database - PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/claims_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_TTL: int = 900  # 15 minutes
    REDIS_AHCIP_CACHE_TTL: int = 86400  # 24 hours
    REDIS_RULE_CACHE_TTL: int = 3600  # 1 hour
    
    # AWS S3 / Document Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "claims-documents"
    S3_PRESIGNED_URL_EXPIRY: int = 3600  # 1 hour
    
    # Document Upload Limits
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf", "image/jpeg", "image/png"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 20
    
    # HIPAA Compliance
    AUDIT_LOG_RETENTION_YEARS: int = 6
    SESSION_IDLE_TIMEOUT_MINUTES: int = 15
    PHI_ENCRYPTION_KEY: Optional[str] = None
    
    # External Services
    AHCIP_SERVICE_URL: Optional[str] = None
    NOTIFICATION_SERVICE_URL: Optional[str] = None
    
    # Identity Provider (OAuth/OIDC)
    OAUTH_PROVIDER_URL: Optional[str] = None
    OAUTH_CLIENT_ID: Optional[str] = None
    OAUTH_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
