"""Bot middlewares registration"""

from aiogram import Dispatcher
from .auth import AuthMiddleware
from .logging import LoggingMiddleware
from .rate_limit import RateLimitMiddleware
from .subscription import SubscriptionMiddleware
from .dependencies import DependencyMiddleware


def register_all_middlewares(dp: Dispatcher) -> None:
    """Register all middlewares"""
    # Temporarily disable DependencyMiddleware to test
    # dp.message.middleware(DependencyMiddleware())
    # dp.callback_query.middleware(DependencyMiddleware())
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware()) 