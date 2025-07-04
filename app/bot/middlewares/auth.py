"""Authentication middleware for user management"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as AiogramUser, Update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_session
from app.services.user_service import UserService
from app.models.user import User
from app.core.logging import logger


class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication and management"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process authentication for incoming updates"""
        
        # Get Telegram user from event
        aiogram_user: AiogramUser = data.get("event_from_user")
        if not aiogram_user:
            return await handler(event, data)
        
        try:
            async with get_session() as session:
                user_service = UserService(session)
                
                # Get or create user
                user = await user_service.get_or_create_user(
                    telegram_id=aiogram_user.id,
                    username=aiogram_user.username,
                    first_name=aiogram_user.first_name,
                    last_name=aiogram_user.last_name
                )
                
                # Add user to event data
                data["user"] = user
                
                # Continue processing
                return await handler(event, data)

        except Exception as e:
            logger.error(f"Auth middleware error: {e}")
            # Continue processing even if auth fails
            data["user"] = None
            data["user_service"] = None
        
        return await handler(event, data) 