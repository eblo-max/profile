"""
Конфигурация приложения
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # IBM Watson
    ibm_watson_api_key: str = Field(..., env="IBM_WATSON_API_KEY")
    ibm_watson_url: str = Field(..., env="IBM_WATSON_URL")
    
    # Microsoft Azure
    azure_cognitive_key: str = Field(..., env="AZURE_COGNITIVE_KEY")
    azure_cognitive_endpoint: str = Field(..., env="AZURE_COGNITIVE_ENDPOINT")
    
    # Google Cloud
    google_cloud_project_id: str = Field(..., env="GOOGLE_CLOUD_PROJECT_ID")
    google_application_credentials: str = Field(..., env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # AWS
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Специализированные API
    crystal_api_key: str = Field(..., env="CRYSTAL_API_KEY")
    receptiviti_api_key: str = Field(..., env="RECEPTIVITI_API_KEY")
    lexalytics_api_key: str = Field(..., env="LEXALYTICS_API_KEY")
    monkeylearn_api_key: str = Field(..., env="MONKEYLEARN_API_KEY")
    
    # Настройки приложения
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_requests_per_minute: int = Field(default=60, env="MAX_REQUESTS_PER_MINUTE")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # FastAPI
    fastapi_host: str = Field(default="0.0.0.0", env="FASTAPI_HOST")
    fastapi_port: int = Field(default=8000, env="FASTAPI_PORT")
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Глобальный экземпляр настроек
settings = Settings() 