"""Admin panel handler"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loguru import logger

from app.bot.keyboards.inline import admin_menu_kb, back_to_main_kb
from app.utils.decorators import admin_only, handle_errors
from app.services.user_service import UserService

router = Router()


@router.message(Command("admin"))
@admin_only
@handle_errors()
async def admin_panel(message: Message):
    """Handle admin panel command"""
    admin_text = """
⚙️ **Админ-панель**

Добро пожаловать в панель администратора PsychoDetective.

Выберите нужный раздел:
"""
    
    await message.answer(
        admin_text,
        reply_markup=admin_menu_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "admin_stats")
@admin_only
@handle_errors()
async def admin_stats(callback: CallbackQuery, user_service: UserService):
    """Show admin statistics"""
    try:
        await callback.answer()
        
        # TODO: Implement real statistics from database
        stats_text = """
📊 **Статистика системы**

👥 **Пользователи:**
• Всего пользователей: 1,234
• Активных за день: 156
• Новых за неделю: 89

📝 **Анализы:**
• Всего анализов: 2,567
• За сегодня: 45
• Популярный тип: Профиль партнера

💎 **Подписки:**
• Premium пользователей: 234
• VIP пользователей: 67
• Конверсия: 24.5%

🤖 **Система:**
• Время работы: 15 дней
• Статус: Работает нормально
• Последний перезапуск: 2 часа назад
"""
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=admin_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing admin stats: {e}")
        await callback.answer("❌ Ошибка при загрузке статистики")


@router.callback_query(F.data == "admin_users")
@admin_only
@handle_errors()
async def admin_users(callback: CallbackQuery):
    """Show users management"""
    try:
        await callback.answer()
        
        users_text = """
👥 **Управление пользователями**

🔍 **Поиск пользователей:**
• По ID: /user_info <user_id>
• По username: /user_search <username>

📊 **Действия:**
• Просмотр профиля
• Блокировка/разблокировка
• Изменение подписки
• История активности

🚧 **В разработке:**
Полный интерфейс управления пользователями будет добавлен в следующих обновлениях.
"""
        
        await callback.message.edit_text(
            users_text,
            reply_markup=admin_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing admin users: {e}")
        await callback.answer("❌ Ошибка при загрузке управления пользователями")


@router.callback_query(F.data == "admin_content")
@admin_only
@handle_errors()
async def admin_content(callback: CallbackQuery):
    """Show content management"""
    try:
        await callback.answer()
        
        content_text = """
📝 **Управление контентом**

📖 **Ежедневный контент:**
• Советы дня
• Уроки отношений
• Упражнения

🎯 **Промпты и анализ:**
• Настройка AI промптов
• Параметры анализа
• Шаблоны отчетов

📢 **Уведомления:**
• Шаблоны сообщений
• Push-уведомления
• Email рассылки

🚧 **В разработке:**
Редактор контента будет добавлен в админ-панель.
"""
        
        await callback.message.edit_text(
            content_text,
            reply_markup=admin_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing admin content: {e}")
        await callback.answer("❌ Ошибка при загрузке управления контентом")


@router.callback_query(F.data == "admin_payments")
@admin_only
@handle_errors()
async def admin_payments(callback: CallbackQuery):
    """Show payments management"""
    try:
        await callback.answer()
        
        payments_text = """
💰 **Управление платежами**

💳 **Статистика платежей:**
• Общий доход: $12,345
• За месяц: $3,456
• Средний чек: $9.99

📊 **Подписки:**
• Premium: 234 активных
• VIP: 67 активных
• Отмены за месяц: 23

🔄 **Возвраты:**
• Запросов на возврат: 5
• Обработано: 3
• Ожидают: 2

🚧 **В разработке:**
Полная система управления платежами и биллинга.
"""
        
        await callback.message.edit_text(
            payments_text,
            reply_markup=admin_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing admin payments: {e}")
        await callback.answer("❌ Ошибка при загрузке управления платежами")


@router.callback_query(F.data == "admin_broadcast")
@admin_only
@handle_errors()
async def admin_broadcast(callback: CallbackQuery):
    """Show broadcast management"""
    try:
        await callback.answer()
        
        broadcast_text = """
📢 **Массовая рассылка**

📨 **Типы рассылок:**
• Уведомления всем пользователям
• Рассылка по сегментам
• Персональные сообщения

🎯 **Сегментация:**
• По типу подписки (Free/Premium/VIP)
• По активности (активные/неактивные)
• По регистрации (новые/старые)

📊 **Статистика:**
• Последняя рассылка: 3 дня назад
• Доставлено: 1,156 / 1,234
• Открыто: 67%

🚧 **Для создания рассылки:**
Используйте команду /broadcast <сообщение>
"""
        
        await callback.message.edit_text(
            broadcast_text,
            reply_markup=admin_menu_kb(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error showing admin broadcast: {e}")
        await callback.answer("❌ Ошибка при загрузке рассылки") 