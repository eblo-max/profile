"""Inline keyboards for bot interface"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional


def main_menu_kb() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Анализ текста", callback_data="analysis_menu"),
        InlineKeyboardButton(text="👤 Профиль партнера", callback_data="profiler_menu")
    )
    builder.row(
        InlineKeyboardButton(text="💕 Совместимость", callback_data="compatibility_menu"),
        InlineKeyboardButton(text="📅 Ежедневные советы", callback_data="daily_menu")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Профиль", callback_data="profile_menu"),
        InlineKeyboardButton(text="💎 Подписка", callback_data="subscription_menu")
    )
    
    return builder.as_markup()


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