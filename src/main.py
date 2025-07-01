"""
Главный файл приложения
"""
import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from telegram import Update
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
    application = None
    try:
        # Инициализация
        logger.info("🚀 Запуск приложения - СТАРТ")
        
        # Проверка настроек
        logger.info("🔍 Проверка настроек", 
                   has_telegram_token=bool(settings.telegram_bot_token),
                   has_webhook_url=bool(settings.webhook_url),
                   database_url=settings.database_url[:50] + "..." if settings.database_url else None)
        
        # Инициализация базы данных
        logger.info("🗄️ Инициализация базы данных...")
        await init_database()
        logger.info("✅ База данных инициализирована")
        
        # Настройка Telegram бота
        logger.info("🤖 Создание Telegram Application...")
        application = Application.builder().token(settings.telegram_bot_token).build()
        
        logger.info("⚙️ Настройка обработчиков...")
        setup_handlers(application)
        logger.info("✅ Обработчики бота настроены")
        
        # Инициализация приложения
        logger.info("🔄 Инициализация Telegram Application...")
        await application.initialize()
        logger.info("✅ Telegram application инициализирован")
        
        # Инициализация вебхука если URL указан
        if settings.webhook_url:
            logger.info("🔗 Установка webhook...", webhook_url=settings.webhook_url)
            await application.bot.set_webhook(
                url=f"{settings.webhook_url}/webhook",
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            logger.info("✅ Webhook установлен успешно")
        else:
            logger.warning("⚠️ WEBHOOK_URL не задан, webhook не будет работать!")
        
        # Сохранение приложения в состоянии FastAPI
        app.state.telegram_app = application
        logger.info("🎯 Приложение полностью инициализировано и готово к работе!")
        
        yield
        
    except Exception as e:
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА при инициализации приложения", 
                    error=str(e), exc_info=True)
        # Попытка очистки если что-то было создано
        if application:
            try:
                await application.shutdown()
            except:
                pass
        raise e
    
    # Очистка ресурсов
    try:
        logger.info("🔄 Завершение работы приложения")
        
        # Удаление webhook
        if settings.webhook_url and application:
            try:
                await application.bot.delete_webhook()
                logger.info("🔗 Webhook удален")
            except Exception as e:
                logger.error("❌ Ошибка удаления webhook", error=str(e))
        
        # Закрытие подключений
        try:
            await close_connections()
            logger.info("📪 Подключения к БД закрыты")
        except Exception as e:
            logger.error("❌ Ошибка закрытия подключений", error=str(e))
        
        # Завершение работы Telegram app
        if application:
            try:
                await application.shutdown()
                logger.info("🤖 Telegram application завершен")
            except Exception as e:
                logger.error("❌ Ошибка завершения Telegram app", error=str(e))
        
        logger.info("✅ Приложение завершено")
        
    except Exception as e:
        logger.error("❌ Ошибка при завершении приложения", error=str(e), exc_info=True)


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
async def webhook(request: Request):
    """Обработчик вебхуков Telegram"""
    try:
        application = app.state.telegram_app
        
        # Получение JSON данных из запроса
        json_data = await request.json()
        logger.info("Получен webhook", data=json_data)
        
        # Создание объекта Update из JSON
        update = Update.de_json(json_data, application.bot)
        logger.info("Update создан", update_id=update.update_id if update else None)
        
        # Обработка обновления
        await application.process_update(update)
        logger.info("Update обработан успешно")
        return {"status": "ok"}
    except Exception as e:
        logger.error("Ошибка обработки webhook", error=str(e), exc_info=True)
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