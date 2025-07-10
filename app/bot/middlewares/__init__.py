"""Bot middlewares registration"""

from aiogram import Dispatcher
from .auth import AuthMiddleware
from .logging import LoggingMiddleware
from .rate_limit import RateLimitMiddleware
from .subscription import SubscriptionMiddleware
from .dependencies import DependenciesMiddleware


def register_all_middlewares(dp: Dispatcher) -> None:
    """Register all middlewares"""
    # Re-enable DependencyMiddleware to provide UserService
    dp.message.middleware(DependenciesMiddleware())
    dp.callback_query.middleware(DependenciesMiddleware())
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Temporarily disable problematic middlewares for testing
    # dp.message.middleware(RateLimitMiddleware())
    # dp.callback_query.middleware(RateLimitMiddleware())
    
    # dp.message.middleware(SubscriptionMiddleware())
    # dp.callback_query.middleware(SubscriptionMiddleware())
    
    # Enable only essential middlewares for now
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware()) 