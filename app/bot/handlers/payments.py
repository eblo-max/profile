"""Payments handler"""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("premium"))
async def premium_purchase(message: Message):
    """Handle premium purchase command"""
    await message.answer("💎 Функция покупки премиума в разработке...") 