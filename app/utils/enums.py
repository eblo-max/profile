"""Common enumerations used across the application"""

from enum import Enum


class SubscriptionType(Enum):
    """User subscription types"""
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


class ActivityType(Enum):
    """User activity types for analytics"""
    USER_REGISTERED = "USER_REGISTERED"
    LOGIN = "LOGIN"
    ANALYSIS_STARTED = "ANALYSIS_STARTED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    PROFILE_CREATED = "PROFILE_CREATED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    COMPATIBILITY_TEST = "COMPATIBILITY_TEST"
    SUBSCRIPTION_PURCHASED = "SUBSCRIPTION_PURCHASED"
    FEATURE_USED = "FEATURE_USED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    LOGOUT = "LOGOUT"


class AnalysisType(Enum):
    """Analysis types"""
    TEXT_ANALYSIS = "TEXT_ANALYSIS"
    VOICE_ANALYSIS = "VOICE_ANALYSIS"
    IMAGE_ANALYSIS = "IMAGE_ANALYSIS"


class UrgencyLevel(Enum):
    """Risk/urgency levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class ContentType(Enum):
    """Daily content types"""
    TIP = "TIP"
    CASE_STUDY = "CASE_STUDY"
    EXERCISE = "EXERCISE"
    QUOTE = "QUOTE"


# Alias for backward compatibility
RiskLevel = UrgencyLevel 