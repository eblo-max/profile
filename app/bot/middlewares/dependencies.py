"""Dependencies middleware for dependency injection"""

from typing import Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.database import get_session
from app.services.ai_service import AIService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.services.analysis_service import AnalysisService
from app.services.subscription_service import SubscriptionService
from app.services.html_pdf_service import HTMLPDFService


class DependenciesMiddleware(BaseMiddleware):
    """Middleware for dependency injection"""
    
    def __init__(self):
        # Create stateless services
        self.ai_service = AIService()
        self.html_pdf_service = HTMLPDFService()
    
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Create session for this request
        async with get_session() as session:
            # Create services with session
            user_service = UserService(session)
            profile_service = ProfileService(session)
            analysis_service = AnalysisService(session)
            subscription_service = SubscriptionService(session)
            
            # Add services to data
            data['session'] = session
            data['ai_service'] = self.ai_service
            data['user_service'] = user_service
            data['profile_service'] = profile_service
            data['analysis_service'] = analysis_service
            data['subscription_service'] = subscription_service
            data['html_pdf_service'] = self.html_pdf_service
            
            return await handler(event, data)


async def get_dependencies() -> Dict[str, Any]:
    """Get services for manual dependency injection"""
    async with get_session() as session:
        return {
            'session': session,
            'ai_service': AIService(),
            'user_service': UserService(session),
            'profile_service': ProfileService(session),
            'analysis_service': AnalysisService(session),
            'subscription_service': SubscriptionService(session),
            'html_pdf_service': HTMLPDFService()
        } 