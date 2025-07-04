"""Logging middleware for bot activity tracking"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update
import time

from app.models.user import User
from app.core.logging import logger


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging bot activities and user interactions"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Log user interactions and bot performance"""
        
        # Get user info
        user: User = data.get("user")
        update: Update = data.get("event_update")
        
        # Start timing
        start_time = time.time()
        
        # Get user identifier
        user_id = user.telegram_id if user else "unknown"
        username = user.username if user else "unknown"
        
        # Log incoming request
        request_info = self._get_request_info(event, update)
        
        logger.info(
            f"Request: {request_info['type']} from user {user_id} (@{username}): {request_info['content']}"
        )
        
        try:
            # Execute handler
            result = await handler(event, data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log successful completion
            logger.info(
                f"Completed: {request_info['type']} for user {user_id} "
                f"in {processing_time:.2f}s"
            )
            
            # Log performance warnings
            if processing_time > 5.0:
                logger.warning(
                    f"Slow response: {request_info['type']} took {processing_time:.2f}s "
                    f"for user {user_id}"
                )
            
            return result
            
        except Exception as e:
            # Calculate processing time for error case
            processing_time = time.time() - start_time
            
            # Log error with context
            logger.error(
                f"Error: {request_info['type']} for user {user_id} "
                f"after {processing_time:.2f}s: {str(e)}",
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    def _get_request_info(self, event: TelegramObject, update: Update) -> Dict[str, str]:
        """Extract request information for logging"""
        
        if isinstance(event, Message):
            if event.text:
                content = event.text[:100] + "..." if len(event.text) > 100 else event.text
                if event.text.startswith('/'):
                    return {
                        'type': 'command',
                        'content': content
                    }
                else:
                    return {
                        'type': 'message',
                        'content': content
                    }
            elif event.document:
                return {
                    'type': 'document',
                    'content': f"file: {event.document.file_name}"
                }
            elif event.photo:
                return {
                    'type': 'photo',
                    'content': "photo upload"
                }
            elif event.voice:
                return {
                    'type': 'voice',
                    'content': "voice message"
                }
            else:
                return {
                    'type': 'message',
                    'content': "unknown message type"
                }
        
        elif isinstance(event, CallbackQuery):
            return {
                'type': 'callback',
                'content': event.data if event.data else "no data"
            }
        
        else:
            return {
                'type': 'unknown',
                'content': str(type(event))
            } 