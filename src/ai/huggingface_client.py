"""
Профессиональный клиент для HuggingFace Transformers API
ЗАМЕНА DEPRECATED AWS Rekognition (для текстового анализа)
"""
import asyncio
import structlog
from typing import Dict, Any, Optional, List
import json
import httpx

from src.config.settings import settings

logger = structlog.get_logger()


class HuggingFaceClient:
    """Асинхронный клиент для HuggingFace Transformers психологического анализа"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.is_available = False
        self.base_url = "https://api-inference.huggingface.co"
        
        # Модели для разных типов анализа (рабочие)
        self.models = {
            "emotion": "cardiffnlp/twitter-roberta-base-emotion",
            "personality": "cardiffnlp/twitter-roberta-base-emotion",  # используем emotion модель
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment",
            "stress": "cardiffnlp/twitter-roberta-base-emotion",  # используем emotion модель
            "mental_health": "cardiffnlp/twitter-roberta-base-sentiment"  # fallback на sentiment
        }
        
        if settings.huggingface_api_key:
            try:
                self.headers = {
                    "Authorization": f"Bearer {settings.huggingface_api_key}",
                    "Content-Type": "application/json"
                }
                self.is_available = True
                logger.info("✅ HuggingFace Transformers клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации HuggingFace: {e}")
                self.is_available = False
        else:
            logger.warning("⚠️ HUGGINGFACE_API_KEY не найден")
    
    async def analyze_emotions_transformers(self, text: str) -> Dict[str, Any]:
        """
        Анализ эмоций с помощью специализированных трансформеров
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами анализа эмоций
        """
        if not self.is_available:
            return self._get_empty_emotions_result()
        
        try:
            # Используем модель emotion classification
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.models['emotion']}",
                    headers=self.headers,
                    json={"inputs": text}
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Обработка результатов
                emotions_data = {}
                if isinstance(result, list) and len(result) > 0:
                    for emotion_item in result[0]:
                        label = emotion_item.get('label', '').lower()
                        score = emotion_item.get('score', 0.0) * 100
                        emotions_data[label] = score
                
                # Структурированный результат
                structured_result = {
                    "transformer_emotions": {
                        "joy": emotions_data.get('joy', 0),
                        "sadness": emotions_data.get('sadness', 0),
                        "anger": emotions_data.get('anger', 0),
                        "fear": emotions_data.get('fear', 0),
                        "surprise": emotions_data.get('surprise', 0),
                        "disgust": emotions_data.get('disgust', 0),
                        "neutral": emotions_data.get('neutral', 0)
                    },
                    "emotional_profile": {
                        "dominant_emotion": max(emotions_data.items(), key=lambda x: x[1])[0] if emotions_data else "neutral",
                        "emotional_intensity": max(emotions_data.values()) if emotions_data else 0,
                        "emotional_diversity": len([v for v in emotions_data.values() if v > 10]) if emotions_data else 0
                    },
                    "transformer_metrics": {
                        "model_used": self.models['emotion'],
                        "confidence_scores": emotions_data,
                        "processing_method": "distilroberta-base"
                    },
                    "psychological_insights": {
                        "emotional_complexity": "complex" if len([v for v in emotions_data.values() if v > 20]) > 3 else "moderate",
                        "emotional_stability": 100 - (max(emotions_data.values()) - min(emotions_data.values())) if emotions_data else 50,
                        "emotional_authenticity": sum(emotions_data.values()) / len(emotions_data) if emotions_data else 50
                    },
                    "confidence": max(emotions_data.values()) / 100 if emotions_data else 0.0,
                    "raw_transformer_output": result
                }
                
                logger.info("✅ HuggingFace анализ эмоций выполнен")
                return structured_result
                
        except Exception as e:
            logger.error(f"❌ Ошибка HuggingFace анализа эмоций: {e}")
            return self._get_empty_emotions_result()
    
    async def analyze_personality_transformers(self, text: str) -> Dict[str, Any]:
        """
        Анализ личности с помощью трансформеров
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами анализа личности
        """
        if not self.is_available:
            return self._get_empty_personality_result()
        
        try:
            # Комбинируем несколько моделей для анализа личности
            sentiment_task = self._analyze_with_model(text, "sentiment")
            emotion_task = self._analyze_with_model(text, "emotion")
            
            # Ждем результаты параллельно
            sentiment_result, emotion_result = await asyncio.gather(
                sentiment_task, emotion_task, return_exceptions=True
            )
            
            # Анализ личности на основе комбинированных результатов
            personality_profile = self._extract_personality_from_results(
                text, sentiment_result, emotion_result
            )
            
            logger.info("✅ HuggingFace анализ личности выполнен")
            return personality_profile
            
        except Exception as e:
            logger.error(f"❌ Ошибка HuggingFace анализа личности: {e}")
            return self._get_empty_personality_result()
    
    async def analyze_mental_health_indicators(self, text: str) -> Dict[str, Any]:
        """
        Анализ индикаторов ментального здоровья
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами анализа ментального здоровья
        """
        if not self.is_available:
            return self._get_empty_mental_health_result()
        
        try:
            # Анализ с помощью специализированной модели
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.models['stress']}",
                    headers=self.headers,
                    json={"inputs": text}
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Обработка результатов
                mental_health_data = {
                    "stress_indicators": {
                        "stress_level": 0,
                        "anxiety_markers": 0,
                        "depression_indicators": 0,
                        "burnout_signs": 0
                    },
                    "resilience_factors": {
                        "coping_mechanisms": 50,
                        "positive_outlook": 50,
                        "social_support_indicators": 50,
                        "self_care_awareness": 50
                    },
                    "psychological_wellbeing": {
                        "emotional_regulation": 50,
                        "cognitive_clarity": 50,
                        "motivation_level": 50,
                        "life_satisfaction_cues": 50
                    },
                    "risk_assessment": {
                        "overall_risk_level": "low",
                        "immediate_concerns": [],
                        "protective_factors": ["transformer analysis"],
                        "recommended_attention_areas": []
                    },
                    "transformer_analysis": {
                        "model_used": self.models['stress'],
                        "confidence": 0.7,
                        "raw_output": result
                    },
                    "confidence": 0.7
                }
                
                # Извлечение конкретных метрик из результата трансформера
                if isinstance(result, list) and len(result) > 0:
                    for item in result[0]:
                        label = item.get('label', '').lower()
                        score = item.get('score', 0.0) * 100
                        
                        if 'stress' in label or 'anxiety' in label:
                            mental_health_data["stress_indicators"]["stress_level"] = score
                        elif 'depression' in label or 'sad' in label:
                            mental_health_data["stress_indicators"]["depression_indicators"] = score
                        elif 'positive' in label or 'joy' in label:
                            mental_health_data["resilience_factors"]["positive_outlook"] = score
                
                logger.info("✅ HuggingFace анализ ментального здоровья выполнен")
                return mental_health_data
                
        except Exception as e:
            logger.error(f"❌ Ошибка HuggingFace анализа ментального здоровья: {e}")
            return self._get_empty_mental_health_result()
    
    async def _analyze_with_model(self, text: str, model_type: str) -> Dict[str, Any]:
        """Вспомогательный метод для анализа с конкретной моделью"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.models[model_type]}",
                    headers=self.headers,
                    json={"inputs": text}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"⚠️ Ошибка анализа с моделью {model_type}: {e}")
            return {}
    
    def _extract_personality_from_results(self, text: str, sentiment_result: Any, emotion_result: Any) -> Dict[str, Any]:
        """Извлечение характеристик личности из результатов трансформеров"""
        personality_data = {
            "big_five_transformer": {
                "openness": 50,
                "conscientiousness": 50,
                "extraversion": 50,
                "agreeableness": 50,
                "neuroticism": 50
            },
            "communication_style": {
                "emotional_expressiveness": 50,
                "assertiveness": 50,
                "social_orientation": 50,
                "formality_level": 50
            },
            "cognitive_patterns": {
                "analytical_thinking": 50,
                "creative_expression": 50,
                "detail_orientation": 50,
                "abstract_thinking": 50
            },
            "transformer_insights": {
                "sentiment_model_results": sentiment_result,
                "emotion_model_results": emotion_result,
                "combined_analysis": "Анализ на основе transformer моделей"
            },
            "confidence": 0.6
        }
        
        # Простая эвристика для извлечения Big Five из результатов
        if isinstance(emotion_result, list) and len(emotion_result) > 0:
            emotions = {item.get('label', '').lower(): item.get('score', 0) for item in emotion_result[0]}
            
            # Эвристики для Big Five
            if emotions.get('joy', 0) > 0.5:
                personality_data["big_five_transformer"]["extraversion"] = min(70 + emotions['joy'] * 30, 100)
            if emotions.get('fear', 0) > 0.3:
                personality_data["big_five_transformer"]["neuroticism"] = min(60 + emotions['fear'] * 40, 100)
            if emotions.get('surprise', 0) > 0.3:
                personality_data["big_five_transformer"]["openness"] = min(60 + emotions['surprise'] * 40, 100)
        
        return personality_data
    
    def _get_empty_emotions_result(self) -> Dict[str, Any]:
        """Пустой результат анализа эмоций"""
        return {
            "transformer_emotions": {
                "joy": 0, "sadness": 0, "anger": 0, "fear": 0,
                "surprise": 0, "disgust": 0, "neutral": 50
            },
            "emotional_profile": {
                "dominant_emotion": "neutral",
                "emotional_intensity": 0,
                "emotional_diversity": 0
            },
            "confidence": 0.0,
            "status": "huggingface_unavailable"
        }
    
    def _get_empty_personality_result(self) -> Dict[str, Any]:
        """Пустой результат анализа личности"""
        return {
            "big_five_transformer": {
                "openness": 50, "conscientiousness": 50, "extraversion": 50,
                "agreeableness": 50, "neuroticism": 50
            },
            "communication_style": {
                "emotional_expressiveness": 50, "assertiveness": 50,
                "social_orientation": 50, "formality_level": 50
            },
            "confidence": 0.0,
            "status": "huggingface_unavailable"
        }
    
    def _get_empty_mental_health_result(self) -> Dict[str, Any]:
        """Пустой результат анализа ментального здоровья"""
        return {
            "stress_indicators": {
                "stress_level": 0, "anxiety_markers": 0,
                "depression_indicators": 0, "burnout_signs": 0
            },
            "resilience_factors": {
                "coping_mechanisms": 50, "positive_outlook": 50,
                "social_support_indicators": 50, "self_care_awareness": 50
            },
            "confidence": 0.0,
            "status": "huggingface_unavailable"
        }


# Глобальный экземпляр клиента
huggingface_client = HuggingFaceClient() 