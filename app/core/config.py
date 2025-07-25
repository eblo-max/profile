"""Application configuration using Pydantic settings"""

import os
from typing import Optional, List, Dict
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "PsychoDetective Bot"
    DEBUG: bool = Field(False, env="DEBUG")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ENVIRONMENT: str = Field("production", env="ENVIRONMENT")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    WEBHOOK_MODE: bool = Field(False, env="WEBHOOK_MODE")
    WEBHOOK_URL: Optional[str] = Field(None, env="WEBHOOK_URL")
    WEBHOOK_SECRET: Optional[str] = Field(None, env="WEBHOOK_SECRET")
    
    @property
    def BOT_TOKEN(self) -> str:
        """Alias for TELEGRAM_BOT_TOKEN for backward compatibility"""
        return self.TELEGRAM_BOT_TOKEN
    
    # AI Configuration - только AIML API
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # AIML API Configuration for Claude 3.7
    AIML_API_KEY: Optional[str] = Field(None, env="AIML_API_KEY")
    AIML_API_URL: str = Field("https://api.aimlapi.com/chat/completions", env="AIML_API_URL")
    USE_AIML_API: bool = Field(False, env="USE_AIML_API")
    AIML_CLAUDE_MODEL: str = Field("claude-3-7-sonnet", env="AIML_CLAUDE_MODEL")
    
    # Token Limits (adaptive based on model)
    MAX_TOKENS_DEFAULT: int = Field(17000, env="MAX_TOKENS_DEFAULT")
    MAX_TOKENS_MEGA: int = Field(20000, env="MAX_TOKENS_MEGA") 
    MAX_TOKENS_ANALYSIS: int = Field(17000, env="MAX_TOKENS_ANALYSIS")
    MAX_TOKENS_PROFILING: int = Field(18000, env="MAX_TOKENS_PROFILING")
    
    # Thinking tokens for Claude 3.7
    MAX_THINKING_TOKENS: int = Field(15000, env="MAX_THINKING_TOKENS")
    
    # Model-specific token limits
    @property
    def model_max_tokens(self) -> int:
        """Get max tokens for current model"""
        if self.USE_AIML_API:
            return 200000  # AIML API поддерживает до 200k токенов
        
        # Fallback для других моделей
        return 8192
        
    @property
    def effective_claude_model(self) -> str:
        """Get the effective Claude model name"""
        if self.USE_AIML_API:
            return self.AIML_CLAUDE_MODEL
        return "claude-3-5-sonnet-20241022"  # Default fallback
    
    # PDF Generation
    CLOUDLAYER_API_KEY: Optional[str] = Field(None, env="CLOUDLAYER_API_KEY")
    
    # AI Performance
    MAX_CONCURRENT_AI_REQUESTS: int = Field(10, env="MAX_CONCURRENT_AI_REQUESTS")
    AI_REQUEST_TIMEOUT: int = Field(30, env="AI_REQUEST_TIMEOUT")
    AI_RETRY_ATTEMPTS: int = Field(3, env="AI_RETRY_ATTEMPTS")
    AI_RETRY_DELAY: float = Field(1.0, env="AI_RETRY_DELAY")
    AI_RATE_LIMIT_SECONDS: float = Field(3.0, env="AI_RATE_LIMIT_SECONDS")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_POOL_SIZE: int = Field(20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(30, env="DB_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(10, env="REDIS_POOL_SIZE")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(3600, env="RATE_LIMIT_WINDOW")
    
    # Subscription Limits
    FREE_ANALYSES_LIMIT: int = Field(3, env="FREE_ANALYSES_LIMIT")
    PREMIUM_ANALYSES_LIMIT: int = Field(999, env="PREMIUM_ANALYSES_LIMIT")
    
    # Server
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # Payments
    YOOKASSA_SHOP_ID: Optional[str] = Field(None, env="YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: Optional[str] = Field(None, env="YOOKASSA_SECRET_KEY")
    
    # Railway specific
    RAILWAY_ENVIRONMENT: Optional[str] = Field(None, env="RAILWAY_ENVIRONMENT")
    RAILWAY_SERVICE_ID: Optional[str] = Field(None, env="RAILWAY_SERVICE_ID")
    
    # Content Configuration
    DAILY_CONTENT_CACHE_TTL: int = Field(3600, env="DAILY_CONTENT_CACHE_TTL")
    USER_SESSION_TTL: int = Field(86400, env="USER_SESSION_TTL")  # 24 hours
    
    # Security
    ALLOWED_HOSTS: List[str] = Field(["*"], env="ALLOWED_HOSTS")
    ADMIN_USER_IDS: List[int] = Field([], env="ADMIN_USER_IDS")
    
    # Простая эффективная система анализа
    ENHANCED_ANALYSIS: bool = Field(True, env="ENHANCED_ANALYSIS")
    ANALYSIS_CACHE_TTL: int = Field(3600, env="ANALYSIS_CACHE_TTL")  # 1 час
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        """Ensure database URL uses asyncpg for async support"""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v
    
    @field_validator("ADMIN_USER_IDS", mode="before")
    @classmethod
    def parse_admin_user_ids(cls, v):
        """Parse comma-separated admin user IDs"""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        elif isinstance(v, int):
            return [v]
        elif isinstance(v, list):
            return v
        return []
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.RAILWAY_ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.DEBUG or not self.is_production
    

    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings() 