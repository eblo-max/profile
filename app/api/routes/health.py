"""Health check endpoints"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.redis import redis_client
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'production')
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/detailed")
async def detailed_health_check(session: AsyncSession = Depends(get_db)):
    """Detailed health check with database and Redis status"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Check database
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        health_status["services"]["database"] = {
            "status": "healthy",
            "response_time_ms": None  # Could add timing here
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = {
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check AI service (basic check)
    try:
        from app.services.ai_service import AIService
        ai_service = AIService()
        # Just check if service can be initialized
        health_status["services"]["ai"] = {
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"AI service health check failed: {e}")
        health_status["services"]["ai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/health/ready")
async def readiness_check(session: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe"""
    
    try:
        # Check if database is ready
        await session.execute(text("SELECT 1"))
        
        # Check if Redis is ready
        await redis_client.ping()
        
        return {"status": "ready"}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/health/config")
async def config_check():
    """Check configuration status"""
    try:
        config_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "config": {
                "bot_token_configured": bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', None)),
                "database_url_configured": bool(getattr(settings, 'DATABASE_URL', None)),
                "redis_url_configured": bool(getattr(settings, 'REDIS_URL', None)),
                "webhook_url_configured": bool(getattr(settings, 'WEBHOOK_URL', None)),
                "claude_api_key_configured": bool(getattr(settings, 'CLAUDE_API_KEY', None)),
                "environment": getattr(settings, 'ENVIRONMENT', 'unknown'),
                "railway_environment": getattr(settings, 'RAILWAY_ENVIRONMENT', None)
            }
        }
        
        return config_status
        
    except Exception as e:
        logger.error(f"Config check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    
    # Basic liveness check - just return if process is running
    return {"status": "alive"} 