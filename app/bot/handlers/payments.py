"""Payments handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loguru import logger

from app.bot.keyboards.inline import subscription_menu_kb, back_to_main_kb
from app.utils.decorators import handle_errors
from app.services.user_service import UserService

router = Router()


@router.message(Command("premium"))
@handle_errors()
async def premium_purchase(message: Message):
    """Handle premium purchase command"""
    await message.answer("💎 Функция покупки премиума в разработке...")


@router.callback_query(F.data == "trial_subscription")
@handle_errors()
async def trial_subscription(callback: CallbackQuery, user_service: UserService):
    """Handle trial subscription request"""
    try:
        await callback.answer()
        
        trial_text = """
🎁 **Бесплатная пробная версия**

**Premium на 7 дней бесплатно!**

✨ **Что включено:**
• Безлимитный анализ текстов
• Детальные профили партнеров
• Расширенные рекомендации
• Приоритетная поддержка

⏰ **Условия:**
• Доступно только новым пользователям
• Автоматическое продление отключено
• Без привязки карты

🚧 **В разработке:**
Система пробных подписок будет добавлена в ближайшее время.

Пока что все функции доступны бесплатно! 🎉
"""
        
        await callback.message.edit_text(
            trial_text,
            reply_markup=subscription_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error handling trial subscription: {e}")
        await callback.answer("❌ Ошибка при обработке пробной подписки") 