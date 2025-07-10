"""Main application entry point"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger

from app.core.config import settings
from app.core.database import init_database
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
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting application...")
        
        # Initialize database
        await init_database()
        logger.info("Database initialized")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized")
        
        # Initialize bot
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
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
            logger.info(f"Webhook set to {settings.WEBHOOK_URL}/webhook")
        else:
            # Delete webhook for polling mode
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted, using polling mode")
        
        # Store bot and dispatcher in app state
        app.state.bot = bot
        app.state.dp = dp
        
        logger.info("Application started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Cleanup
        try:
            if hasattr(app.state, 'bot'):
                await app.state.bot.session.close()
            await close_redis()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


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
        await init_database()
        logger.info("Database initialized")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized")
        
        # Create bot
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
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
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main()) 