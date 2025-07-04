"""Text analysis handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.decorators import handle_errors
from app.bot.keyboards.inline import analysis_menu_kb, back_to_main_kb

router = Router()

@router.callback_query(F.data == "analysis_menu")
@handle_errors
async def show_analysis_menu(callback: CallbackQuery):
    """Show analysis menu"""
    menu_text = """
📝 **Анализ текста**

Выберите тип анализа:

📱 **Анализ переписки** - загрузите файл с диалогом
💬 **Анализ сообщения** - отправьте текст для анализа
📊 **История анализов** - посмотрите предыдущие результаты

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=analysis_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "analyze_chat")
@handle_errors 
async def analyze_chat(callback: CallbackQuery):
    """Handle chat analysis"""
    await callback.message.edit_text(
        "📱 **Анализ переписки**\n\n"
        "Отправьте файл с вашей перепиской (txt, json) или скопируйте текст диалога.\n\n"
        "📋 Поддерживаемые форматы:\n"
        "• Обычный текст\n"
        "• Экспорт из WhatsApp\n"
        "• Экспорт из Telegram\n\n"
        "🔒 Ваши данные обрабатываются конфиденциально.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "analyze_message")
@handle_errors
async def analyze_message(callback: CallbackQuery):
    """Handle message analysis"""
    await callback.message.edit_text(
        "💬 **Анализ сообщения**\n\n"
        "Отправьте текст сообщения для анализа.\n\n"
        "🎯 Я проанализирую:\n"
        "• Эмоциональный тон\n"
        "• Скрытые мотивы\n"
        "• Признаки манипуляций\n"
        "• Уровень искренности\n\n"
        "Просто отправьте сообщение следующим текстом.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "analysis_history")
@handle_errors
async def analysis_history(callback: CallbackQuery):
    """Show analysis history"""
    await callback.message.edit_text(
        "📊 **История анализов**\n\n"
        "У вас пока нет сохраненных анализов.\n\n"
        "После проведения анализа результаты будут доступны здесь.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("analyze"))
async def analyze_text(message: Message):
    """Handle text analysis command"""
    await message.answer("📝 Функция анализа текста в разработке...") 