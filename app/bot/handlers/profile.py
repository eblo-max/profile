"""User profile handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.exceptions import handle_errors
from app.bot.keyboards.inline import (
    profile_menu_kb, subscription_menu_kb, back_to_main_kb, 
    profile_edit_kb, back_to_profile_kb
)
from app.services.user_service import UserService
from app.core.logging import logger

router = Router()

@router.callback_query(F.data == "profile_menu")
@handle_errors
async def show_profile_menu(callback: CallbackQuery):
    """Show user profile menu"""
    menu_text = """
⚙️ **Мой профиль**

Управление вашим профилем и настройками:

📝 **Редактировать профиль** - изменить личные данные
📊 **Моя статистика** - просмотр активности и анализов
🏆 **Достижения** - ваши успехи в приложении
⚙️ **Настройки** - уведомления и предпочтения

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=profile_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: CallbackQuery, user_service: UserService) -> None:
    """Show profile editing menu"""
    try:
        # Get user data from database
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден",
                reply_markup=back_to_profile_kb()
            )
            return
        
        # Get subscription info
        subscription = None
        if user.subscriptions:
            subscription = user.subscriptions[0]  # Get the latest subscription
        
        # Format gender display
        gender_display = "Не указан"
        if user.gender == "male":
            gender_display = "Мужской"
        elif user.gender == "female":
            gender_display = "Женский"
        elif user.gender:
            gender_display = user.gender.capitalize()
        
        # Format age group display
        age_display = user.age_group or "Не указана"
        
        # Format interests
        interests_text = "Не указаны"
        if user.interests_list:
            interests_text = ", ".join(user.interests_list)
        
        # Format goals
        goals_text = "Не указаны"
        if user.goals_list:
            goals_text = ", ".join(user.goals_list)
        
        profile_text = f"""📝 **Редактирование профиля**

👤 **Имя:** {user.display_name or 'Не указано'}
🚻 **Пол:** {gender_display}
🎂 **Возрастная группа:** {age_display}
💫 **Интересы:** {interests_text}
🎯 **Цели:** {goals_text}
📋 **О себе:** {user.bio or 'Не указано'}

💎 **Подписка:** {user.subscription_type}
📊 **Анализов выполнено:** {user.total_analyses}

Для изменения профиля используйте команду /start"""

        await callback.message.edit_text(
            profile_text,
            reply_markup=profile_edit_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in edit_profile: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке данных.\nДля изменения профиля воспользуйтесь командой /start.",
            reply_markup=back_to_profile_kb()
        )

@router.callback_query(F.data == "my_stats")
@handle_errors
async def my_stats(callback: CallbackQuery):
    """Show user statistics"""
    await callback.message.edit_text(
        "📊 **Моя статистика**\n\n"
        "📅 Дата регистрации: Сегодня\n"
        "📝 Количество анализов: 0\n"
        "👤 Созданных профилей: 0\n"
        "💕 Тестов совместимости: 0\n"
        "⭐ Рейтинг активности: Новичок\n\n"
        "Используйте бота больше для получения более детальной статистики!",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "achievements")
@handle_errors
async def achievements(callback: CallbackQuery):
    """Show user achievements"""
    await callback.message.edit_text(
        "🏆 **Достижения**\n\n"
        "🎉 **Добро пожаловать!** ✅\n"
        "*Зарегистрировались в PsychoDetective*\n\n"
        "🔒 **Первый анализ** ❌\n"
        "*Проведите первый анализ текста*\n\n"
        "🔒 **Знаток отношений** ❌\n"
        "*Пройдите 5 тестов совместимости*\n\n"
        "🔒 **Мастер профилей** ❌\n"
        "*Создайте 3 профиля партнеров*",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "settings")
@handle_errors
async def settings(callback: CallbackQuery):
    """Show user settings"""
    await callback.message.edit_text(
        "⚙️ **Настройки**\n\n"
        "🔔 **Уведомления:**\n"
        "✅ Ежедневные советы\n"
        "✅ Напоминания об анализах\n"
        "❌ Еженедельная статистика\n\n"
        "🌍 **Язык:** Русский\n"
        "⏰ **Часовой пояс:** UTC+3\n\n"
        "Для изменения настроек обратитесь в поддержку.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "subscription_menu")
@handle_errors
async def show_subscription_menu(callback: CallbackQuery):
    """Show subscription menu"""
    menu_text = """
💎 **Подписка**

Расширьте возможности анализа:

💎 **Premium** - больше анализов и возможностей
👑 **VIP** - безлимитные анализы и приоритет
💳 **Купить подписку** - выберите подходящий план
📋 **Моя подписка** - текущий статус

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=subscription_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "premium_info")
@handle_errors
async def premium_info(callback: CallbackQuery):
    """Show Premium subscription info"""
    await callback.message.edit_text(
        "💎 **Premium подписка**\n\n"
        "💰 **Цена:** 299₽/месяц\n\n"
        "✨ **Возможности:**\n"
        "• 50 анализов в месяц\n"
        "• Детальные отчеты\n"
        "• История анализов\n"
        "• Приоритетная поддержка\n"
        "• Дополнительные тесты\n\n"
        "🎯 Идеально для регулярного использования",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "vip_info")
@handle_errors
async def vip_info(callback: CallbackQuery):
    """Show VIP subscription info"""
    await callback.message.edit_text(
        "👑 **VIP подписка**\n\n"
        "💰 **Цена:** 599₽/месяц\n\n"
        "🌟 **Возможности:**\n"
        "• Безлимитные анализы\n"
        "• AI-консультации\n"
        "• Персональные рекомендации\n"
        "• Эксклюзивный контент\n"
        "• Приоритетная поддержка 24/7\n"
        "• Ранний доступ к новым функциям\n\n"
        "👑 Максимальный уровень сервиса",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "buy_subscription")
@handle_errors
async def buy_subscription(callback: CallbackQuery):
    """Handle subscription purchase"""
    await callback.message.edit_text(
        "💳 **Покупка подписки**\n\n"
        "Выберите способ оплаты:\n\n"
        "💎 **Premium** - 299₽/месяц\n"
        "👑 **VIP** - 599₽/месяц\n\n"
        "💳 Доступные способы оплаты:\n"
        "• Банковская карта\n"
        "• ЮMoney\n"
        "• СБП\n\n"
        "Функция оплаты будет доступна в ближайшее время.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "my_subscription")
@handle_errors
async def my_subscription(callback: CallbackQuery):
    """Show current subscription"""
    await callback.message.edit_text(
        "📋 **Моя подписка**\n\n"
        "📊 **Текущий план:** Free\n"
        "📅 **Дата активации:** -\n"
        "⏰ **Действует до:** -\n"
        "📈 **Использовано анализов:** 0/3\n\n"
        "💡 Обновите подписку для расширенных возможностей!",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("myprofile"))
async def my_profile(message: Message):
    """Handle user profile command"""
    await message.answer("👤 Функция управления профилем в разработке...") 