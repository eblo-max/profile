"""Security utilities and helpers"""

import hashlib
import hmac
import secrets
from typing import Optional
from datetime import datetime, timedelta

from app.core.config import settings


def generate_token(length: int = 32) -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(length)


def generate_referral_code(user_id: int) -> str:
    """Generate referral code for user"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    data = f"{user_id}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:8].upper()


def verify_telegram_data(data: dict, bot_token: str) -> bool:
    """Verify Telegram WebApp data integrity"""
    try:
        # Extract hash from data
        received_hash = data.pop('hash', None)
        if not received_hash:
            return False
        
        # Create data check string
        data_check_arr = []
        for key, value in sorted(data.items()):
            data_check_arr.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_arr)
        
        # Create secret key
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(received_hash, calculated_hash)
        
    except Exception:
        return False


def sanitize_text(text: str, max_length: int = 4000) -> str:
    """Sanitize user input text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '`']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text


def is_admin_user(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.ADMIN_USER_IDS


def create_session_key(user_id: int) -> str:
    """Create session key for user"""
    timestamp = datetime.utcnow().isoformat()
    data = f"{user_id}:{timestamp}:{settings.SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    import re
    pattern = r'^[\+]?[1-9][\d]{0,15}$'
    return bool(re.match(pattern, phone.strip()))


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip().lower()))


def hash_data(data: str, salt: Optional[str] = None) -> str:
    """Hash sensitive data with optional salt"""
    if salt is None:
        salt = settings.SECRET_KEY
    
    combined = f"{data}:{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self._requests = {}
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> tuple[bool, int]:
        """
        Check if request is allowed
        Returns (allowed, remaining_requests)
        """
        now = datetime.utcnow()
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Clean old requests
        cutoff = now - timedelta(seconds=window)
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > cutoff
        ]
        
        # Check limit
        current_count = len(self._requests[key])
        if current_count >= limit:
            return False, 0
        
        # Add current request
        self._requests[key].append(now)
        
        return True, limit - current_count - 1


# Global rate limiter instance
rate_limiter = RateLimiter() 