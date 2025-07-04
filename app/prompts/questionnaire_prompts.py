"""Questionnaire prompts for personality and compatibility analysis"""

# Partner Profiler Questions
PROFILER_QUESTIONS = {
    1: {
        "question": "Как ваш партнер обычно реагирует, когда вы не соглашаетесь с его мнением?",
        "description": "Опишите конкретные примеры реакций на несогласие"
    },
    2: {
        "question": "Как партнер относится к вашим друзьям и семье? Поощряет ли общение с ними?",
        "description": "Расскажите о его отношении к вашему окружению"
    },
    3: {
        "question": "Как ваш партнер ведет себя, когда злится или расстроен?",
        "description": "Опишите его поведение в конфликтных ситуациях"
    },
    4: {
        "question": "Уважает ли партнер ваши границы и личное пространство?",
        "description": "Приведите примеры соблюдения или нарушения границ"
    },
    5: {
        "question": "Как партнер относится к вашим успехам и достижениям?",
        "description": "Поддерживает ли он ваши цели и празднует успехи?"
    }
}

# Personality Type Questions  
PERSONALITY_QUESTIONS = {
    1: {
        "question": "Как вы обычно реагируете на критику или негативную обратную связь?",
        "options": [
            "Принимаю к сведению и работаю над улучшением",
            "Защищаюсь и объясняю свои действия", 
            "Расстраиваюсь, но потом анализирую",
            "Злюсь и считаю критику несправедливой"
        ]
    },
    2: {
        "question": "Что для вас важнее всего в отношениях?",
        "options": [
            "Взаимопонимание и эмоциональная близость",
            "Стабильность и надежность партнера",
            "Общие интересы и совместная деятельность",
            "Страсть и романтика"
        ]
    },
    3: {
        "question": "Как вы ведете себя в конфликтных ситуациях?",
        "options": [
            "Стараюсь найти компромисс и решить проблему",
            "Избегаю конфликтов и жду, пока всё уладится",
            "Открыто выражаю свои эмоции и мнение",
            "Анализирую ситуацию и ищу логичное решение"
        ]
    }
}

# Compatibility Test Questions
COMPATIBILITY_QUESTIONS = {
    1: {
        "question": "Как вы предпочитаете проводить свободное время?",
        "description": "Опишите ваши любимые виды отдыха и хобби"
    },
    2: {
        "question": "Что для вас означает идеальный вечер вдвоем?",
        "description": "Расскажите о ваших представлениях о качественном времени вместе"
    },
    3: {
        "question": "Как вы видите свое будущее через 5 лет?",
        "description": "Поделитесь вашими планами и мечтами на будущее"
    },
    4: {
        "question": "Что для вас важнее: карьера или семья? Почему?",
        "description": "Объясните ваши приоритеты и ценности"
    },
    5: {
        "question": "Как вы разрешаете конфликты в отношениях?",
        "description": "Опишите ваш подход к решению разногласий"
    }
}

# Question templates for dynamic generation
def get_profiler_question(question_id: int) -> dict:
    """Get profiler question by ID"""
    return PROFILER_QUESTIONS.get(question_id, {
        "question": "Вопрос не найден",
        "description": ""
    })

def get_personality_question(question_id: int) -> dict:
    """Get personality question by ID"""
    return PERSONALITY_QUESTIONS.get(question_id, {
        "question": "Вопрос не найден",
        "options": []
    })

def get_compatibility_question(question_id: int) -> dict:
    """Get compatibility question by ID"""
    return COMPATIBILITY_QUESTIONS.get(question_id, {
        "question": "Вопрос не найден", 
        "description": ""
    })

def format_profiler_questions() -> str:
    """Format all profiler questions for display"""
    questions_text = "🔍 **АНАЛИЗ ПАРТНЕРА**\n\n"
    questions_text += "Ответьте на следующие вопросы о вашем партнере максимально честно и подробно:\n\n"
    
    for q_id, q_data in PROFILER_QUESTIONS.items():
        questions_text += f"**{q_id}. {q_data['question']}**\n"
        questions_text += f"_{q_data['description']}_\n\n"
    
    return questions_text

def format_personality_questions() -> str:
    """Format personality questions for display"""
    questions_text = "🧠 **ОПРЕДЕЛЕНИЕ ТИПА ЛИЧНОСТИ**\n\n"
    
    for q_id, q_data in PERSONALITY_QUESTIONS.items():
        questions_text += f"**{q_id}. {q_data['question']}**\n"
        for i, option in enumerate(q_data['options'], 1):
            questions_text += f"{i}. {option}\n"
        questions_text += "\n"
    
    return questions_text

def format_compatibility_questions() -> str:
    """Format compatibility questions for display"""
    questions_text = "💕 **ТЕСТ НА СОВМЕСТИМОСТЬ**\n\n"
    questions_text += "Ответьте на вопросы от себя и от лица партнера:\n\n"
    
    for q_id, q_data in COMPATIBILITY_QUESTIONS.items():
        questions_text += f"**{q_id}. {q_data['question']}**\n"
        questions_text += f"_{q_data['description']}_\n\n"
    
    return questions_text

# Additional helper functions
def validate_profiler_answers(answers: dict) -> tuple[bool, str]:
    """Validate profiler answers completeness"""
    required_questions = list(PROFILER_QUESTIONS.keys())
    missing_questions = []
    
    for q_id in required_questions:
        if q_id not in answers or not answers[q_id].strip():
            missing_questions.append(q_id)
    
    if missing_questions:
        return False, f"Пропущены ответы на вопросы: {', '.join(map(str, missing_questions))}"
    
    return True, "Все ответы получены"

def validate_personality_answers(answers: dict) -> tuple[bool, str]:
    """Validate personality answers"""
    required_questions = list(PERSONALITY_QUESTIONS.keys())
    missing_questions = []
    
    for q_id in required_questions:
        if q_id not in answers:
            missing_questions.append(q_id)
    
    if missing_questions:
        return False, f"Пропущены ответы на вопросы: {', '.join(map(str, missing_questions))}"
    
    return True, "Все ответы получены"

def validate_compatibility_answers(user_answers: dict, partner_answers: dict) -> tuple[bool, str]:
    """Validate compatibility test answers"""
    required_questions = list(COMPATIBILITY_QUESTIONS.keys())
    
    # Check user answers
    missing_user = [q_id for q_id in required_questions if q_id not in user_answers or not user_answers[q_id].strip()]
    if missing_user:
        return False, f"Пропущены ваши ответы на вопросы: {', '.join(map(str, missing_user))}"
    
    # Check partner answers  
    missing_partner = [q_id for q_id in required_questions if q_id not in partner_answers or not partner_answers[q_id].strip()]
    if missing_partner:
        return False, f"Пропущены ответы партнера на вопросы: {', '.join(map(str, missing_partner))}"
    
    return True, "Все ответы получены"

# Sample answers for testing
SAMPLE_PROFILER_ANSWERS = {
    1: "Обычно он спокойно выслушивает мое мнение, но иногда может настаивать на своем. В целом уважает мою точку зрения.",
    2: "Хорошо относится к моим друзьям, иногда мы все вместе проводим время. С семьей отношения теплые.",
    3: "Когда злится, может повысить голос, но потом извиняется. Старается контролировать эмоции.",
    4: "В основном да, но иногда может быть навязчивым, когда хочет больше внимания.",
    5: "Всегда поддерживает мои успехи, гордится мной и помогает достигать целей."
}

SAMPLE_COMPATIBILITY_ANSWERS = {
    "user": {
        1: "Люблю читать книги, смотреть фильмы, заниматься йогой. Ценю спокойный отдых дома.",
        2: "Уютный ужин дома, интересные разговоры, может быть фильм или настольные игры.",
        3: "Вижу себя в стабильных отношениях, возможно с детьми, развитие в карьере.",
        4: "Считаю, что важен баланс. Семья дает смысл, но карьера - это самореализация.",
        5: "Предпочитаю открытый разговор, выяснение позиций и поиск компромисса."
    },
    "partner": {
        1: "Активный отдых, спорт, путешествия. Не люблю сидеть дома без дела.",
        2: "Романтический ужин в ресторане, прогулка по городу, новые впечатления.",
        3: "Хочу путешествовать, открыть свой бизнес, жить яркой насыщенной жизнью.",
        4: "Карьера на первом месте, семья потом. Нужно сначала добиться успеха.",
        5: "Не люблю долгие разговоры о проблемах, лучше отвлечься и забыть."
    }
} 