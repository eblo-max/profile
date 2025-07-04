"""Application constants"""

# Import enums from dedicated enums module
from enum import Enum
from app.utils.enums import SubscriptionType, AnalysisType, UrgencyLevel, ActivityType, ContentType, PaymentStatus


class PersonalityType(str, Enum):
    """Personality type enumeration"""
    EMPATH = "Эмпат"
    ANALYST = "Аналитик"
    DEFENDER = "Защитник"
    HARMONIZER = "Гармонизатор"
    ADAPTIVE = "Адаптивный тип"


# Bot configuration constants
BOT_COMMANDS = [
    ("start", "🚀 Начать работу с ботом"),
    ("menu", "🏠 Главное меню"),
    ("analyze", "🚩 Анализ переписки"),
    ("profile", "👤 Мой профиль"),
    ("help", "❓ Помощь"),
    ("support", "🆘 Поддержка"),
]

# Analysis limits
FREE_ANALYSIS_LIMIT = 3
PREMIUM_ANALYSIS_LIMIT = 999
VIP_ANALYSIS_LIMIT = 999

# Rate limiting
RATE_LIMIT_MESSAGES = 30  # messages per minute
RATE_LIMIT_ANALYSES = 10  # analyses per hour

# AI configuration
MAX_TEXT_LENGTH = 4000
MAX_VOICE_DURATION = 300  # seconds
MIN_TEXT_LENGTH = 10

# Cache TTL (seconds)
USER_CACHE_TTL = 3600  # 1 hour
CONTENT_CACHE_TTL = 7200  # 2 hours
ANALYSIS_CACHE_TTL = 1800  # 30 minutes

# Subscription prices (in rubles)
SUBSCRIPTION_PRICES = {
    SubscriptionType.PREMIUM: 299,
    SubscriptionType.VIP: 899,
}

# Emergency contacts
CRISIS_HOTLINES = {
    "ru": "8-800-2000-122",  # Детский телефон доверия
    "general": "8-800-7000-600",  # Общероссийский телефон доверия
}

# Admin user IDs (to be overridden by environment)
ADMIN_USER_IDS = []

# Supported languages
SUPPORTED_LANGUAGES = ["ru", "en"]

# File size limits
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Regex patterns
PHONE_PATTERN = r"^[\+]?[1-9][\d]{0,15}$"
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Error messages
ERROR_MESSAGES = {
    "rate_limit": "⏰ Слишком много запросов. Попробуй через минуту.",
    "analysis_limit": "📊 Лимит анализов исчерпан. Обнови подписку для продолжения.",
    "ai_error": "🤖 Временные проблемы с AI. Попробуй позже.",
    "database_error": "💾 Ошибка базы данных. Обратись в поддержку.",
    "unknown_error": "❌ Произошла ошибка. Попробуй позже или обратись в поддержку.",
}

# Success messages
SUCCESS_MESSAGES = {
    "analysis_complete": "✅ Анализ завершен!",
    "profile_saved": "💾 Профиль сохранен!",
    "subscription_activated": "🎉 Подписка активирована!",
    "settings_updated": "⚙️ Настройки обновлены!",
}

# Notification templates
NOTIFICATION_TEMPLATES = {
    "daily_tip": "💡 <b>Совет дня</b>\n\n{content}",
    "analysis_reminder": "📊 Не забудь проанализировать важные сообщения!",
    "subscription_expires": "⏰ Твоя подписка истекает через {days} дней.",
    "new_feature": "🆕 Новая функция доступна: {feature_name}",
} 