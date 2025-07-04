"""Reply keyboards for bot interface"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def share_contact_kb() -> ReplyKeyboardMarkup:
    """Keyboard to share contact"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📞 Поделиться контактом", request_contact=True)
    )
    builder.row(
        KeyboardButton(text="❌ Отмена")
    )
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    """Cancel keyboard"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="❌ Отмена")
    )
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def main_menu_reply_kb() -> ReplyKeyboardMarkup:
    """Main menu reply keyboard"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📝 Анализ"),
        KeyboardButton(text="👤 Профиль партнера")
    )
    builder.row(
        KeyboardButton(text="💕 Совместимость"),
        KeyboardButton(text="📅 Советы")
    )
    builder.row(
        KeyboardButton(text="⚙️ Профиль"),
        KeyboardButton(text="💎 Подписка")
    )
    
    return builder.as_markup(
        resize_keyboard=True
    ) 