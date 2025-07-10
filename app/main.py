"""Main application entry point"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.logging import setup_logging

# Import bot components
from app.bot.handlers import (
    start, profile, profiler, analysis, 
    compatibility, daily, payments, admin
)
from app.bot.middlewares.auth import AuthMiddleware
from app.bot.middlewares.logging import LoggingMiddleware
from app.bot.middlewares.rate_limit import RateLimitMiddleware
from app.bot.middlewares.subscription import SubscriptionMiddleware
from app.bot.middlewares.dependencies import DependenciesMiddleware

# Import API routes
from app.api.routes import health, analytics, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Setup logging first
    setup_logging()
    logger.info("Starting application...")
    
    # Initialize services with error handling
    db_initialized = False
    redis_initialized = False
    bot_initialized = False
    
    try:
        # Initialize database
        try:
            await init_db()
            db_initialized = True
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            # Don't fail the whole app, just log the error
        
        # Initialize Redis
        try:
            await init_redis()
            redis_initialized = True
            logger.info("✅ Redis initialized")
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            # Don't fail the whole app, just log the error
        
        # Initialize bot (only if we have a bot token)
        try:
            if settings.BOT_TOKEN:
                bot = Bot(
                    token=settings.BOT_TOKEN,
                    parse_mode=ParseMode.HTML
                )
                
                # Create dispatcher
                dp = Dispatcher()
                
                # Setup middlewares
                dp.message.middleware(DependenciesMiddleware())
                dp.callback_query.middleware(DependenciesMiddleware())
                dp.message.middleware(AuthMiddleware())
                dp.callback_query.middleware(AuthMiddleware())
                dp.message.middleware(LoggingMiddleware())
                dp.callback_query.middleware(LoggingMiddleware())
                dp.message.middleware(RateLimitMiddleware())
                dp.callback_query.middleware(RateLimitMiddleware())
                dp.message.middleware(SubscriptionMiddleware())
                dp.callback_query.middleware(SubscriptionMiddleware())
                
                # Register handlers
                dp.include_router(start.router)
                dp.include_router(profile.router)
                dp.include_router(profiler.router)
                dp.include_router(analysis.router)
                dp.include_router(compatibility.router)
                dp.include_router(daily.router)
                dp.include_router(payments.router)
                dp.include_router(admin.router)
                
                # Set webhook if configured
                if settings.WEBHOOK_URL:
                    await bot.set_webhook(
                        url=f"{settings.WEBHOOK_URL}/webhook",
                        secret_token=settings.WEBHOOK_SECRET
                    )
                    logger.info(f"✅ Webhook set to {settings.WEBHOOK_URL}/webhook")
                else:
                    # Delete webhook for polling mode
                    await bot.delete_webhook(drop_pending_updates=True)
                    logger.info("✅ Webhook deleted, using polling mode")
                
                # Store bot and dispatcher in app state
                app.state.bot = bot
                app.state.dp = dp
                bot_initialized = True
                logger.info("✅ Bot initialized")
            else:
                logger.warning("⚠️ No BOT_TOKEN provided, bot not initialized")
                
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            # Don't fail the whole app, just log the error
        
        logger.info("🚀 Application started successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        # Don't raise, just log the error
    finally:
        # Cleanup
        logger.info("🔄 Starting application shutdown...")
        try:
            if bot_initialized and hasattr(app.state, 'bot'):
                await app.state.bot.session.close()
                logger.info("✅ Bot session closed")
        except Exception as e:
            logger.error(f"❌ Error closing bot session: {e}")
        
        try:
            if db_initialized:
                await close_db()
                logger.info("✅ Database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing database: {e}")
        
        try:
            if redis_initialized:
                await close_redis()
                logger.info("✅ Redis connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis: {e}")
        
        logger.info("🏁 Application shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="PsychoDetective Bot API",
        description="Telegram bot for psychological partner analysis",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Include API routes
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(analytics.router, prefix="/api", tags=["analytics"])
    app.include_router(webhooks.router, prefix="", tags=["webhooks"])
    
    return app


def create_webhook_app() -> web.Application:
    """Create aiohttp app for webhook handling"""
    
    # Create FastAPI app
    fastapi_app = create_app()
    
    # Create aiohttp app
    aiohttp_app = web.Application()
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=fastapi_app.state.dp,
        bot=fastapi_app.state.bot,
        secret_token=settings.WEBHOOK_SECRET
    )
    webhook_requests_handler.register(aiohttp_app, path="/webhook")
    
    # Mount FastAPI app
    setup_application(aiohttp_app, fastapi_app)
    
    return aiohttp_app


async def main():
    """Main function for polling mode"""
    
    # Setup logging
    setup_logging()
    logger.info("Starting bot in polling mode...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized")
        
        # Create bot
        bot = Bot(
            token=settings.BOT_TOKEN,
            parse_mode=ParseMode.HTML
        )
        
        # Create dispatcher
        dp = Dispatcher()
        
        # Setup middlewares
        dp.message.middleware(DependenciesMiddleware())
        dp.callback_query.middleware(DependenciesMiddleware())
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
        dp.message.middleware(RateLimitMiddleware())
        dp.callback_query.middleware(RateLimitMiddleware())
        dp.message.middleware(SubscriptionMiddleware())
        dp.callback_query.middleware(SubscriptionMiddleware())
        
        # Register handlers
        dp.include_router(start.router)
        dp.include_router(profile.router)
        dp.include_router(profiler.router)
        dp.include_router(analysis.router)
        dp.include_router(compatibility.router)
        dp.include_router(daily.router)
        dp.include_router(payments.router)
        dp.include_router(admin.router)
        
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        logger.info("Bot started in polling mode")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await close_db()
        await close_redis()


if __name__ == "__main__":
    import os
    import uvicorn
    
    # Проверяем, запускаемся ли мы на Railway (production)
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
        # Production mode - запускаем FastAPI с uvicorn
        port = int(os.getenv("PORT", 8000))
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Development mode - запускаем polling
        asyncio.run(main()) 