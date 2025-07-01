"""
Состояния для машины состояний бота
"""
from telegram.ext import ConversationHandler


class AnalysisStates:
    """Состояния анализа"""
    
    # Основные состояния
    START = 0
    MENU = 1
    
    # Сбор данных
    COLLECT_TEXT = 10
    COLLECT_IMAGES = 11
    COLLECT_SOCIAL = 12
    
    # Подтверждение
    CONFIRM_DATA = 20
    
    # Обработка
    PROCESSING = 30
    
    # Результаты
    SHOW_RESULTS = 40
    DETAILED_VIEW = 41
    
    # Дополнительные функции
    HISTORY = 50
    SETTINGS = 51
    
    # Завершение
    END = ConversationHandler.END


class DataCollectionStates:
    """Состояния сбора данных"""
    
    # Типы данных
    TEXT_INPUT = 100
    TEXT_FILE = 101
    
    IMAGE_UPLOAD = 110
    IMAGE_URL = 111
    
    SOCIAL_PROFILE = 120
    SOCIAL_POSTS = 121
    
    # Дополнительная информация
    PERSONAL_INFO = 130
    CONTEXT_INFO = 131


class ProcessingStates:
    """Состояния обработки"""
    
    # Этапы анализа
    WATSON_ANALYSIS = 200
    AZURE_ANALYSIS = 201
    GOOGLE_ANALYSIS = 202
    AWS_ANALYSIS = 203
    
    CRYSTAL_ANALYSIS = 210
    RECEPTIVITI_ANALYSIS = 211
    LEXALYTICS_ANALYSIS = 212
    MONKEYLEARN_ANALYSIS = 213
    
    # Синтез
    CLAUDE_SYNTHESIS = 220
    
    # Валидация
    CROSS_VALIDATION = 230
    CONFIDENCE_SCORING = 231
    BIAS_DETECTION = 232
    
    # Финализация
    REPORT_GENERATION = 240


class MenuStates:
    """Состояния меню"""
    
    MAIN_MENU = 300
    ANALYSIS_MENU = 301
    HISTORY_MENU = 302
    SETTINGS_MENU = 303
    HELP_MENU = 304 