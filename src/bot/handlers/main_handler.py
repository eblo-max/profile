"""
Основные обработчики команд бота
"""
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ConversationHandler, filters
)
import structlog

from src.bot.states.analysis_states import AnalysisStates
from src.ai.analysis_engine import analysis_engine

logger = structlog.get_logger()


async def start_command(update: Update, context) -> int:
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info("🎯 Вызван start_command", user_id=user.id, username=user.username)
    
    welcome_text = f"""
🧠 **Добро пожаловать в Psychology AI Bot!**

Привет, {user.first_name}! 

Я помогу создать детальный психологический портрет на основе:
• 📝 Текстовых данных
• 📸 Фотографий
• 🌐 Социальных сетей

**Мои возможности:**
✅ Анализ личности через 8+ AI сервисов
✅ Научно обоснованные результаты
✅ Полная прозрачность источников
✅ Кросс-валидация данных

Нажми /menu чтобы начать анализ!
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )
    
    logger.info("✅ start_command завершен", user_id=user.id, next_state=AnalysisStates.MENU)
    return AnalysisStates.MENU


async def menu_command(update: Update, context) -> int:
    """Обработчик команды /menu"""
    user = update.effective_user
    logger.info("🎯 Вызван menu_command", user_id=user.id)
    
    menu_text = """
🎯 **Главное меню**

Выберите действие:

1️⃣ /analyze - Начать новый анализ
2️⃣ /history - История анализов
3️⃣ /settings - Настройки
4️⃣ /help - Помощь

Что хотите сделать?
    """
    
    await update.message.reply_text(
        menu_text,
        parse_mode='Markdown'
    )
    
    logger.info("✅ menu_command завершен", user_id=user.id)
    return AnalysisStates.MENU


async def analyze_command(update: Update, context) -> int:
    """Начать новый анализ"""
    user = update.effective_user
    logger.info("🎯 Вызван analyze_command", user_id=user.id)
    
    analyze_text = """
🔍 **Новый психологический анализ**

Для точного анализа мне нужны данные:

📝 **Текст** - сообщения, посты, письма
📸 **Фото** - портреты для анализа эмоций
🌐 **Соцсети** - профили, публикации

Отправьте текст или загрузите изображение для начала анализа.

💡 *Чем больше данных - тем точнее результат!*
    """
    
    await update.message.reply_text(
        analyze_text,
        parse_mode='Markdown'
    )
    
    logger.info("✅ analyze_command завершен", user_id=user.id)
    return AnalysisStates.COLLECT_TEXT


async def text_handler(update: Update, context) -> int:
    """Обработчик текстовых сообщений"""
    text = update.message.text
    user = update.effective_user
    
    # Сохранение текста в контекст
    if not context.user_data.get('collected_data'):
        context.user_data['collected_data'] = {}
    
    context.user_data['collected_data']['text'] = text
    
    await update.message.reply_text(
        f"✅ Получен текст ({len(text)} символов)\n\n"
        f"Хотите добавить еще данных или начать анализ?\n\n"
        f"/start_analysis - Начать анализ\n"
        f"/add_image - Добавить фото\n"
        f"/menu - Главное меню"
    )
    
    logger.info("Получен текст от пользователя", 
                user_id=user.id, text_length=len(text))
    
    return AnalysisStates.CONFIRM_DATA


async def start_analysis_command(update: Update, context) -> int:
    """Запуск анализа"""
    user = update.effective_user
    collected_data = context.user_data.get('collected_data', {})
    
    if not collected_data or not collected_data.get('text'):
        await update.message.reply_text(
            "❌ **Нет данных для анализа!**\n\n"
            "Пожалуйста, отправьте текст для анализа.\n"
            "Используйте /analyze чтобы начать заново."
        )
        return AnalysisStates.COLLECT_TEXT
    
    logger.info("🚀 Запускаю реальный AI анализ", 
               user_id=user.id, 
               text_length=len(collected_data['text']))
    
    # Показ процесса анализа
    processing_message = await update.message.reply_text(
        "🔄 **Запускаю AI анализ...**\n\n"
        "📊 **Этапы обработки:**\n"
        "🔄 Anthropic Claude - комплексный анализ\n"
        "🔄 Валидация результатов\n"
        "🔄 Генерация отчета\n\n"
        "⏳ *Это займет 30-60 секунд...*",
        parse_mode='Markdown'
    )
    
    try:
        # Реальный анализ через AI движок
        analysis_result = await analysis_engine.quick_analyze(
            text=collected_data['text'],
            user_id=user.id,
            telegram_id=user.id
        )
        
        # Обновление сообщения с результатом
        await processing_message.edit_text(
            analysis_result,
            parse_mode='Markdown'
        )
        
        # Добавление кнопок действий
        await update.message.reply_text(
            "🎯 **Что дальше?**\n\n"
            "• `/analyze` - Новый анализ\n"
            "• `/history` - История анализов\n"
            "• `/menu` - Главное меню\n\n"
            "💡 *Tip: Отправьте больше текста для более точного анализа*",
            parse_mode='Markdown'
        )
        
        # Очистка собранных данных
        context.user_data['collected_data'] = {}
        
        logger.info("✅ AI анализ завершен успешно", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка AI анализа", user_id=user.id, error=str(e))
        
        # Сообщение об ошибке
        await processing_message.edit_text(
            "❌ **Ошибка анализа**\n\n"
            f"Произошла ошибка: {str(e)}\n\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.\n\n"
            "Используйте /menu для возврата в главное меню.",
            parse_mode='Markdown'
        )
    
    return AnalysisStates.SHOW_RESULTS


async def help_command(update: Update, context) -> int:
    """Помощь"""
    help_text = """
📚 **Помощь - Psychology AI Bot**

**Команды:**
/start - Начать работу
/menu - Главное меню  
/analyze - Новый анализ
/history - История анализов
/help - Эта справка

**Как работает анализ:**
1. Загрузите данные (текст/фото)
2. Подтвердите запуск анализа
3. Получите детальный отчет

**Типы анализа:**
• Личностный профиль (Big5)
• Эмоциональное состояние
• Поведенческие паттерны
• Когнитивные особенности

**Источники данных:**
• IBM Watson Personality Insights
• Azure Cognitive Services
• Google Cloud Natural Language
• AWS Rekognition
• Crystal API (DISC)
• Receptiviti API

Есть вопросы? Напишите /start
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )
    
    return AnalysisStates.MENU


async def cancel_handler(update: Update, context) -> int:
    """Отмена разговора"""
    await update.message.reply_text(
        "❌ Операция отменена.\n"
        "Используйте /start для начала работы."
    )
    
    return ConversationHandler.END


async def test_command(update: Update, context):
    """Простая команда для тестирования"""
    user = update.effective_user
    logger.info("🧪 Тест команда получена", user_id=user.id)
    
    await update.message.reply_text(
        f"✅ **Тест успешен!**\n\n"
        f"Привет, {user.first_name}!\n"
        f"Webhook работает корректно.\n"
        f"User ID: {user.id}"
    )
    
    logger.info("✅ Тест команда отправлена", user_id=user.id)


def setup_handlers(application: Application):
    """Настройка всех обработчиков"""
    
    # Простая команда для тестирования (БЕЗ ConversationHandler)
    application.add_handler(CommandHandler("test", test_command))
    logger.info("✅ Простой test handler добавлен")
    
    # Создание ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("menu", menu_command),
        ],
        states={
            AnalysisStates.MENU: [
                CommandHandler("analyze", analyze_command),
                CommandHandler("history", help_command),  # Заглушка
                CommandHandler("settings", help_command),  # Заглушка
                CommandHandler("help", help_command),
            ],
            AnalysisStates.COLLECT_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler),
                CommandHandler("add_image", help_command),  # Заглушка
                CommandHandler("menu", menu_command),
            ],
            AnalysisStates.CONFIRM_DATA: [
                CommandHandler("start_analysis", start_analysis_command),
                CommandHandler("add_image", help_command),  # Заглушка
                CommandHandler("menu", menu_command),
            ],
            AnalysisStates.SHOW_RESULTS: [
                CommandHandler("menu", menu_command),
                CommandHandler("analyze", analyze_command),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            CommandHandler("menu", menu_command),
        ],
        per_user=True,
        per_chat=True,
    )
    
    # Добавление обработчиков
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    logger.info("✅ Все обработчики бота настроены") 