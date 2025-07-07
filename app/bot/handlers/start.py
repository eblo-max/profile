"""Start handler for bot initialization and main menu"""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_session
from app.services.user_service import UserService
from app.bot.keyboards.inline import main_menu_kb, back_to_main_kb
from app.bot.states import OnboardingStates, UserProfileStates
from app.utils.decorators import handle_errors
from app.core.logging import logger

router = Router()


@router.message(CommandStart())
# @handle_errors  # Временно убираем для проверки
async def start_command(message: Message, state: FSMContext) -> None:
    """Handle /start command"""
    logger.info(f"START: Handler called for user {message.from_user.id}")
    logger.info(f"START: Message text: {message.text}")
    logger.info(f"START: Chat ID: {message.chat.id}")
    try:
        logger.info("START: Creating session")
        async with get_session() as session:
            logger.info("START: Session created, getting user service")
            user_service = UserService(session)
            
            logger.info("START: Getting or creating user")
            # Get or create user
            user = await user_service.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            logger.info(f"START: User created/found: {user.id}")
            
            logger.info("START: Starting onboarding")
            # Always show onboarding for /start command
            await start_onboarding(message, state)
            logger.info("START: Onboarding called successfully")
                
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        logger.exception("START: Full error traceback:")
        await message.answer(
            "😔 Произошла ошибка при запуске бота. Попробуйте снова.",
            reply_markup=back_to_main_kb()
        )


@router.message(Command("menu"))
@router.callback_query(F.data == "main_menu")
# @handle_errors  # Временно убираем для проверки
async def show_main_menu(message_or_query, state: FSMContext = None) -> None:
    """Show main menu"""
    
    if state:
        await state.clear()
    
    welcome_text = """
🤖 **PsychoDetective** - ваш помощник в анализе отношений

🎯 **Что я умею:**

📝 **Анализ текста** - анализирую переписки и сообщения на предмет:
   • Манипуляций и токсичного поведения
   • Эмоционального состояния собеседника
   • Скрытых мотивов и намерений

👤 **Профиль партнера** - создаю психологический портрет на основе:
   • Ваших наблюдений и ответов на вопросы
   • Анализа поведенческих паттернов
   • Выявления красных флагов

💕 **Тест совместимости** - оцениваю совместимость между партнерами:
   • По ценностям и жизненным целям
   • По стилю общения и решения конфликтов
   • По эмоциональным потребностям

📅 **Ежедневные советы** - получайте полезный контент:
   • Советы по улучшению отношений
   • Упражнения для развития эмпатии
   • Уроки здоровой коммуникации

Выберите нужный раздел в меню ниже ⬇️
"""
    
    if isinstance(message_or_query, Message):
        await message_or_query.answer(
            welcome_text,
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )
    else:
        await message_or_query.message.edit_text(
            welcome_text,
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )
        await message_or_query.answer()


async def start_onboarding(message: Message, state: FSMContext) -> None:
    """Start user onboarding process"""
    logger.info("ONBOARDING: Starting")
    await state.set_state(OnboardingStates.welcome)
    
    onboarding_text = """
👋 **Добро пожаловать в PsychoDetective!**

Я помогу вам лучше понимать отношения и принимать более осознанные решения.

🎯 **Настройка профиля:**
1. Укажите ваши данные для персонализации
2. Получите доступ ко всем функциям
3. Начните анализировать отношения

⏱️ Это займет всего 2-3 минуты.

Готовы настроить профиль? 🚀

💡 *Или используйте команду /menu для перехода в главное меню*
"""
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Настроить профиль", callback_data="confirm_onboarding_start"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    logger.info("ONBOARDING: Sending message")
    await message.answer(
        onboarding_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    logger.info("ONBOARDING: Message sent")


@router.callback_query(F.data == "confirm_onboarding_start")
@handle_errors
async def start_profile_setup(callback: CallbackQuery, state: FSMContext) -> None:
    """Start profile setup during onboarding"""
    from app.bot.states import UserProfileStates
    
    await state.set_state(UserProfileStates.waiting_for_name)
    
    setup_text = """
📝 **Настройка профиля**

Как к вам обращаться? Введите ваше имя:

💡 *Эта информация поможет мне персонализировать общение с вами*
"""
    
    await callback.message.edit_text(
        setup_text,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(F.text, UserProfileStates.waiting_for_name)
@handle_errors
async def process_user_name(message: Message, state: FSMContext) -> None:
    """Process user name during setup"""
    name = message.text.strip()
    
    if len(name) > 50:
        await message.answer(
            "😅 Имя слишком длинное. Пожалуйста, введите имя покороче (до 50 символов):"
        )
        return
    
    await state.update_data(name=name)
    await state.set_state(UserProfileStates.waiting_for_gender)
    
    from app.bot.keyboards.inline import gender_kb
    
    await message.answer(
        f"Приятно познакомиться, {name}! 😊\n\n"
        "Укажите ваш пол (это поможет мне лучше анализировать ваши отношения):",
        reply_markup=gender_kb()
    )


@router.callback_query(F.data.startswith("gender_"), UserProfileStates.waiting_for_gender)
@handle_errors
async def process_user_gender(callback: CallbackQuery, state: FSMContext) -> None:
    """Process user gender selection"""
    gender_data = callback.data.split("_")[1]
    
    if gender_data == "skip":
        gender = None
    else:
        gender = gender_data
    
    await state.update_data(gender=gender)
    await state.set_state(UserProfileStates.waiting_for_age)
    
    from app.bot.keyboards.inline import age_group_kb
    
    await callback.message.edit_text(
        "Выберите вашу возрастную группу:",
        reply_markup=age_group_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("age_"), UserProfileStates.waiting_for_age)
@handle_errors
async def process_user_age(callback: CallbackQuery, state: FSMContext) -> None:
    """Process user age group selection"""
    age_data = callback.data.split("_", 1)[1]
    
    if age_data == "skip":
        age_group = None
    else:
        age_group = age_data.replace("_", "-")
    
    await state.update_data(age_group=age_group)
    await complete_profile_setup(callback, state)


async def complete_profile_setup(callback: CallbackQuery, state: FSMContext) -> None:
    """Complete profile setup and save to database"""
    user_data = await state.get_data()
    
    try:
        async with get_session() as session:
            user_service = UserService(session)
            
            # Update user profile
            await user_service.update_user_profile(
                telegram_id=callback.from_user.id,
                name=user_data.get("name"),
                gender=user_data.get("gender"),
                age_group=user_data.get("age_group")
            )
            
            await state.clear()
            await show_main_menu(callback)
            await callback.answer("✅ Профиль сохранен!")
            
    except Exception as e:
        logger.error(f"Error completing profile setup: {e}")
        await callback.answer("❌ Ошибка при сохранении профиля")


@router.callback_query(F.data == "cancel_onboarding")
@handle_errors
async def cancel_onboarding(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel onboarding and go to main menu"""
    await state.clear()
    await show_main_menu(callback, state)


@router.message(Command("help"))
# @handle_errors  # Временно убираем для проверки
async def help_command(message: Message) -> None:
    """Show help information"""
    help_text = """
🆘 **Справка по PsychoDetective**

**Основные команды:**
/start - Запуск бота и главное меню
/menu - Показать главное меню
/help - Показать справку
/profile - Мой профиль
/support - Техническая поддержка

**Основные функции:**

📝 **Анализ текста**
• Загрузите файл с перепиской или введите текст
• Получите анализ на предмет манипуляций и токсичности
• Рекомендации по дальнейшим действиям

👤 **Профиль партнера**
• Ответьте на вопросы о вашем партнере
• Получите психологический портрет
• Выявите потенциальные красные флаги

💕 **Тест совместимости**
• Пройдите тест на совместимость
• Сравните ваши профили
• Получите рекомендации по улучшению отношений

📅 **Ежедневные советы**
• Полезные советы каждый день
• Упражнения для улучшения отношений
• Образовательный контент

**Подписки:**
💎 Premium - расширенные возможности анализа
👑 VIP - безлимитные анализы и приоритетная поддержка

По вопросам: /support
"""
    
    await message.answer(
        help_text,
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )


@router.message(Command("support"))
@handle_errors
async def support_command(message: Message) -> None:
    """Show support information"""
    support_text = """
🆘 *Техническая поддержка*

Если у вас возникли вопросы или проблемы:

📧 *Email:* support@psychodetective.bot
📱 *Telegram:* @psychodetective\\_support

*Часто задаваемые вопросы:*

❓ *Как работает анализ текста?*
Наша ИИ-система анализирует паттерны общения, эмоциональные маркеры и признаки манипулятивного поведения.

❓ *Безопасны ли мои данные?*
Да, все данные шифруются и не передаются третьим лицам. Мы соблюдаем GDPR.

❓ *Как отменить подписку?*
Обратитесь в поддержку или воспользуйтесь настройками подписки в профиле.

❓ *Точность анализа?*
Наша система имеет точность 89% в выявлении манипулятивных паттернов, но результаты носят рекомендательный характер.

*Время ответа:* до 24 часов
"""
    
    await message.answer(
        support_text,
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )


@router.message(Command("test"))
async def test_command(message: Message) -> None:
    """Simple test command without decorators"""
    logger.info(f"TEST: Handler called for user {message.from_user.id}")
    logger.info(f"TEST: Message text: {message.text}")
    logger.info(f"TEST: Chat ID: {message.chat.id}")
    try:
        logger.info("TEST: About to send response")
        await message.answer("✅ Тест успешен! Бот работает.")
        logger.info("TEST: Response sent successfully")
    except Exception as e:
        logger.error(f"TEST: Error sending response: {e}")
        logger.exception("TEST: Full error traceback:")


@router.message(Command("ping"))
async def ping_command(message: Message) -> None:
    """Ultra simple ping command for basic connectivity test"""
    logger.info(f"PING: Received from user {message.from_user.id}")
    await message.answer("🏓 Pong! Бот откликается.") 