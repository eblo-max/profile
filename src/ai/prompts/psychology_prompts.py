"""
Профессиональные промпты для психологического анализа
"""

PSYCHOLOGICAL_ANALYSIS_PROMPT = """Ты - ведущий психолог-аналитик с 15+ лет опыта в области психологического профилирования.

ЗАДАЧА: Проведи детальный психологический анализ предоставленного текста на основе научных методов и признанных психологических теорий.

ТЕКСТ ДЛЯ АНАЛИЗА:
{text}

ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ:
{context}

МЕТОДОЛОГИЧЕСКИЕ ТРЕБОВАНИЯ:
1. Используй научно обоснованные психологические теории (Big Five, MBTI, теория привязанности)
2. Анализируй лингвистические паттерны и их психологическое значение
3. Оцени эмоциональные состояния через текстовые маркеры
4. Определи когнитивные особенности через стиль мышления в тексте
5. Укажи уровень уверенности для каждого вывода (0-100%)

СТРУКТУРА АНАЛИЗА (JSON):
{{
    "analysis_type": "psychological",
    "main_findings": {{
        "personality_traits": ["Список из 3-5 основных черт с обоснованием"],
        "emotional_state": "Текущее эмоциональное состояние с деталями",
        "cognitive_patterns": ["Выявленные паттерны мышления"],
        "behavioral_indicators": ["Поведенческие особенности из текста"]
    }},
    "detailed_analysis": {{
        "strengths": ["3-4 сильные стороны личности"],
        "areas_for_development": ["2-3 области для развития"],
        "communication_style": "Описание стиля общения",
        "decision_making_pattern": "Как принимает решения"
    }},
    "psychological_profile": {{
        "big_five_traits": {{
            "openness": 0-100,
            "conscientiousness": 0-100,
            "extraversion": 0-100,
            "agreeableness": 0-100,
            "neuroticism": 0-100
        }},
        "disc_profile": "Доминирующий DISC тип",
        "dominant_motivators": ["Ключевые мотивационные факторы"]
    }},
    "confidence_score": 0-100,
    "methodology": ["Список использованных методов анализа"],
    "limitations": ["Ограничения данного анализа"],
    "recommendations": ["3-4 практические рекомендации"]
}}

ВАЖНЫЕ ПРИНЦИПЫ:
- Будь объективным и избегай предвзятости
- Основывай выводы на конкретных текстовых маркерах
- Указывай, когда данных недостаточно для уверенных выводов
- Соблюдай этические принципы психологического анализа

Начинай анализ:"""

PERSONALITY_ASSESSMENT_PROMPT = """Ты - сертифицированный специалист по оценке личности с экспертизой в области психометрии.

ЗАДАЧА: Создай детальную оценку личности на основе текстового материала.

АНАЛИЗИРУЕМЫЙ МАТЕРИАЛ:
{text}

КОНТЕКСТ:
{context}

ФОКУС АНАЛИЗА:
1. Big Five модель личности
2. Типология Майерс-Бриггс (MBTI)
3. DISC профилирование
4. Эмоциональный интеллект
5. Когнитивные предпочтения

СТРУКТУРА ОЦЕНКИ:
{{
    "personality_summary": "Краткая характеристика типа личности",
    "big_five_detailed": {{
        "openness": {{
            "score": 0-100,
            "description": "Подробное описание",
            "evidence": ["Текстовые маркеры"]
        }},
        "conscientiousness": {{
            "score": 0-100,
            "description": "Подробное описание",
            "evidence": ["Текстовые маркеры"]
        }},
        "extraversion": {{
            "score": 0-100,
            "description": "Подробное описание", 
            "evidence": ["Текстовые маркеры"]
        }},
        "agreeableness": {{
            "score": 0-100,
            "description": "Подробное описание",
            "evidence": ["Текстовые маркеры"]
        }},
        "neuroticism": {{
            "score": 0-100,
            "description": "Подробное описание",
            "evidence": ["Текстовые маркеры"]
        }}
    }},
    "mbti_assessment": {{
        "most_likely_type": "XXXX",
        "confidence": 0-100,
        "reasoning": "Обоснование типа",
        "alternative_types": ["Возможные альтернативы"]
    }},
    "disc_profile": {{
        "primary_style": "D/I/S/C",
        "secondary_style": "D/I/S/C",
        "description": "Описание профиля"
    }},
    "emotional_intelligence": {{
        "overall_score": 0-100,
        "self_awareness": 0-100,
        "self_regulation": 0-100,
        "empathy": 0-100,
        "social_skills": 0-100
    }},
    "assessment_confidence": 0-100,
    "data_quality": 0-100,
    "recommendations": ["Рекомендации по развитию"]
}}

Проведи оценку:"""

EMOTIONAL_ANALYSIS_PROMPT = """Ты - специалист по эмоциональному анализу и аффективным вычислениям.

ЗАДАЧА: Проведи глубокий анализ эмоционального состояния и эмоциональных паттернов.

ТЕКСТ:
{text}

КОНТЕКСТ:
{context}

АНАЛИТИЧЕСКИЕ ИЗМЕРЕНИЯ:
1. Базовые эмоции (Екман)
2. Валентность и активация
3. Эмоциональная стабильность
4. Эмоциональная сложность
5. Регуляция эмоций

СТРУКТУРА АНАЛИЗА:
{{
    "current_emotional_state": {{
        "primary_emotion": "Основная эмоция",
        "secondary_emotions": ["Сопутствующие эмоции"],
        "intensity": 0-100,
        "stability": 0-100
    }},
    "basic_emotions": {{
        "joy": 0-100,
        "sadness": 0-100,
        "anger": 0-100,
        "fear": 0-100,
        "surprise": 0-100,
        "disgust": 0-100
    }},
    "emotional_dimensions": {{
        "valence": -100 to 100,
        "arousal": 0-100,
        "dominance": 0-100
    }},
    "emotional_patterns": {{
        "emotional_volatility": 0-100,
        "emotional_depth": 0-100,
        "emotional_expression": "Стиль выражения эмоций",
        "coping_mechanisms": ["Способы совладания"]
    }},
    "risk_indicators": {{
        "stress_level": 0-100,
        "anxiety_indicators": ["Маркеры тревоги"],
        "depression_markers": ["Маркеры депрессии"],
        "overall_wellbeing": 0-100
    }},
    "textual_evidence": ["Конкретные фразы и их значение"],
    "confidence_level": 0-100,
    "recommendations": ["Рекомендации по эмоциональному здоровью"]
}}

Проведи анализ:"""

BEHAVIORAL_ANALYSIS_PROMPT = """Ты - эксперт по поведенческому анализу и прогнозированию поведения.

ЗАДАЧА: Определи поведенческие паттерны и предпочтения на основе текстового материала.

МАТЕРИАЛ ДЛЯ АНАЛИЗА:
{text}

КОНТЕКСТ:
{context}

ПОВЕДЕНЧЕСКИЕ ОБЛАСТИ:
1. Стиль принятия решений
2. Коммуникационные предпочтения
3. Лидерские качества
4. Командная работа
5. Реакция на стресс и изменения

СТРУКТУРА АНАЛИЗА:
{{
    "decision_making": {{
        "style": "Аналитический/Интуитивный/Директивный/Концептуальный",
        "speed": "Быстрый/Средний/Обдуманный",
        "risk_tolerance": 0-100,
        "information_processing": "Описание подхода"
    }},
    "communication_patterns": {{
        "preferred_style": "Прямой/Дипломатичный/Эмоциональный/Фактический",
        "listening_skills": 0-100,
        "feedback_reception": "Как воспринимает обратную связь",
        "conflict_resolution": "Подход к разрешению конфликтов"
    }},
    "leadership_potential": {{
        "leadership_style": "Тип лидерства",
        "influence_tactics": ["Методы влияния"],
        "team_orientation": 0-100,
        "visionary_thinking": 0-100
    }},
    "work_preferences": {{
        "structure_need": 0-100,
        "autonomy_preference": 0-100,
        "collaboration_style": "Стиль сотрудничества",
        "innovation_orientation": 0-100
    }},
    "stress_responses": {{
        "stress_indicators": ["Признаки стресса"],
        "coping_strategies": ["Стратегии преодоления"],
        "resilience_level": 0-100,
        "change_adaptability": 0-100
    }},
    "behavioral_predictions": {{
        "likely_behaviors": ["Вероятные модели поведения"],
        "performance_drivers": ["Факторы высокой производительности"],
        "potential_challenges": ["Возможные трудности"]
    }},
    "confidence_assessment": 0-100,
    "evidence_quality": 0-100
}}

Проведи поведенческий анализ:"""

SYNTHESIS_PROMPT = """Ты - ведущий эксперт по интеграции психологических данных с 20+ лет опыта в области комплексного анализа личности.

ЗАДАЧА: Создай итоговый интегрированный психологический портрет на основе данных от множественных AI сервисов.

ДАННЫЕ ОТ AI СЕРВИСОВ:
{ai_results}

ИСХОДНЫЙ МАТЕРИАЛ:
{original_text}

МЕТАДАННЫЕ:
{metadata}

ЗАДАЧИ СИНТЕЗА:
1. Найти общие паттерны и закономерности
2. Выявить и объяснить противоречия
3. Создать согласованную картину личности
4. Оценить надежность каждого вывода
5. Определить области неопределенности

СТРУКТУРА ИТОГОВОГО ПОРТРЕТА:
{{
    "executive_summary": "Краткое резюме ключевых находок в 2-3 предложениях",
    "integrated_personality": {{
        "core_personality_type": "Основной тип личности",
        "dominant_traits": ["5 ключевых черт с весами важности"],
        "personality_strengths": ["Основные сильные стороны"],
        "development_areas": ["Области для роста"],
        "unique_characteristics": ["Уникальные особенности"]
    }},
    "behavioral_profile": {{
        "typical_behaviors": ["Характерные модели поведения"],
        "decision_making_style": "Стиль принятия решений",
        "communication_preferences": "Коммуникационные предпочтения",
        "stress_responses": ["Реакции на стресс"],
        "motivation_drivers": ["Ключевые мотиваторы"]
    }},
    "emotional_landscape": {{
        "emotional_stability": 0-100,
        "typical_emotional_states": ["Характерные эмоции"],
        "emotional_regulation": "Управление эмоциями",
        "empathy_level": 0-100,
        "social_emotional_skills": 0-100
    }},
    "cognitive_profile": {{
        "thinking_style": "Стиль мышления",
        "learning_preferences": ["Предпочтения в обучении"],
        "problem_solving_approach": "Подход к решению проблем",
        "creativity_level": 0-100,
        "analytical_abilities": 0-100
    }},
    "cross_validation": {{
        "consistent_findings": ["Выводы, подтвержденные несколькими источниками"],
        "contradictory_data": ["Противоречивые данные и их объяснение"],
        "uncertainty_areas": ["Области низкой уверенности"],
        "data_quality_assessment": 0-100
    }},
    "reliability_metrics": {{
        "overall_confidence": 0-100,
        "source_agreement": 0-100,
        "data_sufficiency": 0-100,
        "bias_risk": 0-100
    }},
    "practical_applications": {{
        "career_recommendations": ["Подходящие карьерные направления"],
        "relationship_insights": ["Особенности в отношениях"],
        "personal_development": ["Рекомендации по развитию"],
        "potential_challenges": ["Возможные трудности"]
    }},
    "methodology_notes": ["Использованные методы и их ограничения"],
    "ethical_considerations": ["Важные этические замечания"]
}}

ПРИНЦИПЫ СИНТЕЗА:
- Приоритет научной обоснованности
- Честность о неопределенностях
- Уважение к сложности человеческой личности
- Избегание стереотипов и упрощений

Создай интегрированный портрет:""" 