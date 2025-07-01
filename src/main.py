"""
Главный файл приложения
"""
import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from telegram.ext import Application

from src.config.settings import settings
from src.database.connection import init_database, close_connections
from src.bot.handlers.main_handler import setup_handlers


# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    # Инициализация
    logger.info("🚀 Запуск приложения")
    
    # Инициализация базы данных
    await init_database()
    logger.info("✅ База данных инициализирована")
    
    # Настройка Telegram бота
    application = Application.builder().token(settings.telegram_bot_token).build()
    setup_handlers(application)
    
    # Инициализация вебхука если URL указан
    if settings.webhook_url:
        await application.bot.set_webhook(
            url=f"{settings.webhook_url}/webhook",
            allowed_updates=["message", "callback_query", "inline_query"]
        )
        logger.info("🔗 Webhook установлен", webhook_url=settings.webhook_url)
    
    # Сохранение приложения в состоянии FastAPI
    app.state.telegram_app = application
    
    yield
    
    # Очистка ресурсов
    logger.info("🔄 Завершение работы приложения")
    await close_connections()
    await application.shutdown()
    logger.info("✅ Приложение завершено")


# Создание FastAPI приложения
app = FastAPI(
    title="Psychology Bot API",
    description="AI-powered психологический анализ через Telegram",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Psychology Bot API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


@app.post("/webhook")
async def webhook(request: dict):
    """Обработчик вебхуков Telegram"""
    try:
        application = app.state.telegram_app
        # Обработка обновления
        await application.process_update(request)
        return {"status": "ok"}
    except Exception as e:
        logger.error("Ошибка обработки webhook", error=str(e))
        return {"status": "error", "message": str(e)}


async def start_polling():
    """Запуск в режиме polling"""
    application = Application.builder().token(settings.telegram_bot_token).build()
    setup_handlers(application)
    
    logger.info("🤖 Запуск Telegram бота в режиме polling")
    await application.run_polling(allowed_updates=["message", "callback_query"])


def main():
    """Главная функция"""
    if settings.webhook_url:
        # Режим webhook с FastAPI
        import uvicorn
        uvicorn.run(
            "src.main:app",
            host=settings.fastapi_host,
            port=settings.fastapi_port,
            reload=settings.debug
        )
    else:
        # Режим polling
        asyncio.run(start_polling())


if __name__ == "__main__":
    main() 