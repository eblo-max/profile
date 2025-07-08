"""Inline keyboards for bot interface"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional


def build_inline_kb(rows: List[List[tuple]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for row in rows:
        builder.row(*[InlineKeyboardButton(text=btn[0], callback_data=btn[1]) for btn in row])
    return builder.as_markup()


def main_menu_kb() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    return build_inline_kb([
        [("📝 Анализ текста", "analysis_menu"), ("👤 Профиль партнера", "profiler_menu")],
        [("💕 Совместимость", "compatibility_menu"), ("📅 Ежедневные советы", "daily_menu")],
        [("⚙️ Профиль", "profile_menu"), ("💎 Подписка", "subscription_menu")],
    ])


def analysis_menu_kb() -> InlineKeyboardMarkup:
    """Text analysis menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📱 Анализ переписки", callback_data="analyze_chat"),
        InlineKeyboardButton(text="💬 Анализ сообщения", callback_data="analyze_message")
    )
    builder.row(
        InlineKeyboardButton(text="📊 История анализов", callback_data="analysis_history")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def profiler_menu_kb() -> InlineKeyboardMarkup:
    """Partner profiler menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🆕 Новый профиль", callback_data="create_profile"),
        InlineKeyboardButton(text="📋 Мои профили", callback_data="my_profiles")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Рекомендации", callback_data="profile_recommendations")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def compatibility_menu_kb() -> InlineKeyboardMarkup:
    """Compatibility test menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🧪 Пройти тест", callback_data="start_compatibility"),
        InlineKeyboardButton(text="📊 Результаты тестов", callback_data="compatibility_results")
    )
    builder.row(
        InlineKeyboardButton(text="💑 Сравнить профили", callback_data="compare_profiles")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def daily_menu_kb() -> InlineKeyboardMarkup:
    """Daily content menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📖 Совет дня", callback_data="daily_tip"),
        InlineKeyboardButton(text="🎓 Урок дня", callback_data="daily_lesson")
    )
    builder.row(
        InlineKeyboardButton(text="💡 Упражнение дня", callback_data="daily_exercise")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Настройки уведомлений", callback_data="notification_settings")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def profile_menu_kb() -> InlineKeyboardMarkup:
    """User profile menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Редактировать профиль", callback_data="edit_profile"),
        InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def subscription_menu_kb() -> InlineKeyboardMarkup:
    """Subscription menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💎 Premium", callback_data="premium_info"),
        InlineKeyboardButton(text="👑 VIP", callback_data="vip_info")
    )
    builder.row(
        InlineKeyboardButton(text="💳 Купить подписку", callback_data="buy_subscription")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Моя подписка", callback_data="my_subscription")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def admin_menu_kb() -> InlineKeyboardMarkup:
    """Admin menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Контент", callback_data="admin_content"),
        InlineKeyboardButton(text="💰 Платежи", callback_data="admin_payments")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def confirmation_kb(action: str, data: str = "") -> InlineKeyboardMarkup:
    """Confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{data}"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}")
    )
    
    return builder.as_markup()


def back_to_main_kb() -> InlineKeyboardMarkup:
    """Back to main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def back_to_profile_kb() -> InlineKeyboardMarkup:
    """Back to profile menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu")
    )
    
    return builder.as_markup()


def profile_edit_kb() -> InlineKeyboardMarkup:
    """Profile editing menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✏️ Изменить данные", callback_data="start_profile_edit")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def skip_kb(callback_data: str) -> InlineKeyboardMarkup:
    """Skip button keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_{callback_data}")
    )
    
    return builder.as_markup()


def gender_kb() -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
        InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Не указывать", callback_data="gender_skip")
    )
    
    return builder.as_markup()


def age_group_kb() -> InlineKeyboardMarkup:
    """Age group selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="18-25", callback_data="age_18_25"),
        InlineKeyboardButton(text="26-35", callback_data="age_26_35")
    )
    builder.row(
        InlineKeyboardButton(text="36-45", callback_data="age_36_45"),
        InlineKeyboardButton(text="46+", callback_data="age_46_plus")
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Не указывать", callback_data="age_skip")
    )
    
    return builder.as_markup()


def relationship_status_kb() -> InlineKeyboardMarkup:
    """Relationship status keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💑 В отношениях", callback_data="status_relationship"),
        InlineKeyboardButton(text="💔 Не в отношениях", callback_data="status_single")
    )
    builder.row(
        InlineKeyboardButton(text="💍 Женат/замужем", callback_data="status_married"),
        InlineKeyboardButton(text="🤔 Сложно", callback_data="status_complicated")
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Не указывать", callback_data="status_skip")
    )
    
    return builder.as_markup()


def notification_settings_kb(notifications_enabled: bool = True) -> InlineKeyboardMarkup:
    """Notification settings keyboard"""
    builder = InlineKeyboardBuilder()
    
    status = "✅ Включены" if notifications_enabled else "❌ Выключены"
    action = "disable" if notifications_enabled else "enable"
    
    builder.row(
        InlineKeyboardButton(text=f"🔔 Уведомления: {status}", callback_data=f"notifications_{action}")
    )
    builder.row(
        InlineKeyboardButton(text="⏰ Время уведомлений", callback_data="notification_time")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def questionnaire_navigation_kb(current_step: int, total_steps: int, 
                               has_prev: bool = True, has_next: bool = True) -> InlineKeyboardMarkup:
    """Questionnaire navigation keyboard"""
    builder = InlineKeyboardBuilder()
    
    nav_buttons = []
    
    if has_prev and current_step > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"quest_prev_{current_step}")
        )
    
    if has_next and current_step < total_steps:
        nav_buttons.append(
            InlineKeyboardButton(text="Далее ➡️", callback_data=f"quest_next_{current_step}")
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Progress and menu buttons
    builder.row(
        InlineKeyboardButton(
            text=f"📊 {current_step}/{total_steps}",
            callback_data="quest_progress"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="💾 Сохранить и выйти", callback_data="quest_save"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def rating_kb(rating_type: str = "general") -> InlineKeyboardMarkup:
    """Rating keyboard (1-5 stars)"""
    builder = InlineKeyboardBuilder()
    
    stars = []
    for i in range(1, 6):
        stars.append(
            InlineKeyboardButton(
                text="⭐" * i,
                callback_data=f"rate_{rating_type}_{i}"
            )
        )
    
    # Split into rows of 2-3 buttons
    builder.row(stars[0], stars[1])
    builder.row(stars[2], stars[3])
    builder.row(stars[4])
    
    return builder.as_markup()


def subscription_plans_kb() -> InlineKeyboardMarkup:
    """Subscription plans keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💎 Premium - 1 месяц", callback_data="buy_premium_1"),
        InlineKeyboardButton(text="💎 Premium - 3 месяца", callback_data="buy_premium_3")
    )
    builder.row(
        InlineKeyboardButton(text="👑 VIP - 1 месяц", callback_data="buy_vip_1"),
        InlineKeyboardButton(text="👑 VIP - 3 месяца", callback_data="buy_vip_3")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Попробовать бесплатно", callback_data="trial_subscription")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def pagination_kb(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Pagination keyboard"""
    builder = InlineKeyboardBuilder()
    
    buttons = []
    
    # Previous page
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}_page_{current_page - 1}")
        )
    
    # Page info
    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="page_info"
        )
    )
    
    # Next page
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(text="➡️", callback_data=f"{prefix}_page_{current_page + 1}")
        )
    
    if buttons:
        builder.row(*buttons)
    
    return builder.as_markup()


def settings_menu_kb() -> InlineKeyboardMarkup:
    """Settings menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications"),
        InlineKeyboardButton(text="⏰ Время уведомлений", callback_data="settings_time")
    )
    builder.row(
        InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="settings_timezone"),
        InlineKeyboardButton(text="📊 Еженедельная статистика", callback_data="settings_weekly_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ Очистить данные", callback_data="settings_clear_data"),
        InlineKeyboardButton(text="📤 Экспорт данных", callback_data="settings_export_data")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def notification_settings_detailed_kb(user) -> InlineKeyboardMarkup:
    """Detailed notification settings keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Daily tips
    daily_status = "✅" if user.daily_tips_enabled else "❌"
    builder.row(
        InlineKeyboardButton(
            text=f"{daily_status} Ежедневные советы", 
            callback_data="toggle_daily_tips"
        )
    )
    
    # Analysis reminders  
    reminders_status = "✅" if user.analysis_reminders_enabled else "❌"
    builder.row(
        InlineKeyboardButton(
            text=f"{reminders_status} Напоминания об анализах", 
            callback_data="toggle_analysis_reminders"
        )
    )
    
    # Weekly stats
    weekly_status = "✅" if user.weekly_stats_enabled else "❌"
    builder.row(
        InlineKeyboardButton(
            text=f"{weekly_status} Еженедельная статистика", 
            callback_data="toggle_weekly_stats"
        )
    )
    
    # All notifications toggle
    all_status = "✅" if user.notifications_enabled else "❌"
    builder.row(
        InlineKeyboardButton(
            text=f"{all_status} Все уведомления", 
            callback_data="toggle_all_notifications"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def notification_time_kb(current_time: str = "09:00") -> InlineKeyboardMarkup:
    """Notification time selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    times = ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", 
             "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
             "19:00", "20:00", "21:00", "22:00"]
    
    # Show times in rows of 4
    for i in range(0, len(times), 4):
        row_times = times[i:i+4]
        buttons = []
        for time in row_times:
            emoji = "🔥" if time == current_time else "⏰"
            buttons.append(
                InlineKeyboardButton(
                    text=f"{emoji} {time}", 
                    callback_data=f"set_time_{time.replace(':', '_')}"
                )
            )
        builder.row(*buttons)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def timezone_kb(current_timezone: str = "Europe/Moscow") -> InlineKeyboardMarkup:
    """Timezone selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    timezones = [
        ("🇷🇺 Москва (UTC+3)", "Europe/Moscow"),
        ("🇷🇺 Екатеринбург (UTC+5)", "Asia/Yekaterinburg"),
        ("🇷🇺 Новосибирск (UTC+7)", "Asia/Novosibirsk"),
        ("🇷🇺 Владивосток (UTC+10)", "Asia/Vladivostok"),
        ("🇺🇦 Киев (UTC+2)", "Europe/Kiev"),
        ("🇰🇿 Алматы (UTC+6)", "Asia/Almaty"),
        ("🇺🇸 Нью-Йорк (UTC-5)", "America/New_York"),
        ("🇬🇧 Лондон (UTC+0)", "Europe/London"),
    ]
    
    for name, tz in timezones:
        emoji = "🔥" if tz == current_timezone else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {name}", 
                callback_data=f"set_timezone_{tz.replace('/', '_')}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def confirm_clear_data_kb() -> InlineKeyboardMarkup:
    """Confirm data clearing keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🗑️ Да, очистить", callback_data="confirm_clear_data"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="settings_menu")
    )
    
    return builder.as_markup()


def profile_edit_fields_kb() -> InlineKeyboardMarkup:
    """Profile editing fields selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Имя", callback_data="edit_field_name"),
        InlineKeyboardButton(text="🎂 Возрастная группа", callback_data="edit_field_age")
    )
    builder.row(
        InlineKeyboardButton(text="💫 Интересы", callback_data="edit_field_interests"),
        InlineKeyboardButton(text="🎯 Цели", callback_data="edit_field_goals")
    )
    builder.row(
        InlineKeyboardButton(text="📋 О себе", callback_data="edit_field_bio")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Сохранить изменения", callback_data="confirm_profile_save")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_profile_edit"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def confirm_profile_changes_kb() -> InlineKeyboardMarkup:
    """Confirm profile changes keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Сохранить изменения", callback_data="confirm_profile_changes"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_profile_edit")
    )
    
    return builder.as_markup()


def profile_edit_navigation_kb(can_edit: bool, days_until_edit: int = 0) -> InlineKeyboardMarkup:
    """Profile edit navigation with restriction info"""
    builder = InlineKeyboardBuilder()
    
    if can_edit:
        builder.row(
            InlineKeyboardButton(text="✏️ Изменить данные", callback_data="start_profile_edit")
        )
    else:
        remaining_text = f"🔒 Следующее редактирование через {days_until_edit} дн."
        builder.row(
            InlineKeyboardButton(text=remaining_text, callback_data="edit_restriction_info")
        )
    
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup() 