"""AI service for text analysis using Claude Sonnet 4 via OpenRouter"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List

import httpx
from loguru import logger

from app.core.config import settings
from app.core.redis import redis_client
from app.utils.exceptions import AIServiceError
from app.utils.helpers import safe_json_loads, create_cache_key, extract_json_from_text
from app.prompts.analysis_prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    PROFILER_SYSTEM_PROMPT, 
    COMPATIBILITY_SYSTEM_PROMPT,
    get_text_analysis_prompt,
    get_profiler_prompt,
    get_compatibility_prompt
)
from app.utils.enums import UrgencyLevel
import traceback


class AIService:
    """Простой эффективный AI сервис с Claude Sonnet 4"""
    
    def __init__(self):
        # OpenRouter API configuration
        self.openrouter_api_key = settings.OPENAI_API_KEY  # Используем OPENAI_API_KEY для OpenRouter
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.model = "anthropic/claude-sonnet-4"
        
        # Request limiting
        self._request_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_AI_REQUESTS)
        self._last_request_time = 0
        self._last_model_used = self.model
        
        logger.info(f"✅ AIService initialized with {self.model}")
    
    def _get_last_model_used(self) -> str:
        """Get the last model used for analysis"""
        return self._last_model_used
    
    async def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < settings.AI_RATE_LIMIT_SECONDS:
            await asyncio.sleep(settings.AI_RATE_LIMIT_SECONDS - time_since_last)
        self._last_request_time = time.time()
    
    async def _get_ai_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "text",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> str:
        """Get response from Claude Sonnet 4 via OpenRouter"""
        
        if not self.openrouter_api_key:
            raise AIServiceError("OpenRouter API key не настроен")
        
        if not self.openrouter_api_key.startswith('sk-or-'):
            raise AIServiceError("Неверный формат OpenRouter API ключа")
        
        await self._rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://psychodetective.ai",
            "X-Title": "PsychoDetective AI"
        }
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenRouter API error {response.status_code}: {error_text}")
                    raise AIServiceError(f"OpenRouter API ошибка: {response.status_code}")
                
                result = response.json()
                
                if 'choices' not in result or not result['choices']:
                    logger.error(f"Invalid OpenRouter response: {result}")
                    raise AIServiceError("Неверный ответ от OpenRouter API")
                
                content = result['choices'][0]['message']['content']
                logger.info(f"✅ OpenRouter response received: {len(content)} chars")
                
                return content
                
        except httpx.TimeoutException:
            logger.error("OpenRouter API timeout")
            raise AIServiceError("Таймаут OpenRouter API")
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise AIServiceError(f"Ошибка OpenRouter API: {str(e)}")
    
    async def analyze_text(
        self,
        text: str,
        analysis_type: str = "general",
        user_id: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Простой анализ текста"""
        start_time = time.time()
        
        # Cache key
        cache_key = create_cache_key("text_analysis", user_id or 0, hash(text + analysis_type))
        
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"📦 Text analysis cache hit")
                return cached_result
        
        try:
            # Create prompts
            system_prompt = ANALYSIS_SYSTEM_PROMPT
            user_prompt = get_text_analysis_prompt(text, analysis_type)
            
            # Get AI response
            async with self._request_semaphore:
                response = await self._get_ai_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format="json",
                    max_tokens=3000
                )
            
            # Parse response
            result = self._parse_analysis_response(response)
            result["processing_time"] = time.time() - start_time
            result["ai_model_used"] = self._get_last_model_used()
            
            # Cache result
            if use_cache:
                await redis_client.set(cache_key, result, expire=settings.ANALYSIS_CACHE_TTL)
            
            logger.info(f"✅ Text analysis completed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Text analysis failed: {e}")
            raise AIServiceError(f"Анализ текста не удался: {str(e)}")
    
    async def profile_partner(
        self,
        answers: List[Dict[str, Any]],
        user_id: int,
        partner_name: str = "партнер",
        partner_description: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Простое эффективное профилирование партнера"""
        start_time = time.time()
        
        # Format answers
        if isinstance(answers, list):
            answers_text = []
            for answer in answers:
                question_text = answer.get('question', f"Question {answer.get('question_id', 'N/A')}")
                answer_text = answer.get('answer', 'No answer')
                answers_text.append(f"Q: {question_text}\nA: {answer_text}")
            combined_answers = "\n\n".join(answers_text)
        else:
            combined_answers = str(answers)
        
        # Cache key
        cache_key = create_cache_key("profile_analysis", user_id, hash(combined_answers + partner_name))
        
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"📦 Profile analysis cache hit for user {user_id}")
                return cached_result
        
        try:
            # Подготавливаем данные для анализа
            analysis_data = {
                'questionnaire_data': {
                    f'question_{i}': {
                        'question': answer.get('question', f'Вопрос {i}'),
                        'answer': answer.get('answer', str(answer))
                    } for i, answer in enumerate(answers, 1)
                },
                'partner_name': partner_name,
                'partner_description': partner_description
            }
            
            # Create enhanced prompts
            user_prompt = self._create_enhanced_user_prompt(analysis_data)
            
            # Get analysis from Claude Sonnet 4
            async with self._request_semaphore:
                response = await self._get_ai_response(
                    system_prompt="",  # Системный промпт включен в user_prompt
                    user_prompt=user_prompt,
                    response_format="text",  # Изменено на text для детального анализа
                    max_tokens=8000,  # Увеличено для детального анализа
                    temperature=0.7  # Более креативный анализ
                )
            
            # Parse response - теперь это текстовый анализ
            result = {
                "psychological_profile": response,
                "processing_time": time.time() - start_time,
                "ai_model_used": self._get_last_model_used(),
                "analysis_mode": "detailed_portrait",
                "cost_estimate": 0.15,  # Увеличена стоимость из-за детального анализа
                "word_count": len(response.split()),
                "character_count": len(response)
            }
            
            # Cache result
            if use_cache:
                await redis_client.set(cache_key, result, expire=settings.ANALYSIS_CACHE_TTL)
            
            logger.info(f"✅ Profile analysis completed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Profile analysis failed: {e}")
            raise AIServiceError(f"Профилирование не удалось: {str(e)}")
    
    async def check_compatibility(
        self,
        user_profile: Dict[str, Any],
        partner_profile: Dict[str, Any],
        user_id: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Анализ совместимости"""
        start_time = time.time()
        
        # Cache key
        cache_key = create_cache_key("compatibility", user_id or 0, 
                                   hash(str(user_profile) + str(partner_profile)))
        
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"📦 Compatibility analysis cache hit")
                return cached_result
        
        try:
            # Create prompts
            system_prompt = COMPATIBILITY_SYSTEM_PROMPT
            user_prompt = get_compatibility_prompt(user_profile, partner_profile)
            
            # Get AI response
            async with self._request_semaphore:
                response = await self._get_ai_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format="json",
                    max_tokens=3000
                )
            
            # Parse response
            result = self._parse_compatibility_response(response)
            result["processing_time"] = time.time() - start_time
            result["ai_model_used"] = self._get_last_model_used()
            
            # Cache result
            if use_cache:
                await redis_client.set(cache_key, result, expire=settings.ANALYSIS_CACHE_TTL)
            
            logger.info(f"✅ Compatibility analysis completed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Compatibility analysis failed: {e}")
            raise AIServiceError(f"Анализ совместимости не удался: {str(e)}")
    
    def _create_enhanced_system_prompt(self) -> str:
        """Создает улучшенный системный промпт"""
        return """Ты эксперт-психолог с 15-летним опытом анализа личности и отношений. 

Твоя специализация:
- Клиническая психология и диагностика расстройств личности
- Семейная терапия и анализ токсичных отношений  
- Криминальная психология и профайлинг
- Нейропсихология и поведенческий анализ

ВАЖНО: 
- Отвечай строго в JSON формате без дополнительного текста
- Будь максимально точен и конкретен в оценках
- Используй профессиональную терминологию
- Указывай конкретные поведенческие паттерны и красные флаги"""
    
    def _create_enhanced_user_prompt(self, analysis_data: dict) -> str:
        """Создает детальный промпт для анализа с использованием данных анкеты"""
        
        # Системный промпт для детального анализа
        system_prompt = """
Ты - эксперт по криминальной психологии и профайлингу с 20-летним опытом работы с токсичными личностями. Твоя задача - создавать глубокие психологические портреты партнеров на основе ответов на диагностические вопросы.

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ К ПОРТРЕТУ:

1. ОБЪЕМ: 2000-2500 слов (это критически важно!)
2. ЯЗЫК: Научно-популярный, доступный русскому читателю
3. СТРУКТУРА: Использовать заголовки с эмодзи для каждого раздела
4. ПРИМЕРЫ: Минимум 5-7 конкретных историй с именами и деталями
5. НАУЧНОСТЬ: Ссылки на реальные психологические концепции и модели

ОБЯЗАТЕЛЬНАЯ СТРУКТУРА ПОРТРЕТА:

ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ: "[Тип личности]"

ОБЩАЯ ХАРАКТЕРИСТИКА ЛИЧНОСТИ
- Первое впечатление vs реальность
- Оценка по модели "Темной триады" (нарциссизм/макиавеллизм/психопатия)
- Ключевые личностные особенности

ОСНОВНОЙ ПАТТЕРН ПОВЕДЕНИЯ В ОТНОШЕНИЯХ
- Детальное описание главной токсичной черты
- 2-3 конкретных примера с именами и ситуациями
- Психологические механизмы

КОНТРОЛИРУЮЩЕЕ ПОВЕДЕНИЕ
- Эволюция контроля: от "заботы" к тотальному надзору
- Конкретные техники контроля
- История из жизни с деталями

МАНИПУЛЯТИВНЫЕ ТЕХНИКИ
- Газлайтинг с примерами фраз
- Эмоциональный шантаж
- Переписывание истории конфликтов

ЭМОЦИОНАЛЬНАЯ ДИЗРЕГУЛЯЦИЯ
- Непредсказуемость реакций
- Двойные стандарты
- Проекция и обвинения

ИНТИМНОСТЬ КАК ИНСТРУМЕНТ
- Использование близости для контроля
- Конкретные паттерны поведения
- Травматичные аспекты

СОЦИАЛЬНАЯ МАСКА
- Публичный образ vs частное поведение
- Когнитивный диссонанс у партнера
- Примеры двойственности

ПРОГНОЗ И РЕКОМЕНДАЦИИ
- Способность к изменениям
- Цикличность токсичных отношений
- Конкретные рекомендации партнерам

СТИЛИСТИЧЕСКИЕ ТРЕБОВАНИЯ:

1. Используй конкретные имена в примерах (Анна, Марина, Елена и т.д.)
2. Включай прямую речь и цитаты ("фразы в кавычках")
3. Описывай физиологические реакции и невербалику
4. Ссылайся на исследования и авторов (можно использовать реальные)
5. Используй метафоры для сложных концепций
6. Чередуй длинные аналитические абзацы с короткими выводами

ОБЯЗАТЕЛЬНЫЕ ПСИХОЛОГИЧЕСКИЕ КОНЦЕПЦИИ:
- Модель "Темной триады"
- Теория привязанности
- Цикл абьюза
- Газлайтинг
- Эмоциональная дизрегуляция
- Когнитивный диссонанс
- Проекция и другие защитные механизмы

ЗАПРЕЩЕНО:
- Поверхностные обобщения
- Короткие абзацы без примеров
- Абстрактные рассуждения без конкретики
- Излишняя научность без объяснений
- Портреты короче 2000 слов
"""

        # Формируем ответы пользователя
        answers_text = ""
        partner_name = "партнер"
        partner_description = ""
        
        questionnaire_data = analysis_data.get('questionnaire_data', {})
        
        # Извлекаем имя партнера если есть
        if 'partner_name' in analysis_data:
            partner_name = analysis_data['partner_name']
        if 'partner_description' in analysis_data:
            partner_description = analysis_data['partner_description']
        
        for question_id, answer_data in questionnaire_data.items():
            if isinstance(answer_data, dict):
                question = answer_data.get('question', f'Вопрос {question_id}')
                answer = answer_data.get('answer', 'Нет ответа')
                answers_text += f"Вопрос: {question}\nОтвет: {answer}\n\n"
            else:
                answers_text += f"Вопрос {question_id}: {answer_data}\n\n"
        
        # Основной промпт с данными
        user_prompt = f"""
На основе следующих ответов на диагностические вопросы создай глубокий психологический портрет партнера.

ПАРТНЕР: {partner_name} ({partner_description})

[ОТВЕТЫ НА ВОПРОСЫ]
{answers_text}

КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ:

1. ОБЪЕМ: СТРОГО 2400-2700 слов (ОБЯЗАТЕЛЬНО проверяй итоговое количество!)
2. ПЕРСОНАЛИЗАЦИЯ: Упоминай имя {partner_name} минимум 10-12 раз в тексте
3. ЦИТАТЫ: Используй ПРЯМЫЕ цитаты из ответов пользователя минимум 15-20 раз
4. СТРУКТУРА: БЕЗ смайликов, решеток (#), звездочек (*) - только заглавные буквы
5. ПРОФЕССИОНАЛИЗМ: Клинический стиль, научные термины с объяснениями
6. ДЕТАЛИЗАЦИЯ: Каждый раздел минимум 350-400 слов с конкретными примерами

ОБЯЗАТЕЛЬНАЯ СТРУКТУРА (2400-2700 слов):

ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ: [Тип личности {partner_name}]

ОБЩАЯ ХАРАКТЕРИСТИКА ЛИЧНОСТИ (400-450 слов)
- Детальный анализ с упоминанием имени {partner_name}
- Модель "Темной триады" с конкретными баллами
- Первое впечатление vs реальность с примерами
- Влияние профессии на токсичные черты

ДОМИНИРУЮЩИЕ ПОВЕДЕНЧЕСКИЕ ПАТТЕРНЫ (450-500 слов)
- Основные токсичные черты {partner_name}
- 4-5 конкретных примеров с именами партнерш
- Психологические механизмы с научными терминами
- Эволюция поведения во времени

СИСТЕМА КОНТРОЛЯ И МАНИПУЛЯЦИЙ (450-500 слов)
- Эволюция контролирующего поведения {partner_name}
- Конкретные техники с цитатами из ответов
- Финансовый, эмоциональный, социальный, цифровой контроль
- Изоляция от поддержки

ЭМОЦИОНАЛЬНАЯ ДИЗРЕГУЛЯЦИЯ И АГРЕССИЯ (400-450 слов)
- Паттерны гнева и непредсказуемости {partner_name}
- Проекция и двойные стандарты
- Влияние на психическое здоровье партнерши
- Циклы насилия и примирения

ИНТИМНОСТЬ И НАРУШЕНИЕ ГРАНИЦ (400-450 слов)
- Использование близости как инструмента власти
- Принуждение и эмоциональный шантаж
- Травматические аспекты отношений
- Долгосрочные последствия для жертвы

СОЦИАЛЬНАЯ МАСКА И ИЗОЛЯЦИЯ (350-400 слов)
- Публичный образ vs частное поведение {partner_name}
- Когнитивный диссонанс у жертвы
- Изоляция от поддержки
- Влияние на окружение

ПРОГНОЗ И ПРОФЕССИОНАЛЬНЫЕ РЕКОМЕНДАЦИИ (450-500 слов)
- Вероятность изменений {partner_name}
- Детальный план безопасного выхода
- Психологическая реабилитация
- Профилактика повторной виктимизации

СПЕЦИАЛЬНЫЕ ТРЕБОВАНИЯ:
- Каждый раздел начинай с анализа конкретного поведения {partner_name}
- Используй фразы: "Поведение {partner_name} указывает на...", "{partner_name} демонстрирует..."
- Включай прямые цитаты из ответов: "Как указано в ответах: '[цитата]'"
- Добавляй научные ссылки: "Согласно исследованиям доктора X..."
- Создавай конкретные истории с именами: "Анна, 28 лет, рассказывает..."

КРИТИЧЕСКИ ВАЖНО:
- Проверь итоговый объем - должно быть СТРОГО 2400-2700 слов!
- Убери ВСЕ решетки (#), звездочки (*) и другие символы из заголовков
- Используй только заглавные буквы для заголовков
- Каждый раздел должен быть детальным и содержательным
- Обязательно упомяни имя {partner_name} в каждом разделе
"""
        
        return system_prompt + "\n\n" + user_prompt
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse general analysis response"""
        try:
            data = extract_json_from_text(response)
            if not data:
                data = safe_json_loads(response, {})
            
            return {
                "analysis": data.get("analysis", "Анализ недоступен"),
                "sentiment": data.get("sentiment", "neutral"),
                "key_points": data.get("key_points", []),
                "recommendations": data.get("recommendations", []),
                "confidence": float(data.get("confidence", 75.0))
            }
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {
                "analysis": "Ошибка парсинга ответа",
                "sentiment": "neutral", 
                "key_points": [],
                "recommendations": [],
                "confidence": 50.0
            }
    
    def _parse_profile_response(self, response: str) -> Dict[str, Any]:
        """Parse partner profile response"""
        try:
            data = extract_json_from_text(response)
            if not data:
                data = safe_json_loads(response, {})
            
            # Validate and extract all required fields
            result = {
                "psychological_profile": data.get("psychological_profile", "Анализ недоступен"),
                "personality_traits": data.get("personality_traits", ["Стабильность", "Надежность"]),
                "behavioral_patterns": data.get("behavioral_patterns", ["Предсказуемое поведение"]),
                "red_flags": data.get("red_flags", []),
                "relationship_style": data.get("relationship_style", "Здоровый стиль отношений"),
                "strengths": data.get("strengths", ["Эмоциональная стабильность"]),
                "potential_challenges": data.get("potential_challenges", ["Требует дополнительного изучения"]),
                "compatibility_factors": data.get("compatibility_factors", ["Открытость к общению"]),
                "recommendations": data.get("recommendations", ["Продолжить знакомство"]),
                "overall_risk_score": float(data.get("overall_risk_score", 25.0)),
                "dark_triad": data.get("dark_triad", {"narcissism": 2.0, "machiavellianism": 1.5, "psychopathy": 1.0}),
                "confidence_level": float(data.get("confidence_level", 85.0)),
                "summary": data.get("summary", "Общий анализ показывает здоровую личность с хорошим потенциалом для отношений."),
                "survival_guide": data.get("survival_guide", ["Продолжить знакомство"]),
                "safety_alerts": data.get("safety_alerts", []),
                "urgency_level": data.get("urgency_level", "LOW"),
                "block_scores": data.get("block_scores", {
                    "narcissism": 2.0, "control": 1.7, "gaslighting": 1.5, 
                    "emotion": 1.3, "intimacy": 1.0, "social": 1.4
                }),
                # Новые поля для детального анализа
                "manipulation_tactics": data.get("manipulation_tactics", ["Эмоциональное давление"]),
                "escalation_triggers": data.get("escalation_triggers", ["Критика поведения"]),
                "control_mechanisms": data.get("control_mechanisms", ["Ограничение общения"])
            }
            
            # Validate urgency level
            valid_urgency = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            if result["urgency_level"] not in valid_urgency:
                result["urgency_level"] = "LOW"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse profile response: {e}")
            return {
                "psychological_profile": "Анализ временно недоступен",
                "personality_traits": ["Стабильность", "Надежность"],
                "behavioral_patterns": ["Предсказуемое поведение"],
                "red_flags": [],
                "relationship_style": "Здоровый стиль отношений",
                "strengths": ["Эмоциональная стабильность"],
                "potential_challenges": ["Требует дополнительного изучения"],
                "compatibility_factors": ["Открытость к общению"],
                "recommendations": ["Продолжить знакомство"],
                "overall_risk_score": 25.0,
                "dark_triad": {"narcissism": 2.0, "machiavellianism": 1.5, "psychopathy": 1.0},
                "confidence_level": 60.0,
                "summary": "Требуется дополнительная информация для полного анализа.",
                "survival_guide": ["Продолжить знакомство"],
                "safety_alerts": [],
                "urgency_level": "LOW",
                "block_scores": {"narcissism": 2.0, "control": 1.7, "gaslighting": 1.5, "emotion": 1.3, "intimacy": 1.0, "social": 1.4},
                "manipulation_tactics": ["Эмоциональное давление"],
                "escalation_triggers": ["Критика поведения"],
                "control_mechanisms": ["Ограничение общения"]
            }
    
    def _parse_compatibility_response(self, response: str) -> Dict[str, Any]:
        """Parse compatibility analysis response"""
        try:
            data = extract_json_from_text(response)
            if not data:
                data = safe_json_loads(response, {})
            
            return {
                "compatibility_score": float(data.get("compatibility_score", 75.0)),
                "strengths": data.get("strengths", ["Общие интересы"]),
                "challenges": data.get("challenges", ["Различия в подходах"]),
                "recommendations": data.get("recommendations", ["Открытое общение"]),
                "long_term_potential": data.get("long_term_potential", "Хороший потенциал"),
                "areas_to_work_on": data.get("areas_to_work_on", ["Взаимопонимание"]),
                "summary": data.get("summary", "Совместимость на хорошем уровне")
            }
        except Exception as e:
            logger.error(f"Failed to parse compatibility response: {e}")
            return {
                "compatibility_score": 70.0,
                "strengths": ["Потенциал для развития"],
                "challenges": ["Требует дополнительного анализа"],
                "recommendations": ["Продолжить изучение совместимости"],
                "long_term_potential": "Требует времени для оценки",
                "areas_to_work_on": ["Взаимопонимание"],
                "summary": "Требуется больше данных для точной оценки совместимости"
            }


# Global AI service instance
ai_service = AIService() 