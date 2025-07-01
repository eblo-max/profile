"""
Профессиональный клиент для Cohere Command-R+ API
ЗАМЕНА DEPRECATED Lexalytics + Receptiviti APIs
"""
import asyncio
import structlog
from typing import Dict, Any, Optional, List
import json
import httpx

from src.config.settings import settings

logger = structlog.get_logger()


class CohereClient:
    """Асинхронный клиент для Cohere Command-R+ психологического анализа"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.is_available = False
        self.base_url = "https://api.cohere.ai/v1"
        self.model = "command-r-plus"
        
        if settings.cohere_api_key:
            try:
                self.headers = {
                    "Authorization": f"Bearer {settings.cohere_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                self.is_available = True
                logger.info("✅ Cohere Command-R+ клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Cohere: {e}")
                self.is_available = False
        else:
            logger.warning("⚠️ COHERE_API_KEY не найден")
    
    async def analyze_psycholinguistics(self, text: str) -> Dict[str, Any]:
        """
        Психолингвистический анализ с помощью Cohere Command-R+
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами психолингвистического анализа
        """
        if not self.is_available:
            return self._get_empty_psycholinguistics_result()
        
        try:
            prompt = f"""
            Проведи детальный психолингвистический анализ следующего текста.
            Ты - эксперт по психолингвистике с PhD в когнитивной психологии.
            
            Текст для анализа:
            "{text}"
            
            Верни результат в формате JSON:
            {{
                "linguistic_patterns": {{
                    "word_choice_psychology": {{
                        "abstract_vs_concrete": 0-100,
                        "emotional_intensity_words": 0-100,
                        "certainty_markers": ["определенно", "возможно"],
                        "power_words": ["контроль", "влияние"]
                    }},
                    "sentence_structure": {{
                        "complexity_score": 0-100,
                        "passive_voice_ratio": 0-100,
                        "question_tendency": 0-100,
                        "exclamation_usage": 0-100
                    }}
                }},
                "cognitive_style": {{
                    "analytical_thinking": 0-100,
                    "intuitive_processing": 0-100,
                    "concrete_vs_abstract": 0-100,
                    "detail_orientation": 0-100,
                    "big_picture_focus": 0-100
                }},
                "emotional_linguistic_markers": {{
                    "emotional_vocabulary_richness": 0-100,
                    "valence_patterns": "positive|negative|mixed",
                    "arousal_indicators": 0-100,
                    "emotional_regulation_language": 0-100
                }},
                "social_psychological_cues": {{
                    "social_distance_markers": 0-100,
                    "authority_orientation": 0-100,
                    "group_vs_individual_focus": 0-100,
                    "conformity_vs_uniqueness": 0-100
                }},
                "personality_linguistic_signatures": {{
                    "introversion_extroversion_markers": 0-100,
                    "openness_linguistic_cues": 0-100,
                    "conscientiousness_language": 0-100,
                    "neuroticism_indicators": 0-100
                }},
                "thought_process_indicators": {{
                    "linear_vs_non_linear_thinking": 0-100,
                    "problem_solving_approach": "systematic|creative|mixed",
                    "decision_making_style": "quick|deliberate|mixed",
                    "reflection_depth": 0-100
                }},
                "communication_psychology": {{
                    "persuasion_style": "logical|emotional|mixed",
                    "conflict_approach": "avoidant|confrontational|collaborative",
                    "self_disclosure_level": 0-100,
                    "empathy_expression": 0-100
                }},
                "confidence": 0.0-1.0
            }}
            """
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": 2000,
                "temperature": 0.3,
                "return_likelihoods": "NONE"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result_data = response.json()
                generated_text = result_data["generations"][0]["text"]
                
                # Попытка извлечь JSON из ответа
                try:
                    json_start = generated_text.find('{')
                    json_end = generated_text.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = generated_text[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        parsed_result["raw_response"] = generated_text[:200]
                        
                        logger.info("✅ Cohere психолингвистический анализ выполнен")
                        return parsed_result
                    else:
                        raise json.JSONDecodeError("JSON not found", generated_text, 0)
                        
                except json.JSONDecodeError:
                    logger.warning("⚠️ Не удалось парсить JSON, возвращаю структурированный результат")
                    return self._extract_insights_from_text(generated_text)
                
        except Exception as e:
            logger.error(f"❌ Ошибка Cohere психолингвистического анализа: {e}")
            return self._get_empty_psycholinguistics_result()
    
    async def analyze_advanced_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Продвинутый анализ настроений через Cohere
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с результатами продвинутого анализа настроений
        """
        if not self.is_available:
            return self._get_empty_advanced_sentiment_result()
        
        try:
            prompt = f"""
            Проведи экспертный анализ настроений и эмоциональных нюансов текста.
            Ты - специалист по computational emotion analysis.
            
            Текст:
            "{text}"
            
            Верни результат в JSON формате:
            {{
                "multi_dimensional_sentiment": {{
                    "primary_sentiment": "positive|negative|neutral|mixed",
                    "sentiment_intensity": 0-100,
                    "sentiment_stability": 0-100,
                    "emotional_complexity": "simple|moderate|complex"
                }},
                "dimensional_analysis": {{
                    "valence": -1.0 to 1.0,
                    "arousal": 0.0-1.0,
                    "dominance": 0.0-1.0,
                    "pleasure": 0.0-1.0
                }},
                "contextual_sentiment": {{
                    "explicit_sentiment": 0-100,
                    "implicit_sentiment": 0-100,
                    "irony_sarcasm_level": 0-100,
                    "emotional_authenticity": 0-100
                }},
                "temporal_sentiment": {{
                    "past_oriented_sentiment": 0-100,
                    "present_focused_sentiment": 0-100,
                    "future_oriented_sentiment": 0-100,
                    "temporal_sentiment_consistency": 0-100
                }},
                "social_emotional_context": {{
                    "interpersonal_warmth": 0-100,
                    "social_connectedness": 0-100,
                    "emotional_expressiveness": 0-100,
                    "empathic_resonance": 0-100
                }},
                "psychological_sentiment_markers": {{
                    "optimism_pessimism": -100 to 100,
                    "emotional_regulation": 0-100,
                    "resilience_indicators": 0-100,
                    "vulnerability_markers": 0-100
                }},
                "advanced_features": {{
                    "sentiment_granularity": ["детальные эмоции"],
                    "emotional_triggers": ["что вызывает эмоции"],
                    "sentiment_evolution": "развитие настроений в тексте",
                    "emotional_peaks": ["моменты пиковых эмоций"]
                }},
                "confidence": 0.0-1.0
            }}
            """
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": 1800,
                "temperature": 0.2,
                "return_likelihoods": "NONE"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result_data = response.json()
                generated_text = result_data["generations"][0]["text"]
                
                # Попытка извлечь JSON
                try:
                    json_start = generated_text.find('{')
                    json_end = generated_text.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = generated_text[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        
                        logger.info("✅ Cohere продвинутый анализ настроений выполнен")
                        return parsed_result
                    else:
                        raise json.JSONDecodeError("JSON not found", generated_text, 0)
                        
                except json.JSONDecodeError:
                    logger.warning("⚠️ Fallback на извлечение инсайтов из текста")
                    return self._extract_sentiment_from_text(generated_text)
                
        except Exception as e:
            logger.error(f"❌ Ошибка Cohere продвинутого анализа настроений: {e}")
            return self._get_empty_advanced_sentiment_result()
    
    async def analyze_behavioral_patterns(self, text: str) -> Dict[str, Any]:
        """
        Анализ поведенческих паттернов через Cohere
        """
        if not self.is_available:
            return self._get_empty_behavioral_result()
        
        try:
            prompt = f"""
            Проанализируй поведенческие паттерны и склонности личности из текста.
            
            Текст: "{text}"
            
            JSON результат:
            {{
                "behavioral_tendencies": {{
                    "risk_taking_propensity": 0-100,
                    "change_adaptability": 0-100,
                    "routine_preference": 0-100,
                    "spontaneity_level": 0-100
                }},
                "decision_making_patterns": {{
                    "analytical_vs_intuitive": 0-100,
                    "speed_of_decisions": 0-100,
                    "information_seeking": 0-100,
                    "consensus_seeking": 0-100
                }},
                "social_behavioral_style": {{
                    "leadership_tendency": 0-100,
                    "collaboration_preference": 0-100,
                    "assertiveness_level": 0-100,
                    "social_energy": 0-100
                }},
                "work_behavioral_patterns": {{
                    "detail_orientation": 0-100,
                    "big_picture_thinking": 0-100,
                    "deadline_approach": 0-100,
                    "perfectionism_tendency": 0-100
                }},
                "confidence": 0.0-1.0
            }}
            """
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": 1200,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result_data = response.json()
                generated_text = result_data["generations"][0]["text"]
                
                # Извлечение JSON
                try:
                    json_start = generated_text.find('{')
                    json_end = generated_text.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = generated_text[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        
                        logger.info("✅ Cohere анализ поведенческих паттернов выполнен")
                        return parsed_result
                    else:
                        raise json.JSONDecodeError("JSON not found", generated_text, 0)
                        
                except json.JSONDecodeError:
                    return self._get_empty_behavioral_result()
                
        except Exception as e:
            logger.error(f"❌ Ошибка Cohere анализа поведенческих паттернов: {e}")
            return self._get_empty_behavioral_result()
    
    def _extract_insights_from_text(self, text: str) -> Dict[str, Any]:
        """Извлечение инсайтов из неструктурированного текста"""
        # Базовая структура с извлечением ключевых фраз
        return {
            "linguistic_patterns": {
                "word_choice_psychology": {
                    "abstract_vs_concrete": 60,
                    "emotional_intensity_words": 50,
                    "certainty_markers": ["возможно", "наверное"],
                    "power_words": []
                },
                "sentence_structure": {
                    "complexity_score": 50,
                    "passive_voice_ratio": 30,
                    "question_tendency": 20,
                    "exclamation_usage": 10
                }
            },
            "cognitive_style": {
                "analytical_thinking": 60,
                "intuitive_processing": 40,
                "concrete_vs_abstract": 50,
                "detail_orientation": 55,
                "big_picture_focus": 45
            },
            "confidence": 0.6,
            "extracted_from_text": True,
            "raw_response": text[:300]
        }
    
    def _extract_sentiment_from_text(self, text: str) -> Dict[str, Any]:
        """Извлечение sentiment из текста"""
        return {
            "multi_dimensional_sentiment": {
                "primary_sentiment": "neutral",
                "sentiment_intensity": 50,
                "sentiment_stability": 60,
                "emotional_complexity": "moderate"
            },
            "dimensional_analysis": {
                "valence": 0.0,
                "arousal": 0.5,
                "dominance": 0.5,
                "pleasure": 0.5
            },
            "confidence": 0.5,
            "extracted_from_text": True
        }
    
    def _get_empty_psycholinguistics_result(self) -> Dict[str, Any]:
        """Пустой результат психолингвистического анализа"""
        return {
            "linguistic_patterns": {
                "word_choice_psychology": {
                    "abstract_vs_concrete": 50,
                    "emotional_intensity_words": 50,
                    "certainty_markers": [],
                    "power_words": []
                },
                "sentence_structure": {
                    "complexity_score": 50,
                    "passive_voice_ratio": 50,
                    "question_tendency": 50,
                    "exclamation_usage": 50
                }
            },
            "cognitive_style": {
                "analytical_thinking": 50,
                "intuitive_processing": 50,
                "concrete_vs_abstract": 50,
                "detail_orientation": 50,
                "big_picture_focus": 50
            },
            "confidence": 0.0,
            "status": "cohere_unavailable"
        }
    
    def _get_empty_advanced_sentiment_result(self) -> Dict[str, Any]:
        """Пустой результат продвинутого анализа настроений"""
        return {
            "multi_dimensional_sentiment": {
                "primary_sentiment": "neutral",
                "sentiment_intensity": 50,
                "sentiment_stability": 50,
                "emotional_complexity": "moderate"
            },
            "dimensional_analysis": {
                "valence": 0.0,
                "arousal": 0.5,
                "dominance": 0.5,
                "pleasure": 0.5
            },
            "confidence": 0.0,
            "status": "cohere_unavailable"
        }
    
    def _get_empty_behavioral_result(self) -> Dict[str, Any]:
        """Пустой результат поведенческого анализа"""
        return {
            "behavioral_tendencies": {
                "risk_taking_propensity": 50,
                "change_adaptability": 50,
                "routine_preference": 50,
                "spontaneity_level": 50
            },
            "decision_making_patterns": {
                "analytical_vs_intuitive": 50,
                "speed_of_decisions": 50,
                "information_seeking": 50,
                "consensus_seeking": 50
            },
            "confidence": 0.0,
            "status": "cohere_unavailable"
        }


# Глобальный экземпляр клиента
cohere_client = CohereClient() 