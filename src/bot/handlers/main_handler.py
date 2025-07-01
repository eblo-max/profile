"""
Обработчики команд бота (обновлено для python-telegram-bot v21+)
"""
import structlog
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ConversationHandler, filters, ContextTypes
)

from src.bot.states.analysis_states import AnalysisStates
from src.ai.analysis_engine import analysis_engine

logger = structlog.get_logger()


# ===== ПРОСТЫЕ ОБРАБОТЧИКИ (ОСНОВНЫЕ) =====

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    user = update.effective_user
    logger.info("🎯 start_command вызван", user_id=user.id, username=user.username)
    
    try:
        welcome_text = f"""
🧠 **Psychology AI Bot**

Привет, {user.first_name}! 

Я создаю детальные психологические портреты с помощью AI.

**Доступные команды:**
• `/analyze` - Начать анализ
• `/help` - Справка
• `/test` - Проверка бота

**Просто отправь текст** для быстрого анализа!
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        logger.info("✅ start_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в start_command", error=str(e), exc_info=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help"""
    user = update.effective_user
    logger.info("🎯 help_command вызван", user_id=user.id)
    
    try:
        help_text = """
📚 **Справка - Psychology AI Bot**

**Команды:**
• `/start` - Начать работу
• `/analyze` - Запустить анализ
• `/help` - Эта справка
• `/test` - Проверка бота

**Как пользоваться:**
1. Отправьте любой текст боту
2. Получите психологический анализ
3. Увидите профиль личности и рекомендации

**Что анализирует бот:**
• Черты личности (Big Five)
• Эмоциональное состояние  
• Стиль общения
• Поведенческие паттерны

Просто отправьте текст для анализа!
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        logger.info("✅ help_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в help_command", error=str(e), exc_info=True)


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /test"""
    user = update.effective_user
    logger.info("🧪 test_command вызван", user_id=user.id)
    
    try:
        await update.message.reply_text(
            f"✅ **Тест успешен!**\n\n"
            f"Привет, {user.first_name}!\n"
            f"Webhook работает корректно.\n"
            f"User ID: `{user.id}`\n\n"
            f"Используй `/start` для начала.",
            parse_mode='Markdown'
        )
        
        logger.info("✅ test_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в test_command", error=str(e), exc_info=True)


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /analyze"""
    user = update.effective_user
    logger.info("🎯 analyze_command вызван", user_id=user.id)
    
    try:
        analyze_text = """
🔍 **Психологический анализ**

Отправьте текст для анализа:
• Сообщения из соцсетей
• Письма или записи
• Любой текст от 50+ символов

Я проанализирую его через AI и создам психологический портрет.

**Отправьте текст прямо сейчас!**
        """
        
        await update.message.reply_text(analyze_text, parse_mode='Markdown')
        logger.info("✅ analyze_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в analyze_command", error=str(e), exc_info=True)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений - автоматический анализ"""
    user = update.effective_user
    text = update.message.text
    
    logger.info("📝 Получен текст для анализа", 
               user_id=user.id, 
               text_length=len(text),
               first_50_chars=text[:50] + "..." if len(text) > 50 else text)
    
    if len(text) < 20:
        await update.message.reply_text(
            "📝 Для качественного анализа нужен текст от 20+ символов.\n\n"
            "Отправьте более развернутое сообщение!"
        )
        return
    
    try:
        # Показ процесса
        processing_message = await update.message.reply_text(
            "🔄 **Анализирую через AI...**\n\n"
            "⏳ Это займет 30-60 секунд...",
            parse_mode='Markdown'
        )
        
        logger.info("🚀 Запускаю AI анализ", user_id=user.id, text_length=len(text))
        
        # Реальный анализ через AI движок
        analysis_result = await analysis_engine.quick_analyze(
            text=text,
            user_id=user.id,
            telegram_id=user.id
        )
        
        # Обновление сообщения с результатом
        await processing_message.edit_text(
            analysis_result,
            parse_mode='Markdown'
        )
        
        # Кнопки действий
        await update.message.reply_text(
            "🎯 **Что дальше?**\n\n"
            "• Отправьте еще текст для нового анализа\n"
            "• `/help` - Справка\n"
            "• `/start` - Главное меню\n\n"
            "💡 *Больше текста = точнее анализ*",
            parse_mode='Markdown'
        )
        
        logger.info("✅ AI анализ завершен успешно", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в text_message_handler", 
                    user_id=user.id, 
                    error=str(e), 
                    exc_info=True)
        
        try:
            await processing_message.edit_text(
                f"❌ **Ошибка анализа**\n\n"
                f"Произошла ошибка: {str(e)}\n\n"
                f"Попробуйте позже или используйте `/help`",
                parse_mode='Markdown'
            )
        except:
            # Если не удалось отредактировать, отправим новое сообщение
            await update.message.reply_text(
                f"❌ **Ошибка анализа**\n\n"
                f"Попробуйте еще раз или используйте `/help`",
                parse_mode='Markdown'
            )


# ===== CONVERSATION HANDLER (ДОПОЛНИТЕЛЬНЫЙ) =====

async def start_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало анализа через ConversationHandler"""
    user = update.effective_user
    logger.info("🎯 start_analysis вызван", user_id=user.id)
    
    try:
        analyze_text = """
🔍 **Детальный психологический анализ**

Отправьте текст для комплексного анализа:
• Посты из социальных сетей
• Письма или сообщения
• Записи в дневнике
• Любой текст от 100+ символов

Чем больше текста - тем точнее анализ!

**Отправьте текст сейчас:**
        """
        
        await update.message.reply_text(analyze_text, parse_mode='Markdown')
        logger.info("✅ start_analysis завершен", user_id=user.id)
        
        return AnalysisStates.COLLECT_TEXT
        
    except Exception as e:
        logger.error("❌ Ошибка в start_analysis", error=str(e), exc_info=True)
        return ConversationHandler.END


async def collect_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сбор текста для анализа"""
    user = update.effective_user
    text = update.message.text
    
    logger.info("📝 Получен текст в conversation", 
               user_id=user.id, 
               text_length=len(text))
    
    if len(text) < 50:
        await update.message.reply_text(
            "📝 Для детального анализа нужен текст от 50+ символов.\n\n"
            "Отправьте более развернутое сообщение или `/cancel` для отмены."
        )
        return AnalysisStates.COLLECT_TEXT
    
    try:
        # Сохранение текста
        context.user_data['analysis_text'] = text
        
        await update.message.reply_text(
            f"✅ **Текст получен** ({len(text)} символов)\n\n"
            f"**Запустить анализ?**\n\n"
            f"• `/process` - Начать анализ\n"
            f"• Отправьте еще текст для объединения\n"
            f"• `/cancel` - Отменить",
            parse_mode='Markdown'
        )
        
        return AnalysisStates.CONFIRM_DATA
        
    except Exception as e:
        logger.error("❌ Ошибка в collect_text", error=str(e), exc_info=True)
        return ConversationHandler.END


async def process_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка анализа"""
    user = update.effective_user
    text = context.user_data.get('analysis_text', '')
    
    if not text:
        await update.message.reply_text(
            "❌ Нет текста для анализа! Используйте `/start` для начала."
        )
        return ConversationHandler.END
    
    logger.info("🚀 Обработка анализа в conversation", 
               user_id=user.id, 
               text_length=len(text))
    
    try:
        # Показ процесса
        processing_message = await update.message.reply_text(
            "🔄 **Запускаю детальный AI анализ...**\n\n"
            "📊 **Этапы:**\n"
            "🔄 Claude анализ личности\n"
            "🔄 Генерация отчета\n"
            "🔄 Финальная обработка\n\n"
            "⏳ *Займет 60-90 секунд...*",
            parse_mode='Markdown'
        )
        
        # Анализ через AI движок
        analysis_result = await analysis_engine.quick_analyze(
            text=text,
            user_id=user.id,
            telegram_id=user.id
        )
        
        # Отправка результата
        await processing_message.edit_text(
            analysis_result,
            parse_mode='Markdown'
        )
        
        # Действия после анализа
        await update.message.reply_text(
            "🎯 **Анализ завершен!**\n\n"
            "• `/start` - Новый анализ\n"
            "• `/help` - Справка\n\n"
            "Спасибо за использование бота!",
            parse_mode='Markdown'
        )
        
        # Очистка данных
        context.user_data.clear()
        
        logger.info("✅ Анализ через conversation завершен", user_id=user.id)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error("❌ Ошибка в process_analysis", error=str(e), exc_info=True)
        
        await processing_message.edit_text(
            f"❌ **Ошибка анализа**\n\n"
            f"Попробуйте позже: {str(e)[:100]}...\n\n"
            f"Используйте `/start` для повтора.",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена conversation"""
    user = update.effective_user
    logger.info("❌ Отмена conversation", user_id=user.id)
    
    await update.message.reply_text(
        "❌ **Анализ отменен**\n\n"
        "Используйте `/start` для нового анализа."
    )
    
    context.user_data.clear()
    return ConversationHandler.END


def setup_handlers(application: Application) -> None:
    """Настройка всех обработчиков"""
    
    logger.info("⚙️ Настройка обработчиков...")
    
    # ПРОСТЫЕ КОМАНДЫ (ПРИОРИТЕТ 1 - ВСЕГДА РАБОТАЮТ)
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    
    logger.info("✅ Простые команды настроены")
    
    # CONVERSATION HANDLER (ПРИОРИТЕТ 2 - ДЕТАЛЬНЫЙ АНАЛИЗ)
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("detailed", start_analysis),
        ],
        states={
            AnalysisStates.COLLECT_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_text),
                CommandHandler("cancel", cancel_conversation),
            ],
            AnalysisStates.CONFIRM_DATA: [
                CommandHandler("process", process_analysis),
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_text),
                CommandHandler("cancel", cancel_conversation),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conversation),
        ],
        per_user=True,
        per_chat=True,
    )
    
    application.add_handler(conversation_handler)
    logger.info("✅ ConversationHandler настроен")
    
    # ОБРАБОТЧИК ТЕКСТА (ПРИОРИТЕТ 3 - АВТОМАТИЧЕСКИЙ АНАЛИЗ)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            text_message_handler
        )
    )
    
    logger.info("✅ Обработчик текста настроен")
    
    logger.info("🎯 Все обработчики настроены успешно!")
    logger.info("📋 Доступные команды: /start, /help, /test, /analyze, /detailed") 