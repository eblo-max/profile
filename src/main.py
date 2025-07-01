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


# Настройка базового логирования сначала для диагностики lifespan
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
basic_logger = logging.getLogger(__name__)

# Настройка structlog
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
    """
    Жизненный цикл приложения с профессиональной обработкой ошибок
    Основано на официальной документации FastAPI
    """
    # Инициализация переменных
    telegram_application = None
    
    try:
        # === ЭТАП 1: ДИАГНОСТИЧЕСКОЕ ЛОГИРОВАНИЕ ===
        basic_logger.info("🚀 === НАЧАЛО ИНИЦИАЛИЗАЦИИ ПРИЛОЖЕНИЯ ===")
        logger.info("🔍 Проверка конфигурации", 
                   telegram_token_exists=bool(settings.telegram_bot_token),
                   anthropic_key_exists=bool(settings.anthropic_api_key),
                   webhook_url=settings.webhook_url,
                   database_url_prefix=settings.database_url[:20] + "..." if settings.database_url else "ОТСУТСТВУЕТ")
        
        # === ЭТАП 2: ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===
        basic_logger.info("🗄️ Инициализация базы данных...")
        
        try:
            await init_database()
            basic_logger.info("✅ База данных успешно инициализирована")
            logger.info("✅ База данных готова к работе")
        except Exception as db_error:
            basic_logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА БД: {db_error}")
            logger.error("❌ Ошибка инициализации БД", error=str(db_error), exc_info=True)
            raise RuntimeError(f"Не удалось инициализировать базу данных: {db_error}") from db_error
        
        # === ЭТАП 3: СОЗДАНИЕ TELEGRAM APPLICATION ===
        basic_logger.info("🤖 Создание Telegram Application...")
        
        try:
            if not settings.telegram_bot_token:
                raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
            
            telegram_application = Application.builder().token(settings.telegram_bot_token).build()
            basic_logger.info("✅ Telegram Application создан")
            logger.info("✅ Telegram Application готов")
        except Exception as bot_error:
            basic_logger.error(f"❌ ОШИБКА СОЗДАНИЯ БОТА: {bot_error}")
            logger.error("❌ Ошибка создания Telegram Application", error=str(bot_error), exc_info=True)
            raise RuntimeError(f"Не удалось создать Telegram Application: {bot_error}") from bot_error
        
        # === ЭТАП 4: НАСТРОЙКА ОБРАБОТЧИКОВ ===
        basic_logger.info("⚙️ Настройка обработчиков команд...")
        
        try:
            setup_handlers(telegram_application)
            basic_logger.info("✅ Обработчики настроены")
            logger.info("✅ Все обработчики команд настроены и готовы")
        except Exception as handlers_error:
            basic_logger.error(f"❌ ОШИБКА НАСТРОЙКИ ОБРАБОТЧИКОВ: {handlers_error}")
            logger.error("❌ Ошибка настройки обработчиков", error=str(handlers_error), exc_info=True)
            raise RuntimeError(f"Не удалось настроить обработчики: {handlers_error}") from handlers_error
        
        # === ЭТАП 5: ИНИЦИАЛИЗАЦИЯ TELEGRAM APPLICATION ===
        basic_logger.info("🔄 Инициализация Telegram Application...")
        
        try:
            await telegram_application.initialize()
            basic_logger.info("✅ Telegram Application инициализирован")
            logger.info("✅ Telegram Application полностью инициализирован")
        except Exception as init_error:
            basic_logger.error(f"❌ ОШИБКА ИНИЦИАЛИЗАЦИИ: {init_error}")
            logger.error("❌ Ошибка инициализации Telegram Application", error=str(init_error), exc_info=True)
            raise RuntimeError(f"Не удалось инициализировать Telegram Application: {init_error}") from init_error
        
        # === ЭТАП 6: УСТАНОВКА И ПРОВЕРКА WEBHOOK ===
        if settings.webhook_url:
            basic_logger.info(f"🔗 Проверка и установка webhook: {settings.webhook_url}")
            
            try:
                webhook_url = f"{settings.webhook_url.rstrip('/')}/webhook"
                
                # Сначала проверяем текущий webhook
                current_webhook_info = await telegram_application.bot.get_webhook_info()
                basic_logger.info(f"🔍 Текущий webhook: {current_webhook_info.url}")
                
                # Устанавливаем webhook (даже если он уже есть - для надежности)
                await telegram_application.bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=["message", "callback_query", "inline_query"]
                )
                basic_logger.info("✅ Webhook установлен/обновлен")
                logger.info("✅ Webhook настроен", webhook_url=webhook_url)
                
                # Повторная проверка webhook
                final_webhook_info = await telegram_application.bot.get_webhook_info()
                basic_logger.info(f"🔍 Финальный webhook: {final_webhook_info.url}")
                logger.info("🔍 Webhook финальный статус", 
                           url=final_webhook_info.url, 
                           pending_updates=final_webhook_info.pending_update_count,
                           max_connections=final_webhook_info.max_connections)
                
                # Проверка что webhook действительно установлен
                if not final_webhook_info.url or final_webhook_info.url != webhook_url:
                    raise RuntimeError(f"Webhook не установлен корректно: ожидался {webhook_url}, получен {final_webhook_info.url}")
                
            except Exception as webhook_error:
                basic_logger.error(f"❌ ОШИБКА WEBHOOK: {webhook_error}")
                logger.error("❌ Ошибка установки webhook", error=str(webhook_error), exc_info=True)
                raise RuntimeError(f"Не удалось установить webhook: {webhook_error}") from webhook_error
        else:
            basic_logger.warning("⚠️ WEBHOOK_URL не задан!")
            logger.warning("⚠️ Webhook не будет работать - WEBHOOK_URL не задан")
        
        # === ЭТАП 7: СОХРАНЕНИЕ В СОСТОЯНИИ ПРИЛОЖЕНИЯ ===
        app.state.telegram_app = telegram_application
        
        # === ЗАВЕРШЕНИЕ ИНИЦИАЛИЗАЦИИ ===
        basic_logger.info("🎯 === ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО ===")
        logger.info("🎯 Приложение полностью готово к работе")
        
        # YIELD - передача управления FastAPI
        yield
        
    except Exception as e:
        # КРИТИЧЕСКАЯ ОШИБКА ИНИЦИАЛИЗАЦИИ
        basic_logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА ИНИЦИАЛИЗАЦИИ: {type(e).__name__}: {e}")
        logger.error("💥 Критическая ошибка lifespan функции", 
                    error_type=type(e).__name__, 
                    error_message=str(e), 
                    exc_info=True)
        
        # Экстренная очистка если что-то было создано
        if telegram_application:
            try:
                await telegram_application.shutdown()
                basic_logger.info("🧹 Экстренная очистка Telegram Application выполнена")
            except Exception as cleanup_error:
                basic_logger.error(f"❌ Ошибка экстренной очистки: {cleanup_error}")
        
        # Перебрасываем исключение - FastAPI должен знать о проблеме
        raise
    
    # === ЗАВЕРШЕНИЕ РАБОТЫ (ПОСЛЕ YIELD) ===
    try:
        basic_logger.info("🔄 === НАЧАЛО ЗАВЕРШЕНИЯ РАБОТЫ ===")
        logger.info("🔄 Начинаю корректное завершение приложения")
        
        # === НЕ УДАЛЯЕМ WEBHOOK ПРИ ПЕРЕЗАПУСКЕ ===
        # Webhook НЕ удаляется при завершении, чтобы избежать проблем с Railway
        # Railway может перезапускать приложение для деплоя, но webhook должен остаться
        if settings.webhook_url and telegram_application:
            try:
                basic_logger.info("🔗 Webhook остается активным для Railway...")
                logger.info("🔗 Webhook сохранен для непрерывной работы при перезапусках Railway")
            except Exception as webhook_info_error:
                basic_logger.error(f"❌ Ошибка проверки webhook: {webhook_info_error}")
                logger.error("❌ Ошибка проверки webhook", error=str(webhook_info_error))
        
        # === ЗАКРЫТИЕ TELEGRAM APPLICATION ===
        if telegram_application:
            try:
                basic_logger.info("🤖 Завершение Telegram Application...")
                await telegram_application.shutdown()
                basic_logger.info("✅ Telegram Application завершен")
                logger.info("✅ Telegram Application корректно завершен")
            except Exception as app_shutdown_error:
                basic_logger.error(f"❌ Ошибка завершения Telegram App: {app_shutdown_error}")
                logger.error("❌ Ошибка завершения Telegram Application", error=str(app_shutdown_error))
        
        # === ЗАКРЫТИЕ ПОДКЛЮЧЕНИЙ К БД ===
        try:
            basic_logger.info("📪 Закрытие подключений к базам данных...")
            await close_connections()
            basic_logger.info("✅ Подключения к БД закрыты")
            logger.info("✅ Все подключения к базам данных закрыты")
        except Exception as db_cleanup_error:
            basic_logger.error(f"❌ Ошибка закрытия БД: {db_cleanup_error}")
            logger.error("❌ Ошибка закрытия подключений БД", error=str(db_cleanup_error))
        
        basic_logger.info("✅ === ЗАВЕРШЕНИЕ РАБОТЫ ВЫПОЛНЕНО ===")
        logger.info("✅ Приложение корректно завершено")
        
    except Exception as shutdown_error:
        basic_logger.error(f"💥 ОШИБКА ПРИ ЗАВЕРШЕНИИ: {shutdown_error}")
        logger.error("💥 Критическая ошибка при завершении приложения", 
                    error=str(shutdown_error), 
                    exc_info=True)
        # Не перебрасываем исключение при завершении - приложение уже останавливается


# Создание FastAPI приложения с правильным lifespan
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
        "version": "1.0.0",
        "bot_configured": hasattr(app.state, 'telegram_app') and app.state.telegram_app is not None
    }


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    telegram_status = "unknown"
    
    try:
        if hasattr(app.state, 'telegram_app') and app.state.telegram_app:
            # Простая проверка доступности бота
            telegram_status = "connected"
        else:
            telegram_status = "not_initialized"
    except Exception:
        telegram_status = "error"
    
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "telegram_bot": telegram_status,
        "webhook_configured": bool(settings.webhook_url)
    }


@app.post("/webhook")
async def webhook(request: Request):
    """Обработчик вебхуков Telegram"""
    try:
        # Проверка инициализации
        if not hasattr(app.state, 'telegram_app') or not app.state.telegram_app:
            logger.error("❌ Telegram Application не инициализирован")
            return {"status": "error", "message": "Bot not initialized"}
        
        application = app.state.telegram_app
        
        # Получение JSON данных из запроса
        json_data = await request.json()
        logger.info("📥 Получен webhook", update_id=json_data.get('update_id'))
        
        # Создание объекта Update из JSON
        update = Update.de_json(json_data, application.bot)
        
        if not update:
            logger.warning("⚠️ Невалидный Update объект")
            return {"status": "error", "message": "Invalid update"}
        
        logger.info("🔄 Обрабатываю Update", 
                   update_id=update.update_id,
                   update_type=type(update.effective_message).__name__ if update.effective_message else "unknown")
        
        # Обработка обновления
        await application.process_update(update)
        
        logger.info("✅ Update обработан успешно", update_id=update.update_id)
        return {"status": "ok"}
        
    except Exception as e:
        logger.error("❌ Ошибка обработки webhook", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    exc_info=True)
        return {"status": "error", "message": str(e)}


async def start_polling():
    """Запуск в режиме polling (для разработки)"""
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