"""
Система параллельного анализа научных данных через множественные AI модели.

Поддерживаемые AI системы:
- Claude 3.5 Sonnet (общий анализ + синтез)
- GPT-4 (типология личности)  
- Gemini (когнитивные паттерны)
- Cohere (поведенческий анализ)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from datetime import datetime

import anthropic
import openai
# import google.generativeai as genai  # Будет добавлено при настройке
# import cohere  # Будет добавлено при настройке

from .scientific_research_engine import ScientificSource, PersonData
from ..config.settings import Settings

logger = logging.getLogger(__name__)

@dataclass
class AIAnalysisResult:
    """Результат анализа от одной AI системы"""
    ai_model: str
    analysis_type: str
    confidence_score: float
    findings: Dict[str, Any]
    scientific_references: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "ai_model": self.ai_model,
            "analysis_type": self.analysis_type,
            "confidence_score": self.confidence_score,
            "findings": self.findings,
            "scientific_references": self.scientific_references,
            "timestamp": self.timestamp.isoformat()
        }

class MultiAIResearchAnalyzer:
    """Координатор множественного AI анализа"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Инициализация AI клиентов
        self.claude_client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None
        
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        ) if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY else None
        
        # Gemini и Cohere будут добавлены при получении ключей
        self.gemini_client = None
        self.cohere_client = None
        
        # Специализация AI моделей
        self.ai_specializations = {
            "claude": "general_synthesis",
            "gpt4": "personality_typology", 
            "gemini": "cognitive_analysis",
            "cohere": "behavioral_patterns"
        }
    
    async def comprehensive_research_analysis(
        self, 
        person_data: PersonData,
        research_sources: List[ScientificSource]
    ) -> Dict[str, Any]:
        """
        Комплексный анализ через все доступные AI системы
        
        Args:
            person_data: Данные о человеке
            research_sources: Найденные научные источники
            
        Returns:
            Детальный многоуровневый анализ
        """
        logger.info(f"🧠 Запуск мультимодального AI анализа для {person_data.name}")
        
        try:
            # Этап 1: Параллельный анализ через разные AI
            analysis_tasks = []
            
            if self.claude_client:
                analysis_tasks.append(
                    self._claude_general_analysis(person_data, research_sources)
                )
            
            if self.openai_client:
                analysis_tasks.append(
                    self._gpt4_personality_analysis(person_data, research_sources)
                )
            
            # Когда будут добавлены другие модели:
            # if self.gemini_client:
            #     analysis_tasks.append(
            #         self._gemini_cognitive_analysis(person_data, research_sources)
            #     )
            # 
            # if self.cohere_client:
            #     analysis_tasks.append(
            #         self._cohere_behavioral_analysis(person_data, research_sources)
            #     )
            
            # Выполняем все анализы параллельно
            ai_analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Фильтруем успешные результаты
            successful_analyses = [
                result for result in ai_analyses 
                if isinstance(result, AIAnalysisResult)
            ]
            
            logger.info(f"✅ Завершено {len(successful_analyses)} AI анализов")
            
            # Этап 2: Синтез результатов
            final_synthesis = await self._synthesize_ai_results(
                successful_analyses, person_data, research_sources
            )
            
            return {
                "comprehensive_profile": final_synthesis,
                "individual_analyses": [analysis.to_dict() for analysis in successful_analyses],
                "analysis_metadata": {
                    "total_ai_models": len(successful_analyses),
                    "research_sources_used": len(research_sources),
                    "analysis_timestamp": datetime.now().isoformat(),
                    "person_name": person_data.name
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка в мультимодальном анализе: {e}")
            return {
                "comprehensive_profile": f"Произошла ошибка при комплексном анализе: {str(e)}",
                "individual_analyses": [],
                "analysis_metadata": {"error": str(e)}
            }
    
    async def _claude_general_analysis(
        self, 
        person_data: PersonData,
        sources: List[ScientificSource]
    ) -> AIAnalysisResult:
        """Claude: Общий психологический анализ и синтез"""
        try:
            prompt = self._create_claude_prompt(person_data, sources)
            
            response = await self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            
            # Извлекаем структурированные данные из анализа
            findings = self._parse_claude_analysis(analysis_text)
            
            return AIAnalysisResult(
                ai_model="Claude-3.5-Sonnet",
                analysis_type="general_synthesis",
                confidence_score=0.85,
                findings=findings,
                scientific_references=self._extract_references(analysis_text),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка Claude анализа: {e}")
            raise
    
    def _create_claude_prompt(
        self, 
        person_data: PersonData,
        sources: List[ScientificSource]
    ) -> str:
        """Создание промпта для Claude"""
        sources_text = self._format_sources_for_ai(sources[:10])
        
        return f"""
Выполни комплексный психологический анализ на основе научных исследований.

ДАННЫЕ О ЧЕЛОВЕКЕ:
Имя: {person_data.name}
Возраст: {person_data.age}
Профессия: {person_data.occupation}
Поведение: {person_data.behavior_description}
Эмоциональные маркеры: {', '.join(person_data.emotional_markers)}
Социальные паттерны: {', '.join(person_data.social_patterns)}
Когнитивные особенности: {', '.join(person_data.cognitive_traits)}

НАУЧНЫЕ ИСТОЧНИКИ:
{sources_text}

ЗАДАЧА:
Создай детальный психологический профиль, используя научно-обоснованный подход.

ТРЕБУЕМЫЙ ФОРМАТ (JSON):
{{
    "personality_type": "Основной тип личности с обоснованием",
    "big_five_traits": {{
        "openness": {{"score": 0-100, "description": "описание"}},
        "conscientiousness": {{"score": 0-100, "description": "описание"}},
        "extraversion": {{"score": 0-100, "description": "описание"}},
        "agreeableness": {{"score": 0-100, "description": "описание"}},
        "neuroticism": {{"score": 0-100, "description": "описание"}}
    }},
    "emotional_intelligence": {{
        "self_awareness": {{"score": 0-100, "description": "описание"}},
        "self_regulation": {{"score": 0-100, "description": "описание"}},
        "motivation": {{"score": 0-100, "description": "описание"}},
        "empathy": {{"score": 0-100, "description": "описание"}},
        "social_skills": {{"score": 0-100, "description": "описание"}}
    }},
    "cognitive_profile": {{
        "thinking_style": "описание стиля мышления",
        "decision_making": "описание процесса принятия решений",
        "problem_solving": "подход к решению проблем",
        "learning_style": "предпочитаемый стиль обучения"
    }},
    "behavioral_patterns": {{
        "communication_style": "стиль общения",
        "conflict_resolution": "подход к конфликтам",
        "leadership_style": "стиль лидерства",
        "stress_response": "реакция на стресс"
    }},
    "relationship_compatibility": {{
        "attachment_style": "стиль привязанности",
        "romantic_compatibility": "совместимость в отношениях",
        "friendship_patterns": "паттерны дружбы",
        "team_dynamics": "динамика в команде"
    }},
    "professional_profile": {{
        "career_strengths": ["список сильных сторон"],
        "ideal_work_environment": "описание идеальной рабочей среды",
        "leadership_potential": "потенциал лидерства",
        "collaboration_style": "стиль сотрудничества"
    }},
    "potential_challenges": {{
        "stress_vulnerabilities": ["уязвимости к стрессу"],
        "relationship_challenges": ["потенциальные проблемы в отношениях"],
        "professional_risks": ["профессиональные риски"],
        "growth_areas": ["области для развития"]
    }},
    "cultural_considerations": {{
        "cultural_background_impact": "влияние культурного фона",
        "adaptation_patterns": "паттерны адаптации",
        "value_system": "система ценностей"
    }},
    "scientific_validation": {{
        "confidence_level": "уровень уверенности в анализе (0-100)",
        "key_research_support": ["ключевые исследования, поддерживающие выводы"],
        "limitations": ["ограничения анализа"]
    }}
}}

Убедись, что каждый вывод подкреплен научными данными из предоставленных источников.
"""
    
    def _format_sources_for_ai(self, sources: List[ScientificSource]) -> str:
        """Форматирование источников для AI"""
        formatted = []
        
        for i, source in enumerate(sources, 1):
            entry = f"""
ИСТОЧНИК {i}:
- Заголовок: {source.title}
- Авторы: {', '.join(source.authors)}
- Публикация: {source.publication} ({source.year})
- Аннотация: {source.abstract[:300]}...
- Цитирования: {source.citations}
- Оценка качества: {source.quality_score}/100
"""
            formatted.append(entry)
        
        return "\n".join(formatted)
    
    def _parse_claude_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Парсинг структурированного ответа Claude"""
        try:
            # Ищем JSON блок в ответе
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = analysis_text[json_start:json_end]
                return json.loads(json_text)
            else:
                # Если JSON не найден, создаем базовую структуру
                return {
                    "analysis_summary": analysis_text,
                    "parsing_note": "JSON структура не найдена, возвращен текстовый анализ"
                }
                
        except json.JSONDecodeError:
            return {
                "analysis_summary": analysis_text,
                "parsing_note": "Ошибка парсинга JSON, возвращен текстовый анализ"
            }
    
    def _extract_references(self, text: str) -> List[str]:
        """Извлечение научных ссылок из текста"""
        references = []
        
        # Ищем упоминания источников
        patterns = [
            r'ИСТОЧНИК \d+',
            r'\(\d{4}\)',  # Годы в скобках
            r'et al\.',
            r'DOI:.*',
            r'PMID:.*'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            references.extend(matches)
        
        return list(set(references))
    
    async def _gpt4_personality_analysis(
        self, 
        person_data: PersonData,
        sources: List[ScientificSource]
    ) -> AIAnalysisResult:
        """GPT-4: Специализированный анализ типов личности"""
        try:
            prompt = self._create_gpt4_prompt(person_data, sources)
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Парсим структурированный ответ
            findings = self._parse_gpt4_analysis(analysis_text)
            
            return AIAnalysisResult(
                ai_model="GPT-4",
                analysis_type="personality_typology",
                confidence_score=0.80,
                findings=findings,
                scientific_references=self._extract_references(analysis_text),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка GPT-4 анализа: {e}")
            raise
    
    def _create_gpt4_prompt(
        self, 
        person_data: PersonData,
        sources: List[ScientificSource]
    ) -> str:
        """Создание специализированного промпта для GPT-4"""
        sources_text = self._format_sources_for_ai(sources[:8])
        
        return f"""
Проведи углубленный анализ типа личности на основе научных данных.

ЛИЧНЫЕ ДАННЫЕ:
{self._format_person_data(person_data)}

НАУЧНАЯ БАЗА:
{sources_text}

ФОКУС АНАЛИЗА:
1. MBTI типология с научным обоснованием
2. Big Five модель с количественными оценками
3. DISC профиль для рабочей среды
4. Теория типов Юнга
5. Современные модели личности

ТРЕБУЕМЫЙ ФОРМАТ:
```json
{{
    "mbti_analysis": {{
        "primary_type": "4-буквенный код MBTI",
        "confidence": "процент уверенности",
        "cognitive_functions": {{
            "dominant": "описание доминирующей функции",
            "auxiliary": "описание вспомогательной функции",
            "tertiary": "описание третичной функции",
            "inferior": "описание низшей функции"
        }},
        "type_description": "детальное описание типа"
    }},
    "big_five_detailed": {{
        "openness": {{"percentile": 0-100, "facets": ["список граней"]}},
        "conscientiousness": {{"percentile": 0-100, "facets": ["список граней"]}},
        "extraversion": {{"percentile": 0-100, "facets": ["список граней"]}},
        "agreeableness": {{"percentile": 0-100, "facets": ["список граней"]}},
        "neuroticism": {{"percentile": 0-100, "facets": ["список граней"]}}
    }},
    "disc_profile": {{
        "primary_style": "D/I/S/C",
        "secondary_style": "вторичный стиль",
        "workplace_behavior": "поведение на работе",
        "communication_preferences": "предпочтения в общении"
    }},
    "jungian_types": {{
        "attitude": "extraversion/introversion",
        "functions": ["thinking", "feeling", "sensing", "intuition"],
        "type_dynamics": "динамика типа"
    }},
    "modern_models": {{
        "hexaco": "анализ по модели HEXACO",
        "dark_triad": "анализ темной триады",
        "emotional_stability": "эмоциональная стабильность"
    }},
    "scientific_backing": {{
        "research_support": ["поддерживающие исследования"],
        "reliability_scores": "надежность оценок",
        "cross_validation": "кросс-валидация между моделями"
    }}
}}
```

Обеспечь научную обоснованность каждого вывода.
"""
    
    def _format_person_data(self, person_data: PersonData) -> str:
        """Форматирование данных о человеке"""
        return f"""
Имя: {person_data.name}
Возраст: {person_data.age}
Пол: {person_data.gender or 'Не указан'}
Профессия: {person_data.occupation}
Поведенческое описание: {person_data.behavior_description}
Предполагаемый тип: {person_data.suspected_personality_type}
Эмоциональные маркеры: {', '.join(person_data.emotional_markers)}
Социальные паттерны: {', '.join(person_data.social_patterns)}
Когнитивные черты: {', '.join(person_data.cognitive_traits)}
Страна: {person_data.country}
Культурный контекст: {person_data.cultural_context}
"""
    
    def _parse_gpt4_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Парсинг ответа GPT-4"""
        try:
            # Ищем JSON блок
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = analysis_text[json_start:json_end]
                return json.loads(json_text)
            else:
                return {
                    "gpt4_analysis": analysis_text,
                    "note": "Структурированный анализ не найден"
                }
                
        except json.JSONDecodeError:
            return {
                "gpt4_analysis": analysis_text,
                "note": "Ошибка парсинга JSON"
            }
    
    async def _synthesize_ai_results(
        self, 
        ai_analyses: List[AIAnalysisResult],
        person_data: PersonData,
        sources: List[ScientificSource]
    ) -> str:
        """Синтез результатов от всех AI систем"""
        if not ai_analyses:
            return "Не удалось получить результаты AI анализа."
        
        if not self.claude_client:
            return self._create_basic_synthesis(ai_analyses, person_data)
        
        try:
            # Подготовка данных для синтеза
            analyses_summary = self._prepare_synthesis_data(ai_analyses)
            
            synthesis_prompt = f"""
Создай итоговый психологический профиль, объединив результаты анализа от разных AI систем.

ДАННЫЕ О ЧЕЛОВЕКЕ:
{self._format_person_data(person_data)}

РЕЗУЛЬТАТЫ AI АНАЛИЗОВ:
{analyses_summary}

КОЛИЧЕСТВО НАУЧНЫХ ИСТОЧНИКОВ: {len(sources)}

ЗАДАЧА:
Создай финальный, научно-обоснованный психологический профиль, который:
1. Объединяет все полученные данные
2. Разрешает противоречия между разными анализами
3. Выделяет наиболее надежные выводы
4. Указывает области неопределенности
5. Предоставляет практические рекомендации

СТРУКТУРА ОТВЕТА:
## 🧠 КОМПЛЕКСНЫЙ ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ: {person_data.name}

### 📊 МЕТА-АНАЛИЗ
- **Использовано AI моделей:** {len(ai_analyses)}
- **Средний уровень уверенности:** [рассчитай среднее]
- **Согласованность результатов:** [оцени согласованность]

### 🎯 КОНСОЛИДИРОВАННЫЙ ТИП ЛИЧНОСТИ
[Объединенные выводы о типе личности с указанием уровня согласия между AI]

### 🧩 МНОГОМЕРНЫЙ АНАЛИЗ ЧЕРТ
[Синтез оценок по разным моделям личности]

### 💭 ЭМОЦИОНАЛЬНЫЙ И КОГНИТИВНЫЙ ПРОФИЛЬ
[Объединенные данные о эмоциональном интеллекте и когнитивных способностях]

### 👥 СОЦИАЛЬНО-ПОВЕДЕНЧЕСКИЕ ХАРАКТЕРИСТИКИ
[Консолидированный анализ социального поведения]

### 💼 ПРОФЕССИОНАЛЬНЫЕ РЕКОМЕНДАЦИИ
[Объединенные карьерные рекомендации]

### ⚠️ ПОТЕНЦИАЛЬНЫЕ ОБЛАСТИ ВНИМАНИЯ
[Выявленные риски и области для развития]

### 🔄 РАЗРЕШЕНИЕ ПРОТИВОРЕЧИЙ
[Объяснение расхождений в анализах и итоговые выводы]

### 📈 УРОВЕНЬ ДОСТОВЕРНОСТИ
[Общая оценка надежности анализа]

### 🔗 НАУЧНАЯ БАЗА
[Ссылки на ключевые исследования, поддерживающие выводы]

Обеспечь максимальную научную обоснованность и практическую применимость.
"""
            
            response = await self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": synthesis_prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Ошибка синтеза AI результатов: {e}")
            return self._create_basic_synthesis(ai_analyses, person_data)
    
    def _prepare_synthesis_data(self, ai_analyses: List[AIAnalysisResult]) -> str:
        """Подготовка данных анализов для синтеза"""
        synthesis_data = []
        
        for analysis in ai_analyses:
            data = f"""
AI МОДЕЛЬ: {analysis.ai_model}
ТИП АНАЛИЗА: {analysis.analysis_type}
УВЕРЕННОСТЬ: {analysis.confidence_score:.2f}
ВРЕМЯ: {analysis.timestamp.strftime('%Y-%m-%d %H:%M')}

КЛЮЧЕВЫЕ ВЫВОДЫ:
{json.dumps(analysis.findings, indent=2, ensure_ascii=False)}

НАУЧНЫЕ ССЫЛКИ:
{', '.join(analysis.scientific_references[:5])}
"""
            synthesis_data.append(data)
        
        return "\n" + "="*50 + "\n".join(synthesis_data)
    
    def _create_basic_synthesis(
        self, 
        ai_analyses: List[AIAnalysisResult],
        person_data: PersonData
    ) -> str:
        """Создание базового синтеза без Claude"""
        synthesis = f"""
## 🧠 КОМПЛЕКСНЫЙ ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ: {person_data.name}

### 📊 МЕТА-АНАЛИЗ
- **Использовано AI моделей:** {len(ai_analyses)}
- **Анализ проведен:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

### 🎯 РЕЗУЛЬТАТЫ АНАЛИЗА

"""
        
        for i, analysis in enumerate(ai_analyses, 1):
            synthesis += f"""
#### {i}. {analysis.ai_model} - {analysis.analysis_type}
**Уверенность:** {analysis.confidence_score:.1%}

**Ключевые выводы:**
{json.dumps(analysis.findings, indent=2, ensure_ascii=False)}

---
"""
        
        synthesis += f"""
### ⚠️ ВАЖНОЕ ПРИМЕЧАНИЕ
Данный анализ объединяет результаты {len(ai_analyses)} AI систем и основан на научных исследованиях.
Для окончательных выводов рекомендуется консультация с квалифицированным психологом.

*Анализ создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}*
"""
        
        return synthesis 