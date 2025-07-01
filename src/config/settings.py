"""
Конфигурация приложения
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные - обязательные
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # AI API ключи - необязательные для первого запуска
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")  # Замена Watson
    
    # Deprecated Watson (заменен на OpenAI)
    # ibm_watson_api_key: Optional[str] = Field(default=None, env="IBM_WATSON_API_KEY")
    # ibm_watson_url: Optional[str] = Field(default=None, env="IBM_WATSON_URL")
    
    azure_cognitive_key: Optional[str] = Field(default=None, env="AZURE_COGNITIVE_KEY")
    azure_cognitive_endpoint: Optional[str] = Field(default=None, env="AZURE_COGNITIVE_ENDPOINT")
    
    google_cloud_project_id: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT_ID")
    google_application_credentials: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Специализированные API - необязательные
    crystal_api_key: Optional[str] = Field(default=None, env="CRYSTAL_API_KEY")
    receptiviti_api_key: Optional[str] = Field(default=None, env="RECEPTIVITI_API_KEY")
    lexalytics_api_key: Optional[str] = Field(default=None, env="LEXALYTICS_API_KEY")
    monkeylearn_api_key: Optional[str] = Field(default=None, env="MONKEYLEARN_API_KEY")
    
    # 🚀 СОВРЕМЕННЫЕ AI API (2025) - ЗАМЕНА УСТАРЕВШИХ
    
    # Google Gemini 2.0 Flash (замена Google Cloud NL + Azure Cognitive)
    google_gemini_api_key: Optional[str] = Field(default=None, env="GOOGLE_GEMINI_API_KEY")
    
    # Cohere Command-R+ (замена Lexalytics + Receptiviti)
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    
    # HuggingFace Transformers (замена AWS Rekognition для текста)
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Настройки приложения
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_requests_per_minute: int = Field(default=60, env="MAX_REQUESTS_PER_MINUTE")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # FastAPI - Railway автоматически устанавливает PORT
    fastapi_host: str = Field(default="0.0.0.0", env="HOST")
    fastapi_port: int = Field(default=8000, env="PORT")
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    
    # Railway специфичные
    railway_environment: Optional[str] = Field(default=None, env="RAILWAY_ENVIRONMENT")
    railway_project_id: Optional[str] = Field(default=None, env="RAILWAY_PROJECT_ID")
    railway_service_id: Optional[str] = Field(default=None, env="RAILWAY_SERVICE_ID")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Глобальный экземпляр настроек
settings = Settings() 