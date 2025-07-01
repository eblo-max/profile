"""
Профессиональный клиент для IBM Watson Personality Insights
"""
import asyncio
import structlog
from typing import Dict, Any, Optional, List
import json
from ibm_watson import PersonalityInsightsV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

from src.config.settings import settings

logger = structlog.get_logger()


class WatsonClient:
    """Асинхронный клиент для IBM Watson Personality Insights"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.client = None
        self.is_available = False
        
        if settings.ibm_watson_api_key and settings.ibm_watson_url:
            try:
                authenticator = IAMAuthenticator(settings.ibm_watson_api_key)
                self.client = PersonalityInsightsV3(
                    version='2017-10-13',
                    authenticator=authenticator
                )
                self.client.set_service_url(settings.ibm_watson_url)
                self.is_available = True
                logger.info("🧠 Watson клиент инициализирован", 
                           url=settings.ibm_watson_url[:50] + "...")
            except Exception as e:
                logger.error("❌ Ошибка инициализации Watson", error=str(e))
                self.is_available = False
        else:
            logger.warning("⚠️ Watson API ключи не настроены")
    
    async def analyze_personality(self, 
                                 text: str, 
                                 user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Анализ личности через Watson Personality Insights
        
        Args:
            text: Текст для анализа (минимум 100 слов)
            user_context: Дополнительный контекст
            
        Returns:
            Результат анализа Watson с Big Five и другими метриками
        """
        if not self.is_available:
            return {
                "error": "Watson API недоступен",
                "status": "unavailable",
                "fallback": True
            }
        
        try:
            logger.info("🔍 Запуск Watson анализа", 
                       text_length=len(text),
                       user_id=user_context.get('user_id') if user_context else None)
            
            # Проверка минимальной длины текста
            word_count = len(text.split())
            if word_count < 100:
                logger.warning("⚠️ Текст слишком короткий для Watson", word_count=word_count)
                return {
                    "error": f"Нужно минимум 100 слов для Watson анализа (получено: {word_count})",
                    "status": "insufficient_text",
                    "word_count": word_count,
                    "fallback": True
                }
            
            # Выполнение анализа в отдельном потоке (Watson SDK синхронный)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._sync_analyze, 
                text
            )
            
            # Обработка результата
            result = self._process_watson_response(response, text, user_context)
            
            logger.info("✅ Watson анализ завершен", 
                       confidence=result.get('confidence_score', 0),
                       traits_count=len(result.get('big_five_traits', {})))
            
            return result
            
        except ApiException as e:
            logger.error("❌ Watson API ошибка", 
                        error_code=e.code, 
                        error_message=e.message,
                        exc_info=True)
            return {
                "error": f"Watson API ошибка: {e.message}",
                "error_code": e.code,
                "status": "api_error",
                "fallback": True
            }
        except Exception as e:
            logger.error("❌ Неожиданная ошибка Watson", error=str(e), exc_info=True)
            return {
                "error": f"Ошибка Watson анализа: {str(e)}",
                "status": "unexpected_error",
                "fallback": True
            }
    
    def _sync_analyze(self, text: str) -> Dict[str, Any]:
        """Синхронный вызов Watson API"""
        profile = self.client.profile(
            content=text,
            content_type='text/plain',
            consumption_preferences=True,
            raw_scores=True
        ).get_result()
        return profile
    
    def _process_watson_response(self, 
                                response: Dict[str, Any], 
                                original_text: str,
                                user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Обработка ответа Watson в унифицированный формат"""
        
        try:
            # Извлечение Big Five черт
            big_five_traits = {}
            personality = response.get('personality', [])
            
            trait_mapping = {
                'big5_openness': 'openness',
                'big5_conscientiousness': 'conscientiousness', 
                'big5_extraversion': 'extraversion',
                'big5_agreeableness': 'agreeableness',
                'big5_neuroticism': 'neuroticism'
            }
            
            for trait in personality:
                trait_id = trait.get('trait_id')
                if trait_id in trait_mapping:
                    trait_name = trait_mapping[trait_id]
                    percentile = trait.get('percentile', 0) * 100  # Конвертация в проценты
                    raw_score = trait.get('raw_score', 0)
                    
                    big_five_traits[trait_name] = {
                        "percentile": round(percentile, 1),
                        "raw_score": round(raw_score, 3),
                        "description": self._get_trait_description(trait_name, percentile),
                        "level": self._get_trait_level(percentile),
                        "facets": self._extract_facets(trait)
                    }
            
            # Извлечение потребностей (Needs)
            needs = {}
            for need in response.get('needs', []):
                need_id = need.get('trait_id', '').replace('need_', '')
                percentile = need.get('percentile', 0) * 100
                needs[need_id] = {
                    "percentile": round(percentile, 1),
                    "name": need.get('name', need_id),
                    "description": self._get_need_description(need_id, percentile)
                }
            
            # Извлечение ценностей (Values)
            values = {}
            for value in response.get('values', []):
                value_id = value.get('trait_id', '').replace('value_', '')
                percentile = value.get('percentile', 0) * 100
                values[value_id] = {
                    "percentile": round(percentile, 1),
                    "name": value.get('name', value_id),
                    "description": self._get_value_description(value_id, percentile)
                }
            
            # Извлечение предпочтений потребления
            consumption_preferences = {}
            for category in response.get('consumption_preferences', []):
                category_name = category.get('consumption_preference_category_id', '').replace('consumption_preferences_', '')
                preferences = []
                
                for pref in category.get('consumption_preferences', []):
                    preferences.append({
                        "preference_id": pref.get('consumption_preference_id', ''),
                        "name": pref.get('name', ''),
                        "score": pref.get('score', 0)
                    })
                
                consumption_preferences[category_name] = {
                    "category_name": category.get('name', category_name),
                    "preferences": preferences
                }
            
            # Метаданные
            word_count = response.get('word_count', len(original_text.split()))
            warnings = response.get('warnings', [])
            
            # Расчет общего confidence score
            confidence_score = self._calculate_confidence_score(word_count, warnings, big_five_traits)
            
            # Создание основных инсайтов
            main_insights = self._generate_main_insights(big_five_traits, needs, values)
            
            # Унифицированный результат
            result = {
                "service": "watson",
                "status": "success",
                "confidence_score": confidence_score,
                "word_count": word_count,
                "warnings": [w.get('message', str(w)) for w in warnings],
                
                # Основные результаты
                "big_five_traits": big_five_traits,
                "psychological_needs": needs,
                "core_values": values,
                "consumption_preferences": consumption_preferences,
                
                # Анализ и инсайты
                "main_insights": main_insights,
                "personality_summary": self._create_personality_summary(big_five_traits),
                "behavioral_predictions": self._generate_behavioral_predictions(big_five_traits, needs, values),
                
                # Метаданные
                "analysis_metadata": {
                    "watson_version": "2017-10-13",
                    "text_length": len(original_text),
                    "analysis_timestamp": asyncio.get_event_loop().time(),
                    "user_context": user_context
                },
                
                # Сырые данные для отладки
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error("❌ Ошибка обработки Watson ответа", error=str(e), exc_info=True)
            return {
                "error": f"Ошибка обработки Watson данных: {str(e)}",
                "status": "processing_error",
                "fallback": True,
                "raw_response": response
            }
    
    def _extract_facets(self, trait: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение фасетов черт личности"""
        facets = {}
        for child in trait.get('children', []):
            facet_id = child.get('trait_id', '')
            percentile = child.get('percentile', 0) * 100
            facets[facet_id] = {
                "percentile": round(percentile, 1),
                "name": child.get('name', facet_id),
                "description": f"Уровень: {self._get_trait_level(percentile)}"
            }
        return facets
    
    def _get_trait_description(self, trait_name: str, percentile: float) -> str:
        """Описание черт личности Big Five"""
        descriptions = {
            "openness": {
                "high": "Открыт к новому опыту, креативен, любознателен",
                "medium": "Сбалансированное отношение к новизне и традициям", 
                "low": "Предпочитает знакомое и проверенное, практичен"
            },
            "conscientiousness": {
                "high": "Организован, дисциплинирован, целеустремлен",
                "medium": "Умеренно организован, гибкий в планировании",
                "low": "Спонтанен, адаптивен, менее структурирован"
            },
            "extraversion": {
                "high": "Общительный, энергичный, любит быть в центре внимания",
                "medium": "Сбалансированная социальность, амбиверт",
                "low": "Предпочитает одиночество, рефлексивен, сдержан"
            },
            "agreeableness": {
                "high": "Доброжелательный, отзывчивый, склонен к сотрудничеству",
                "medium": "Сбалансированное отношение к людям",
                "low": "Независимый, прямолинейный, скептически настроенный"
            },
            "neuroticism": {
                "high": "Эмоционально чувствительный, склонен к беспокойству",
                "medium": "Умеренная эмоциональная реактивность",
                "low": "Эмоционально стабильный, спокойный, устойчивый к стрессу"
            }
        }
        
        level = self._get_trait_level(percentile)
        return descriptions.get(trait_name, {}).get(level, f"Уровень {trait_name}: {level}")
    
    def _get_trait_level(self, percentile: float) -> str:
        """Определение уровня черты"""
        if percentile >= 70:
            return "high"
        elif percentile >= 30:
            return "medium"
        else:
            return "low"
    
    def _get_need_description(self, need_id: str, percentile: float) -> str:
        """Описание психологических потребностей"""
        need_descriptions = {
            "challenge": "Потребность в сложных задачах и испытаниях",
            "closeness": "Потребность в близости и интимных отношениях",
            "curiosity": "Потребность в исследовании и познании нового",
            "excitement": "Потребность в острых ощущениях и приключениях",
            "harmony": "Потребность в гармонии и избегании конфликтов",
            "ideal": "Потребность в совершенстве и высоких стандартах",
            "liberty": "Потребность в свободе и независимости",
            "love": "Потребность в любви и принятии",
            "practicality": "Потребность в практичности и эффективности",
            "self_expression": "Потребность в самовыражении и креативности",
            "stability": "Потребность в стабильности и предсказуемости",
            "structure": "Потребность в структуре и организации"
        }
        
        base_desc = need_descriptions.get(need_id, f"Потребность в {need_id}")
        level = "высокая" if percentile >= 70 else "умеренная" if percentile >= 30 else "низкая"
        return f"{base_desc} ({level} важность)"
    
    def _get_value_description(self, value_id: str, percentile: float) -> str:
        """Описание ценностей"""
        value_descriptions = {
            "conservation": "Ценность традиций, безопасности и стабильности",
            "openness_to_change": "Ценность новизны, независимости и разнообразия",
            "hedonism": "Ценность удовольствия и наслаждения жизнью",
            "self_enhancement": "Ценность личных достижений и успеха",
            "self_transcendence": "Ценность помощи другим и социальной справедливости"
        }
        
        base_desc = value_descriptions.get(value_id, f"Ценность {value_id}")
        level = "очень важна" if percentile >= 70 else "умеренно важна" if percentile >= 30 else "менее важна"
        return f"{base_desc} ({level})"
    
    def _calculate_confidence_score(self, 
                                  word_count: int, 
                                  warnings: List[Dict], 
                                  big_five_traits: Dict[str, Any]) -> float:
        """Расчет уверенности в результатах Watson"""
        base_confidence = 85.0
        
        # Штраф за малое количество слов
        if word_count < 600:
            base_confidence -= (600 - word_count) * 0.05
        
        # Штраф за предупреждения
        base_confidence -= len(warnings) * 5
        
        # Бонус за полноту данных
        if len(big_five_traits) == 5:
            base_confidence += 5
        
        return max(50.0, min(95.0, base_confidence))
    
    def _generate_main_insights(self, 
                               big_five_traits: Dict[str, Any],
                               needs: Dict[str, Any], 
                               values: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация основных инсайтов"""
        insights = {
            "dominant_traits": [],
            "key_motivators": [],
            "behavioral_tendencies": [],
            "strengths": [],
            "growth_areas": []
        }
        
        # Доминирующие черты (> 70 перцентиль)
        for trait_name, trait_data in big_five_traits.items():
            percentile = trait_data.get('percentile', 0)
            if percentile >= 70:
                insights["dominant_traits"].append({
                    "trait": trait_name,
                    "percentile": percentile,
                    "description": trait_data.get('description', '')
                })
        
        # Ключевые мотиваторы (топ потребности)
        sorted_needs = sorted(needs.items(), key=lambda x: x[1]['percentile'], reverse=True)
        insights["key_motivators"] = [
            {"need": need_id, "strength": need_data['percentile'], "description": need_data['description']}
            for need_id, need_data in sorted_needs[:3]
        ]
        
        return insights
    
    def _create_personality_summary(self, big_five_traits: Dict[str, Any]) -> str:
        """Создание краткого резюме личности"""
        high_traits = []
        low_traits = []
        
        trait_names_ru = {
            "openness": "открытость",
            "conscientiousness": "добросовестность",
            "extraversion": "экстраверсия", 
            "agreeableness": "доброжелательность",
            "neuroticism": "нейротизм"
        }
        
        for trait_name, trait_data in big_five_traits.items():
            percentile = trait_data.get('percentile', 0)
            trait_ru = trait_names_ru.get(trait_name, trait_name)
            
            if percentile >= 70:
                high_traits.append(trait_ru)
            elif percentile <= 30:
                low_traits.append(trait_ru)
        
        summary = "Профиль личности по Watson: "
        
        if high_traits:
            summary += f"высокие показатели по {', '.join(high_traits)}"
        
        if low_traits:
            if high_traits:
                summary += f", низкие по {', '.join(low_traits)}"
            else:
                summary += f"низкие показатели по {', '.join(low_traits)}"
        
        if not high_traits and not low_traits:
            summary += "сбалансированный профиль с умеренными показателями"
        
        return summary
    
    def _generate_behavioral_predictions(self, 
                                       big_five_traits: Dict[str, Any],
                                       needs: Dict[str, Any],
                                       values: Dict[str, Any]) -> List[str]:
        """Генерация поведенческих предсказаний"""
        predictions = []
        
        # Предсказания на основе Big Five
        for trait_name, trait_data in big_five_traits.items():
            percentile = trait_data.get('percentile', 0)
            level = trait_data.get('level', 'medium')
            
            if trait_name == "conscientiousness" and level == "high":
                predictions.append("Склонен к планированию и соблюдению дедлайнов")
            elif trait_name == "extraversion" and level == "high": 
                predictions.append("Активно ищет социальные взаимодействия")
            elif trait_name == "openness" and level == "high":
                predictions.append("Открыт к экспериментам и новым идеям")
        
        return predictions[:5]  # Топ 5 предсказаний
    
    async def validate_api_connection(self) -> Dict[str, Any]:
        """Проверка подключения к Watson API"""
        if not self.is_available:
            return {"status": "unavailable", "error": "API ключи не настроены"}
        
        try:
            # Тестовый анализ короткого текста
            test_text = "This is a test message for Watson API validation. " * 20  # ~100 слов
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._sync_analyze,
                test_text
            )
            
            return {
                "status": "connected",
                "version": "2017-10-13",
                "word_count": response.get('word_count', 0),
                "traits_detected": len(response.get('personality', []))
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "error_type": type(e).__name__
            }


# Глобальный экземпляр клиента
watson_client = WatsonClient() 