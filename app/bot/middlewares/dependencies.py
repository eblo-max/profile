"""Dependencies middleware for dependency injection"""

from typing import Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.ai_service import AIService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.services.analysis_service import AnalysisService
from app.services.subscription_service import SubscriptionService
from app.services.html_pdf_service import HTMLPDFService


class DependenciesMiddleware(BaseMiddleware):
    """Middleware for dependency injection"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.user_service = UserService()
        self.profile_service = ProfileService()
        self.analysis_service = AnalysisService()
        self.subscription_service = SubscriptionService()
        self.html_pdf_service = HTMLPDFService()
    
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Add services to data
        data['ai_service'] = self.ai_service
        data['user_service'] = self.user_service
        data['profile_service'] = self.profile_service
        data['analysis_service'] = self.analysis_service
        data['subscription_service'] = self.subscription_service
        data['html_pdf_service'] = self.html_pdf_service
        
        return await handler(event, data)


def get_dependencies() -> Dict[str, Any]:
    """Get services for manual dependency injection"""
    return {
        'ai_service': AIService(),
        'user_service': UserService(),
        'profile_service': ProfileService(),
        'analysis_service': AnalysisService(),
        'subscription_service': SubscriptionService(),
        'html_pdf_service': HTMLPDFService()
    } 