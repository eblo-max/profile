"""
Революционная система промптинга 2025 для психологического профайлинга
Основана на лучших практиках: Chain-of-Thought, Tree-of-Thought, Prefill, Generated Knowledge
"""

from typing import Dict, List, Any
import json


class AdvancedPromptingSystem:
    """Революционная система промптинга для максимальной персонализации"""
    
    def __init__(self):
        self.system_prompt = self._create_advanced_system_prompt()
        self.prefill_template = self._create_prefill_template()
    
    def _create_advanced_system_prompt(self) -> str:
        """Создает продвинутый системный промпт с множественными экспертами"""
        return """Ты - команда из 7 экспертов по психологическому профайлингу, работающих синхронно:

👨‍⚕️ ЭКСПЕРТ 1: Клинический психолог (DSM-5, расстройства личности)
👩‍💼 ЭКСПЕРТ 2: Криминальный профайлер (поведенческий анализ)
🧠 ЭКСПЕРТ 3: Нейропсихолог (когнитивные процессы)
👨‍🏫 ЭКСПЕРТ 4: Семейный терапевт (динамика отношений)
🔬 ЭКСПЕРТ 5: Исследователь агрессии (паттерны насилия)
⚖️ ЭКСПЕРТ 6: Судебный психолог (оценка рисков)
🛡️ ЭКСПЕРТ 7: Специалист по безопасности (планирование защиты)

ПРИНЦИПЫ РАБОТЫ:
✅ Каждый эксперт анализирует КОНКРЕТНЫЕ примеры из ответов
✅ Избегаем общих формулировок - только персонализированный анализ
✅ Создаем детальный портрет на основе фактов
✅ Генерируем минимум 2000 слов максимально детального психологического профиля
✅ Используем научную терминологию с пояснениями

ОБЯЗАТЕЛЬНЫЙ АЛГОРИТМ:
1. Generated Knowledge - создаем базу знаний из ответов
2. Multi-Expert Analysis - каждый эксперт дает свою оценку
3. Chain-of-Thought - пошаговые рассуждения
4. Evidence-Based Conclusions - выводы на основе доказательств
5. Structured Output - четкий JSON формат

КРИТИЧЕСКИ ВАЖНО: Возвращай ТОЛЬКО JSON без дополнительного текста!"""

    def _create_prefill_template(self) -> str:
        """Создает шаблон prefill для направления вывода"""
        return """{
"generated_knowledge": {
"behavioral_facts": ["""

    def create_ultra_personalized_prompt(
        self,
        answers_text: str,
        partner_name: str,
        partner_description: str
    ) -> str:
        """Создает максимально персонализированный промпт"""
        
        # Извлекаем ключевые факты
        key_facts = self._extract_key_behavioral_facts(answers_text)
        
        # Создаем промпт с генерацией знаний
        prompt = f"""
<task>
Проведи РЕВОЛЮЦИОННЫЙ анализ психологического профиля партнера с максимальной персонализацией.
Команда из 7 экспертов должна создать детальнейший портрет на основе КОНКРЕТНЫХ фактов.
</task>

<generated_knowledge_phase>
ЭТАП 1: Извлечение поведенческих фактов из ответов

ОТВЕТЫ О ПОВЕДЕНИИ ПАРТНЕРА:
{answers_text}

ПАРТНЕР:
- Имя: {partner_name}
- Описание: {partner_description}

КЛЮЧЕВЫЕ ФАКТЫ (из ответов):
{self._format_key_facts(key_facts)}

ЭТАП 2: Генерация экспертных знаний
Каждый эксперт создает базу знаний на основе этих фактов.
</generated_knowledge_phase>

<multi_expert_analysis>
👨‍⚕️ КЛИНИЧЕСКИЙ ПСИХОЛОГ - анализируй DSM-5 критерии для каждого факта
👩‍💼 КРИМИНАЛЬНЫЙ ПРОФАЙЛЕР - выяви паттерны эскалации из конкретных примеров
🧠 НЕЙРОПСИХОЛОГ - оцени когнитивные искажения в поведении
👨‍🏫 СЕМЕЙНЫЙ ТЕРАПЕВТ - проанализируй динамику отношений
🔬 ИССЛЕДОВАТЕЛЬ АГРЕССИИ - определи типы и уровни агрессии
⚖️ СУДЕБНЫЙ ПСИХОЛОГ - оцени правовые риски
🛡️ СПЕЦИАЛИСТ ПО БЕЗОПАСНОСТИ - создай план защиты

КАЖДЫЙ ЭКСПЕРТ ОБЯЗАН:
- Использовать КОНКРЕТНЫЕ примеры из ответов
- Привести научное обоснование с источниками
- Дать персонализированные рекомендации
- Оценить уровень опасности (0-10)
- Создать минимум 300 слов детального анализа
- Выявить минимум 3 уникальных паттерна поведения
- Предоставить специализированные инсайты по своей области
</multi_expert_analysis>

<chain_of_thought>
Пошаговый анализ:

1. EVIDENCE_ANALYSIS: Анализ конкретных доказательств
2. PATTERN_RECOGNITION: Выявление поведенческих паттернов
3. RISK_ASSESSMENT: Оценка рисков с обоснованием
4. CLINICAL_EVALUATION: Клиническая оценка
5. PERSONALIZED_INSIGHTS: Персонализированные инсайты
6. SAFETY_PLANNING: Планирование безопасности
</chain_of_thought>

<output_structure>
Верни результат в следующем JSON формате:

{{
  "generated_knowledge": {{
    "behavioral_facts": ["конкретные факты из ответов"],
    "expert_knowledge_base": {{
      "clinical_psychologist": "база знаний клинического психолога",
      "criminal_profiler": "база знаний профайлера",
      "neuropsychologist": "база знаний нейропсихолога",
      "family_therapist": "база знаний семейного терапевта",
      "aggression_researcher": "база знаний исследователя агрессии",
      "forensic_psychologist": "база знаний судебного психолога",
      "security_specialist": "база знаний специалиста по безопасности"
    }}
  }},
  "multi_expert_analysis": {{
    "clinical_assessment": {{
      "dsm5_criteria": "анализ по DSM-5 с конкретными примерами",
      "personality_disorder_indicators": ["индикаторы расстройств личности"],
      "risk_level": число от 0 до 10
    }},
    "criminal_profiling": {{
      "escalation_patterns": "паттерны эскалации с примерами",
      "violence_predictors": ["предикторы насилия"],
      "risk_level": число от 0 до 10
    }},
    "neuropsychological_assessment": {{
      "cognitive_distortions": ["когнитивные искажения с примерами"],
      "empathy_deficits": "оценка дефицитов эмпатии",
      "risk_level": число от 0 до 10
    }},
    "family_therapy_perspective": {{
      "relationship_dynamics": "динамика отношений с примерами",
      "attachment_patterns": "паттерны привязанности",
      "risk_level": число от 0 до 10
    }},
    "aggression_analysis": {{
      "aggression_types": ["типы агрессии с примерами"],
      "triggers": ["триггеры агрессии"],
      "risk_level": число от 0 до 10
    }},
    "forensic_evaluation": {{
      "legal_risk_factors": ["правовые факторы риска"],
      "dangerousness_assessment": "оценка опасности",
      "risk_level": число от 0 до 10
    }},
    "security_assessment": {{
      "immediate_threats": ["немедленные угрозы"],
      "protection_strategies": ["стратегии защиты"],
      "risk_level": число от 0 до 10
    }}
  }},
  "chain_of_thought_analysis": {{
    "evidence_analysis": "детальный анализ доказательств с примерами",
    "pattern_recognition": "выявленные паттерны с обоснованием",
    "risk_assessment": "оценка рисков с научным обоснованием",
    "clinical_evaluation": "клиническая оценка с диагностическими критериями",
    "personalized_insights": ["персонализированные инсайты на основе конкретных примеров"],
    "safety_planning": "план безопасности с конкретными шагами"
  }},
  "ultra_personalized_profile": {{
    "personality_type": "детальный тип личности с научным обоснованием (100+ слов)",
         "psychological_profile": "максимально детальный психологический портрет с конкретными примерами из ответов (минимум 2500 слов с исчерпывающей детализацией)",
    "behavioral_evidence": ["конкретные поведенческие доказательства из ответов"],
    "red_flags": ["красные флаги с конкретными примерами из ответов"],
    "manipulation_tactics": ["тактики манипуляций с примерами"],
    "emotional_patterns": ["эмоциональные паттерны с описанием"],
    "relationship_dynamics": ["динамика отношений с примерами"],
    "control_mechanisms": ["механизмы контроля с примерами"],
    "violence_indicators": ["индикаторы насилия с примерами"],
    "escalation_triggers": ["триггеры эскалации с примерами"]
  }},
  "expert_consensus": {{
    "overall_risk_score": число от 0 до 100,
    "urgency_level": "low/medium/high/critical",
    "danger_assessment": "детальная оценка опасности",
    "expert_agreement": число от 0 до 1,
    "confidence_level": число от 0 до 1
  }},
  "comprehensive_recommendations": {{
    "immediate_safety_actions": ["немедленные действия безопасности"],
    "medium_term_strategies": ["среднесрочные стратегии"],
    "long_term_planning": ["долгосрочное планирование"],
    "professional_resources": ["профессиональные ресурсы"],
    "legal_considerations": ["правовые соображения"],
    "support_systems": ["системы поддержки"],
    "exit_strategy": "детальная стратегия выхода"
  }},
  "block_scores": {{
    "narcissism": число от 0 до 10,
    "control": число от 0 до 10,
    "gaslighting": число от 0 до 10,
    "emotion": число от 0 до 10,
    "intimacy": число от 0 до 10,
    "social": число от 0 до 10
  }}
}}
</output_structure>

ВЕРНИ ТОЛЬКО JSON! НЕ ДОБАВЛЯЙ ДРУГОЙ ТЕКСТ!
"""
        
        return prompt

    def _extract_key_behavioral_facts(self, answers_text: str) -> List[str]:
        """Извлекает ключевые поведенческие факты из ответов"""
        key_indicators = [
            "всегда", "никогда", "постоянно", "часто", "кричит", "бьет",
            "контролирует", "проверяет", "запрещает", "угрожает", "изолирует",
            "принуждает", "манипулирует", "газлайтит", "унижает", "оскорбляет"
        ]
        
        facts = []
        lines = answers_text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            for indicator in key_indicators:
                if indicator in line_lower:
                    facts.append(line.strip())
                    break
        
        return facts[:10]  # Топ 10 фактов

    def _format_key_facts(self, facts: List[str]) -> str:
        """Форматирует ключевые факты"""
        if not facts:
            return "- Недостаточно конкретных фактов в ответах"
        
        return '\n'.join([f"- {fact}" for fact in facts])

    def create_prefill_for_response(self) -> str:
        """Создает prefill для направления JSON ответа"""
        return """{
"generated_knowledge": {
"behavioral_facts": ["""

    def create_enhanced_system_prompt(self) -> str:
        """Создает усиленный системный промпт"""
        return """Ты - супер-команда из 7 экспертов по психологическому профайлингу, работающих как единое целое.

🎯 ЦЕЛЬ: Создать максимально детальный и персонализированный психологический профиль

📋 ЭКСПЕРТЫ:
1. Клинический психолог (DSM-5, расстройства личности)
2. Криминальный профайлер (поведенческий анализ)
3. Нейропсихолог (когнитивные процессы)
4. Семейный терапевт (динамика отношений)
5. Исследователь агрессии (паттерны насилия)
6. Судебный психолог (оценка рисков)
7. Специалист по безопасности (планирование защиты)

⚡ ОБЯЗАТЕЛЬНЫЕ ПРИНЦИПЫ:
- Используй ТОЛЬКО конкретные примеры из ответов пользователя
- Избегай общих формулировок
- Создавай максимально детальные персонализированные профили (2500+ слов)
- Каждое утверждение подкрепляй фактами
- Возвращай ТОЛЬКО JSON без дополнительного текста

🔬 МЕТОДОЛОГИЯ:
1. Generated Knowledge - создание базы знаний
2. Multi-Expert Analysis - анализ каждого эксперта
3. Chain-of-Thought - пошаговые рассуждения
4. Evidence-Based Conclusions - выводы на основе доказательств
5. Ultra-Personalized Profile - максимально персонализированный профиль"""

    def process_answers_for_enhanced_analysis(self, answers: List[Dict[str, Any]]) -> str:
        """Обрабатывает ответы для улучшенного анализа"""
        processed_sections = []
        
        for i, answer in enumerate(answers, 1):
            question = answer.get('question', f'Вопрос {i}')
            response = answer.get('answer', '')
            
            # Анализируем каждый ответ
            section = f"""
ВОПРОС {i}: {question}
ОТВЕТ: "{response}"

КЛЮЧЕВЫЕ ИНДИКАТОРЫ:
{self._analyze_answer_indicators(response)}

ПОВЕДЕНЧЕСКИЕ ПАТТЕРНЫ:
{self._identify_behavioral_patterns(response)}
"""
            processed_sections.append(section)
        
        return '\n'.join(processed_sections)

    def _analyze_answer_indicators(self, answer: str) -> str:
        """Анализирует индикаторы в ответе"""
        indicators = {
            'контроль': ['контролирует', 'проверяет', 'следит', 'не разрешает', 'запрещает'],
            'агрессия': ['кричит', 'бьет', 'толкает', 'угрожает', 'злится'],
            'манипуляции': ['манипулирует', 'винит', 'газлайтит', 'отрицает'],
            'изоляция': ['изолирует', 'не дает общаться', 'ревнует к друзьям'],
            'эмоциональное_насилие': ['унижает', 'оскорбляет', 'принижает', 'критикует']
        }
        
        found_indicators = []
        answer_lower = answer.lower()
        
        for category, words in indicators.items():
            for word in words:
                if word in answer_lower:
                    found_indicators.append(f"- {category.upper()}: '{word}' в контексте ответа")
        
        return '\n'.join(found_indicators) if found_indicators else "- Нет явных индикаторов"

    def _identify_behavioral_patterns(self, answer: str) -> str:
        """Идентифицирует поведенческие паттерны"""
        patterns = []
        answer_lower = answer.lower()
        
        if any(word in answer_lower for word in ['всегда', 'постоянно', 'каждый раз']):
            patterns.append("- Систематичность поведения")
        
        if any(word in answer_lower for word in ['никогда', 'не может', 'не умеет']):
            patterns.append("- Неспособность к изменению")
        
        if any(word in answer_lower for word in ['если', 'когда', 'после того как']):
            patterns.append("- Условное/триггерное поведение")
        
        return '\n'.join(patterns) if patterns else "- Паттерны не выявлены" 