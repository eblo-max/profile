"""Logging configuration using Loguru"""

import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """Setup application logging"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler for development
    if settings.DEBUG:
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True,
        )
    else:
        # Production logging (Railway/Docker friendly)
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            serialize=False,
        )
    
    # File handler for persistent logging
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        catch=True,
    )
    
    # Sentry integration for production
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.loguru import LoguruIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment="production" if settings.is_production else "development",
            integrations=[
                LoguruIntegration(level=20),  # logging.INFO level
            ],
            traces_sample_rate=0.1 if settings.is_production else 1.0,
        )
        
        logger.info("✅ Sentry integration enabled")
    
    logger.info(f"✅ Logging setup complete (level: {settings.LOG_LEVEL})") 