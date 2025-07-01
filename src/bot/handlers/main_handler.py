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

logger = structlog.get_logger()


async def start_command(update: Update, context) -> str:
    """Обработчик команды /start"""
    user = update.effective_user
    
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
    
    logger.info("Пользователь запустил бота", user_id=user.id)
    return AnalysisStates.MENU


async def menu_command(update: Update, context) -> str:
    """Обработчик команды /menu"""
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
    
    return AnalysisStates.MENU


async def analyze_command(update: Update, context) -> str:
    """Начать новый анализ"""
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
    
    return AnalysisStates.COLLECT_TEXT


async def text_handler(update: Update, context) -> str:
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


async def start_analysis_command(update: Update, context) -> str:
    """Запуск анализа"""
    collected_data = context.user_data.get('collected_data', {})
    
    if not collected_data:
        await update.message.reply_text(
            "❌ Нет данных для анализа!\n"
            "Отправьте текст или изображение."
        )
        return AnalysisStates.COLLECT_TEXT
    
    # Показ процесса анализа
    processing_text = """
🔄 **Запускаю анализ...**

📊 Этапы обработки:
□ IBM Watson - анализ личности
□ Azure Cognitive - эмоции
□ Google Cloud - сущности
□ AWS Rekognition - лица
□ Claude - синтез результатов

⏳ Это займет 1-2 минуты...
    """
    
    await update.message.reply_text(
        processing_text,
        parse_mode='Markdown'
    )
    
    # TODO: Здесь будет вызов движка анализа
    
    # Пока заглушка
    await update.message.reply_text(
        "🚧 **Функция в разработке**\n\n"
        "Система анализа будет готова после настройки всех AI сервисов.\n\n"
        "/menu - Вернуться в меню"
    )
    
    return AnalysisStates.SHOW_RESULTS


async def help_command(update: Update, context) -> str:
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


def setup_handlers(application: Application):
    """Настройка всех обработчиков"""
    
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
    
    logger.info("✅ Обработчики бота настроены") 