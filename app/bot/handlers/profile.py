"""User profile handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.utils.decorators import handle_errors
from app.bot.states import ProfileEditStates
from app.bot.keyboards.inline import (
    profile_menu_kb, subscription_menu_kb, back_to_main_kb, 
    profile_edit_kb, back_to_profile_kb, settings_menu_kb,
    notification_settings_detailed_kb, notification_time_kb,
    timezone_kb, confirm_clear_data_kb, profile_edit_fields_kb,
    confirm_profile_changes_kb, profile_edit_navigation_kb,
    age_group_kb, gender_kb
)
from app.services.user_service import UserService
from app.core.logging import logger
from app.core.database import get_session

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
    """Show profile editing menu with restriction info"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден. Используйте /start для регистрации.",
                reply_markup=back_to_main_kb()
            )
            return
        
        # Check if user can edit profile
        can_edit = user.can_edit_profile
        days_until_edit = user.days_until_next_edit
        
        # Format current profile data
        gender_display = "Не указан"
        if user.gender == "male":
            gender_display = "Мужской"
        elif user.gender == "female":
            gender_display = "Женский"
        elif user.gender:
            gender_display = user.gender.capitalize()
        
        age_display = user.age_group or "Не указана"
        
        interests_text = "Не указаны"
        if user.interests_list:
            interests_text = ", ".join(user.interests_list)
        
        goals_text = "Не указаны"
        if user.goals_list:
            goals_text = ", ".join(user.goals_list)
        
        # Create profile text with editing info
        if can_edit:
            edit_info = "✅ **Доступно редактирование профиля**\n\n"
        else:
            last_edit = user.last_profile_edit.strftime('%d.%m.%Y') if user.last_profile_edit else "Никогда"
            edit_info = f"""🔒 **Редактирование ограничено**

📅 **Последнее изменение:** {last_edit}
⏳ **Следующее редактирование через:** {days_until_edit} дн.

💡 *Редактирование профиля доступно раз в 30 дней*

"""
        
        profile_text = f"""📝 **Редактирование профиля**

{edit_info}👤 **Имя:** {user.display_name or 'Не указано'}
🚻 **Пол:** {gender_display}
🎂 **Возрастная группа:** {age_display}
💫 **Интересы:** {interests_text}
🎯 **Цели:** {goals_text}
📋 **О себе:** {user.bio or 'Не указано'}

💎 **Подписка:** {user.subscription_type}
📊 **Анализов выполнено:** {user.total_analyses}"""
        
        await callback.message.edit_text(
            profile_text,
            reply_markup=profile_edit_navigation_kb(can_edit, days_until_edit),
            parse_mode="Markdown"
        )
        await callback.answer()

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


# === Profile Editing Handlers ===

@router.callback_query(F.data == "start_profile_edit")
@handle_errors
async def start_profile_edit(callback: CallbackQuery, state: FSMContext):
    """Start profile editing process"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        if not user.can_edit_profile:
            days_until_edit = user.days_until_next_edit
            await callback.answer(
                f"🔒 Редактирование доступно через {days_until_edit} дн.",
                show_alert=True
            )
            return
        
        # Store current user data in state for editing
        await state.update_data(
            user_id=user.id,
            original_name=user.name,
            original_age_group=user.age_group,
            original_interests=user.interests,
            original_goals=user.goals,
            original_bio=user.bio,
            changes_made={}
        )
        
        await state.set_state(ProfileEditStates.select_field)
        
        edit_text = """✏️ **Редактирование профиля**

Выберите поле для изменения:

👤 **Имя** - ваше отображаемое имя
🎂 **Возрастная группа** - диапазон возраста  
💫 **Интересы** - ваши увлечения и хобби
🎯 **Цели** - что вы хотите получить от анализов
📋 **О себе** - краткое описание

💡 *Изменения будут сохранены только после подтверждения*"""
        
        await callback.message.edit_text(
            edit_text,
            reply_markup=profile_edit_fields_kb(),
            parse_mode="Markdown"
        )
        await callback.answer()


@router.callback_query(F.data == "edit_restriction_info")
@handle_errors
async def edit_restriction_info(callback: CallbackQuery):
    """Show information about edit restrictions"""
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        last_edit = user.last_profile_edit.strftime('%d.%m.%Y') if user.last_profile_edit else "Никогда"
        days_until_edit = user.days_until_next_edit
        
        info_text = f"""🔒 **Информация об ограничениях**

📅 **Последнее редактирование:** {last_edit}
⏳ **До следующего редактирования:** {days_until_edit} дн.

🔐 **Почему есть ограничение?**
• Предотвращение злоупотреблений
• Стабильность анализов
• Качество рекомендаций

💎 **Премиум подписчики могут редактировать чаще!**

Хотите изменить подписку?"""
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="💎 Подписка", callback_data="subscription_menu")
        )
        builder.row(
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        
        await callback.message.edit_text(
            info_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
        await callback.answer()


@router.callback_query(F.data == "edit_field_name", ProfileEditStates.select_field)
@handle_errors
async def edit_field_name(callback: CallbackQuery, state: FSMContext):
    """Start editing user name"""
    data = await state.get_data()
    current_name = data.get('original_name', 'Не указано')
    
    await state.set_state(ProfileEditStates.waiting_for_name)
    
    name_text = f"""👤 **Изменение имени**

📝 **Текущее имя:** {current_name}

✏️ Введите новое имя (от 2 до 50 символов):

💡 *Это имя будет отображаться в вашем профиле и анализах*"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_profile_edit")
    )
    
    await callback.message.edit_text(
        name_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ProfileEditStates.waiting_for_name)
@handle_errors
async def process_new_name(message: Message, state: FSMContext):
    """Process new name input"""
    new_name = message.text.strip()
    
    # Validate name
    if len(new_name) < 2 or len(new_name) > 50:
        await message.answer(
            "❌ Имя должно содержать от 2 до 50 символов. Попробуйте ещё раз:",
            parse_mode="Markdown"
        )
        return
    
    # Update state data
    data = await state.get_data()
    data['changes_made']['name'] = new_name
    await state.update_data(changes_made=data['changes_made'])
    
    await state.set_state(ProfileEditStates.select_field)
    
    success_text = f"""✅ **Имя изменено**

👤 **Новое имя:** {new_name}

Выберите следующее поле для изменения или сохраните изменения:"""
    
    await message.answer(
        success_text,
        reply_markup=profile_edit_fields_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "edit_field_age", ProfileEditStates.select_field)
@handle_errors
async def edit_field_age(callback: CallbackQuery, state: FSMContext):
    """Start editing age group"""
    data = await state.get_data()
    current_age = data.get('original_age_group', 'Не указана')
    
    await state.set_state(ProfileEditStates.waiting_for_age)
    
    age_text = f"""🎂 **Изменение возрастной группы**

📊 **Текущая группа:** {current_age}

Выберите новую возрастную группу:"""
    
    await callback.message.edit_text(
        age_text,
        reply_markup=age_group_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("age_"), ProfileEditStates.waiting_for_age)
@handle_errors
async def process_new_age(callback: CallbackQuery, state: FSMContext):
    """Process new age group selection"""
    age_mapping = {
        "age_18_25": "18-25",
        "age_26_35": "26-35", 
        "age_36_45": "36-45",
        "age_46_plus": "46+",
        "age_skip": None
    }
    
    new_age = age_mapping.get(callback.data, None)
    
    # Update state data
    data = await state.get_data()
    data['changes_made']['age_group'] = new_age
    await state.update_data(changes_made=data['changes_made'])
    
    await state.set_state(ProfileEditStates.select_field)
    
    age_display = new_age or "Не указана"
    success_text = f"""✅ **Возрастная группа изменена**

🎂 **Новая группа:** {age_display}

Выберите следующее поле для изменения или сохраните изменения:"""
    
    await callback.message.edit_text(
        success_text,
        reply_markup=profile_edit_fields_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "edit_field_interests", ProfileEditStates.select_field)
@handle_errors
async def edit_field_interests(callback: CallbackQuery, state: FSMContext):
    """Start editing interests"""
    data = await state.get_data()
    
    # Parse current interests
    try:
        import json
        current_interests = json.loads(data.get('original_interests', '[]')) if data.get('original_interests') else []
    except:
        current_interests = []
    
    current_text = ", ".join(current_interests) if current_interests else "Не указаны"
    
    await state.set_state(ProfileEditStates.waiting_for_interests)
    
    interests_text = f"""💫 **Изменение интересов**

🎯 **Текущие интересы:** {current_text}

✏️ Введите новые интересы через запятую:

📝 **Примеры:** музыка, спорт, путешествия, книги, готовка

💡 *Интересы помогают создавать более точные анализы*"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_profile_edit")
    )
    
    await callback.message.edit_text(
        interests_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ProfileEditStates.waiting_for_interests)
@handle_errors
async def process_new_interests(message: Message, state: FSMContext):
    """Process new interests input"""
    import json
    
    interests_text = message.text.strip()
    
    if not interests_text:
        new_interests = []
    else:
        # Parse interests from comma-separated text
        new_interests = [interest.strip() for interest in interests_text.split(',')]
        new_interests = [interest for interest in new_interests if interest]  # Remove empty
        
        if len(new_interests) > 10:
            await message.answer(
                "❌ Максимум 10 интересов. Попробуйте ещё раз:",
                parse_mode="Markdown"
            )
            return
    
    # Convert to JSON for storage
    interests_json = json.dumps(new_interests, ensure_ascii=False)
    
    # Update state data
    data = await state.get_data()
    data['changes_made']['interests'] = interests_json
    await state.update_data(changes_made=data['changes_made'])
    
    await state.set_state(ProfileEditStates.select_field)
    
    interests_display = ", ".join(new_interests) if new_interests else "Не указаны"
    success_text = f"""✅ **Интересы изменены**

💫 **Новые интересы:** {interests_display}

Выберите следующее поле для изменения или сохраните изменения:"""
    
    await message.answer(
        success_text,
        reply_markup=profile_edit_fields_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "edit_field_goals", ProfileEditStates.select_field)
@handle_errors
async def edit_field_goals(callback: CallbackQuery, state: FSMContext):
    """Start editing goals"""
    data = await state.get_data()
    
    # Parse current goals
    try:
        import json
        current_goals = json.loads(data.get('original_goals', '[]')) if data.get('original_goals') else []
    except:
        current_goals = []
    
    current_text = ", ".join(current_goals) if current_goals else "Не указаны"
    
    await state.set_state(ProfileEditStates.waiting_for_goals)
    
    goals_text = f"""🎯 **Изменение целей**

🎲 **Текущие цели:** {current_text}

✏️ Введите новые цели через запятую:

📝 **Примеры:** улучшить отношения, понять себя, развить эмпатию

💡 *Цели помогают персонализировать рекомендации*"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_profile_edit")
    )
    
    await callback.message.edit_text(
        goals_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ProfileEditStates.waiting_for_goals)
@handle_errors
async def process_new_goals(message: Message, state: FSMContext):
    """Process new goals input"""
    import json
    
    goals_text = message.text.strip()
    
    if not goals_text:
        new_goals = []
    else:
        # Parse goals from comma-separated text
        new_goals = [goal.strip() for goal in goals_text.split(',')]
        new_goals = [goal for goal in new_goals if goal]  # Remove empty
        
        if len(new_goals) > 10:
            await message.answer(
                "❌ Максимум 10 целей. Попробуйте ещё раз:",
                parse_mode="Markdown"
            )
            return
    
    # Convert to JSON for storage
    goals_json = json.dumps(new_goals, ensure_ascii=False)
    
    # Update state data
    data = await state.get_data()
    data['changes_made']['goals'] = goals_json
    await state.update_data(changes_made=data['changes_made'])
    
    await state.set_state(ProfileEditStates.select_field)
    
    goals_display = ", ".join(new_goals) if new_goals else "Не указаны"
    success_text = f"""✅ **Цели изменены**

🎯 **Новые цели:** {goals_display}

Выберите следующее поле для изменения или сохраните изменения:"""
    
    await message.answer(
        success_text,
        reply_markup=profile_edit_fields_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "edit_field_bio", ProfileEditStates.select_field)
@handle_errors
async def edit_field_bio(callback: CallbackQuery, state: FSMContext):
    """Start editing bio"""
    data = await state.get_data()
    current_bio = data.get('original_bio', 'Не указано')
    
    await state.set_state(ProfileEditStates.waiting_for_bio)
    
    bio_text = f"""📋 **Изменение описания "О себе"**

📝 **Текущее описание:** {current_bio}

✏️ Введите новое описание (до 500 символов):

💡 *Опишите себя, свой характер, особенности*"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_profile_edit")
    )
    
    await callback.message.edit_text(
        bio_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ProfileEditStates.waiting_for_bio)
@handle_errors
async def process_new_bio(message: Message, state: FSMContext):
    """Process new bio input"""
    new_bio = message.text.strip()
    
    # Validate bio length
    if len(new_bio) > 500:
        await message.answer(
            "❌ Описание не должно превышать 500 символов. Попробуйте ещё раз:",
            parse_mode="Markdown"
        )
        return
    
    # Update state data
    data = await state.get_data()
    data['changes_made']['bio'] = new_bio if new_bio else None
    await state.update_data(changes_made=data['changes_made'])
    
    await state.set_state(ProfileEditStates.select_field)
    
    bio_display = new_bio if new_bio else "Не указано"
    success_text = f"""✅ **Описание изменено**

📋 **Новое описание:** {bio_display}

Выберите следующее поле для изменения или сохраните изменения:"""
    
    await message.answer(
        success_text,
        reply_markup=profile_edit_fields_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "confirm_profile_save")
@handle_errors
async def confirm_profile_save(callback: CallbackQuery, state: FSMContext):
    """Show confirmation before saving changes"""
    data = await state.get_data()
    changes = data.get('changes_made', {})
    
    if not changes:
        await callback.answer("❌ Нет изменений для сохранения", show_alert=True)
        return
    
    await state.set_state(ProfileEditStates.confirming_changes)
    
    # Build changes summary
    changes_text = "📝 **Подтверждение изменений**\n\n"
    changes_text += "🔄 **Будут изменены:**\n\n"
    
    for field, value in changes.items():
        if field == 'name':
            changes_text += f"👤 **Имя:** {value}\n"
        elif field == 'age_group':
            changes_text += f"🎂 **Возрастная группа:** {value or 'Не указана'}\n"
        elif field == 'interests':
            try:
                import json
                interests_list = json.loads(value) if value else []
                interests_display = ", ".join(interests_list) if interests_list else "Не указаны"
                changes_text += f"💫 **Интересы:** {interests_display}\n"
            except:
                changes_text += f"💫 **Интересы:** Не указаны\n"
        elif field == 'goals':
            try:
                import json
                goals_list = json.loads(value) if value else []
                goals_display = ", ".join(goals_list) if goals_list else "Не указаны"
                changes_text += f"🎯 **Цели:** {goals_display}\n"
            except:
                changes_text += f"🎯 **Цели:** Не указаны\n"
        elif field == 'bio':
            changes_text += f"📋 **О себе:** {value or 'Не указано'}\n"
    
    changes_text += "\n⚠️ **Внимание:** Следующее редактирование будет доступно через 30 дней!\n\n"
    changes_text += "Сохранить изменения?"
    
    # Only edit if the content differs from current message
    current_text = callback.message.text
    if current_text != changes_text:
        await callback.message.edit_text(
            changes_text,
            reply_markup=confirm_profile_changes_kb(),
            parse_mode="Markdown"
        )
        await callback.answer()
    else:
        # If content is the same, just answer callback
        await callback.answer("Подтвердите сохранение")


@router.callback_query(F.data == "confirm_profile_save", ProfileEditStates.confirming_changes)
@handle_errors
async def save_profile_changes(callback: CallbackQuery, state: FSMContext):
    """Save the profile changes to database"""
    data = await state.get_data()
    changes = data.get('changes_made', {})
    user_id = data.get('user_id')
    
    if not changes or not user_id:
        await callback.answer("❌ Ошибка при сохранении", show_alert=True)
        await state.clear()
        return
    
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_id(user_id)
        
        if not user or not user.can_edit_profile:
            await callback.answer("❌ Редактирование недоступно", show_alert=True)
            await state.clear()
            return
        
        try:
            # Apply changes
            for field, value in changes.items():
                if field == 'name':
                    user.name = value
                elif field == 'age_group':
                    user.age_group = value
                elif field == 'interests':
                    user.interests = value
                elif field == 'goals':
                    user.goals = value
                elif field == 'bio':
                    user.bio = value
            
            # Update last edit time
            user.update_profile_edit_time()
            
            await session.commit()
            
            await state.clear()
            
            success_text = """✅ **Профиль успешно обновлён!**

🎉 Изменения сохранены
📅 Следующее редактирование будет доступно через 30 дней

Обновлённые данные будут учтены в следующих анализах."""
            
            # Always edit to success message since it's different content
            await callback.message.edit_text(
                success_text,
                reply_markup=back_to_main_kb(),
                parse_mode="Markdown"
            )
            await callback.answer("✅ Профиль обновлён!", show_alert=True)
            
        except Exception as e:
            logger.error(f"Error saving profile changes: {e}")
            await callback.answer("❌ Ошибка при сохранении", show_alert=True)


@router.callback_query(F.data == "cancel_profile_edit")
@handle_errors
async def cancel_profile_edit(callback: CallbackQuery, state: FSMContext):
    """Cancel profile editing"""
    await state.clear()
    
    cancel_text = """❌ **Редактирование отменено**

Изменения не сохранены.

Вы можете вернуться к редактированию в любое время."""
    
    await callback.message.edit_text(
        cancel_text,
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer("❌ Редактирование отменено") 