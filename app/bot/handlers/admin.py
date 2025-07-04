"""Admin panel handler"""

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Handle admin panel command"""
    builder = InlineKeyboardBuilder()
    builder.row(
        dict(text="📊 Статистика", callback_data="admin_stats"),
        dict(text="👥 Пользователи", callback_data="admin_users")
    )
    builder.row(
        dict(text="📢 Рассылка", callback_data="admin_broadcast")
    )
    await message.answer("⚙️ Админ-панель. Выберите действие:", reply_markup=builder.as_markup())

@router.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_menu_callback(callback: CallbackQuery):
    if callback.data == "admin_stats":
        await callback.message.edit_text("📊 Статистика: (заглушка)")
    elif callback.data == "admin_users":
        await callback.message.edit_text("👥 Пользователи: (заглушка)")
    elif callback.data == "admin_broadcast":
        await callback.message.edit_text("📢 Рассылка: (заглушка)")
    await callback.answer() 