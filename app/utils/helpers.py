"""Helper functions and utilities"""

import asyncio
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import quote

from loguru import logger


def format_text_for_telegram(text: str, max_length: int = 4096) -> str:
    """
    Format text for Telegram message (HTML markup safe)
    
    Args:
        text: Text to format
        max_length: Maximum length for Telegram message
        
    Returns:
        Formatted text
    """
    if not text:
        return ""
    
    # Escape HTML characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text


def extract_user_mention(user) -> str:
    """
    Extract user mention for logging
    
    Args:
        user: Telegram user object
        
    Returns:
        User mention string
    """
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    elif hasattr(user, 'first_name'):
        return user.first_name
    else:
        return f"ID:{user.id}"


def create_cache_key(*parts) -> str:
    """
    Create cache key from parts
    
    Args:
        parts: Parts to include in cache key
        
    Returns:
        Cache key string
    """
    key_parts = [str(part) for part in parts if part is not None]
    return ":".join(key_parts)


def generate_analysis_id(user_id: int, text: str) -> str:
    """
    Generate unique analysis ID
    
    Args:
        user_id: User ID
        text: Text being analyzed
        
    Returns:
        Unique analysis ID
    """
    timestamp = datetime.utcnow().isoformat()
    data = f"{user_id}:{text[:100]}:{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Format datetime for display
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return "N/A"
    
    return dt.strftime(format_str)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes
    
    Args:
        text: Text to analyze
        words_per_minute: Average reading speed
        
    Returns:
        Reading time in minutes
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    
    return reading_time


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Text to analyze
        top_n: Number of top keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction based on word frequency
    # Remove common Russian stop words
    stop_words = {
        'и', 'в', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все',
        'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы',
        'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет',
        'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если',
        'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять',
        'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они',
        'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем',
        'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под',
        'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой',
        'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы',
        'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при',
        'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот',
        'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве',
        'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда',
        'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно',
        'всю', 'между'
    }
    
    # Extract words
    words = re.findall(r'\b[а-яё]+\b', text.lower())
    
    # Filter stop words and short words
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in keywords[:top_n]]


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to split
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """
    Normalize score to a specific range
    
    Args:
        score: Score to normalize
        min_val: Minimum value of range
        max_val: Maximum value of range
        
    Returns:
        Normalized score
    """
    return max(min_val, min(max_val, round(score, 1)))


def get_urgency_emoji(urgency_level: str) -> str:
    """
    Get emoji for urgency level
    
    Args:
        urgency_level: Urgency level
        
    Returns:
        Corresponding emoji
    """
    urgency_emojis = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🟠",
        "critical": "🔴"
    }
    
    return urgency_emojis.get(urgency_level, "⚪")


def format_analysis_result(analysis: Dict[str, Any]) -> str:
    """
    Format analysis result for display
    
    Args:
        analysis: Analysis result dictionary
        
    Returns:
        Formatted text for display
    """
    if not analysis:
        return "❌ Анализ не удался"
    
    toxicity_score = analysis.get("toxicity_score", 0)
    urgency_level = analysis.get("urgency_level", "low")
    red_flags = analysis.get("red_flags", [])
    analysis_text = analysis.get("analysis", "")
    recommendation = analysis.get("recommendation", "")
    patterns = analysis.get("patterns_detected", [])
    
    urgency_emoji = get_urgency_emoji(urgency_level)
    
    # Create result text
    result = f"""
🔍 <b>Результат анализа</b>

{urgency_emoji} <b>Уровень токсичности:</b> {toxicity_score}/10
⚠️ <b>Степень опасности:</b> {urgency_level.upper()}

🚩 <b>Обнаруженные красные флаги:</b>
"""
    
    if red_flags:
        for flag in red_flags[:5]:  # Limit to 5 flags
            result += f"• {flag}\n"
    else:
        result += "• Серьезных красных флагов не обнаружено\n"
    
    if patterns:
        result += f"\n🎭 <b>Паттерны поведения:</b>\n"
        for pattern in patterns[:3]:  # Limit to 3 patterns
            result += f"• {pattern}\n"
    
    if analysis_text:
        result += f"\n📊 <b>Анализ:</b>\n{analysis_text[:400]}..."
    
    if recommendation:
        result += f"\n💡 <b>Рекомендация:</b>\n{recommendation[:300]}..."
    
    return result


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Create text progress bar
    
    Args:
        current: Current progress
        total: Total amount
        length: Length of progress bar
        
    Returns:
        Progress bar string
    """
    if total <= 0:
        return "▓" * length
    
    progress = min(1.0, current / total)
    filled = int(progress * length)
    
    bar = "▓" * filled + "░" * (length - filled)
    percentage = int(progress * 100)
    
    return f"{bar} {percentage}%"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {json_str[:100]}...")
        return default


def format_subscription_status(subscription_type: str, expires_at: Optional[datetime] = None) -> str:
    """
    Format subscription status for display
    
    Args:
        subscription_type: Type of subscription
        expires_at: Expiration date
        
    Returns:
        Formatted subscription status
    """
    emojis = {
        "free": "🆓",
        "premium": "💎", 
        "vip": "⭐"
    }
    
    emoji = emojis.get(subscription_type, "❓")
    status = f"{emoji} {subscription_type.title()}"
    
    if expires_at and subscription_type != "free":
        days_left = (expires_at - datetime.utcnow()).days
        if days_left > 0:
            status += f" (осталось {days_left} дн.)"
        else:
            status += " (истекла)"
    
    return status


async def safe_delete_message(message, delay: float = 0) -> bool:
    """
    Safely delete message with optional delay
    
    Args:
        message: Message to delete
        delay: Delay before deletion
        
    Returns:
        True if deleted successfully
    """
    try:
        if delay > 0:
            await asyncio.sleep(delay)
        
        await message.delete()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete message: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Filename
        
    Returns:
        File extension (lowercase)
    """
    if not filename or '.' not in filename:
        return ""
    
    return filename.split('.')[-1].lower()


def human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}" 