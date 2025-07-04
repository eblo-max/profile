"""Admin panel handler"""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Handle admin panel command"""
    await message.answer("⚙️ Функция админ панели в разработке...") 