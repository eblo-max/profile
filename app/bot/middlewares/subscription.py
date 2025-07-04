"""Subscription middleware for access control"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.models.user import User
from app.utils.enums import SubscriptionType
from app.core.logging import logger
from app.core.config import settings


class SubscriptionMiddleware(BaseMiddleware):
    """Middleware for subscription-based access control"""
    
    # Features that require premium subscription
    PREMIUM_FEATURES = {
        'analyze_chat',
        'create_detailed_profile',
        'advanced_compatibility',
        'bulk_analysis',
        'export_results'
    }
    
    # Features that require VIP subscription
    VIP_FEATURES = {
        'unlimited_analysis',
        'priority_support',
        'custom_reports',
        'ai_coaching'
    }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Check subscription access for features"""
        
        user: User = data.get("user")
        if not user:
            return await handler(event, data)
        
        # Basic commands and callbacks that should ALWAYS work
        BASIC_COMMANDS = {'start', 'help', 'menu', 'support', 'settings'}
        BASIC_CALLBACKS = {'main_menu', 'back', 'cancel', 'help', 'profile_menu', 'subscription_menu'}
        
        # Get callback data or command to check feature access
        feature = None
        should_check = True
        
        if isinstance(event, CallbackQuery) and event.data:
            # Don't check subscription for basic callbacks
            if event.data in BASIC_CALLBACKS:
                should_check = False
            else:
                feature = event.data
        elif isinstance(event, Message) and event.text:
            # Extract feature from text commands
            if event.text.startswith('/'):
                command = event.text[1:].split()[0]
                # Don't check subscription for basic commands
                if command in BASIC_COMMANDS:
                    should_check = False
                else:
                    feature = command
        
        # Only check subscription for non-basic features
        if should_check and feature:
            # Check if feature requires premium
            if feature in self.PREMIUM_FEATURES:
                if user.subscription_type == SubscriptionType.FREE:
                    await self._send_subscription_required(event, "Premium")
                    return  # Block only premium features
            
            # Check if feature requires VIP
            elif feature in self.VIP_FEATURES:
                if user.subscription_type in [SubscriptionType.FREE, SubscriptionType.PREMIUM]:
                    await self._send_subscription_required(event, "VIP")
                    return  # Block only VIP features
        
        # Add subscription info to data
        data["subscription_type"] = user.subscription_type
        data["is_premium"] = user.subscription_type in [SubscriptionType.PREMIUM, SubscriptionType.VIP]
        data["is_vip"] = user.subscription_type == SubscriptionType.VIP
        
        return await handler(event, data)
    
    async def _send_subscription_required(self, event, required_tier: str) -> None:
        """Send subscription required message"""
        
        message_text = f"""
🔒 **Требуется подписка {required_tier}**

Эта функция доступна только для пользователей с подпиской {required_tier}.

**Преимущества {required_tier}:**
"""
        
        if required_tier == "Premium":
            message_text += """
💎 **Premium подписка:**
• Расширенный анализ текстов
• Детальные профили партнеров
• Продвинутые тесты совместимости
• Экспорт результатов
• Приоритетная поддержка

💰 **Цена:** 299₽/месяц
"""
        else:  # VIP
            message_text += """
👑 **VIP подписка:**
• Все возможности Premium
• Безлимитные анализы
• ИИ-коучинг по отношениям
• Персональные отчеты
• Мгновенная поддержка

💰 **Цена:** 599₽/месяц
"""
        
        from app.bot.keyboards.inline import subscription_plans_kb
        
        try:
            if isinstance(event, CallbackQuery):
                try:
                    await event.message.edit_text(
                        message_text,
                        reply_markup=subscription_plans_kb(),
                        parse_mode="Markdown"
                    )
                except Exception:
                    await event.message.answer(
                        message_text,
                        reply_markup=subscription_plans_kb(),
                        parse_mode="Markdown"
                    )
                await event.answer(f"Требуется подписка {required_tier}")
            elif isinstance(event, Message):
                await event.answer(
                    message_text,
                    reply_markup=subscription_plans_kb(),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error sending subscription required message: {e}") 