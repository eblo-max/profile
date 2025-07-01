"""
Состояния для машины состояний бота
"""
from telegram.ext import ConversationHandler


class AnalysisStates:
    """Состояния анализа"""
    
    # Основные состояния
    START = "start"
    MENU = "menu"
    
    # Сбор данных
    COLLECT_TEXT = "collect_text"
    COLLECT_IMAGES = "collect_images"
    COLLECT_SOCIAL = "collect_social"
    
    # Подтверждение
    CONFIRM_DATA = "confirm_data"
    
    # Обработка
    PROCESSING = "processing"
    
    # Результаты
    SHOW_RESULTS = "show_results"
    DETAILED_VIEW = "detailed_view"
    
    # Дополнительные функции
    HISTORY = "history"
    SETTINGS = "settings"
    
    # Завершение
    END = ConversationHandler.END


class DataCollectionStates:
    """Состояния сбора данных"""
    
    # Типы данных
    TEXT_INPUT = "text_input"
    TEXT_FILE = "text_file"
    
    IMAGE_UPLOAD = "image_upload"
    IMAGE_URL = "image_url"
    
    SOCIAL_PROFILE = "social_profile"
    SOCIAL_POSTS = "social_posts"
    
    # Дополнительная информация
    PERSONAL_INFO = "personal_info"
    CONTEXT_INFO = "context_info"


class ProcessingStates:
    """Состояния обработки"""
    
    # Этапы анализа
    WATSON_ANALYSIS = "watson_analysis"
    AZURE_ANALYSIS = "azure_analysis"
    GOOGLE_ANALYSIS = "google_analysis"
    AWS_ANALYSIS = "aws_analysis"
    
    CRYSTAL_ANALYSIS = "crystal_analysis"
    RECEPTIVITI_ANALYSIS = "receptiviti_analysis"
    LEXALYTICS_ANALYSIS = "lexalytics_analysis"
    MONKEYLEARN_ANALYSIS = "monkeylearn_analysis"
    
    # Синтез
    CLAUDE_SYNTHESIS = "claude_synthesis"
    
    # Валидация
    CROSS_VALIDATION = "cross_validation"
    CONFIDENCE_SCORING = "confidence_scoring"
    BIAS_DETECTION = "bias_detection"
    
    # Финализация
    REPORT_GENERATION = "report_generation"


class MenuStates:
    """Состояния меню"""
    
    MAIN_MENU = "main_menu"
    ANALYSIS_MENU = "analysis_menu"
    HISTORY_MENU = "history_menu"
    SETTINGS_MENU = "settings_menu"
    HELP_MENU = "help_menu" 