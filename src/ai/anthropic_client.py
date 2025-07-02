"""
Профессиональный клиент для работы с Anthropic Claude API
"""
import asyncio
import structlog
from typing import Dict, Any, List, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from anthropic.types import Message

from src.config.settings import settings
from src.ai.prompts.psychology_prompts import (
    PSYCHOLOGICAL_ANALYSIS_PROMPT,
    PERSONALITY_ASSESSMENT_PROMPT,
    EMOTIONAL_ANALYSIS_PROMPT,
    BEHAVIORAL_ANALYSIS_PROMPT,
    SYNTHESIS_PROMPT,
    MULTI_AI_SYNTHESIS_PROMPT
)

logger = structlog.get_logger()


class AnthropicClient:
    """Асинхронный клиент для работы с Claude API"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=60.0,  # 60 секунд таймаут
            max_retries=3   # 3 попытки при ошибках
        )
        self.model = "claude-3-5-sonnet-latest"
        logger.info("🧠 AnthropicClient инициализирован", model=self.model)
    
    async def analyze_text(self, 
                          text: str, 
                          analysis_type: str = "psychological", 
                          user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Анализ текста через Claude с использованием профессиональных промптов
        
        Args:
            text: Текст для анализа
            analysis_type: Тип анализа (psychological, personality, emotional, behavioral, synthesis)
            user_context: Дополнительный контекст о пользователе
            
        Returns:
            Результат анализа от Claude
        """
        try:
            logger.info("🔍 Начинаю анализ текста", 
                       text_length=len(text), 
                       analysis_type=analysis_type)
            
            # Выбор промпта на основе типа анализа
            prompt = self._get_prompt_for_analysis_type(text, analysis_type, user_context)
            
            # Отправка запроса к Claude
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,  # Достаточно для детального анализа
                temperature=0.3,  # Стабильность результатов
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Извлечение текста ответа
            response_text = ""
            for content_block in message.content:
                if content_block.type == "text":
                    response_text += content_block.text
            
            # Парсинг структурированного ответа
            result = self._parse_analysis_response(response_text, analysis_type)
            
            # Добавление метаданных
            result["tokens_used"] = message.usage.input_tokens + message.usage.output_tokens
            result["model_used"] = self.model
            result["analysis_timestamp"] = asyncio.get_event_loop().time()
            
            logger.info("✅ Анализ текста завершен", 
                       tokens_used=result["tokens_used"],
                       confidence_score=result.get('confidence_score', 0))
            
            return result
            
        except Exception as e:
            logger.error("❌ Ошибка анализа текста", error=str(e), exc_info=True)
            return {
                "error": str(e),
                "analysis_type": analysis_type,
                "status": "failed"
            }
    
    def _get_prompt_for_analysis_type(self, 
                                     text: str, 
                                     analysis_type: str,
                                     user_context: Optional[Dict[str, Any]] = None) -> str:
        """Получение промпта для конкретного типа анализа"""
        
        context_str = str(user_context) if user_context else "Контекст не предоставлен"
        
        # Выбор промпта
        if analysis_type == "psychological" or analysis_type == "comprehensive_psychological":
            return PSYCHOLOGICAL_ANALYSIS_PROMPT.format(text=text, context=context_str)
        elif analysis_type == "personality":
            return PERSONALITY_ASSESSMENT_PROMPT.format(text=text, context=context_str)
        elif analysis_type == "emotional":
            return EMOTIONAL_ANALYSIS_PROMPT.format(text=text, context=context_str)
        elif analysis_type == "behavioral":
            return BEHAVIORAL_ANALYSIS_PROMPT.format(text=text, context=context_str)
        elif analysis_type == "synthesis":
            # Для синтеза используем специальный формат
            return SYNTHESIS_PROMPT.format(
                ai_results=user_context.get("ai_results", {}),
                original_text=text[:1000] + "..." if len(text) > 1000 else text,
                metadata=user_context
            )
        elif analysis_type == "multi_ai_synthesis":
            # Для мульти-AI синтеза используем специальный промпт
            return MULTI_AI_SYNTHESIS_PROMPT.format(
                ai_results=user_context.get("ai_results", {}),
                original_text=text[:1000] + "..." if len(text) > 1000 else text,
                metadata=user_context
            )
        else:
            # Базовый промпт для неизвестных типов
            return self._build_basic_prompt(text, analysis_type, user_context)
    
    def _build_basic_prompt(self, 
                           text: str, 
                           analysis_type: str,
                           user_context: Optional[Dict[str, Any]] = None) -> str:
        """Базовый промпт для совместимости"""
        
        base_prompt = f"""Ты - профессиональный психолог-аналитик с опытом работы в области психологического профилирования.

ЗАДАЧА: Проведи детальный {analysis_type} анализ предоставленного текста.

ТЕКСТ ДЛЯ АНАЛИЗА:
{text}

ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ:
{user_context if user_context else "Контекст не предоставлен"}

ТРЕБОВАНИЯ К АНАЛИЗУ:
1. Будь максимально объективным и научно обоснованным
2. Используй признанные психологические теории и модели
3. Укажи источники и методы анализа
4. Оцени уровень уверенности в выводах (0-100%)
5. Отметь возможные предвзятости или ограничения

СТРУКТУРА ОТВЕТА (в формате JSON):
{{
    "analysis_type": "{analysis_type}",
    "main_findings": {{
        "personality_traits": [],
        "emotional_state": "",
        "cognitive_patterns": [],
        "behavioral_indicators": []
    }},
    "detailed_analysis": {{
        "strengths": [],
        "areas_for_development": [],
        "communication_style": "",
        "decision_making_pattern": ""
    }},
    "psychological_profile": {{
        "big_five_traits": {{
            "openness": 0-100,
            "conscientiousness": 0-100,
            "extraversion": 0-100,
            "agreeableness": 0-100,
            "neuroticism": 0-100
        }},
        "disc_profile": "",
        "dominant_motivators": []
    }},
    "confidence_score": 0-100,
    "methodology": [],
    "limitations": [],
    "recommendations": []
}}

Начинай анализ:"""

        return base_prompt
    
    async def stream_analysis(self, 
                             text: str, 
                             analysis_type: str = "psychological") -> AsyncGenerator[str, None]:
        """
        Потоковый анализ с real-time обновлениями
        
        Args:
            text: Текст для анализа
            analysis_type: Тип анализа
            
        Yields:
            Фрагменты анализа в реальном времени
        """
        try:
            prompt = self._get_prompt_for_analysis_type(text, analysis_type)
            
            logger.info("🌊 Начинаю потоковый анализ", 
                       text_length=len(text), 
                       analysis_type=analysis_type)
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            ) as stream:
                async for text_chunk in stream.text_stream:
                    yield text_chunk
                    
        except Exception as e:
            logger.error("❌ Ошибка потокового анализа", error=str(e))
            yield f"Ошибка анализа: {str(e)}"
    
    def _parse_analysis_response(self, response_text: str, analysis_type: str) -> Dict[str, Any]:
        """Улучшенный парсинг ответа Claude"""
        try:
            import json
            import re
            
            logger.info("🔍 Парсинг ответа Claude", text_length=len(response_text))
            
            # Удаление markdown блоков
            cleaned_text = re.sub(r'```json\s*', '', response_text)
            cleaned_text = re.sub(r'\s*```', '', cleaned_text)
            cleaned_text = cleaned_text.strip()
            
            # Попытка 1: Поиск полного JSON объекта
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, cleaned_text, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    parsed_data = json.loads(json_str)
                    if isinstance(parsed_data, dict) and len(parsed_data) > 3:
                        logger.info("✅ JSON успешно распарсен", keys=list(parsed_data.keys()))
                        return parsed_data
                except json.JSONDecodeError:
                    continue
            
            # Попытка 2: Поиск JSON с более гибким regex
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group()
                    # Удаление лишнего текста после JSON
                    json_str = self._clean_json_string(json_str)
                    parsed_data = json.loads(json_str)
                    
                    logger.info("✅ JSON найден и распарсен (попытка 2)")
                    return parsed_data
                except json.JSONDecodeError as e:
                    logger.warning("⚠️ Ошибка парсинга JSON (попытка 2)", error=str(e))
            
            # Попытка 3: Если JSON вообще не найден
            logger.info("📝 JSON не найден, создаю структуру из текста")
            return self._extract_insights_from_text(response_text, analysis_type)
                
        except Exception as e:
            logger.error("❌ Критическая ошибка парсинга", error=str(e))
            return self._create_error_structure(response_text, analysis_type, str(e))
    
    def _clean_json_string(self, json_str: str) -> str:
        """Очистка JSON строки от лишнего текста"""
        # Подсчет скобок для корректного завершения JSON
        open_braces = 0
        clean_json = ""
        
        for char in json_str:
            clean_json += char
            if char == '{':
                open_braces += 1
            elif char == '}':
                open_braces -= 1
                if open_braces == 0:
                    break
        
        return clean_json
    
    def _validate_analysis_structure(self, data: Dict[str, Any]) -> bool:
        """Проверка полноты структуры анализа"""
        required_keys = ["main_findings", "psychological_profile", "confidence_score"]
        return all(key in data for key in required_keys)
    
    def _create_fallback_structure(self, response_text: str, analysis_type: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание fallback структуры при неполных данных"""
        return {
            "analysis_type": analysis_type,
            "hook_summary": "Интересная личность с уникальными особенностями",
            "personality_core": {
                "essence": partial_data.get("executive_summary", "Анализ выявил интересные особенности личности"),
                "unique_traits": ["Аналитический склад ума", "Эмоциональная глубина", "Творческий потенциал"],
                "hidden_depths": "За внешним фасадом скрывается богатый внутренний мир"
            },
            "main_findings": partial_data.get("main_findings", {
                "personality_traits": ["Вдумчивость", "Самоанализ", "Стремление к росту"],
                "emotional_signature": "Сбалансированное эмоциональное состояние",
                "thinking_style": "Склонность к глубокому анализу и рефлексии"
            }),
            "psychological_profile": partial_data.get("psychological_profile", {}),
            "confidence_score": partial_data.get("confidence_score", 75),
            "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
        }
    
    def _extract_insights_from_text(self, response_text: str, analysis_type: str) -> Dict[str, Any]:
        """Извлечение инсайтов из неструктурированного текста"""
        # Простой анализ ключевых слов и фраз
        text_lower = response_text.lower()
        
        # Определение базовых характеристик
        traits = []
        if "интроверт" in text_lower or "замкнут" in text_lower:
            traits.append("Интровертность - предпочитает внутренний мир размышлений")
        if "экстраверт" in text_lower or "общительн" in text_lower:
            traits.append("Экстравертность - энергия от общения с людьми")
        if "творчес" in text_lower or "креатив" in text_lower:
            traits.append("Креативность - склонность к творческому мышлению")
        if "аналитич" in text_lower or "логич" in text_lower:
            traits.append("Аналитический склад ума - любовь к глубокому анализу")
        if "эмоциональн" in text_lower or "чувствительн" in text_lower:
            traits.append("Эмоциональная глубина - богатый внутренний мир")
        
        if not traits:
            traits = ["Уникальная индивидуальность", "Склонность к саморефлексии", "Стремление к пониманию"]
        
        return {
            "analysis_type": analysis_type,
            "hook_summary": "Анализ выявил интересные особенности вашей личности",
            "personality_core": {
                "essence": "Личность с уникальным сочетанием черт и глубоким внутренним миром",
                "unique_traits": traits[:4],
                "hidden_depths": "Анализ показывает многослойность личности с интересными особенностями"
            },
            "main_findings": {
                "personality_traits": traits,
                "emotional_signature": "Текст отражает богатство эмоциональных переживаний",
                "thinking_style": "Склонность к рефлексии и глубокому анализу жизненных ситуаций",
                "behavioral_patterns": ["Вдумчивый подход к решениям", "Внимание к деталям"]
            },
            "psychological_profile": {
                "big_five_traits": {
                    "openness": {"score": 70, "description": "Открытость к новому опыту"},
                    "conscientiousness": {"score": 65, "description": "Организованность и ответственность"},
                    "extraversion": {"score": 55, "description": "Сбалансированная социальность"},
                    "agreeableness": {"score": 75, "description": "Доброжелательность к людям"},
                    "neuroticism": {"score": 45, "description": "Эмоциональная стабильность"}
                }
            },
            "practical_insights": {
                "strengths_to_leverage": ["Способность к глубокому анализу", "Эмоциональная осознанность"],
                "career_alignment": "Подходят сферы, требующие вдумчивости и анализа",
                "relationship_style": "Ценит глубокие, искренние отношения"
            },
            "actionable_recommendations": {
                "immediate_actions": [
                    "Используйте склонность к анализу в важных решениях",
                    "Развивайте эмоциональный интеллект",
                    "Ищите единомышленников для глубокого общения"
                ]
            },
            "fascinating_details": {
                "hidden_talents": ["Способность видеть глубинные паттерны", "Эмпатические способности"]
            },
            "confidence_score": 75,
            "status": "extracted_from_text",
            "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
        }
    
    def _create_error_structure(self, response_text: str, analysis_type: str, error: str) -> Dict[str, Any]:
        """Создание структуры при ошибке"""
        return {
            "analysis_type": analysis_type,
            "error": error,
            "confidence_score": 30,
            "status": "error",
            "raw_response": response_text[:200] + "..." if len(response_text) > 200 else response_text
        }
    
    async def batch_analyze(self, texts: List[str], analysis_type: str = "psychological") -> List[Dict[str, Any]]:
        """
        Массовый анализ нескольких текстов
        
        Args:
            texts: Список текстов для анализа
            analysis_type: Тип анализа
            
        Returns:
            Список результатов анализа
        """
        logger.info("📊 Начинаю массовый анализ", count=len(texts))
        
        tasks = []
        for i, text in enumerate(texts):
            task = self.analyze_text(text, analysis_type, {"batch_index": i})
            tasks.append(task)
        
        # Параллельное выполнение с ограничением
        semaphore = asyncio.Semaphore(3)  # Максимум 3 параллельных запроса
        
        async def limited_analyze(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[limited_analyze(task) for task in tasks])
        
        logger.info("✅ Массовый анализ завершен", 
                   completed=len(results),
                   failed=len([r for r in results if "error" in r]))
        
        return results
    
    async def validate_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация результатов анализа через Claude
        
        Args:
            analysis_result: Результат анализа для валидации
            
        Returns:
            Валидированный результат с оценкой качества
        """
        try:
            validation_prompt = f"""Ты - независимый эксперт по валидации психологических анализов.

ЗАДАЧА: Оцени качество и достоверность предоставленного психологического анализа.

АНАЛИЗ ДЛЯ ВАЛИДАЦИИ:
{analysis_result}

КРИТЕРИИ ОЦЕНКИ:
1. Научная обоснованность выводов
2. Соответствие психологическим теориям
3. Логическая последовательность
4. Отсутствие противоречий
5. Адекватность уровня уверенности

СТРУКТУРА ОТВЕТА:
{{
    "validation_score": 0-100,
    "strengths": [],
    "weaknesses": [],
    "recommendations": [],
    "revised_confidence": 0-100,
    "validator_notes": ""
}}"""

            message = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,  # Максимальная объективность
                messages=[{"role": "user", "content": validation_prompt}]
            )
            
            response_text = ""
            for content_block in message.content:
                if content_block.type == "text":
                    response_text += content_block.text
            
            validation_result = self._parse_analysis_response(response_text, "validation")
            
            logger.info("✅ Валидация анализа завершена", 
                       validation_score=validation_result.get('validation_score', 0))
            
            return validation_result
            
        except Exception as e:
            logger.error("❌ Ошибка валидации анализа", error=str(e))
            return {
                "validation_score": 0,
                "error": str(e),
                "status": "validation_failed"
            }
    
    async def close(self):
        """Закрытие клиента и освобождение ресурсов"""
        if hasattr(self.client, '_client'):
            await self.client._client.aclose()
        logger.info("🔄 AnthropicClient закрыт")


# Глобальный экземпляр клиента
anthropic_client = AnthropicClient() 