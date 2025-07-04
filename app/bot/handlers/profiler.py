"""Partner profiler handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.utils.decorators import handle_errors
from app.bot.keyboards.inline import profiler_menu_kb, back_to_main_kb

router = Router()

@router.callback_query(F.data == "profiler_menu")
@handle_errors
async def show_profiler_menu(callback: CallbackQuery):
    """Show partner profiler menu"""
    menu_text = """
👤 **Профиль партнера**

Создайте психологический портрет на основе ваших наблюдений:

🆕 **Новый профиль** - ответьте на вопросы о партнере
📋 **Мои профили** - посмотрите созданные профили
🎯 **Рекомендации** - получите советы на основе анализа

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=profiler_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "create_profile")
@handle_errors
async def create_profile(callback: CallbackQuery):
    """Handle create profile"""
    await callback.message.edit_text(
        "🆕 **Создание профиля партнера**\n\n"
        "Я задам вам несколько вопросов о вашем партнере для создания психологического портрета.\n\n"
        "📋 Вопросы касаются:\n"
        "• Поведенческих паттернов\n"
        "• Эмоциональных реакций\n"
        "• Стиля общения\n"
        "• Отношения к конфликтам\n\n"
        "⏱️ Это займет 5-7 минут.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "my_profiles")
@handle_errors
async def my_profiles(callback: CallbackQuery):
    """Show user profiles"""
    await callback.message.edit_text(
        "📋 **Мои профили**\n\n"
        "У вас пока нет созданных профилей.\n\n"
        "Создайте первый профиль партнера для получения персонализированного анализа.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "profile_recommendations")
@handle_errors
async def profile_recommendations(callback: CallbackQuery):
    """Show profile recommendations"""
    await callback.message.edit_text(
        "🎯 **Рекомендации**\n\n"
        "Создайте профиль партнера для получения персонализированных рекомендаций.\n\n"
        "📊 На основе анализа вы получите:\n"
        "• Советы по улучшению отношений\n"
        "• Предупреждения о красных флагах\n"
        "• Стратегии эффективного общения",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("profile"))
async def create_partner_profile(message: Message):
    """Handle create profile command"""
    await message.answer("👤 Создание профиля партнера в разработке...") 