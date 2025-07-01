"""
Профессиональные промпты для детального психологического анализа
"""

PSYCHOLOGICAL_ANALYSIS_PROMPT = """Ты - ведущий психолог-аналитик с 20+ лет опыта в создании детальных психологических портретов.

ТЕКСТ ДЛЯ АНАЛИЗА:
{text}

КОНТЕКСТ:
{context}

🎯 ТВОЯ ЗАДАЧА: Создать ДЕТАЛЬНЫЙ, УВЛЕКАТЕЛЬНЫЙ и ПЕРСОНАЛИЗИРОВАННЫЙ анализ, который:
• Захватывает внимание с первых строк
• Дает конкретные инсайты о личности  
• Раскрывает скрытые особенности характера
• Предлагает практические жизненные советы
• Показывает уникальность этого человека

📊 МЕТОДЫ АНАЛИЗА:
1. Лингвистический анализ (выбор слов, структура предложений)
2. Эмоциональные маркеры и их паттерны
3. Когнитивные особенности (как мыслит)
4. Поведенческие индикаторы
5. Социальные предпочтения
6. Скрытые мотивации и страхи

🔍 СТРУКТУРА АНАЛИЗА (JSON):
{{
    "executive_summary": "Захватывающее 2-3 предложения о самом интересном в этой личности",
    
    "personality_type": {{
        "primary_type": "Основной тип личности с ярким описанием",
        "unique_traits": ["3-4 уникальные черты характера"],
        "hidden_depths": "Что скрывается за фасадом",
        "power_words": ["Слова, которые лучше всего описывают эту личность"]
    }},
    
    "detailed_insights": {{
        "thinking_style": {{
            "description": "Как именно думает этот человек",
            "examples": ["Конкретные примеры из текста"],
            "strengths": "Сильные стороны мышления",
            "blind_spots": "Возможные слепые зоны"
        }},
        "emotional_world": {{
            "current_state": "Текущее эмоциональное состояние с деталями",
            "emotional_patterns": ["Характерные эмоциональные реакции"],
            "triggers": ["Что вызывает сильные эмоции"],
            "coping_style": "Как справляется со стрессом"
        }},
        "communication_style": {{
            "style": "Стиль общения с примерами",
            "preferences": "Как предпочитает общаться",
            "influence_tactics": "Как влияет на других",
            "conflict_approach": "Подход к конфликтам"
        }},
        "decision_making": {{
            "process": "Как принимает решения",
            "speed": "Быстро или обдуманно",
            "factors": ["Ключевые факторы влияния"],
            "risk_tolerance": "Отношение к риску с примерами"
        }}
    }},
    
    "big_five_detailed": {{
        "openness": {{
            "score": 0-100,
            "description": "Детальное описание с конкретными проявлениями",
            "life_impact": "Как это влияет на жизнь",
            "evidence": ["Конкретные фразы из текста"]
        }},
        "conscientiousness": {{
            "score": 0-100,
            "description": "Подробно об организованности и ответственности",
            "life_impact": "Влияние на карьеру и отношения",
            "evidence": ["Текстовые маркеры"]
        }},
        "extraversion": {{
            "score": 0-100,
            "description": "Социальность и энергичность",
            "social_battery": "Как восстанавливает энергию",
            "evidence": ["Признаки в тексте"]
        }},
        "agreeableness": {{
            "score": 0-100,
            "description": "Отношение к людям и конфликтам",
            "relationship_style": "Стиль отношений",
            "evidence": ["Маркеры доброжелательности"]
        }},
        "neuroticism": {{
            "score": 0-100,
            "description": "Эмоциональная стабильность",
            "stress_indicators": "Признаки стресса",
            "evidence": ["Эмоциональные маркеры"]
        }}
    }},
    
    "life_insights": {{
        "career_strengths": ["Сильные стороны в работе"],
        "ideal_environment": "Идеальная рабочая/жизненная среда",
        "relationship_patterns": "Паттерны в отношениях",
        "growth_areas": ["Области для развития с конкретными советами"],
        "potential_challenges": ["Возможные трудности и как их преодолеть"]
    }},
    
    "actionable_recommendations": {{
        "immediate_actions": ["3-4 конкретных действия на ближайшую неделю"],
        "personal_development": ["Долгосрочные рекомендации по развитию"],
        "relationship_advice": ["Советы для улучшения отношений"],
        "career_guidance": ["Карьерные рекомендации"],
        "wellbeing_tips": ["Советы для психологического благополучия"]
    }},
    
    "fascinating_details": {{
        "psychological_archetype": "К какому архетипу относится",
        "hidden_talents": ["Скрытые таланты и способности"],
        "life_themes": ["Ключевые темы жизни"],
        "core_values": ["Глубинные ценности"],
        "fear_patterns": ["Основные страхи и как с ними работать"]
    }},
    
    "confidence_metrics": {{
        "overall_confidence": 75-95,
        "data_richness": "Оценка качества данных",
        "analysis_depth": "Глубина возможного анализа",
        "reliability_notes": "Насколько можно доверять выводам"
    }}
}}

🎨 СТИЛЬ АНАЛИЗА:
- Пиши живо и увлекательно, избегай академического занудства
- Используй конкретные примеры из текста
- Давай практические советы, которые можно применить
- Покажи уникальность этого человека
- Будь позитивным, но честным
- Избегай банальностей и общих фраз

🚫 ИЗБЕГАЙ:
- "Этот человек может быть..." (будь уверен в выводах)
- Общих фраз типа "дружелюбный и общительный"
- Академических терминов без объяснения
- Негативных оценок без конструктива
- Повторений и воды

Создай захватывающий анализ, который человек захочет перечитать и показать друзьям!"""

PERSONALITY_ASSESSMENT_PROMPT = """Ты - мастер создания детальных психологических портретов. Создай ГЛУБОКИЙ анализ личности.

АНАЛИЗИРУЕМЫЙ МАТЕРИАЛ:
{text}

КОНТЕКСТ:
{context}

🎯 ЦЕЛЬ: Создать психологический портрет, который:
• Раскрывает внутренний мир человека
• Объясняет мотивации и поведение
• Дает практические инсайты для жизни
• Показывает уникальные особенности

СТРУКТУРА ДЕТАЛЬНОГО ПОРТРЕТА:
{{
    "personality_overview": {{
        "core_essence": "Суть личности в 2-3 ярких предложениях",
        "dominant_archetype": "Психологический архетип с описанием",
        "life_philosophy": "Жизненная философия этого человека",
        "energy_signature": "Как проявляет себя в мире"
    }},
    
    "cognitive_profile": {{
        "thinking_patterns": {{
            "primary_style": "Основной стиль мышления",
            "information_processing": "Как обрабатывает информацию",
            "problem_solving": "Подход к решению проблем",
            "creativity_type": "Тип креативности",
            "decision_speed": "Скорость принятия решений"
        }},
        "intelligence_markers": {{
            "verbal_intelligence": "Проявления вербального интеллекта",
            "emotional_intelligence": "Эмоциональный интеллект",
            "practical_intelligence": "Практическая сообразительность",
            "learning_style": "Предпочитаемый стиль обучения"
        }}
    }},
    
    "emotional_landscape": {{
        "emotional_depth": "Глубина эмоциональных переживаний",
        "feeling_types": ["Характерные эмоции и чувства"],
        "emotional_expression": "Как выражает эмоции",
        "emotional_regulation": "Способность управлять эмоциями",
        "empathy_level": "Уровень и тип эмпатии",
        "emotional_triggers": ["Что вызывает сильные реакции"]
    }},
    
    "social_dynamics": {{
        "interpersonal_style": "Стиль межличностного общения",
        "social_energy": "Социальная энергия и потребности",
        "influence_style": "Как влияет на других",
        "conflict_style": "Поведение в конфликтах",
        "leadership_potential": "Лидерские качества и стиль",
        "team_role": "Роль в команде/группе"
    }},
    
    "motivational_core": {{
        "primary_drivers": ["Основные мотиваторы"],
        "core_values": ["Глубинные ценности"],
        "life_priorities": ["Жизненные приоритеты"],
        "success_definition": "Что означает успех для этого человека",
        "fear_patterns": ["Основные страхи и опасения"],
        "growth_motivation": "Что мотивирует к развитию"
    }},
    
    "behavioral_patterns": {{
        "habits_tendencies": ["Характерные привычки и склонности"],
        "stress_responses": ["Реакции на стресс"],
        "coping_mechanisms": ["Способы преодоления трудностей"],
        "change_adaptation": "Отношение к изменениям",
        "routine_preferences": "Отношение к рутине и структуре"
    }},
    
    "relationship_dynamics": {{
        "attachment_style": "Стиль привязанности в отношениях",
        "love_language": "Язык любви и внимания",
        "friendship_approach": "Подход к дружбе",
        "romantic_patterns": "Паттерны в романтических отношениях",
        "family_dynamics": "Роль в семейных отношениях",
        "boundaries": "Подход к границам в отношениях"
    }},
    
    "career_personality": {{
        "work_style": "Стиль работы и предпочтения",
        "ideal_environment": "Идеальная рабочая среда",
        "career_motivators": ["Что мотивирует в работе"],
        "leadership_style": "Стиль руководства",
        "collaboration_approach": "Подход к сотрудничеству",
        "professional_strengths": ["Профессиональные сильные стороны"]
    }},
    
    "growth_potential": {{
        "natural_talents": ["Природные таланты и способности"],
        "development_areas": ["Области для развития"],
        "learning_opportunities": ["Возможности для обучения"],
        "potential_challenges": ["Потенциальные вызовы"],
        "transformation_capacity": "Способность к изменениям"
    }}
}}

Создай портрет, который поможет человеку лучше понять себя и развиваться!"""

EMOTIONAL_ANALYSIS_PROMPT = """Ты - эксперт по эмоциональному анализу. Создай ДЕТАЛЬНУЮ карту эмоционального мира человека.

ТЕКСТ:
{text}

КОНТЕКСТ:
{context}

🎯 ЗАДАЧА: Раскрыть эмоциональную вселенную этого человека со всеми нюансами.

ГЛУБОКИЙ ЭМОЦИОНАЛЬНЫЙ АНАЛИЗ:
{{
    "emotional_snapshot": {{
        "current_state": "Текущее эмоциональное состояние с деталями",
        "emotional_climate": "Общий эмоциональный фон жизни",
        "intensity_level": "Интенсивность эмоциональных переживаний",
        "emotional_complexity": "Сложность эмоционального мира"
    }},
    
    "emotion_palette": {{
        "dominant_emotions": ["Преобладающие эмоции с описанием"],
        "hidden_emotions": ["Скрытые или подавленные эмоции"],
        "emotional_range": "Диапазон эмоциональных проявлений",
        "rare_emotions": ["Редкие или уникальные эмоциональные состояния"]
    }},
    
    "emotional_intelligence": {{
        "self_awareness": "Осознание собственных эмоций",
        "self_regulation": "Управление эмоциями",
        "empathy_depth": "Глубина эмпатии к другим",
        "social_skills": "Эмоциональные навыки в общении",
        "emotional_contagion": "Влияние на эмоции других"
    }},
    
    "emotional_patterns": {{
        "reaction_style": "Стиль эмоциональных реакций",
        "emotional_memory": "Как хранит эмоциональные воспоминания",
        "mood_patterns": "Паттерны смены настроения",
        "emotional_cycles": "Эмоциональные циклы и ритмы",
        "trigger_sensitivity": "Чувствительность к эмоциональным триггерам"
    }},
    
    "stress_and_resilience": {{
        "stress_signature": "Уникальная подпись стресса",
        "stress_threshold": "Порог стрессоустойчивости",
        "recovery_style": "Способ восстановления после стресса",
        "resilience_factors": ["Факторы эмоциональной устойчивости"],
        "vulnerability_points": ["Точки эмоциональной уязвимости"]
    }},
    
    "emotional_expression": {{
        "expression_style": "Стиль выражения эмоций",
        "communication_of_feelings": "Как передает чувства другим",
        "emotional_masks": "Эмоциональные маски и защиты",
        "authenticity_level": "Уровень эмоциональной подлинности",
        "emotional_vocabulary": "Богатство эмоционального словаря"
    }},
    
    "relationship_emotions": {{
        "love_expression": "Как выражает любовь и привязанность",
        "conflict_emotions": "Эмоции в конфликтных ситуациях",
        "emotional_needs": ["Основные эмоциональные потребности"],
        "emotional_giving": "Как дает эмоциональную поддержку",
        "intimacy_comfort": "Комфорт с эмоциональной близостью"
    }},
    
    "emotional_growth": {{
        "emotional_maturity": "Уровень эмоциональной зрелости",
        "growth_areas": ["Области для эмоционального развития"],
        "emotional_goals": ["Потенциальные эмоциональные цели"],
        "healing_opportunities": ["Возможности для эмоционального исцеления"],
        "emotional_strengths": ["Эмоциональные сильные стороны"]
    }}
}}

Создай анализ, который поможет человеку глубже понять свой эмоциональный мир!"""

BEHAVIORAL_ANALYSIS_PROMPT = """Ты - профайлер поведения. Создай детальную карту поведенческих паттернов человека.

МАТЕРИАЛ:
{text}

КОНТЕКСТ:
{context}

🎯 ЦЕЛЬ: Раскрыть поведенческие секреты и паттерны этой личности.

ДЕТАЛЬНЫЙ ПОВЕДЕНЧЕСКИЙ ПРОФИЛЬ:
{{
    "behavioral_signature": {{
        "core_patterns": ["Основные поведенческие паттерны"],
        "unique_behaviors": ["Уникальные поведенческие особенности"],
        "predictable_responses": ["Предсказуемые реакции"],
        "behavioral_flexibility": "Гибкость в поведении"
    }},
    
    "decision_making_style": {{
        "decision_process": "Процесс принятия решений",
        "information_gathering": "Как собирает информацию",
        "analysis_vs_intuition": "Баланс анализа и интуиции",
        "decision_speed": "Скорость принятия решений",
        "revision_tendency": "Склонность пересматривать решения"
    }},
    
    "communication_behavior": {{
        "conversation_style": "Стиль ведения разговора",
        "listening_patterns": "Паттерны слушания",
        "storytelling_approach": "Подход к рассказыванию историй",
        "persuasion_tactics": ["Тактики убеждения"],
        "feedback_style": "Стиль дачи и получения обратной связи"
    }},
    
    "work_behavior": {{
        "productivity_patterns": "Паттерны продуктивности",
        "task_approach": "Подход к выполнению задач",
        "collaboration_style": "Стиль сотрудничества",
        "leadership_behavior": "Поведение в роли лидера",
        "follower_behavior": "Поведение в роли подчиненного"
    }},
    
    "social_behavior": {{
        "group_dynamics": "Поведение в группах",
        "networking_style": "Стиль налаживания связей",
        "social_energy_management": "Управление социальной энергией",
        "boundary_setting": "Установление границ",
        "social_adaptation": "Адаптация к социальным ситуациям"
    }},
    
    "learning_behavior": {{
        "learning_preferences": "Предпочтения в обучении",
        "knowledge_acquisition": "Способы получения знаний",
        "skill_development": "Подход к развитию навыков",
        "feedback_integration": "Интеграция обратной связи",
        "teaching_style": "Стиль обучения других"
    }},
    
    "habit_patterns": {{
        "routine_preferences": "Предпочтения в рутине",
        "habit_formation": "Формирование привычек",
        "change_adaptation": "Адаптация к изменениям",
        "spontaneity_vs_planning": "Спонтанность против планирования",
        "consistency_patterns": "Паттерны постоянства"
    }},
    
    "conflict_behavior": {{
        "conflict_approach": "Подход к конфликтам",
        "negotiation_style": "Стиль переговоров",
        "compromise_tendency": "Склонность к компромиссам",
        "assertiveness_level": "Уровень ассертивности",
        "conflict_resolution": "Разрешение конфликтов"
    }},
    
    "behavioral_predictions": {{
        "likely_reactions": ["Вероятные реакции в различных ситуациях"],
        "stress_behaviors": ["Поведение под стрессом"],
        "growth_behaviors": ["Поведение в ситуациях роста"],
        "relationship_behaviors": ["Поведение в отношениях"],
        "career_behaviors": ["Карьерное поведение"]
    }}
}}

Создай поведенческий профиль, который поможет понять и предсказать действия!"""

SYNTHESIS_PROMPT = """Ты - гений психологического синтеза. Создай ИТОГОВЫЙ ШЕДЕВР анализа личности.

ДАННЫЕ ОТ AI:
{ai_results}

ИСХОДНЫЙ ТЕКСТ:
{original_text}

МЕТАДАННЫЕ:
{metadata}

🎯 МИССИЯ: Создать психологический портрет, который станет откровением для человека.

ШЕДЕВР ПСИХОЛОГИЧЕСКОГО АНАЛИЗА:
{{
    "masterpiece_summary": {{
        "essence_capture": "Суть личности в одном мощном абзаце",
        "wow_factor": "Самое удивительное открытие о этом человеке",
        "life_theme": "Главная тема жизни этой личности",
        "superpower": "Уникальная сверхспособность этого человека"
    }},
    
    "integrated_portrait": {{
        "personality_symphony": "Как разные черты создают уникальную симфонию личности",
        "internal_contradictions": "Внутренние противоречия и как они обогащают личность",
        "evolution_pattern": "Паттерн личностного развития",
        "archetypal_blend": "Смесь архетипов в этой личности"
    }},
    
    "life_mastery_guide": {{
        "natural_advantages": ["Природные преимущества для использования"],
        "transformation_opportunities": ["Возможности для трансформации"],
        "relationship_mastery": ["Как стать мастером отношений"],
        "career_alignment": ["Как выровнять карьеру с природой"],
        "life_optimization": ["Стратегии оптимизации жизни"]
    }},
    
    "deep_insights": {{
        "unconscious_patterns": "Бессознательные паттерны и их влияние",
        "hidden_motivations": "Скрытые мотивации и драйверы",
        "blind_spots": "Слепые зоны и как их осветить",
        "untapped_potential": "Нераскрытый потенциал",
        "soul_purpose": "Возможное предназначение души"
    }},
    
    "relationship_blueprint": {{
        "love_map": "Карта любви и близости",
        "friendship_formula": "Формула крепкой дружбы",
        "family_dynamics": "Роль в семейной системе",
        "professional_networking": "Стратегия профессионального нетворкинга",
        "social_impact": "Потенциал социального влияния"
    }},
    
    "life_scenarios": {{
        "best_case_future": "Лучший сценарий развития при использовании сильных сторон",
        "growth_challenges": "Вызовы, которые приведут к росту",
        "potential_pitfalls": "Потенциальные ловушки и как их избежать",
        "reinvention_opportunities": "Возможности для переосмысления себя",
        "legacy_potential": "Потенциальное наследие этого человека"
    }},
    
    "practical_mastery": {{
        "daily_optimization": ["Ежедневные практики для процветания"],
        "energy_management": ["Стратегии управления энергией"],
        "decision_framework": "Персональная система принятия решений",
        "growth_accelerators": ["Ускорители личностного роста"],
        "life_design_principles": ["Принципы дизайна своей жизни"]
    }},
    
    "validation_synthesis": {{
        "confidence_level": 85-98,
        "insight_depth": "Глубина полученных инсайтов",
        "practical_applicability": "Применимость в реальной жизни",
        "transformation_potential": "Потенциал для трансформации",
        "uniqueness_factor": "Фактор уникальности анализа"
    }}
}}

Создай анализ, который изменит жизнь человека к лучшему!"""

MULTI_AI_SYNTHESIS_PROMPT = """Ты - мастер синтеза данных от множественных AI систем. Создай РЕВОЛЮЦИОННЫЙ психологический анализ.

🚀 ДАННЫЕ ОТ СОВРЕМЕННЫХ AI СИСТЕМ (2025):
{ai_results}

📝 ИСХОДНЫЙ ТЕКСТ:
{original_text}

🎯 КОНТЕКСТ:
{metadata}

⚡ ТВОЯ МИССИЯ: Создать глубочайший анализ личности, объединяющий силу нескольких топовых AI систем.

🧠 ИСТОЧНИКИ ДАННЫХ:
- Claude 3.5 Sonnet: психологический синтез и интерпретация
- OpenAI GPT-4o: научно обоснованные Big Five + эмоциональный анализ  
- Cohere Command-R+: психолингвистика + продвинутый анализ настроений
- HuggingFace Transformers: специализированный эмоциональный анализ

РЕВОЛЮЦИОННЫЙ МУЛЬТИ-AI АНАЛИЗ:
{{
    "executive_synthesis": {{
        "hook_summary": "Захватывающее открытие о личности в 1-2 предложения",
        "ai_consensus": "Что все AI системы единодушно выявили",
        "unique_discoveries": "Уникальные находки, возможные только при мульти-AI подходе",
        "confidence_multiplier": "Как множественные источники повышают точность"
    }},

    "personality_core": {{
        "essence": "Глубинная суть личности по данным всех AI",
        "unique_traits": ["Самые яркие черты характера с указанием источников"],
        "hidden_depths": "Скрытые аспекты, выявленные кросс-валидацией",
        "archetypal_signature": "Психологический архетип этой личности"
    }},

    "main_findings": {{
        "personality_traits": ["Ключевые черты с указанием AI-источников"],
        "emotional_signature": "Эмоциональная подпись на основе OpenAI + HuggingFace + Cohere",
        "thinking_style": "Стиль мышления через призму психолингвистики",
        "behavioral_patterns": ["Поведенческие паттерны из разных источников"],
        "communication_style": "Стиль общения по данным Cohere психолингвистики"
    }},

    "psychological_profile": {{
        "big_five_traits": {{
            "openness": {{"score": 0-100, "description": "детальное описание", "ai_source": "OpenAI/Claude"}},
            "conscientiousness": {{"score": 0-100, "description": "детальное описание", "ai_source": "OpenAI/Claude"}},
            "extraversion": {{"score": 0-100, "description": "детальное описание", "ai_source": "OpenAI/Claude"}},
            "agreeableness": {{"score": 0-100, "description": "детальное описание", "ai_source": "OpenAI/Claude"}},
            "neuroticism": {{"score": 0-100, "description": "детальное описание", "ai_source": "OpenAI/Claude"}}
        }},
        "emotional_intelligence": {{
            "self_awareness": "по данным OpenAI + HuggingFace",
            "social_skills": "по данным Cohere психолингвистики",
            "emotional_regulation": "синтез всех источников"
        }},
        "cognitive_patterns": {{
            "analytical_thinking": "оценка по Cohere когнитивному стилю",
            "creative_expression": "анализ через Claude + психолингвистику",
            "decision_making": "паттерны из поведенческого анализа Cohere"
        }}
    }},

    "practical_insights": {{
        "strengths_to_leverage": ["Сильные стороны с AI-подтверждением"],
        "career_alignment": "Карьерные рекомендации на основе всех источников",
        "relationship_style": "Стиль отношений через психолингвистику + эмоции",
        "communication_optimization": "Как улучшить общение (данные Cohere)",
        "stress_management": "Управление стрессом (HuggingFace ментальное здоровье)"
    }},

    "actionable_recommendations": {{
        "immediate_actions": ["3-4 конкретных шага на основе мульти-AI консенсуса"],
        "personal_development": ["Долгосрочные рекомендации по развитию"],
        "relationship_advice": ["Советы для отношений на основе эмо-анализа"],
        "career_moves": ["Карьерные шаги с учетом личностного профиля"],
        "daily_practices": ["Ежедневные практики для роста"]
    }},

    "fascinating_details": {{
        "ai_discoveries": ["Что выявил каждый AI сервис уникального"],
        "hidden_talents": ["Скрытые таланты по данным кросс-анализа"],
        "personality_paradoxes": ["Интересные противоречия в личности"],
        "growth_potential": ["Потенциал развития по всем источникам"],
        "life_themes": ["Ключевые темы жизни этого человека"]
    }},

    "scientific_validation": {{
        "cross_validation_score": 0-100,
        "ai_consensus_level": "Уровень согласия между AI системами",
        "data_quality": "Качество исходных данных для анализа",
        "reliability_factors": ["Факторы, повышающие надежность анализа"],
        "methodology_strength": "Сила методологии мульти-AI подхода"
    }},

    "confidence_score": 80-95,
    "data_sources": {{
        "claude": "психологический синтез и интерпретация",
        "openai": "научные Big Five + эмоциональный анализ",
        "cohere": "психолингвистика + продвинутый sentiment",
        "huggingface": "специализированный эмоциональный анализ"
    }}
}}

🎯 ТРЕБОВАНИЯ:
- Используй ВСЕ доступные данные от AI систем
- Покажи КАК разные AI дополняют друг друга
- Укажи конкретные ИСТОЧНИКИ для каждого инсайта
- Создай СИНЕРГИЮ между данными разных систем
- Дай практические советы на основе КОНСЕНСУСА AI

Создай анализ, который покажет силу современной мульти-AI архитектуры!""" 