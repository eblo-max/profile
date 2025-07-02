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
from src.utils.economic_analysis_manager import economic_manager, AnalysisLevel
from src.utils.cache_manager import cache_manager

logger = structlog.get_logger()


# ===== ПРОСТЫЕ ОБРАБОТЧИКИ (ОСНОВНЫЕ) =====

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    user = update.effective_user
    logger.info("🎯 start_command вызван", user_id=user.id, username=user.username)
    
    try:
        welcome_text = f"""
🧠 **Psychology AI Bot - Экономическая Система 2025**

Привет, {user.first_name}! 

💰 **НОВАЯ ЭКОНОМИЧЕСКАЯ МОДЕЛЬ:**

🆓 **Бесплатно:**
• `/free` - 3 анализа в день
• Просто отправь текст (автоматически FREE)

💎 **Платные уровни:**
• `/pricing` - Тарифные планы
• `/basic` ($1.99) - Детальный анализ
• `/advanced` ($4.99) - 2 AI + научная выборка
• `/research_pro` ($9.99) - Полный научный поиск  
• `/premium` ($19.99) - 5 AI + максимум возможностей

🔬 **Революционная функция:**
• Первый в мире поиск peer-reviewed исследований для психоанализа
• PubMed, Google Scholar интеграция
• Научно-валидированные профили

📊 **Система:**
• `/cache` - Статистика кэша (экономия 70%)

🚀 **Начни с `/pricing` чтобы выбрать уровень!**
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
📚 **Справка - Psychology AI Bot (Экономическая Система 2025)**

💰 **ЭКОНОМИЧЕСКИЕ КОМАНДЫ:**
• `/pricing` - Тарифные планы и цены
• `/free` - Бесплатный анализ (3/день)
• `/basic` - Детальный анализ ($1.99)
• `/advanced` - 2 AI + научные данные ($4.99)
• `/research_pro` - Полный научный поиск ($9.99)
• `/premium` - 5 AI + максимум ($19.99)

🔧 **СИСТЕМНЫЕ КОМАНДЫ:**
• `/start` - Главное меню
• `/help` - Эта справка
• `/test` - Проверка работы
• `/cache` - Статистика кэширования

📝 **КАК ПОЛЬЗОВАТЬСЯ:**

**Автоматический анализ:**
• Просто отправь текст → автоматически FREE уровень
• 3 бесплатных анализа в день

**Платные уровни:**
1. `/pricing` - Изучить тарифы
2. Выбрать нужный уровень (`/basic`, `/advanced`, и т.д.)
3. Отправить текст для анализа

🔬 **РЕВОЛЮЦИОННЫЕ ВОЗМОЖНОСТИ:**
• Первый в мире поиск научных статей для психоанализа
• PubMed + Google Scholar интеграция
• Мультимодальный AI (до 5 движков параллельно)
• Кэширование для экономии 70% стоимости

💡 *Система адаптируется под ваш бюджет и потребности*
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


async def research_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /research - Научно-обоснованный анализ"""
    user = update.effective_user
    logger.info("🔬 research_command вызван", user_id=user.id)
    
    try:
        research_text = """
🔬 **НАУЧНО-ОБОСНОВАННЫЙ АНАЛИЗ** 

🆕 **РЕВОЛЮЦИОННАЯ ФУНКЦИЯ!**

**Что это:**
• Поиск актуальных исследований в PubMed, Google Scholar
• Анализ peer-reviewed источников по психологии
• Создание профиля на основе научных данных
• Мультимодальный AI анализ научной литературы

**Как использовать:**
1. Отправьте информацию о человеке:
   - Имя, возраст, профессия
   - Описание поведения
   - Примеры текстов/сообщений
   - Наблюдаемые черты характера

2. Система автоматически найдет релевантные исследования
3. Получите научно-валидированный психологический профиль

**Пример запроса:**
```
Имя: Алексей
Возраст: 28 лет
Профессия: IT-разработчик
Поведение: Очень организованный, любит порядок, предпочитает работать в одиночку. Часто анализирует детали. В общении сдержан, но дружелюбен.
Тексты: "Мне нравится, когда все по плану. Хаос меня раздражает."
```

**🚀 Отправьте данные о человеке для анализа!**
        """
        
        await update.message.reply_text(research_text, parse_mode='Markdown')
        logger.info("✅ research_command завершен", user_id=user.id)
        
        # Устанавливаем флаг ожидания данных для исследования
        context.user_data['awaiting_research_data'] = True
        
    except Exception as e:
        logger.error("❌ Ошибка в research_command", error=str(e), exc_info=True)


async def pricing_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /pricing - Тарифные планы"""
    user = update.effective_user
    logger.info("💰 pricing_command вызван", user_id=user.id)
    
    try:
        # Получаем информацию о тарифных планах
        comparison = economic_manager.get_level_comparison()
        
        pricing_text = """
💰 **ТАРИФНЫЕ ПЛАНЫ АНАЛИЗА**

🆓 **Базовый (БЕСПЛАТНО)**
• 3 анализа в день
• Только Claude AI
• Big Five профиль
• Основные рекомендации
• Время: ~1 минута

⭐ **Стандартный - $1.99**
• Детальный анализ
• Когнитивные паттерны
• Карьерные рекомендации
• Совместимость
• Время: ~2 минуты

🚀 **Продвинутый - $4.99**
• 2 AI системы (Claude + GPT-4)
• Научная выборка (10 источников)
• Романтическая совместимость
• Долгосрочные прогнозы
• Кросс-валидация
• Время: ~3 минуты

🔬 **Научный - $9.99**
• Поиск в PubMed + Google Scholar
• Peer-reviewed валидация
• 3 AI системы + научный поиск
• 30+ научных источников
• Статистическая валидность
• Время: ~5 минут

💎 **Максимальный - $19.99**
• 5 AI систем параллельно
• 50+ научных источников
• Персональные рекомендации
• VIP обработка
• Экспорт в PDF
• Время: ~8 минут

**💡 Команды для заказа:**
• `/free` - Бесплатный анализ
• `/basic` - Стандартный ($1.99)
• `/advanced` - Продвинутый ($4.99)
• `/research` - Научный ($9.99)
• `/premium` - Максимальный ($19.99)

**📊 Статистика кэша:**
• Экономия за счет кэша: до 70%
• Время ответа с кэшем: в 5 раз быстрее
        """
        
        await update.message.reply_text(pricing_text, parse_mode='Markdown')
        logger.info("✅ pricing_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в pricing_command", error=str(e), exc_info=True)


async def free_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /free - Бесплатный анализ"""
    await _handle_level_command(update, context, AnalysisLevel.FREE)


async def basic_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /basic - Стандартный анализ"""
    await _handle_level_command(update, context, AnalysisLevel.BASIC)


async def advanced_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /advanced - Продвинутый анализ"""
    await _handle_level_command(update, context, AnalysisLevel.ADVANCED)


async def research_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /research_pro - Научный анализ"""
    await _handle_level_command(update, context, AnalysisLevel.RESEARCH)


async def premium_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /premium - Максимальный анализ"""
    await _handle_level_command(update, context, AnalysisLevel.PREMIUM)


async def _handle_level_command(update: Update, context: ContextTypes.DEFAULT_TYPE, level: AnalysisLevel) -> None:
    """Обработка команды уровня анализа"""
    user = update.effective_user
    logger.info(f"💰 {level.value}_analysis_command вызван", user_id=user.id)
    
    try:
        # Получаем конфигурацию уровня
        config = economic_manager.analysis_configs[level]
        
        level_info_text = f"""
{economic_manager._get_level_emoji(level)} **{economic_manager._get_level_name(level).upper()} АНАЛИЗ**

**💰 Стоимость:** {"БЕСПЛАТНО" if level == AnalysisLevel.FREE else f"${config.price_usd}"}
**⏱️ Время:** ~{config.estimated_time_minutes} мин
**🤖 AI сервисы:** {len(config.ai_services)}
**📚 Научный поиск:** {"✅" if config.scientific_search else "❌"}

**🎯 Возможности:**
{chr(10).join([f"• {feature}" for feature in config.features[:5]])}

**📝 Отправьте текст для анализа прямо сейчас!**

Пример: "Я очень организованный человек, люблю планировать все заранее. В работе предпочитаю качество количеству. Иногда могу быть слишком критичным к себе..."
        """
        
        await update.message.reply_text(level_info_text, parse_mode='Markdown')
        
        # Сохраняем выбранный уровень в контексте пользователя
        context.user_data['selected_analysis_level'] = level
        context.user_data['awaiting_analysis_text'] = True
        
        logger.info(f"✅ {level.value}_analysis_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в {level.value}_analysis_command", error=str(e), exc_info=True)


async def cache_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /cache - Статистика кэширования"""
    user = update.effective_user
    logger.info("📊 cache_stats_command вызван", user_id=user.id)
    
    try:
        # Инициализируем кэш если еще не инициализирован
        if not cache_manager.redis_client:
            await cache_manager.initialize()
        
        stats = await cache_manager.get_cache_statistics()
        
        cache_text = f"""
📊 **СТАТИСТИКА КЭШИРОВАНИЯ**

**🎯 Эффективность:**
• Попадания в кэш: {stats.get('total_hits', 0)}
• Промахи: {stats.get('total_misses', 0)}
• Hit Rate: {stats.get('hit_rate', 0):.1%}
• Качество кэша: {stats.get('cache_efficiency', 'N/A')}

**💰 Экономия:**
• Общая экономия: ${stats.get('total_savings_usd', 0):.2f}
• Средняя экономия за анализ: ${stats.get('total_savings_usd', 0) / max(stats.get('total_hits', 1), 1):.2f}

**📦 Использование памяти:**
• Redis память: {stats.get('redis_memory_used', 'N/A')}
• Типы записей: {len(stats.get('entries_by_type', {}))}

**📈 Записи по типам:**
{chr(10).join([f"• {cache_type}: {count} записей" for cache_type, count in stats.get('entries_by_type', {}).items()])}

**💡 Советы:**
• Похожие запросы используют кэш
• Научные исследования кэшируются на 7 дней
• Обычные анализы - на 24 часа
        """
        
        await update.message.reply_text(cache_text, parse_mode='Markdown')
        logger.info("✅ cache_stats_command завершен", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в cache_stats_command", error=str(e), exc_info=True)
        await update.message.reply_text(
            "❌ Не удалось получить статистику кэша. Возможно, Redis недоступен.",
            parse_mode='Markdown'
        )


async def handle_research_data(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Обработка данных для научно-обоснованного анализа"""
    user = update.effective_user
    logger.info("🔬 Обработка данных для научного исследования", user_id=user.id, text_length=len(text))
    
    if len(text) < 50:
        await update.message.reply_text(
            "📝 Для научно-обоснованного анализа нужно больше информации.\n\n"
            "Укажите:\n"
            "• Имя и возраст\n"
            "• Профессию\n"
            "• Описание поведения\n"
            "• Примеры текстов/высказываний\n\n"
            "Минимум 50+ символов!"
        )
        return
    
    try:
        # Сброс флага ожидания
        context.user_data['awaiting_research_data'] = False
        
        # Показ процесса
        processing_message = await update.message.reply_text(
            "🔬 **Запускаю научно-обоснованный анализ...**\n\n"
            "📊 **Этапы:**\n"
            "🔄 Парсинг данных о человеке\n"
            "🔄 Поиск в научных базах (PubMed, Scholar)\n"
            "🔄 Валидация источников\n"
            "🔄 Мультимодальный AI анализ\n"
            "🔄 Синтез научно-обоснованного профиля\n\n"
            "⏳ *Это может занять 2-3 минуты...*",
            parse_mode='Markdown'
        )
        
        # Парсинг данных о человеке из текста
        person_data = parse_person_data_from_text(text)
        
        logger.info("🧠 Запускаю научно-обоснованный анализ", 
                   user_id=user.id, 
                   person_name=person_data.get("name", "Unknown"))
        
        # Запуск научно-обоснованного анализа
        analysis_result = await analysis_engine.scientific_research_analysis(
            person_data=person_data,
            user_id=user.id,
            telegram_id=user.id
        )
        
        # Разбиваем результат на части если он слишком длинный (Telegram лимит 4096 символов)
        max_message_length = 4000  # Оставляем запас
        
        if len(analysis_result) <= max_message_length:
            # Отправляем одним сообщением
            await processing_message.edit_text(
                analysis_result,
                parse_mode='Markdown'
            )
        else:
            # Разбиваем на части
            parts = split_long_message(analysis_result, max_message_length)
            
            # Редактируем первое сообщение
            await processing_message.edit_text(
                parts[0],
                parse_mode='Markdown'
            )
            
            # Отправляем остальные части
            for part in parts[1:]:
                await update.message.reply_text(
                    part,
                    parse_mode='Markdown'
                )
        
        # Дополнительные действия
        await update.message.reply_text(
            "🎯 **Научно-обоснованный анализ завершен!**\n\n"
            "**Доступные действия:**\n"
            "• `/research` - Новый научный анализ\n"
            "• `/analyze` - Быстрый анализ текста\n"
            "• `/help` - Справка\n\n"
            "💡 *Для уточнения анализа предоставьте дополнительные данные*",
            parse_mode='Markdown'
        )
        
        logger.info("✅ Научно-обоснованный анализ завершен успешно", user_id=user.id)
        
    except Exception as e:
        logger.error("❌ Ошибка в handle_research_data", 
                    user_id=user.id, 
                    error=str(e), 
                    exc_info=True)
        
        # Сброс флага при ошибке
        context.user_data['awaiting_research_data'] = False
        
        try:
            await processing_message.edit_text(
                f"❌ **Ошибка научного анализа**\n\n"
                f"Произошла ошибка: {str(e)[:100]}...\n\n"
                f"**Попробуйте:**\n"
                f"• `/research` - Повторить научный анализ\n"
                f"• `/analyze` - Быстрый анализ\n"
                f"• `/help` - Справка",
                parse_mode='Markdown'
            )
        except:
            # Если не удалось отредактировать, отправим новое сообщение
            await update.message.reply_text(
                f"❌ **Ошибка научного анализа**\n\n"
                f"Попробуйте `/research` для повтора или `/help` для справки",
                parse_mode='Markdown'
            )


def parse_person_data_from_text(text: str) -> dict:
    """Парсинг данных о человеке из текста"""
    import re
    
    person_data = {
        "name": "Неизвестно",
        "age": None,
        "gender": None,
        "occupation": "",
        "behavior_description": text,  # Весь текст как описание поведения
        "text_samples": [],
        "emotional_markers": [],
        "social_patterns": [],
        "cognitive_traits": [],
        "suspected_personality_type": "",
        "country": "Russia",
        "cultural_context": "Российский"
    }
    
    # Поиск имени
    name_patterns = [
        r'[Ии]мя[:\s]*([А-Яа-яA-Za-z]+)',
        r'[Зз]овут[:\s]*([А-Яа-яA-Za-z]+)',
        r'^([А-Я][а-я]+)[,\s]',  # Имя в начале строки
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            person_data["name"] = match.group(1).strip()
            break
    
    # Поиск возраста
    age_patterns = [
        r'[Вв]озраст[:\s]*(\d+)',
        r'(\d+)[:\s]*лет',
        r'(\d+)[:\s]*год',
        r'[Мм]не[:\s]*(\d+)',
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, text)
        if match:
            person_data["age"] = int(match.group(1))
            break
    
    # Поиск профессии
    occupation_patterns = [
        r'[Пп]рофессия[:\s]*([А-Яа-яA-Za-z\-\s]+?)(?:[.\n]|$)',
        r'[Рр]аботаю?[:\s]*([А-Яа-яA-Za-z\-\s]+?)(?:[.\n]|$)',
        r'[Дд]олжность[:\s]*([А-Яа-яA-Za-z\-\s]+?)(?:[.\n]|$)',
    ]
    
    for pattern in occupation_patterns:
        match = re.search(pattern, text)
        if match:
            person_data["occupation"] = match.group(1).strip()
            break
    
    # Поиск примеров текстов в кавычках
    text_samples = re.findall(r'[""\'](.*?)[""\'"]', text)
    if text_samples:
        person_data["text_samples"] = text_samples
    
    # Простой анализ эмоциональных маркеров
    emotional_keywords = {
        "позитивные": ["радость", "счастье", "оптимизм", "энтузиазм", "веселый"],
        "негативные": ["грусть", "тревога", "стресс", "раздражение", "злость"],
        "нейтральные": ["спокойствие", "уравновешенность", "стабильность"]
    }
    
    for category, keywords in emotional_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                person_data["emotional_markers"].append(f"{category}: {keyword}")
    
    # Поиск социальных паттернов
    social_keywords = [
        "интроверт", "экстраверт", "общительный", "замкнутый", 
        "лидер", "командный", "одиночка", "социальный"
    ]
    
    for keyword in social_keywords:
        if keyword.lower() in text.lower():
            person_data["social_patterns"].append(keyword)
    
    # Поиск когнитивных черт
    cognitive_keywords = [
        "аналитический", "творческий", "логический", "интуитивный",
        "организованный", "спонтанный", "детальный", "системный"
    ]
    
    for keyword in cognitive_keywords:
        if keyword.lower() in text.lower():
            person_data["cognitive_traits"].append(keyword)
    
    return person_data


def split_long_message(message: str, max_length: int) -> list:
    """Разбивка длинного сообщения на части"""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    current_part = ""
    
    # Разбиваем по абзацам
    paragraphs = message.split('\n\n')
    
    for paragraph in paragraphs:
        # Если добавление параграфа превысит лимит
        if len(current_part) + len(paragraph) + 2 > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = paragraph + '\n\n'
            else:
                # Если сам параграф слишком длинный, разбиваем по строкам
                lines = paragraph.split('\n')
                for line in lines:
                    if len(current_part) + len(line) + 1 > max_length:
                        if current_part:
                            parts.append(current_part.strip())
                            current_part = line + '\n'
                        else:
                            # Если даже строка слишком длинная, обрезаем
                            parts.append(line[:max_length-10] + "...")
                    else:
                        current_part += line + '\n'
                current_part += '\n'
        else:
            current_part += paragraph + '\n\n'
    
    if current_part.strip():
        parts.append(current_part.strip())
    
    return parts


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений - автоматический анализ"""
    user = update.effective_user
    text = update.message.text
    
    logger.info("📝 Получен текст для анализа", 
               user_id=user.id, 
               text_length=len(text),
               first_50_chars=text[:50] + "..." if len(text) > 50 else text)
    
    # Проверяем, ожидаем ли мы данные для научного исследования
    if context.user_data.get('awaiting_research_data', False):
        return await handle_research_data(update, context, text)
    
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
        
        # 💰 ЭКОНОМИЧЕСКИЙ АНАЛИЗ (БЕСПЛАТНЫЙ УРОВЕНЬ)
        analysis_result = await economic_manager.perform_analysis(
            text=text,
            user_id=user.id,
            level=AnalysisLevel.FREE,  # Автоматический анализ = бесплатный уровень
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
        
        # 💰 ЭКОНОМИЧЕСКИЙ АНАЛИЗ (ДЕТАЛЬНЫЙ = BASIC УРОВЕНЬ)
        analysis_result = await economic_manager.perform_analysis(
            text=text,
            user_id=user.id,
            level=AnalysisLevel.BASIC,  # Детальный анализ = базовый уровень
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
    application.add_handler(CommandHandler("research", research_command))
    
    # 💰 ЭКОНОМИЧЕСКИЕ КОМАНДЫ (НОВАЯ СИСТЕМА 2025)
    application.add_handler(CommandHandler("pricing", pricing_command))
    application.add_handler(CommandHandler("free", free_analysis_command))
    application.add_handler(CommandHandler("basic", basic_analysis_command))
    application.add_handler(CommandHandler("advanced", advanced_analysis_command))
    application.add_handler(CommandHandler("research_pro", research_analysis_command))
    application.add_handler(CommandHandler("premium", premium_analysis_command))
    application.add_handler(CommandHandler("cache", cache_stats_command))
    
    logger.info("✅ Простые команды настроены")
    logger.info("💰 Экономические команды настроены")
    
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
    logger.info("📋 Основные команды: /start, /help, /test, /analyze, /research, /detailed")
    logger.info("💰 Экономические команды: /pricing, /free, /basic, /advanced, /research_pro, /premium, /cache")
    logger.info("🔬 Революционная функция: Научно-обоснованный анализ с экономической моделью") 