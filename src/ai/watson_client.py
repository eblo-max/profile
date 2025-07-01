"""
Профессиональный клиент для OpenAI GPT-4o 
ЗАМЕНА DEPRECATED IBM Watson Personality Insights
"""
import asyncio
import structlog
from typing import Dict, Any, Optional, List
import json
from openai import AsyncOpenAI

from src.config.settings import settings

logger = structlog.get_logger()


class OpenAIClient:
    """Асинхронный клиент для OpenAI GPT-4o психологического анализа"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.client = None
        self.is_available = False
        
        if settings.openai_api_key:
            try:
                self.client = AsyncOpenAI(
                    api_key=settings.openai_api_key,
                    timeout=60.0,
                    max_retries=3
                )
                self.is_available = True
                logger.info("✅ OpenAI GPT-4o клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации OpenAI: {e}")
                self.is_available = False
        else:
            logger.warning("⚠️ OPENAI_API_KEY не найден")
    
    async def analyze_personality(self, text: str) -> Dict[str, Any]:
        """
        Анализ личности с помощью GPT-4o
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами анализа личности
        """
        if not self.is_available:
            return self._get_empty_personality_result()
        
        try:
            personality_prompt = f"""
            Проанализируй следующий текст с точки зрения психологии личности.
            Оцени по шкале 0-100 следующие характеристики Big Five:
            1. Открытость опыту (Openness)
            2. Добросовестность (Conscientiousness) 
            3. Экстраверсия (Extraversion)
            4. Доброжелательность (Agreeableness)
            5. Нейротизм (Neuroticism)
            
            Также определи тип MBTI и DISC профиль.
            
            Текст для анализа:
            {text}
            
            Верни результат СТРОГО в JSON формате:
            {{
                "big_five": {{
                    "openness": 85,
                    "conscientiousness": 75,
                    "extraversion": 60,
                    "agreeableness": 90,
                    "neuroticism": 25
                }},
                "mbti": "ENFJ",
                "disc": "Influencer",
                "confidence": 0.87,
                "summary": "Краткая характеристика личности"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": personality_prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info("✅ OpenAI анализ личности выполнен")
            return result
            
        except json.JSONDecodeError:
            logger.error("❌ Ошибка парсинга JSON от OpenAI")
            return self._get_empty_personality_result()
        except Exception as e:
            logger.error(f"❌ Ошибка OpenAI анализа личности: {e}")
            return self._get_empty_personality_result()
    
    async def analyze_emotions(self, text: str) -> Dict[str, Any]:
        """
        Анализ эмоций с помощью GPT-4o
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами анализа эмоций
        """
        if not self.is_available:
            return self._get_empty_emotion_result()
        
        try:
            emotion_prompt = f"""
            Проанализируй эмоциональное состояние автора текста.
            Определи основные эмоции и их интенсивность по шкале 0-100.
            
            Анализируй следующие эмоции:
            - Радость (Joy)
            - Грусть (Sadness)  
            - Гнев (Anger)
            - Страх (Fear)
            - Удивление (Surprise)
            - Отвращение (Disgust)
            - Тревога (Anxiety)
            - Уверенность (Confidence)
            
            Текст для анализа:
            {text}
            
            Верни результат СТРОГО в JSON формате:
            {{
                "emotions": {{
                    "joy": 75,
                    "sadness": 20,
                    "anger": 10,
                    "fear": 30,
                    "surprise": 15,
                    "disgust": 5,
                    "anxiety": 25,
                    "confidence": 70
                }},
                "dominant_emotion": "joy",
                "emotional_tone": "positive",
                "intensity": 0.75,
                "confidence": 0.89
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": emotion_prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info("✅ OpenAI анализ эмоций выполнен")
            return result
            
        except json.JSONDecodeError:
            logger.error("❌ Ошибка парсинга JSON от OpenAI")
            return self._get_empty_emotion_result()
        except Exception as e:
            logger.error(f"❌ Ошибка OpenAI анализа эмоций: {e}")
            return self._get_empty_emotion_result()
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Анализ настроений с помощью GPT-4o
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами анализа настроений
        """
        if not self.is_available:
            return self._get_empty_sentiment_result()
        
        try:
            sentiment_prompt = f"""
            Проанализируй настроение (sentiment) следующего текста.
            Определи общий тон, полярность и уверенность.
            
            Текст для анализа:
            {text}
            
            Верни результат СТРОГО в JSON формате:
            {{
                "sentiment": "positive",
                "polarity": 0.7,
                "confidence": 0.85,
                "subjectivity": 0.6,
                "categories": ["optimistic", "motivated", "friendly"]
            }}
            
            Где:
            - sentiment: "positive", "negative", "neutral"
            - polarity: от -1 (очень негативно) до +1 (очень позитивно)
            - confidence: уверенность в оценке (0-1)
            - subjectivity: субъективность (0=объективно, 1=субъективно)
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": sentiment_prompt}],
                temperature=0.2,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info("✅ OpenAI анализ настроений выполнен")
            return result
            
        except json.JSONDecodeError:
            logger.error("❌ Ошибка парсинга JSON от OpenAI")
            return self._get_empty_sentiment_result()
        except Exception as e:
            logger.error(f"❌ Ошибка OpenAI анализа настроений: {e}")
            return self._get_empty_sentiment_result()
    
    def _get_empty_personality_result(self) -> Dict[str, Any]:
        """Пустой результат анализа личности"""
        return {
            "big_five": {
                "openness": 50,
                "conscientiousness": 50,
                "extraversion": 50,
                "agreeableness": 50,
                "neuroticism": 50
            },
            "mbti": "Unknown",
            "disc": "Unknown",
            "confidence": 0.0,
            "summary": "OpenAI недоступен"
        }
    
    def _get_empty_emotion_result(self) -> Dict[str, Any]:
        """Пустой результат анализа эмоций"""
        return {
            "emotions": {
                "joy": 50, "sadness": 50, "anger": 50, "fear": 50,
                "surprise": 50, "disgust": 50, "anxiety": 50, "confidence": 50
            },
            "dominant_emotion": "neutral",
            "emotional_tone": "neutral",
            "intensity": 0.5,
            "confidence": 0.0
        }
    
    def _get_empty_sentiment_result(self) -> Dict[str, Any]:
        """Пустой результат анализа настроений"""
        return {
            "sentiment": "neutral",
            "polarity": 0.0,
            "confidence": 0.0,
            "subjectivity": 0.5,
            "categories": ["unknown"]
        }


# Глобальный экземпляр клиента
openai_client = OpenAIClient() 