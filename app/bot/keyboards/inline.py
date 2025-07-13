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
        InlineKeyboardButton(text="Новый профиль", callback_data="create_profile"),
        InlineKeyboardButton(text="Мои профили", callback_data="my_profiles")
    )
    builder.row(
        InlineKeyboardButton(text="Рекомендации", callback_data="profile_recommendations")
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


def profiler_full_navigation_kb(
    current_state: str, 
    current_num: int, 
    total_questions: int,
    block_name: str = "",
    can_skip: bool = False
) -> InlineKeyboardMarkup:
    """Advanced navigation for full profiler questionnaire"""
    builder = InlineKeyboardBuilder()
    
    # Visual progress bar
    progress_filled = int((current_num / total_questions) * 10)
    progress_bar = "█" * progress_filled + "░" * (10 - progress_filled)
    
    # Answer buttons will be added in the handler, this is just navigation
    
    # Navigation row
    nav_buttons = []
    
    # Previous button (except for first question)
    if current_num > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prof_prev_{current_state}")
        )
    
    # Progress indicator with visual bar
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"📊 {current_num}/{total_questions}", 
            callback_data="prof_progress_info"
        )
    )
    
    # Skip button for non-critical questions
    if can_skip:
        nav_buttons.append(
            InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"prof_skip_{current_state}")
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Block progress info
    if block_name:
        builder.row(
            InlineKeyboardButton(
                text=f"📋 Блок: {block_name}", 
                callback_data="prof_block_info"
            )
        )
    
    # Quick actions
    actions_row = []
    actions_row.append(
        InlineKeyboardButton(text="💾 Сохранить", callback_data="prof_save_progress")
    )
    actions_row.append(
        InlineKeyboardButton(text="❌ Выход", callback_data="prof_exit_confirm")
    )
    
    builder.row(*actions_row)
    
    return builder.as_markup()


def profiler_results_navigation_kb(
    urgency_level: str,
    has_safety_alerts: bool = False,
    overall_risk: float = 0.0
) -> InlineKeyboardMarkup:
    """Advanced results navigation with risk-based options"""
    builder = InlineKeyboardBuilder()
    
    # Main analysis options
    builder.row(
        InlineKeyboardButton(text="📊 Полный анализ", callback_data="prof_detailed_analysis"),
        InlineKeyboardButton(text="💡 Рекомендации", callback_data="prof_recommendations")
    )
    
    # Risk-specific options
    if urgency_level in ["HIGH", "CRITICAL"] or has_safety_alerts:
        builder.row(
            InlineKeyboardButton(text="🚨 План безопасности", callback_data="prof_safety_plan"),
            InlineKeyboardButton(text="📞 Экстренная помощь", callback_data="prof_emergency_help")
        )
    
    # Additional analysis
    builder.row(
        InlineKeyboardButton(text="🔍 Анализ по блокам", callback_data="prof_block_analysis"),
        InlineKeyboardButton(text="📈 Динамика рисков", callback_data="prof_risk_trends")
    )
    
    # Export and sharing
    builder.row(
        InlineKeyboardButton(text="📄 PDF отчет", callback_data="prof_generate_pdf"),
        InlineKeyboardButton(text="📋 Краткий отчет", callback_data="prof_brief_report")
    )
    
    if overall_risk < 70:  # Only for lower risk profiles
        builder.row(
            InlineKeyboardButton(text="📤 Поделиться", callback_data="prof_share_results")
        )
    
    # Profile management
    builder.row(
        InlineKeyboardButton(text="💾 Сохранить профиль", callback_data="prof_save_profile"),
        InlineKeyboardButton(text="🔄 Пройти заново", callback_data="prof_restart")
    )
    
    # Navigation
    builder.row(
        InlineKeyboardButton(text="📋 Мои профили", callback_data="prof_my_profiles"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def profiler_block_analysis_kb(
    block_scores: dict,
    current_block: str = ""
) -> InlineKeyboardMarkup:
    """Navigation for detailed block analysis"""
    builder = InlineKeyboardBuilder()
    
    # Block navigation buttons with risk indicators
    block_info = {
        "narcissism": {"name": "🧠 Нарциссизм", "emoji": "🧠"},
        "control": {"name": "🎯 Контроль", "emoji": "🎯"},
        "gaslighting": {"name": "🔄 Газлайтинг", "emoji": "🔄"},
        "emotion": {"name": "💭 Эмоции", "emoji": "💭"},
        "intimacy": {"name": "💕 Интимность", "emoji": "💕"},
        "social": {"name": "👥 Социальное", "emoji": "👥"}
    }
    
    # Create rows of block buttons
    block_buttons = []
    for block_key, info in block_info.items():
        score = block_scores.get(block_key, 0)
        risk_indicator = "🔴" if score >= 7 else "🟡" if score >= 4 else "🟢"
        
        # Highlight current block
        if block_key == current_block:
            text = f"▶️ {info['name']} {risk_indicator}"
        else:
            text = f"{info['emoji']} {info['name']} {risk_indicator}"
        
        block_buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=f"prof_view_block_{block_key}"
            )
        )
    
    # Arrange in rows of 2
    for i in range(0, len(block_buttons), 2):
        row_buttons = block_buttons[i:i+2]
        builder.row(*row_buttons)
    
    # Summary and comparison
    builder.row(
        InlineKeyboardButton(text="📊 Общая сводка", callback_data="prof_blocks_summary"),
        InlineKeyboardButton(text="⚖️ Сравнение блоков", callback_data="prof_blocks_compare")
    )
    
    # Navigation
    builder.row(
        InlineKeyboardButton(text="⬅️ К результатам", callback_data="prof_back_to_results"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def profiler_safety_plan_kb(urgency_level: str) -> InlineKeyboardMarkup:
    """Safety plan navigation based on urgency level"""
    builder = InlineKeyboardBuilder()
    
    # Emergency contacts (always visible)
    builder.row(
        InlineKeyboardButton(text="🚨 Служба 112", url="tel:112"),
        InlineKeyboardButton(text="☎️ Горячая линия", url="tel:88007000600")
    )
    
    if urgency_level == "CRITICAL":
        # Critical situation options
        builder.row(
            InlineKeyboardButton(text="🏃‍♀️ План эвакуации", callback_data="prof_evacuation_plan"),
            InlineKeyboardButton(text="📋 Документы", callback_data="prof_emergency_docs")
        )
        builder.row(
            InlineKeyboardButton(text="🏠 Безопасные места", callback_data="prof_safe_places"),
            InlineKeyboardButton(text="👥 Сеть поддержки", callback_data="prof_support_network")
        )
    
    elif urgency_level == "HIGH":
        # High risk options
        builder.row(
            InlineKeyboardButton(text="🛡️ Границы безопасности", callback_data="prof_safety_boundaries"),
            InlineKeyboardButton(text="📱 Приложения помощи", callback_data="prof_safety_apps")
        )
        builder.row(
            InlineKeyboardButton(text="💬 Коды безопасности", callback_data="prof_safety_codes"),
            InlineKeyboardButton(text="🗂️ Документирование", callback_data="prof_incident_docs")
        )
    
    # Professional help
    builder.row(
        InlineKeyboardButton(text="👨‍⚕️ Психолог", callback_data="prof_find_therapist"),
        InlineKeyboardButton(text="⚖️ Юридическая помощь", callback_data="prof_legal_help")
    )
    
    # Self-care and resources
    builder.row(
        InlineKeyboardButton(text="🧘‍♀️ Техники выживания", callback_data="prof_coping_techniques"),
        InlineKeyboardButton(text="📚 Ресурсы", callback_data="prof_safety_resources")
    )
    
    # Navigation
    builder.row(
        InlineKeyboardButton(text="⬅️ К результатам", callback_data="prof_back_to_results"),
        InlineKeyboardButton(text="💡 Рекомендации", callback_data="prof_recommendations")
    )
    
    return builder.as_markup()


def profiler_my_profiles_kb(profiles_count: int = 0) -> InlineKeyboardMarkup:
    """My profiles management keyboard"""
    builder = InlineKeyboardBuilder()
    
    if profiles_count > 0:
        # Profile management options
        builder.row(
            InlineKeyboardButton(text="📋 Список профилей", callback_data="prof_list_profiles"),
            InlineKeyboardButton(text="🔍 Поиск профиля", callback_data="prof_search_profiles")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Сравнить профили", callback_data="prof_compare_profiles"),
            InlineKeyboardButton(text="📈 История изменений", callback_data="prof_profile_history")
        )
        builder.row(
            InlineKeyboardButton(text="📤 Экспорт данных", callback_data="prof_export_profiles"),
            InlineKeyboardButton(text="🗑️ Удалить профиль", callback_data="prof_delete_profile")
        )
    else:
        # No profiles yet
        builder.row(
            InlineKeyboardButton(text="📝 Создать первый профиль", callback_data="create_profile")
        )
    
    # Always available options
    builder.row(
        InlineKeyboardButton(text="➕ Новый профиль", callback_data="create_profile"),
        InlineKeyboardButton(text="📚 Гайд по профилям", callback_data="prof_profile_guide")
    )
    
    builder.row(
        InlineKeyboardButton(text="👤 Профайлер", callback_data="profiler_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def profiler_confirmation_kb(action: str, data: str = "") -> InlineKeyboardMarkup:
    """Confirmation dialogs for profiler actions"""
    builder = InlineKeyboardBuilder()
    
    if action == "exit":
        builder.row(
            InlineKeyboardButton(text="✅ Сохранить и выйти", callback_data="prof_save_and_exit"),
            InlineKeyboardButton(text="❌ Выйти без сохранения", callback_data="prof_exit_no_save")
        )
        builder.row(
            InlineKeyboardButton(text="↩️ Продолжить анкету", callback_data="prof_continue")
        )
    
    elif action == "restart":
        builder.row(
            InlineKeyboardButton(text="🔄 Да, начать заново", callback_data="prof_confirm_restart"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="prof_back_to_results")
        )
    
    elif action == "delete_profile":
        builder.row(
            InlineKeyboardButton(text="🗑️ Удалить навсегда", callback_data=f"prof_confirm_delete_{data}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="prof_my_profiles")
        )
    
    elif action == "share":
        builder.row(
            InlineKeyboardButton(text="📤 Поделиться анонимно", callback_data="prof_share_anonymous"),
            InlineKeyboardButton(text="📧 Отправить на email", callback_data="prof_share_email")
        )
        builder.row(
            InlineKeyboardButton(text="❌ Отменить", callback_data="prof_back_to_results")
        )
    
    return builder.as_markup()


def profiler_progress_visual_kb(
    current_num: int,
    total_questions: int,
    block_progress: dict
) -> InlineKeyboardMarkup:
    """Visual progress display with block breakdown"""
    builder = InlineKeyboardBuilder()
    
    # Overall progress
    overall_percent = int((current_num / total_questions) * 100)
    builder.row(
        InlineKeyboardButton(
            text=f"📊 Общий прогресс: {overall_percent}% ({current_num}/{total_questions})",
            callback_data="prof_progress_details"
        )
    )
    
    # Block progress indicators
    block_names = {
        "narcissism": "🧠 Нарциссизм",
        "control": "🎯 Контроль", 
        "gaslighting": "🔄 Газлайтинг",
        "emotion": "💭 Эмоции",
        "intimacy": "💕 Интимность",
        "social": "👥 Социальное"
    }
    
    for block_key, name in block_names.items():
        completed = block_progress.get(f"{block_key}_completed", 0)
        total = block_progress.get(f"{block_key}_total", 0)
        
        if total > 0:
            percent = int((completed / total) * 100)
            status = "✅" if completed == total else "⏳" if completed > 0 else "⏸️"
            
            builder.row(
                InlineKeyboardButton(
                    text=f"{status} {name}: {percent}% ({completed}/{total})",
                    callback_data=f"prof_block_progress_{block_key}"
                )
            )
    
    # Time estimate
    questions_left = total_questions - current_num
    time_estimate = questions_left * 30  # 30 seconds per question
    
    if time_estimate > 60:
        time_text = f"⏱️ Осталось: ~{time_estimate//60} мин"
    else:
        time_text = f"⏱️ Осталось: ~{time_estimate} сек"
    
    builder.row(
        InlineKeyboardButton(text=time_text, callback_data="prof_time_info")
    )
    
    builder.row(
        InlineKeyboardButton(text="↩️ Назад к вопросу", callback_data="prof_back_to_question")
    )
    
    return builder.as_markup() 


def get_profiler_keyboard() -> InlineKeyboardMarkup:
    """Get profiler main keyboard"""
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


def get_profiler_navigation_keyboard(current_step: int, total_steps: int) -> InlineKeyboardMarkup:
    """Get profiler navigation keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Previous button
    if current_step > 1:
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"profiler_prev_{current_step}")
        )
    
    # Next button
    if current_step < total_steps:
        builder.row(
            InlineKeyboardButton(text="➡️ Далее", callback_data=f"profiler_next_{current_step}")
        )
    
    # Finish button
    if current_step == total_steps:
        builder.row(
            InlineKeyboardButton(text="✅ Завершить", callback_data="profiler_finish")
        )
    
    # Cancel button
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="profiler_cancel")
    )
    
    return builder.as_markup()


def get_profiler_question_keyboard(question_id: str, options: List[str]) -> InlineKeyboardMarkup:
    """Create keyboard with answer options for profiler questions"""
    builder = InlineKeyboardBuilder()
    
    # Add answer options
    for i, option in enumerate(options):
        builder.row(
            InlineKeyboardButton(
                text=f"{i+1}. {option}",
                callback_data=f"answer_{question_id}_{i}"
            )
        )
    
    # Add navigation buttons
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_back"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="profiler_cancel")
    )
    
    return builder.as_markup() 