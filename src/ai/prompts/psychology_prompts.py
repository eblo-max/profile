"""
Простые и надежные промпты для психологического анализа
"""

PSYCHOLOGICAL_ANALYSIS_PROMPT = """Ты психолог. Проанализируй этот текст и верни результат СТРОГО в JSON формате.

ТЕКСТ: {text}

Верни ответ в формате JSON:
{{
    "hook_summary": "Краткая интересная особенность личности",
    "personality_core": {{
        "essence": "Суть личности в 1-2 предложениях",
        "unique_traits": ["черта 1", "черта 2", "черта 3"],
        "hidden_depths": "Что скрывается за внешним проявлением"
    }},
    "main_findings": {{
        "thinking_style": "Как думает этот человек",
        "emotional_signature": "Эмоциональные особенности",
        "behavioral_patterns": ["паттерн 1", "паттерн 2"]
    }},
    "big_five_detailed": {{
        "openness": {{"score": 75, "description": "Описание открытости"}},
        "conscientiousness": {{"score": 65, "description": "Описание организованности"}},
        "extraversion": {{"score": 55, "description": "Описание общительности"}},
        "agreeableness": {{"score": 70, "description": "Описание доброжелательности"}},
        "neuroticism": {{"score": 45, "description": "Описание эмоциональности"}}
    }},
    "life_insights": {{
        "career_strengths": ["сила 1", "сила 2"],
        "ideal_environment": "Идеальная среда для работы",
        "relationship_patterns": "Паттерны в отношениях",
        "growth_areas": ["область роста 1", "область роста 2"]
    }},
    "actionable_recommendations": {{
        "immediate_actions": ["совет 1", "совет 2", "совет 3"],
        "personal_development": ["развитие 1", "развитие 2"],
        "career_guidance": ["карьерный совет 1", "карьерный совет 2"]
    }},
    "fascinating_details": {{
        "psychological_archetype": "Архетип личности",
        "hidden_talents": ["талант 1", "талант 2"],
        "core_values": ["ценность 1", "ценность 2"]
    }},
    "confidence_score": 85
}}

ВАЖНО: Отвечай ТОЛЬКО JSON, без дополнительного текста!"""

PERSONALITY_ASSESSMENT_PROMPT = """Анализируй личность. Верни только JSON.

ТЕКСТ: {text}

JSON ответ:
{{
    "personality_type": "Тип личности",
    "big_five": {{
        "openness": 75,
        "conscientiousness": 65,
        "extraversion": 55,
        "agreeableness": 70,
        "neuroticism": 45
    }},
    "strengths": ["сила 1", "сила 2"],
    "areas_for_growth": ["область 1", "область 2"],
    "confidence_score": 80
}}"""

EMOTIONAL_ANALYSIS_PROMPT = """Анализируй эмоции в тексте. Только JSON.

ТЕКСТ: {text}

JSON:
{{
    "dominant_emotion": "радость",
    "emotional_intensity": 75,
    "emotional_stability": 65,
    "emotions_detected": ["эмоция1", "эмоция2"],
    "confidence_score": 80
}}"""

BEHAVIORAL_ANALYSIS_PROMPT = """Анализируй поведенческие паттерны. Только JSON.

ТЕКСТ: {text}

JSON:
{{
    "behavioral_style": "Описание стиля поведения",
    "decision_making": "Как принимает решения",
    "social_behavior": "Социальное поведение",
    "patterns": ["паттерн 1", "паттерн 2"],
    "confidence_score": 75
}}"""

SYNTHESIS_PROMPT = """Объедини результаты анализов в единый портрет.

РЕЗУЛЬТАТЫ: {ai_results}
ТЕКСТ: {original_text}

JSON ответ:
{{
    "synthesized_profile": "Объединенный профиль личности",
    "key_insights": ["инсайт 1", "инсайт 2"],
    "combined_big_five": {{
        "openness": 75,
        "conscientiousness": 65,
        "extraversion": 55,
        "agreeableness": 70,
        "neuroticism": 45
    }},
    "final_recommendations": ["рекомендация 1", "рекомендация 2"],
    "confidence_score": 85
}}"""

MULTI_AI_SYNTHESIS_PROMPT = """Создай финальный психологический портрет на основе данных от нескольких AI.

ДАННЫЕ ОТ AI: {ai_results}
ОРИГИНАЛЬНЫЙ ТЕКСТ: {original_text}

Верни JSON:
{{
    "hook_summary": "Захватывающее описание личности",
    "personality_core": {{
        "essence": "Суть личности",
        "unique_traits": ["уникальная черта 1", "уникальная черта 2"],
        "hidden_depths": "Скрытые глубины"
    }},
    "detailed_insights": {{
        "thinking_style": {{
            "description": "Стиль мышления",
            "strengths": "Сильные стороны"
        }},
        "emotional_world": {{
            "current_state": "Эмоциональное состояние",
            "emotional_patterns": ["паттерн 1", "паттерн 2"]
        }}
    }},
    "life_insights": {{
        "career_strengths": ["сила 1", "сила 2"],
        "ideal_environment": "Идеальная среда"
    }},
    "actionable_recommendations": {{
        "immediate_actions": ["действие 1", "действие 2"],
        "personal_development": ["развитие 1", "развитие 2"]
    }},
    "confidence_score": 90
}}

ОТВЕЧАЙ ТОЛЬКО JSON!""" 