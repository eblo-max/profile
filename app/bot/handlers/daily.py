"""Daily content handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.exceptions import handle_errors
from app.bot.keyboards.inline import daily_menu_kb, back_to_main_kb

router = Router()

@router.callback_query(F.data == "daily_menu")
@handle_errors
async def show_daily_menu(callback: CallbackQuery):
    """Show daily content menu"""
    menu_text = """
📅 **Ежедневные советы**

Получайте полезный контент каждый день:

📖 **Совет дня** - практические рекомендации
🎓 **Урок дня** - изучайте психологию отношений
💡 **Упражнение дня** - развивайте эмоциональный интеллект
🔔 **Настройки уведомлений** - управляйте уведомлениями

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=daily_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "daily_tip")
@handle_errors
async def daily_tip(callback: CallbackQuery):
    """Show daily tip"""
    await callback.message.edit_text(
        "📖 **Совет дня**\n\n"
        "💡 *Активное слушание - ключ к пониманию*\n\n"
        "Когда ваш партнер говорит, сосредоточьтесь полностью на его словах. "
        "Не думайте о своем ответе, пока он говорит. Задавайте уточняющие вопросы, "
        "чтобы показать, что вы действительно слушаете.\n\n"
        "🎯 **Попробуйте сегодня:**\n"
        "Выделите 15 минут для разговора с партнером, полностью сосредоточившись на нем.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "daily_lesson")
@handle_errors
async def daily_lesson(callback: CallbackQuery):
    """Show daily lesson"""
    await callback.message.edit_text(
        "🎓 **Урок дня: Языки любви**\n\n"
        "Каждый человек выражает и принимает любовь по-разному:\n\n"
        "💬 **Слова поощрения** - комплименты, поддержка\n"
        "⏰ **Время** - качественное время вместе\n"
        "🎁 **Подарки** - знаки внимания\n"
        "🤝 **Помощь** - дела и услуги\n"
        "🫂 **Прикосновения** - физическая близость\n\n"
        "📚 Определите свой язык любви и язык вашего партнера для лучшего понимания.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "daily_exercise")
@handle_errors
async def daily_exercise(callback: CallbackQuery):
    """Show daily exercise"""
    await callback.message.edit_text(
        "💡 **Упражнение дня: Благодарность**\n\n"
        "🎯 **Цель:** Укрепить позитивную связь с партнером\n\n"
        "📝 **Как выполнить:**\n"
        "1. Вспомните 3 вещи, за которые вы благодарны партнеру сегодня\n"
        "2. Скажите ему об этом прямо и искренне\n"
        "3. Будьте конкретными: не просто 'спасибо', а 'спасибо за...'\n\n"
        "✨ **Результат:** Партнер почувствует себя ценным и любимым",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "notification_settings")
@handle_errors
async def notification_settings(callback: CallbackQuery):
    """Show notification settings"""
    await callback.message.edit_text(
        "🔔 **Настройки уведомлений**\n\n"
        "Управляйте получением ежедневного контента:\n\n"
        "✅ Ежедневные советы: Включено\n"
        "✅ Напоминания о упражнениях: Включено\n"
        "❌ Еженедельная статистика: Отключено\n\n"
        "⏰ Время уведомлений: 09:00\n\n"
        "Для изменения настроек обратитесь в поддержку.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("daily"))
async def daily_content(message: Message):
    """Handle daily content command"""
    await message.answer("📅 Функция ежедневного контента в разработке...") 