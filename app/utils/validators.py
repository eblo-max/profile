"""Validators for input data"""

import re
from typing import Optional, List, Dict, Any

from app.utils.constants import (
    MAX_TEXT_LENGTH, MIN_TEXT_LENGTH, MAX_FILE_SIZE, 
    PHONE_PATTERN, EMAIL_PATTERN
)
from app.utils.exceptions import (
    TextTooLongError, TextTooShortError, InvalidFileFormatError,
    FileTooLargeError, ValidationError
)


def validate_text_length(
    text: str,
    min_length: int = MIN_TEXT_LENGTH,
    max_length: int = MAX_TEXT_LENGTH
) -> str:
    """
    Validate text length
    
    Args:
        text: Text to validate
        min_length: Minimum required length
        max_length: Maximum allowed length
        
    Returns:
        Validated text
        
    Raises:
        TextTooShortError: If text is too short
        TextTooLongError: If text is too long
    """
    if not text or len(text.strip()) < min_length:
        raise TextTooShortError(min_length)
    
    if len(text) > max_length:
        raise TextTooLongError(max_length)
    
    return text.strip()


def validate_phone_number(phone: str) -> str:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Validated phone number
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone:
        raise ValidationError("Phone number is required")
    
    phone = phone.strip()
    if not re.match(PHONE_PATTERN, phone):
        raise ValidationError("Invalid phone number format")
    
    return phone


def validate_email(email: str) -> str:
    """
    Validate email format
    
    Args:
        email: Email to validate
        
    Returns:
        Validated email
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email is required")
    
    email = email.strip().lower()
    if not re.match(EMAIL_PATTERN, email):
        raise ValidationError("Invalid email format")
    
    return email


def validate_telegram_user_id(user_id: int) -> int:
    """
    Validate Telegram user ID
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Validated user ID
        
    Raises:
        ValidationError: If user ID is invalid
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError("Invalid user ID")
    
    # Telegram user IDs are typically 9-10 digits
    if user_id < 1000000 or user_id > 9999999999:
        raise ValidationError("Invalid Telegram user ID range")
    
    return user_id


def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> int:
    """
    Validate file size
    
    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        Validated file size
        
    Raises:
        FileTooLargeError: If file is too large
    """
    if file_size > max_size:
        raise FileTooLargeError(max_size)
    
    return file_size


def validate_file_format(filename: str, allowed_formats: List[str]) -> str:
    """
    Validate file format
    
    Args:
        filename: Name of the file
        allowed_formats: List of allowed file extensions
        
    Returns:
        Validated filename
        
    Raises:
        InvalidFileFormatError: If file format is not allowed
    """
    if not filename:
        raise ValidationError("Filename is required")
    
    file_extension = filename.lower().split('.')[-1]
    if file_extension not in [fmt.lower() for fmt in allowed_formats]:
        raise InvalidFileFormatError(allowed_formats)
    
    return filename


def validate_analysis_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate analysis data structure
    
    Args:
        data: Analysis data to validate
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If data structure is invalid
    """
    required_fields = ["text", "user_id"]
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate text
    data["text"] = validate_text_length(data["text"])
    
    # Validate user ID
    data["user_id"] = validate_telegram_user_id(data["user_id"])
    
    return data


def validate_personality_answers(answers: Dict[int, str]) -> Dict[int, str]:
    """
    Validate personality questionnaire answers
    
    Args:
        answers: Dictionary of question_id -> answer
        
    Returns:
        Validated answers
        
    Raises:
        ValidationError: If answers are invalid
    """
    if not answers:
        raise ValidationError("Answers are required")
    
    # Validate we have answers for questions 1, 2, 3
    required_questions = [1, 2, 3]
    for question_id in required_questions:
        if question_id not in answers:
            raise ValidationError(f"Missing answer for question {question_id}")
        
        answer = answers[question_id]
        if not answer or not answer.strip():
            raise ValidationError(f"Empty answer for question {question_id}")
        
        # Validate answer length
        if len(answer) > 500:
            raise ValidationError(f"Answer for question {question_id} is too long")
    
    return answers


def validate_compatibility_answers(
    user_answers: Dict[int, str],
    partner_answers: Dict[int, str]
) -> tuple[Dict[int, str], Dict[int, str]]:
    """
    Validate compatibility test answers
    
    Args:
        user_answers: User's answers
        partner_answers: Partner's answers
        
    Returns:
        Tuple of validated answers
        
    Raises:
        ValidationError: If answers are invalid
    """
    # Validate both sets of answers have 5 questions
    required_questions = [1, 2, 3, 4, 5]
    
    for question_id in required_questions:
        # Check user answers
        if question_id not in user_answers:
            raise ValidationError(f"Missing user answer for question {question_id}")
        
        user_answer = user_answers[question_id]
        if not user_answer or not user_answer.strip():
            raise ValidationError(f"Empty user answer for question {question_id}")
        
        # Check partner answers
        if question_id not in partner_answers:
            raise ValidationError(f"Missing partner answer for question {question_id}")
        
        partner_answer = partner_answers[question_id]
        if not partner_answer or not partner_answer.strip():
            raise ValidationError(f"Empty partner answer for question {question_id}")
        
        # Validate answer length
        if len(user_answer) > 500:
            raise ValidationError(f"User answer for question {question_id} is too long")
        
        if len(partner_answer) > 500:
            raise ValidationError(f"Partner answer for question {question_id} is too long")
    
    return user_answers, partner_answers


def validate_profiler_answers(answers: Dict[int, str]) -> Dict[int, str]:
    """
    Validate partner profiler answers
    
    Args:
        answers: Dictionary of question_id -> answer
        
    Returns:
        Validated answers
        
    Raises:
        ValidationError: If answers are invalid
    """
    if not answers:
        raise ValidationError("Profiler answers are required")
    
    # Validate we have answers for questions 1-5
    required_questions = [1, 2, 3, 4, 5]
    for question_id in required_questions:
        if question_id not in answers:
            raise ValidationError(f"Missing profiler answer for question {question_id}")
        
        answer = answers[question_id]
        if not answer or not answer.strip():
            raise ValidationError(f"Empty profiler answer for question {question_id}")
        
        # Validate answer length (profiler answers can be longer)
        if len(answer) > 1000:
            raise ValidationError(f"Profiler answer for question {question_id} is too long")
    
    return answers


def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Remove potentially dangerous HTML/script tags
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<style[^>]*>.*?</style>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text.strip()


def validate_subscription_type(subscription_type: str) -> str:
    """
    Validate subscription type
    
    Args:
        subscription_type: Subscription type to validate
        
    Returns:
        Validated subscription type
        
    Raises:
        ValidationError: If subscription type is invalid
    """
    from app.utils.enums import SubscriptionType
    
    valid_types = [s.value for s in SubscriptionType]
    
    if subscription_type not in valid_types:
        raise ValidationError(f"Invalid subscription type. Valid types: {valid_types}")
    
    return subscription_type


def validate_urgency_level(urgency: str) -> str:
    """
    Validate urgency level
    
    Args:
        urgency: Urgency level to validate
        
    Returns:
        Validated urgency level
        
    Raises:
        ValidationError: If urgency level is invalid
    """
    from app.utils.enums import UrgencyLevel
    
    valid_levels = [u.value for u in UrgencyLevel]
    
    if urgency not in valid_levels:
        raise ValidationError(f"Invalid urgency level. Valid levels: {valid_levels}")
    
    return urgency 