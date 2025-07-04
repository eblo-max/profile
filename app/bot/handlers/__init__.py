"""Bot handlers registration and initialization"""

from aiogram import Dispatcher
from .start import router as start_router
from .analysis import router as analysis_router
from .profiler import router as profiler_router
from .compatibility import router as compatibility_router
from .daily import router as daily_router
from .profile import router as profile_router
from .payments import router as payments_router
from .admin import router as admin_router


def register_all_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers"""
    dp.include_router(start_router)
    dp.include_router(analysis_router)
    dp.include_router(profiler_router)
    dp.include_router(compatibility_router)
    dp.include_router(daily_router)
    dp.include_router(profile_router)
    dp.include_router(payments_router)
    dp.include_router(admin_router) 