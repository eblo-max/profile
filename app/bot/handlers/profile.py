"""User profile handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.decorators import handle_errors
from app.bot.keyboards.inline import (
    profile_menu_kb, subscription_menu_kb, back_to_main_kb, 
    profile_edit_kb, back_to_profile_kb, settings_menu_kb,
    notification_settings_detailed_kb, notification_time_kb,
    timezone_kb, confirm_clear_data_kb
)
from app.services.user_service import UserService
from app.core.logging import logger
from app.core.database import get_session
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

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
@handle_errors
async def edit_profile(callback: CallbackQuery) -> None:
    """Show profile editing menu"""
    try:
        async with get_session() as session:
            user_service = UserService(session)
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
            await callback.answer()
        
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
async def settings_menu(callback: CallbackQuery):
    """Show interactive settings menu"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден. Используйте /start для регистрации.",
                reply_markup=back_to_main_kb()
            )
            return
        
        settings_text = f"""⚙️ **Настройки профиля**

👤 **Пользователь:** {user.display_name}
💎 **Подписка:** {user.subscription_type}

🔔 **Уведомления:** {"✅ Включены" if user.notifications_enabled else "❌ Выключены"}
⏰ **Время уведомлений:** {user.notification_time}
🌍 **Часовой пояс:** {user.timezone}

📊 **Статистика анализов:** {user.total_analyses}
📅 **Дата регистрации:** {user.registration_date.strftime('%d.%m.%Y')}

Выберите что хотите настроить:"""
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=settings_menu_kb(),
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


# === Settings Handlers ===

@router.callback_query(F.data == "settings_menu")
@handle_errors
async def back_to_settings_menu(callback: CallbackQuery):
    """Return to settings menu"""
    await settings_menu(callback)


@router.callback_query(F.data == "settings_notifications")
@handle_errors
async def notification_settings(callback: CallbackQuery):
    """Show detailed notification settings"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        settings_text = f"""🔔 **Настройки уведомлений**

📱 **Текущие настройки:**

✅ **Ежедневные советы:** {"Включены" if user.daily_tips_enabled else "Выключены"}
📝 **Напоминания об анализах:** {"Включены" if user.analysis_reminders_enabled else "Выключены"}  
📊 **Еженедельная статистика:** {"Включена" if user.weekly_stats_enabled else "Выключена"}

🔔 **Все уведомления:** {"Включены" if user.notifications_enabled else "Выключены"}

⏰ **Время:** {user.notification_time}
🌍 **Часовой пояс:** {user.timezone}

Нажмите на настройку для изменения:"""
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=notification_settings_detailed_kb(user),
            parse_mode="Markdown"
        )
        await callback.answer()


@router.callback_query(F.data == "toggle_daily_tips")
@handle_errors
async def toggle_daily_tips(callback: CallbackQuery):
    """Toggle daily tips setting"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Toggle setting
        user.daily_tips_enabled = not user.daily_tips_enabled
        await session.commit()
        
        status = "включены" if user.daily_tips_enabled else "выключены"
        await callback.answer(f"🔔 Ежедневные советы {status}", show_alert=True)
        
        # Refresh the settings page
        await notification_settings(callback)


@router.callback_query(F.data == "toggle_analysis_reminders")
@handle_errors
async def toggle_analysis_reminders(callback: CallbackQuery):
    """Toggle analysis reminders setting"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Toggle setting
        user.analysis_reminders_enabled = not user.analysis_reminders_enabled
        await session.commit()
        
        status = "включены" if user.analysis_reminders_enabled else "выключены"
        await callback.answer(f"📝 Напоминания об анализах {status}", show_alert=True)
        
        # Refresh the settings page
        await notification_settings(callback)


@router.callback_query(F.data == "toggle_weekly_stats")
@handle_errors
async def toggle_weekly_stats(callback: CallbackQuery):
    """Toggle weekly stats setting"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Toggle setting
        user.weekly_stats_enabled = not user.weekly_stats_enabled
        await session.commit()
        
        status = "включена" if user.weekly_stats_enabled else "выключена"
        await callback.answer(f"📊 Еженедельная статистика {status}", show_alert=True)
        
        # Refresh the settings page
        await notification_settings(callback)


@router.callback_query(F.data == "toggle_all_notifications")
@handle_errors
async def toggle_all_notifications(callback: CallbackQuery):
    """Toggle all notifications setting"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Toggle setting
        user.notifications_enabled = not user.notifications_enabled
        await session.commit()
        
        status = "включены" if user.notifications_enabled else "выключены"
        await callback.answer(f"🔔 Все уведомления {status}", show_alert=True)
        
        # Refresh the settings page
        await notification_settings(callback)


@router.callback_query(F.data == "settings_time")
@handle_errors
async def notification_time_settings(callback: CallbackQuery):
    """Show notification time settings"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        time_text = f"""⏰ **Время уведомлений**

🕘 **Текущее время:** {user.notification_time}
🌍 **Часовой пояс:** {user.timezone}

📱 В это время вы будете получать:
• Ежедневные советы
• Напоминания о проведении анализов
• Еженедельную статистику

Выберите удобное время:"""
        
        await callback.message.edit_text(
            time_text,
            reply_markup=notification_time_kb(user.notification_time),
            parse_mode="Markdown"
        )
        await callback.answer()


@router.callback_query(F.data.startswith("set_time_"))
@handle_errors
async def set_notification_time(callback: CallbackQuery):
    """Set notification time"""
    time_str = callback.data.replace("set_time_", "").replace("_", ":")
    
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Update time
        user.notification_time = time_str
        await session.commit()
        
        await callback.answer(f"⏰ Время уведомлений установлено: {time_str}", show_alert=True)
        
        # Refresh the time settings page
        await notification_time_settings(callback)


@router.callback_query(F.data == "settings_timezone")
@handle_errors
async def timezone_settings(callback: CallbackQuery):
    """Show timezone settings"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        timezone_text = f"""🌍 **Часовой пояс**

🕘 **Текущий часовой пояс:** {user.timezone}
⏰ **Время уведомлений:** {user.notification_time}

📍 Выберите ваш часовой пояс для корректного времени уведомлений:"""
        
        await callback.message.edit_text(
            timezone_text,
            reply_markup=timezone_kb(user.timezone),
            parse_mode="Markdown"
        )
        await callback.answer()


@router.callback_query(F.data.startswith("set_timezone_"))
@handle_errors
async def set_timezone(callback: CallbackQuery):
    """Set user timezone"""
    timezone_str = callback.data.replace("set_timezone_", "").replace("_", "/")
    
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Update timezone
        user.timezone = timezone_str
        await session.commit()
        
        await callback.answer(f"🌍 Часовой пояс установлен: {timezone_str}", show_alert=True)
        
        # Refresh the timezone settings page
        await timezone_settings(callback)


@router.callback_query(F.data == "settings_weekly_stats")
@handle_errors
async def weekly_stats_settings(callback: CallbackQuery):
    """Show weekly stats settings"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        status = "включена" if user.weekly_stats_enabled else "выключена"
        
        stats_text = f"""📊 **Еженедельная статистика**

📈 **Статус:** {status.capitalize()}

📅 **Что включает еженедельная статистика:**
• Количество проведённых анализов
• Наиболее частые темы анализа
• Динамика вашей активности
• Персональные рекомендации

📨 Статистика отправляется каждый понедельник в {user.notification_time}"""
        
        toggle_status = "❌ Отключить" if user.weekly_stats_enabled else "✅ Включить"
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=toggle_status, callback_data="toggle_weekly_stats")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="settings_menu"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
        await callback.answer()


@router.callback_query(F.data == "settings_clear_data")
@handle_errors
async def clear_data_warning(callback: CallbackQuery):
    """Show data clearing warning"""
    warning_text = """🗑️ **Очистка данных**

⚠️ **ВНИМАНИЕ!** Эта операция необратима.

🗂️ **Будут удалены:**
• Все ваши анализы текстов
• История профилей партнёров
• Результаты тестов совместимости
• Пользовательская статистика
• Настройки (кроме основных)

💾 **НЕ будут удалены:**
• Основной профиль (имя, возраст, пол)
• Тип подписки
• Дата регистрации

❓ **Вы действительно хотите очистить все данные?**"""
    
    await callback.message.edit_text(
        warning_text,
        reply_markup=confirm_clear_data_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear_data")
@handle_errors
async def confirm_clear_data(callback: CallbackQuery):
    """Clear user data"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        try:
            # Clear user data but keep basic profile
            user.analyses_count = 0
            user.total_analyses = 0
            user.last_analysis_date = None
            user.notes = None
            
            # Reset notification settings to defaults
            user.notifications_enabled = True
            user.daily_tips_enabled = True
            user.analysis_reminders_enabled = True
            user.weekly_stats_enabled = False
            user.notification_time = "09:00"
            user.timezone = "Europe/Moscow"
            
            await session.commit()
            
            success_text = """✅ **Данные успешно очищены**

🗂️ **Удалено:**
• Статистика анализов
• Пользовательские заметки
• Настройки уведомлений сброшены

👤 **Ваш основной профиль сохранён**

Вы можете продолжить использование бота."""
            
            await callback.message.edit_text(
                success_text,
                reply_markup=back_to_main_kb(),
                parse_mode="Markdown"
            )
            await callback.answer("🗑️ Данные очищены", show_alert=True)
            
        except Exception as e:
            logger.error(f"Error clearing user data: {e}")
            await callback.answer("❌ Ошибка при очистке данных", show_alert=True)


@router.callback_query(F.data == "settings_export_data")
@handle_errors
async def export_data(callback: CallbackQuery):
    """Export user data"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Generate data export
        export_data = f"""📤 **Экспорт ваших данных**

👤 **Профиль:**
• Имя: {user.display_name}
• Пол: {user.gender or 'Не указан'}
• Возрастная группа: {user.age_group or 'Не указана'}
• Тип подписки: {user.subscription_type}

📊 **Статистика:**
• Дата регистрации: {user.registration_date.strftime('%d.%m.%Y %H:%M')}
• Всего анализов: {user.total_analyses}
• Анализов в этом месяце: {user.analyses_count}
• Последний анализ: {user.last_analysis_date.strftime('%d.%m.%Y %H:%M') if user.last_analysis_date else 'Нет'}

⚙️ **Настройки:**
• Уведомления: {'Включены' if user.notifications_enabled else 'Выключены'}
• Ежедневные советы: {'Включены' if user.daily_tips_enabled else 'Выключены'}
• Напоминания: {'Включены' if user.analysis_reminders_enabled else 'Выключены'}
• Еженедельная статистика: {'Включена' if user.weekly_stats_enabled else 'Выключена'}
• Время уведомлений: {user.notification_time}
• Часовой пояс: {user.timezone}

📋 Полный экспорт данных в файле скоро будет доступен."""
        
        await callback.message.edit_text(
            export_data,
            reply_markup=back_to_main_kb(),
            parse_mode="Markdown"
        )
        await callback.answer() 