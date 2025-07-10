"""Compatibility test handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loguru import logger

from app.bot.keyboards.inline import compatibility_menu_kb, back_to_main_kb
from app.utils.decorators import handle_errors
from app.services.user_service import UserService

router = Router()


@router.callback_query(F.data == "compatibility_menu")
@handle_errors()
async def show_compatibility_menu(callback: CallbackQuery):
    """Show compatibility menu"""
    menu_text = """
💕 **Тест совместимости**

Узнайте, насколько вы подходите друг другу!

🧪 **Пройти тест** - ответьте на вопросы о ваших отношениях
📊 **Результаты тестов** - посмотрите предыдущие результаты  
💑 **Сравнить профили** - сравните психологические профили

Выберите действие:
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=compatibility_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "start_compatibility")
@handle_errors()
async def start_compatibility(callback: CallbackQuery):
    """Start compatibility test"""
    try:
        await callback.answer()
        
        compatibility_text = """
🧪 **Тест совместимости**

**Как это работает:**

1️⃣ **Ответьте на вопросы** о ваших отношениях
2️⃣ **Получите анализ** совместимости по разным аспектам
3️⃣ **Изучите рекомендации** по улучшению отношений

📋 **Что анализируется:**
• Эмоциональная совместимость
• Ценности и жизненные цели  
• Стиль общения
• Решение конфликтов
• Интимность и близость

⏱️ **Время прохождения:** 10-15 минут

🚧 **В разработке:**
Полный тест совместимости будет добавлен в ближайшее время.
"""
        
        await callback.message.edit_text(
            compatibility_text,
            reply_markup=compatibility_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error starting compatibility test: {e}")
        await callback.answer("❌ Ошибка при запуске теста")


@router.callback_query(F.data == "compatibility_results")
@handle_errors()
async def compatibility_results(callback: CallbackQuery, user_service: UserService):
    """Show compatibility results"""
    try:
        await callback.answer()
        
        results_text = """
📊 **Результаты тестов совместимости**

У вас пока нет пройденных тестов совместимости.

🧪 **Чтобы получить результаты:**
1. Пройдите тест совместимости
2. Результаты сохранятся автоматически
3. Вы сможете отслеживать динамику

💡 **Совет:** Проходите тест периодически, чтобы видеть, как развиваются ваши отношения.
"""
        
        await callback.message.edit_text(
            results_text,
            reply_markup=compatibility_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing compatibility results: {e}")
        await callback.answer("❌ Ошибка при загрузке результатов")


@router.callback_query(F.data == "compare_profiles")
@handle_errors()
async def compare_profiles(callback: CallbackQuery):
    """Compare partner profiles"""
    try:
        await callback.answer()
        
        compare_text = """
💑 **Сравнение профилей**

Сравните психологические профили партнеров для глубокого анализа совместимости.

**Что нужно:**
• Ваш психологический профиль
• Профиль вашего партнера

**Что вы получите:**
• Детальное сравнение личностных черт
• Анализ потенциальных конфликтных зон
• Рекомендации по гармонизации отношений
• Советы по общению и взаимопониманию

🚧 **В разработке:**
Функция сравнения профилей будет доступна после создания системы профилей партнеров.

💡 **Пока что:** Создайте профиль партнера в разделе "Профиль партнера".
"""
        
        await callback.message.edit_text(
            compare_text,
            reply_markup=compatibility_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing profile comparison: {e}")
        await callback.answer("❌ Ошибка при загрузке сравнения профилей") 