"""Main entry point for PsychoDetective bot application"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import init_redis, close_redis
from app.core.logging import setup_logging, logger
from app.bot.handlers import register_all_handlers
from app.bot.middlewares import register_all_middlewares
from app.api.routes import health, analytics, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    
    # Startup
    logger.info("Starting PsychoDetective application...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized")
        
        # Initialize bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        dp = Dispatcher()
        
        # Register middlewares and handlers
        register_all_middlewares(dp)
        register_all_handlers(dp)
        
        # Set webhook if configured
        if settings.WEBHOOK_URL:
            await bot.set_webhook(
                url=f"{settings.WEBHOOK_URL}/webhook",
                drop_pending_updates=True
            )
            logger.info(f"Webhook set to {settings.WEBHOOK_URL}/webhook")
        
        # Store bot in app state
        app.state.bot = bot
        app.state.dp = dp
        
        logger.info("Application startup completed")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down application...")
    
    try:
        # Close bot session
        if hasattr(app.state, 'bot'):
            await app.state.bot.session.close()
        
        # Close Redis
        await close_redis()
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="PsychoDetective Bot API",
        description="API for PsychoDetective relationship analysis bot",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Include API routes
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(analytics.router, prefix="/api", tags=["analytics"])
    app.include_router(webhooks.router, prefix="", tags=["webhooks"])
    
    return app


def create_webhook_app() -> web.Application:
    """Create aiohttp application for webhook handling"""
    
    app = create_app()
    
    # Create aiohttp app
    aiohttp_app = web.Application()
    
    # Setup webhook handler
    @aiohttp_app.router.post("/webhook")
    async def webhook_handler(request: web.Request) -> web.Response:
        """Handle Telegram webhook"""
        try:
            bot = app.state.bot
            dp = app.state.dp
            
            # Create simple request handler
            handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
            
            # Process webhook
            return await handler.handle(request)
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.Response(status=500)
    
    # Setup FastAPI integration
    setup_application(aiohttp_app, dp, bot=app.state.bot)
    
    return aiohttp_app


async def run_polling():
    """Run bot in polling mode (for development)"""
    
    logger.info("Starting bot in polling mode...")
    
    try:
        # Initialize database and Redis
        await init_db()
        await init_redis()
        
        # Create bot and dispatcher
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        dp = Dispatcher()
        
        # Register middlewares and handlers
        register_all_middlewares(dp)
        register_all_handlers(dp)
        
        # Start polling
        logger.info("Bot polling started")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error in polling mode: {e}")
        raise
    finally:
        # Cleanup
        await close_redis()
        if 'bot' in locals():
            await bot.session.close()


def run_webhook():
    """Run application in webhook mode (for production)"""
    
    logger.info("Starting application in webhook mode...")
    
    # Create FastAPI app
    app = create_app()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_config=None,  # Use our custom logging
        access_log=False,
        workers=1 if settings.DEBUG else 2
    )


def main():
    """Main entry point"""
    
    # Setup logging
    setup_logging()
    
    logger.info("PsychoDetective Bot starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    if settings.WEBHOOK_URL:
        # Production mode with webhook
        logger.info("Running in webhook mode")
        run_webhook()
    else:
        # Development mode with polling
        logger.info("Running in polling mode")
        asyncio.run(run_polling())


if __name__ == "__main__":
    main() 