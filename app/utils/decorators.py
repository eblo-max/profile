"""Decorators for bot handlers"""

import asyncio
from functools import wraps
from typing import Callable, Any, Union

from aiogram.types import Message, CallbackQuery
from loguru import logger

from app.core.config import settings
from app.core.redis import redis_client
from app.utils.exceptions import RateLimitError, PsychoDetectiveException
from app.utils.constants import ERROR_MESSAGES


def rate_limit(
    requests: int = None,
    window: int = None,
    key_prefix: str = "rate_limit"
) -> Callable:
    """
    Rate limiting decorator for bot handlers
    
    Args:
        requests: Number of requests allowed (default from settings)
        window: Time window in seconds (default from settings)
        key_prefix: Redis key prefix
    """
    if requests is None:
        requests = settings.RATE_LIMIT_REQUESTS
    if window is None:
        window = settings.RATE_LIMIT_WINDOW
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract user_id from first argument (Message or CallbackQuery)
            event = args[0]
            if isinstance(event, (Message, CallbackQuery)):
                user_id = event.from_user.id
            else:
                # Skip rate limiting if we can't identify user
                return await func(*args, **kwargs)
            
            # Create rate limit key
            rate_limit_key = f"{key_prefix}:{user_id}"
            
            try:
                # Check rate limit using Redis
                allowed, remaining = await redis_client.set_rate_limit(
                    rate_limit_key, requests, window
                )
                
                if not allowed:
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    
                    if isinstance(event, Message):
                        await event.answer(ERROR_MESSAGES["rate_limit"])
                    elif isinstance(event, CallbackQuery):
                        await event.answer(ERROR_MESSAGES["rate_limit"], show_alert=True)
                    
                    return
                
                # Execute original function
                return await func(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Rate limit error: {e}")
                # Allow request on Redis error
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def handle_errors(func_or_send_error: Union[Callable, bool] = True, log_errors: bool = True) -> Callable:
    """
    Error handling decorator for bot handlers
    Supports both @handle_errors and @handle_errors() syntax
    
    Args:
        func_or_send_error: Function (if used as @handle_errors) or send_error_message flag
        log_errors: Whether to log errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Determine actual settings
            send_error_message = func_or_send_error if isinstance(func_or_send_error, bool) else True
            
            try:
                # Simply execute the handler function
                return await func(*args, **kwargs)
                
            except PsychoDetectiveException as e:
                # Log business logic errors
                if log_errors:
                    logger.warning(f"PsychoDetective error in {func.__name__}: {e}")
                
                # Send user-friendly error message if needed
                if send_error_message:
                    event = args[0] if args else None
                    error_message = ERROR_MESSAGES.get(e.code, e.message)
                    
                    try:
                        if isinstance(event, Message):
                            await event.answer(f"⚠️ {error_message}")
                        elif isinstance(event, CallbackQuery):
                            await event.answer(f"⚠️ {error_message}", show_alert=True)
                    except Exception as send_error:
                        logger.error(f"Failed to send error message: {send_error}")
                
                # For business logic errors, we don't re-raise - just handle gracefully
                return None
                
            except Exception as e:
                # Log unexpected errors
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    logger.exception("Full traceback:")
                
                # Send generic error message to user
                if send_error_message:
                    event = args[0] if args else None
                    
                    try:
                        if isinstance(event, Message):
                            await event.answer("😔 Произошла ошибка. Попробуйте позже.")
                        elif isinstance(event, CallbackQuery):
                            await event.answer("😔 Произошла ошибка. Попробуйте позже.", show_alert=True)
                    except Exception as send_error:
                        logger.error(f"Failed to send error message: {send_error}")
                
                # For unexpected errors, we also don't re-raise in production
                # This ensures the bot stays responsive
                return None
        
        return wrapper
    
    # Support both @handle_errors and @handle_errors() syntax
    if callable(func_or_send_error):
        # Used as @handle_errors (without parentheses)
        func = func_or_send_error
        return decorator(func)
    else:
        # Used as @handle_errors() (with parentheses)
        return decorator


def typing_action(action: str = "typing") -> Callable:
    """
    Show typing action decorator
    
    Args:
        action: Chat action to show (typing, upload_photo, etc.)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            event = args[0]
            if isinstance(event, Message):
                # Show typing action
                await event.bot.send_chat_action(event.chat.id, action)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def admin_only(func: Callable) -> Callable:
    """Decorator to restrict access to admin users only"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        event = args[0]
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            
            if user_id not in settings.ADMIN_USER_IDS:
                logger.warning(f"Non-admin user {user_id} attempted admin action")
                
                if isinstance(event, Message):
                    await event.answer("❌ У вас нет прав для выполнения этого действия")
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ У вас нет прав для выполнения этого действия", show_alert=True)
                
                return
        
        return await func(*args, **kwargs)
    
    return wrapper


def subscription_required(subscription_type: str = "premium") -> Callable:
    """
    Decorator to require specific subscription
    
    Args:
        subscription_type: Required subscription type
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            from app.services.user_service import UserService
            from app.core.database import get_session
            
            event = args[0]
            if isinstance(event, (Message, CallbackQuery)):
                user_id = event.from_user.id
                
                async with get_session() as session:
                    user_service = UserService(session)
                    user = await user_service.get_user_by_telegram_id(user_id)
                    
                    if not user:
                        error_msg = "❌ Пользователь не найден. Используйте /start"
                    elif subscription_type == "premium" and not user.is_premium:
                        error_msg = "💎 Эта функция доступна только с Premium подпиской"
                    elif subscription_type == "vip" and not user.is_vip:
                        error_msg = "⭐ Эта функция доступна только с VIP подпиской"
                    else:
                        # User has required subscription
                        return await func(*args, **kwargs)
                    
                    # Send error message
                    if isinstance(event, Message):
                        await event.answer(error_msg)
                    elif isinstance(event, CallbackQuery):
                        await event.answer(error_msg, show_alert=True)
                    
                    return
        
        return wrapper
    return decorator


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Retry decorator for functions that might fail
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Delay between attempts in seconds
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        await asyncio.sleep(delay * (attempt + 1))
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
            
            # Re-raise the last exception if all attempts failed
            raise last_exception
        
        return wrapper
    return decorator


def log_handler_call(func: Callable) -> Callable:
    """Decorator to log handler calls for debugging"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        event = args[0]
        user_info = ""
        
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            username = event.from_user.username or "none"
            user_info = f"user_id={user_id}, username={username}"
        
        logger.info(f"Handler {func.__name__} called by {user_info}")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Handler {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Handler {func.__name__} failed: {e}")
            raise
    
    return wrapper 