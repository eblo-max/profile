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
    
    # 🔬 НАУЧНЫЙ ПОИСК API (2025 - РЕВОЛЮЦИОННАЯ МУЛЬТИИСТОЧНИКОВАЯ СИСТЕМА)
    
    # === ОСНОВНЫЕ ПОИСКОВЫЕ СИСТЕМЫ ===
    serpapi_api_key: Optional[str] = Field(default=None, env="SERPAPI_API_KEY")  # Google Scholar
    brave_search_api_key: Optional[str] = Field(default=None, env="BRAVE_SEARCH_API_KEY")  # Brave Search
    semantic_scholar_api_key: Optional[str] = Field(default=None, env="SEMANTIC_SCHOLAR_API_KEY")  # Semantic Scholar
    crossref_api_key: Optional[str] = Field(default=None, env="CROSSREF_API_KEY")  # CrossRef API
    dimensions_api_key: Optional[str] = Field(default=None, env="DIMENSIONS_API_KEY")  # Dimensions API
    
    # === МЕДИЦИНСКИЕ И ПСИХОЛОГИЧЕСКИЕ БАЗЫ ===
    pubmed_api_key: Optional[str] = Field(default=None, env="PUBMED_API_KEY")  # PubMed API
    psycinfo_api_key: Optional[str] = Field(default=None, env="PSYCINFO_API_KEY")  # PsycINFO
    apa_psycnet_api_key: Optional[str] = Field(default=None, env="APA_PSYCNET_API_KEY")  # APA PsycNet
    sage_research_api_key: Optional[str] = Field(default=None, env="SAGE_RESEARCH_API_KEY")  # SAGE Research
    taylor_francis_api_key: Optional[str] = Field(default=None, env="TAYLOR_FRANCIS_API_KEY")  # Taylor & Francis
    
    # === УНИВЕРСИТЕТСКИЕ И ИНСТИТУЦИОНАЛЬНЫЕ API ===
    mit_api_key: Optional[str] = Field(default=None, env="MIT_API_KEY")  # MIT DSpace
    stanford_api_key: Optional[str] = Field(default=None, env="STANFORD_API_KEY")  # Stanford Digital Repository
    harvard_api_key: Optional[str] = Field(default=None, env="HARVARD_API_KEY")  # Harvard DASH
    oxford_api_key: Optional[str] = Field(default=None, env="OXFORD_API_KEY")  # Oxford Academic
    cambridge_api_key: Optional[str] = Field(default=None, env="CAMBRIDGE_API_KEY")  # Cambridge Core
    springer_api_key: Optional[str] = Field(default=None, env="SPRINGER_API_KEY")  # Springer Nature
    elsevier_api_key: Optional[str] = Field(default=None, env="ELSEVIER_API_KEY")  # Elsevier ScienceDirect
    wiley_api_key: Optional[str] = Field(default=None, env="WILEY_API_KEY")  # Wiley Online Library
    
    # === РОССИЙСКИЕ И СНГ ИСТОЧНИКИ ===
    elibrary_api_key: Optional[str] = Field(default=None, env="ELIBRARY_API_KEY")  # eLibrary.ru
    cyberleninka_api_key: Optional[str] = Field(default=None, env="CYBERLENINKA_API_KEY")  # КиберЛенинка
    rsci_api_key: Optional[str] = Field(default=None, env="RSCI_API_KEY")  # РИНЦ
    msu_api_key: Optional[str] = Field(default=None, env="MSU_API_KEY")  # МГУ Истина
    spbpu_api_key: Optional[str] = Field(default=None, env="SPBPU_API_KEY")  # СПбПУ
    
    # === ЕВРОПЕЙСКИЕ ИСТОЧНИКИ ===
    hal_api_key: Optional[str] = Field(default=None, env="HAL_API_KEY")  # HAL (Франция)
    dblp_api_key: Optional[str] = Field(default=None, env="DBLP_API_KEY")  # DBLP Computer Science
    arxiv_api_key: Optional[str] = Field(default=None, env="ARXIV_API_KEY")  # arXiv
    researchgate_api_key: Optional[str] = Field(default=None, env="RESEARCHGATE_API_KEY")  # ResearchGate
    academia_api_key: Optional[str] = Field(default=None, env="ACADEMIA_API_KEY")  # Academia.edu
    
    # === АЗИАТСКО-ТИХООКЕАНСКИЕ ИСТОЧНИКИ ===
    j_stage_api_key: Optional[str] = Field(default=None, env="J_STAGE_API_KEY")  # J-STAGE (Япония)
    cnki_api_key: Optional[str] = Field(default=None, env="CNKI_API_KEY")  # CNKI (Китай)
    scielo_api_key: Optional[str] = Field(default=None, env="SCIELO_API_KEY")  # SciELO (Латинская Америка)
    
    # === СПЕЦИАЛИЗИРОВАННЫЕ ПСИХОЛОГИЧЕСКИЕ ИСТОЧНИКИ ===
    apa_divisions_api_key: Optional[str] = Field(default=None, env="APA_DIVISIONS_API_KEY")  # APA Divisions
    bps_api_key: Optional[str] = Field(default=None, env="BPS_API_KEY")  # British Psychological Society
    psychology_today_api_key: Optional[str] = Field(default=None, env="PSYCHOLOGY_TODAY_API_KEY")  # Psychology Today
    personality_research_api_key: Optional[str] = Field(default=None, env="PERSONALITY_RESEARCH_API_KEY")  # Personality Research
    
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
    
    # 💰 ЭКОНОМИЧЕСКИЕ НАСТРОЙКИ (2025)
    
    # Тарифные планы и лимиты
    free_analyses_per_day: int = Field(default=3, env="FREE_ANALYSES_PER_DAY")
    basic_price_usd: float = Field(default=1.99, env="BASIC_PRICE_USD")
    advanced_price_usd: float = Field(default=4.99, env="ADVANCED_PRICE_USD")
    research_price_usd: float = Field(default=9.99, env="RESEARCH_PRICE_USD")
    premium_price_usd: float = Field(default=19.99, env="PREMIUM_PRICE_USD")
    
    # AI сервисы стоимость (примерные в USD за 1000 токенов)
    claude_cost_per_1k_tokens: float = Field(default=0.015, env="CLAUDE_COST_PER_1K")
    openai_cost_per_1k_tokens: float = Field(default=0.01, env="OPENAI_COST_PER_1K")
    gemini_cost_per_1k_tokens: float = Field(default=0.0075, env="GEMINI_COST_PER_1K")
    cohere_cost_per_1k_tokens: float = Field(default=0.0075, env="COHERE_COST_PER_1K")
    
    # Кэширование и оптимизация
    analysis_cache_ttl_hours: int = Field(default=24, env="ANALYSIS_CACHE_TTL_HOURS")
    scientific_cache_ttl_hours: int = Field(default=168, env="SCIENTIFIC_CACHE_TTL_HOURS")  # 7 дней
    max_concurrent_ai_requests: int = Field(default=3, env="MAX_CONCURRENT_AI_REQUESTS")
    
    # Rate limiting
    requests_per_minute_per_user: int = Field(default=5, env="REQUESTS_PER_MINUTE_PER_USER")
    daily_cost_limit_usd: float = Field(default=100.0, env="DAILY_COST_LIMIT_USD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Игнорируем дополнительные поля в .env


# Глобальный экземпляр настроек
settings = Settings() 