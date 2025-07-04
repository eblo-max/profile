"""Compatibility test handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.decorators import handle_errors
from app.bot.keyboards.inline import compatibility_menu_kb, back_to_main_kb

router = Router()

@router.callback_query(F.data == "compatibility_menu")
@handle_errors
async def show_compatibility_menu(callback: CallbackQuery):
    """Show compatibility test menu"""
    menu_text = """
💕 **Тест совместимости**

Узнайте насколько вы подходите друг другу:

🧪 **Пройти тест** - ответьте на вопросы о ваших отношениях
📊 **Результаты тестов** - посмотрите предыдущие результаты
💑 **Сравнить профили** - сопоставьте ваши личности

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=compatibility_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "start_compatibility")
@handle_errors
async def start_compatibility(callback: CallbackQuery):
    """Start compatibility test"""
    await callback.message.edit_text(
        "🧪 **Тест совместимости**\n\n"
        "Я задам вам вопросы о ваших отношениях для анализа совместимости.\n\n"
        "📋 Тест включает:\n"
        "• Общие ценности и цели\n"
        "• Стиль общения\n"
        "• Решение конфликтов\n"
        "• Эмоциональная близость\n\n"
        "⏱️ Время прохождения: 10-15 минут",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "compatibility_results")
@handle_errors
async def compatibility_results(callback: CallbackQuery):
    """Show compatibility results"""
    await callback.message.edit_text(
        "📊 **Результаты тестов**\n\n"
        "У вас пока нет пройденных тестов совместимости.\n\n"
        "Пройдите первый тест для получения детального анализа ваших отношений.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "compare_profiles")
@handle_errors
async def compare_profiles(callback: CallbackQuery):
    """Compare profiles"""
    await callback.message.edit_text(
        "💑 **Сравнение профилей**\n\n"
        "Создайте профили для сравнения личностных характеристик.\n\n"
        "📊 Сравнение покажет:\n"
        "• Совпадения в ценностях\n"
        "• Дополняющие качества\n"
        "• Потенциальные конфликтные зоны\n"
        "• Рекомендации по улучшению совместимости",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("compatibility"))
async def compatibility_test(message: Message):
    """Handle compatibility test command"""
    await message.answer("💕 Функция теста совместимости в разработке...") 