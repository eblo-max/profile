"""Rate limiting middleware"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from datetime import datetime, timedelta

from app.models.user import User
from app.services.user_service import UserService
from app.utils.enums import SubscriptionType, ActivityType
from app.core.redis import redis_client
from app.core.logging import logger


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user actions"""
    
    # Rate limits for different actions (per day for free users)
    RATE_LIMITS = {
        'text_analysis': 3,      # Free: 3/day, Premium: 9/day, VIP: unlimited
        'profile_creation': 1,    # Free: 1/day, Premium: 3/day, VIP: unlimited
        'compatibility_test': 2,  # Free: 2/day, Premium: 6/day, VIP: unlimited
        'ai_request': 5,         # Free: 5/day, Premium: 15/day, VIP: unlimited
    }
    
    # Actions that should be rate limited
    RATE_LIMITED_ACTIONS = {
        'analyze_message',
        'analyze_chat',
        'create_profile',
        'start_compatibility',
        'ai_coaching'
    }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Check rate limits for user actions"""
        
        user: User = data.get("user")
        user_service: UserService = data.get("user_service")
        
        if not user or not user_service:
            return await handler(event, data)
        
        # Get action from callback data or message
        action = None
        
        if isinstance(event, CallbackQuery) and event.data:
            action = event.data
        elif isinstance(event, Message) and event.text:
            if event.text.startswith('/'):
                action = event.text[1:].split()[0]
        
        # Check if action should be rate limited
        if action and action in self.RATE_LIMITED_ACTIONS:
            # Get rate limit type
            limit_type = self._get_limit_type(action)
            if limit_type:
                # Check rate limit
                allowed, remaining = await self._check_rate_limit(
                    user, limit_type, user_service
                )
                
                if not allowed:
                    await self._send_rate_limit_message(event, limit_type, user.subscription_type)
                    return
                
                # Add remaining uses to data
                data["rate_limit_remaining"] = remaining
        
        return await handler(event, data)
    
    def _get_limit_type(self, action: str) -> str:
        """Get rate limit type for action"""
        if action in ['analyze_message', 'analyze_chat']:
            return 'text_analysis'
        elif action == 'create_profile':
            return 'profile_creation'
        elif action == 'start_compatibility':
            return 'compatibility_test'
        elif action in ['ai_coaching']:
            return 'ai_request'
        return None
    
    async def _check_rate_limit(
        self,
        user: User,
        limit_type: str,
        user_service: UserService
    ) -> tuple[bool, int]:
        """Check if user has exceeded rate limit"""
        
        # VIP users have no limits
        if user.subscription_type == SubscriptionType.VIP:
            return True, 999
        
        # Get base limit
        base_limit = self.RATE_LIMITS.get(limit_type, 1)
        
        # Premium users get 3x limit
        if user.subscription_type == SubscriptionType.PREMIUM:
            limit = base_limit * 3
        else:
            limit = base_limit
        
        # Check using Redis for faster access
        try:
            key = f"rate_limit:{user.telegram_id}:{limit_type}"
            current_count = await redis_client.get(key)
            
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            if current_count >= limit:
                return False, 0
            
            # Increment counter
            await redis_client.incr(key)
            await redis_client.expire(key, 86400)  # 24 hours
            
            return True, limit - current_count - 1
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to database check
            return await user_service.check_rate_limit(
                user.telegram_id,
                limit_type,
                limit,
                24
            )
    
    async def _send_rate_limit_message(
        self,
        event,
        limit_type: str,
        subscription_type: SubscriptionType
    ) -> None:
        """Send rate limit exceeded message"""
        
        # Get friendly names for limits
        action_names = {
            'text_analysis': 'анализ текста',
            'profile_creation': 'создание профиля',
            'compatibility_test': 'тест совместимости',
            'ai_request': 'ИИ-запрос'
        }
        
        action_name = action_names.get(limit_type, 'действие')
        base_limit = self.RATE_LIMITS.get(limit_type, 1)
        
        if subscription_type == SubscriptionType.FREE:
            current_limit = base_limit
            upgrade_text = """
💎 **Увеличьте лимиты с Premium:**
• В 3 раза больше анализов
• Расширенные возможности
• Приоритетная поддержка

👑 **Безлимитный доступ с VIP:**
• Неограниченные анализы
• Все премиум функции
• Персональный ИИ-коуч
"""
        else:  # Premium
            current_limit = base_limit * 3
            upgrade_text = """
👑 **Безлимитный доступ с VIP:**
• Неограниченные анализы
• Все премиум функции
• Персональный ИИ-коуч
• Мгновенная поддержка
"""
        
        message_text = f"""
⏰ **Лимит исчерпан**

Вы достигли дневного лимита на {action_name}: {current_limit} раз.

Лимит обновится завтра в 00:00 UTC.

{upgrade_text}
"""
        
        from app.bot.keyboards.inline import subscription_plans_kb
        
        try:
            if isinstance(event, CallbackQuery):
                await event.message.edit_text(
                    message_text,
                    reply_markup=subscription_plans_kb(),
                    parse_mode="Markdown"
                )
                await event.answer("Лимит исчерпан")
            elif isinstance(event, Message):
                await event.answer(
                    message_text,
                    reply_markup=subscription_plans_kb(),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error sending rate limit message: {e}")
    
    async def log_action(
        self,
        user_id: int,
        action_type: str,
        user_service: UserService
    ) -> None:
        """Log user action for rate limiting"""
        try:
            activity_type_map = {
                'text_analysis': ActivityType.TEXT_ANALYZED,
                'profile_creation': ActivityType.PROFILE_CREATED,
                'compatibility_test': ActivityType.COMPATIBILITY_TEST,
                'ai_request': ActivityType.AI_REQUEST
            }
            
            activity_type = activity_type_map.get(action_type)
            if activity_type:
                await user_service.log_activity(user_id, activity_type)
                
        except Exception as e:
            logger.error(f"Error logging action: {e}") 