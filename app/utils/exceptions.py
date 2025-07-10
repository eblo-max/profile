"""Custom exceptions for the application"""

import functools
from typing import Callable, Any
from loguru import logger


class PsychoDetectiveException(Exception):
    """Base exception for PsychoDetective Bot"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AIServiceError(PsychoDetectiveException):
    """Exception raised when AI service fails"""
    def __init__(self, message: str = "AI service unavailable"):
        super().__init__(message, "AI_ERROR")


class RateLimitError(PsychoDetectiveException):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT")


class DatabaseError(PsychoDetectiveException):
    """Exception raised for database errors"""
    def __init__(self, message: str = "Database error"):
        super().__init__(message, "DATABASE_ERROR")


class ValidationError(PsychoDetectiveException):
    """Exception raised for validation errors"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(PsychoDetectiveException):
    """Exception raised for authentication errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class SubscriptionError(PsychoDetectiveException):
    """Exception raised for subscription-related errors"""
    def __init__(self, message: str = "Subscription error"):
        super().__init__(message, "SUBSCRIPTION_ERROR")


class PaymentError(PsychoDetectiveException):
    """Exception raised for payment errors"""
    def __init__(self, message: str = "Payment failed"):
        super().__init__(message, "PAYMENT_ERROR")


class ContentNotFoundError(PsychoDetectiveException):
    """Exception raised when content is not found"""
    def __init__(self, message: str = "Content not found"):
        super().__init__(message, "CONTENT_NOT_FOUND")


class UserNotFoundError(PsychoDetectiveException):
    """Exception raised when user is not found"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")


class AnalysisLimitError(PsychoDetectiveException):
    """Exception raised when analysis limit is reached"""
    def __init__(self, message: str = "Analysis limit reached"):
        super().__init__(message, "ANALYSIS_LIMIT")


class ServiceError(PsychoDetectiveException):
    """Exception raised for service errors"""
    def __init__(self, message: str = "Service error"):
        super().__init__(message, "SERVICE_ERROR")


class TextTooLongError(ValidationError):
    """Exception raised when text is too long"""
    def __init__(self, max_length: int):
        message = f"Text too long. Maximum {max_length} characters allowed."
        super().__init__(message)


class TextTooShortError(ValidationError):
    """Exception raised when text is too short"""
    def __init__(self, min_length: int):
        message = f"Text too short. Minimum {min_length} characters required."
        super().__init__(message)


class InvalidFileFormatError(ValidationError):
    """Exception raised for invalid file formats"""
    def __init__(self, allowed_formats: list):
        message = f"Invalid file format. Allowed: {', '.join(allowed_formats)}"
        super().__init__(message)


class FileTooLargeError(ValidationError):
    """Exception raised when file is too large"""
    def __init__(self, max_size: int):
        message = f"File too large. Maximum size: {max_size // (1024*1024)}MB"
        super().__init__(message)


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in bot handlers"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except PsychoDetectiveException as e:
            logger.error(f"Business logic error in {func.__name__}: {e}")
            # Здесь можно добавить отправку сообщения пользователю
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            # Здесь можно добавить отправку сообщения об ошибке
            raise
    return wrapper 