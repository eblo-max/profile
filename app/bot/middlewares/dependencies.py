"""Dependency injection middleware"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.core.database import get_session
from app.services.user_service import UserService
from app.services.ai_service import AIService


class DependencyMiddleware(BaseMiddleware):
    """Middleware for dependency injection"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Inject dependencies into handler"""
        
        # Get database session using proper async context manager
        async with get_session() as db_session:
            try:
                # Create services
                user_service = UserService(db_session)
                ai_service = AIService()
                
                # Inject into data
                data["user_service"] = user_service
                data["ai_service"] = ai_service
                data["db_session"] = db_session
                
                # Call handler
                result = await handler(event, data)
                
                # Commit session if all went well
                await db_session.commit()
                
                return result
                
            except Exception:
                # Rollback on error
                await db_session.rollback()
                raise 