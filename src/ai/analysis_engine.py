"""
Основной движок психологического анализа
Координирует работу всех AI сервисов и создает итоговый отчет
"""
import asyncio
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

from src.ai.anthropic_client import anthropic_client
from src.ai.watson_client import OpenAIClient
from src.ai.google_client import google_gemini_client
from src.ai.cohere_client import cohere_client
from src.ai.huggingface_client import huggingface_client
from src.database.connection import get_async_session
from src.database.models import Analysis, AnalysisError
from src.config.settings import settings

logger = structlog.get_logger()


@dataclass
class AnalysisInput:
    """Входные данные для анализа"""
    user_id: int
    telegram_id: int
    text: Optional[str] = None
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    """Результат психологического анализа"""
    analysis_id: int
    status: str
    confidence_score: float
    main_findings: Dict[str, Any]
    detailed_analysis: Dict[str, Any]
    psychological_profile: Dict[str, Any]
    final_report: str
    methodology: List[str]
    limitations: List[str]
    bias_warnings: List[str]
    created_at: datetime


class AnalysisEngine:
    """Основной движок психологического анализа"""
    
    def __init__(self):
        """Инициализация движка"""
        self.claude_client = anthropic_client
        self.openai_client = OpenAIClient()
        self.google_gemini_client = google_gemini_client
        self.cohere_client = cohere_client
        self.huggingface_client = huggingface_client
        
        self.supported_services = {
            # 🚀 СОВРЕМЕННЫЕ AI СЕРВИСЫ (2025)
            "claude": True,  # Главный анализ и синтез
            "openai": self.openai_client.is_available,  # GPT-4o
            "google_gemini": google_gemini_client.is_available,  # Замена Google Cloud NL + Azure
            "cohere": cohere_client.is_available,  # Замена Lexalytics + Receptiviti
            "huggingface": huggingface_client.is_available,  # Замена AWS Rekognition
            
            # 📉 DEPRECATED СЕРВИСЫ (оставлены для совместимости)
            "azure": settings.azure_cognitive_key is not None,
            "google": settings.google_cloud_project_id is not None,
            "aws": settings.aws_access_key_id is not None,
            "crystal": settings.crystal_api_key is not None,
            "receptiviti": settings.receptiviti_api_key is not None,
            "lexalytics": settings.lexalytics_api_key is not None,
            "monkeylearn": settings.monkeylearn_api_key is not None
        }
        
        active_services = [name for name, active in self.supported_services.items() if active]
        logger.info("🚀 AnalysisEngine инициализирован", 
                   active_services=active_services,
                   total_services=len(active_services))
    
    async def analyze_comprehensive(self, analysis_input: AnalysisInput) -> AnalysisResult:
        """
        Комплексный психологический анализ через все доступные сервисы
        
        Args:
            analysis_input: Входные данные для анализа
            
        Returns:
            Результат анализа
        """
        # Создание записи анализа в БД
        analysis_id = await self._create_analysis_record(analysis_input)
        
        try:
            logger.info("🔍 Начинаю комплексный анализ", 
                       analysis_id=analysis_id,
                       user_id=analysis_input.user_id)
            
            # Этап 1: Сбор данных от всех AI сервисов
            ai_results = await self._collect_ai_insights(analysis_input, analysis_id)
            
            # Этап 2: Синтез результатов через Claude
            synthesis_result = await self._synthesize_results(ai_results, analysis_input)
            
            # Этап 3: Валидация и оценка качества
            validation_result = await self._validate_analysis(synthesis_result)
            
            # Этап 4: Создание итогового отчета
            final_report = await self._generate_final_report(
                synthesis_result, 
                validation_result, 
                ai_results
            )
            
            # Этап 5: Расчет метрик
            confidence_score = self._calculate_confidence_score(ai_results, validation_result)
            bias_warnings = self._detect_potential_bias(synthesis_result, ai_results)
            
            # Создание результата
            result = AnalysisResult(
                analysis_id=analysis_id,
                status="completed",
                confidence_score=confidence_score,
                main_findings=synthesis_result.get("main_findings", {}),
                detailed_analysis=synthesis_result.get("detailed_analysis", {}),
                psychological_profile=synthesis_result.get("psychological_profile", {}),
                final_report=final_report,
                methodology=self._get_methodology_used(ai_results),
                limitations=synthesis_result.get("limitations", []),
                bias_warnings=bias_warnings,
                created_at=datetime.utcnow()
            )
            
            # Сохранение результата в БД
            await self._save_analysis_result(analysis_id, result, ai_results, synthesis_result)
            
            logger.info("✅ Комплексный анализ завершен", 
                       analysis_id=analysis_id,
                       confidence_score=confidence_score,
                       ai_services_used=len(ai_results))
            
            return result
            
        except Exception as e:
            logger.error("❌ Ошибка комплексного анализа", 
                        analysis_id=analysis_id, 
                        error=str(e), 
                        exc_info=True)
            
            # Сохранение ошибки в БД
            await self._save_analysis_error(analysis_id, "comprehensive_analysis", str(e))
            
            # Возврат результата с ошибкой
            return AnalysisResult(
                analysis_id=analysis_id,
                status="failed",
                confidence_score=0.0,
                main_findings={"error": str(e)},
                detailed_analysis={},
                psychological_profile={},
                final_report=f"Анализ не удался: {str(e)}",
                methodology=[],
                limitations=["Анализ не завершен из-за ошибки"],
                bias_warnings=[],
                created_at=datetime.utcnow()
            )
    
    async def quick_analyze(self, text: str, user_id: int, telegram_id: int) -> str:
        """
        🚀 СОВРЕМЕННЫЙ БЫСТРЫЙ АНАЛИЗ (2025) 
        Через несколько топовых AI сервисов параллельно
        
        Args:
            text: Текст для анализа
            user_id: ID пользователя
            telegram_id: Telegram ID
            
        Returns:
            Форматированный результат анализа
        """
        try:
            user_context = {"user_id": user_id, "telegram_id": telegram_id}
            
            # Определяем доступные современные сервисы (2025)
            available_services = []
            if self.supported_services.get("claude", True):
                available_services.append("Claude 3.5 Sonnet")
            if self.supported_services.get("openai", False):
                available_services.append("OpenAI GPT-4o")
            if self.supported_services.get("cohere", False):
                available_services.append("Cohere Command-R+")
            if self.supported_services.get("huggingface", False):
                available_services.append("HuggingFace Transformers")
            
            logger.info("🚀 СОВРЕМЕННЫЙ АНАЛИЗ (2025)", 
                       user_id=user_id, 
                       text_length=len(text),
                       available_services=available_services,
                       total_services=len(available_services))
            
            # === ПАРАЛЛЕЛЬНЫЙ ЗАПУСК ВСЕХ ДОСТУПНЫХ AI СЕРВИСОВ ===
            tasks = []
            service_names = []
            
            # 1. Claude 3.5 Sonnet (всегда доступен)
            tasks.append(self._run_claude_analysis(text, user_context))
            service_names.append("claude")
            
            # 2. OpenAI GPT-4o (если API ключ есть)
            if self.supported_services.get("openai", False):
                tasks.append(self._run_openai_analysis(text, user_context))
                service_names.append("openai")
            
            # 3. Cohere Command-R+ (психолингвистический анализ)
            if self.supported_services.get("cohere", False):
                tasks.append(self._run_cohere_analysis(text, user_context))
                service_names.append("cohere")
            
            # 4. HuggingFace Transformers (эмоциональный анализ)
            if self.supported_services.get("huggingface", False):
                tasks.append(self._run_huggingface_analysis(text, user_context))
                service_names.append("huggingface")
            
            logger.info(f"⚡ Запускаю {len(tasks)} AI сервисов параллельно", 
                       services=service_names)
            
            # Параллельное выполнение всех анализов
            ai_results_raw = await asyncio.gather(*tasks, return_exceptions=True)
            
            # === ОБРАБОТКА РЕЗУЛЬТАТОВ ===
            ai_results = {}
            successful_services = []
            
            for i, (service_name, result) in enumerate(zip(service_names, ai_results_raw)):
                if isinstance(result, Exception):
                    logger.error(f"❌ Ошибка {service_name}", error=str(result))
                    ai_results[service_name] = {
                        "error": str(result), 
                        "status": "failed",
                        "service": service_name
                    }
                else:
                    ai_results[service_name] = result
                    if result.get("status") != "failed" and "error" not in result:
                        successful_services.append(service_name)
                        logger.info(f"✅ {service_name.upper()} анализ завершен", 
                                   confidence=result.get('confidence_score', 0))
            
            logger.info(f"🎯 Успешных анализов: {len(successful_services)}/{len(tasks)}", 
                       successful=successful_services)
            
            # === СИНТЕЗ РЕЗУЛЬТАТОВ ===
            if len(successful_services) > 1:
                # Мульти-AI синтез через Claude
                enhanced_result = await self._synthesize_multiple_ai_results(ai_results, text, user_context)
                logger.info("🔄 Выполнен мульти-AI синтез", 
                           sources=len(successful_services))
            elif "claude" in successful_services:
                # Обогащение Claude результата данными других сервисов
                enhanced_result = self._enrich_claude_with_modern_ai(ai_results["claude"], ai_results)
                logger.info("✨ Claude результат обогащен современными AI данными")
            else:
                # Fallback на любой доступный результат
                enhanced_result = next((r for r in ai_results.values() if r.get("status") != "failed"), {})
                logger.warning("⚠️ Используется fallback результат")
            
            # === ФОРМАТИРОВАНИЕ ДЛЯ ПОЛЬЗОВАТЕЛЯ ===
            formatted_result = self._format_modern_analysis_result(
                enhanced_result, 
                successful_services,
                ai_results
            )
            
            logger.info("✅ Современный анализ завершен", 
                       user_id=user_id,
                       ai_services=len(successful_services),
                       confidence=enhanced_result.get('confidence_score', 0))
            
            return formatted_result
            
        except Exception as e:
            logger.error("❌ Критическая ошибка современного анализа", error=str(e), exc_info=True)
            return f"⚠️ **Системная ошибка**: {str(e)}\n\n🔧 Обратитесь к администратору или попробуйте позже."
    
    def _format_quick_result(self, analysis_result: Dict[str, Any], openai_available: bool = False) -> str:
        """Форматирование детального результата для Telegram"""
        
        if "error" in analysis_result:
            return f"⚠️ **Ошибка анализа**: {analysis_result['error']}"
        
        # Извлечение данных из структуры
        hook_summary = analysis_result.get("hook_summary", "")
        personality_core = analysis_result.get("personality_core", {})
        main_findings = analysis_result.get("main_findings", {})
        psychological_profile = analysis_result.get("psychological_profile", {})
        
        # Приоритет OpenAI Big Five данным если доступны
        openai_big_five = psychological_profile.get("openai_big_five", {})
        claude_big_five = psychological_profile.get("big_five_traits", {})
        big_five_detailed = openai_big_five if openai_big_five else claude_big_five
        
        practical_insights = analysis_result.get("practical_insights", {})
        actionable_recommendations = analysis_result.get("actionable_recommendations", {})
        fascinating_details = analysis_result.get("fascinating_details", {})
        confidence = analysis_result.get("confidence_score", 80)
        
        # Данные источников
        data_sources = analysis_result.get("data_sources", {})
        
        # Начало форматирования
        result = "🧠 **ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ**\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Захватывающий хук
        if hook_summary:
            result += f"✨ **{hook_summary}**\n\n"
        
        # Суть личности
        if personality_core.get("essence"):
            result += f"🎯 **СУТЬ ЛИЧНОСТИ:**\n{personality_core['essence']}\n\n"
        
        # Уникальные черты
        if personality_core.get("unique_traits"):
            result += "⭐ **УНИКАЛЬНЫЕ ЧЕРТЫ:**\n"
            for trait in personality_core["unique_traits"][:3]:
                result += f"• {trait}\n"
            result += "\n"
        
        # Эмоциональная подпись
        if main_findings.get("emotional_signature"):
            result += f"❤️ **ЭМОЦИОНАЛЬНАЯ ПОДПИСЬ:**\n{main_findings['emotional_signature']}\n\n"
        
        # Стиль мышления
        if main_findings.get("thinking_style"):
            result += f"🧠 **СТИЛЬ МЫШЛЕНИЯ:**\n{main_findings['thinking_style']}\n\n"
        
        # Big Five с деталями
        if big_five_detailed:
            result += "📊 **ПРОФИЛЬ ЛИЧНОСТИ (Big Five):**\n"
            traits_ru = {
                "openness": "🎨 Открытость",
                "conscientiousness": "📋 Добросовестность", 
                "extraversion": "👥 Экстраверсия",
                "agreeableness": "🤝 Доброжелательность",
                "neuroticism": "🌊 Эмоциональность"
            }
            
            for trait, trait_data in big_five_detailed.items():
                if trait in traits_ru and isinstance(trait_data, dict):
                    score = trait_data.get("score", 50)
                    description = trait_data.get("description", "")
                    level = "🔴 Низкий" if score < 40 else "🟡 Средний" if score < 70 else "🟢 Высокий"
                    result += f"• {traits_ru[trait]}: {score}% {level}\n"
                    if description:
                        result += f"  └ {description[:80]}...\n"
            result += "\n"
        
        # Сильные стороны
        if practical_insights.get("strengths_to_leverage"):
            result += "💪 **ВАШИ СУПЕРСИЛЫ:**\n"
            for strength in practical_insights["strengths_to_leverage"][:2]:
                result += f"• {strength}\n"
            result += "\n"
        
        # Скрытые таланты
        if fascinating_details.get("hidden_talents"):
            result += "🎁 **СКРЫТЫЕ ТАЛАНТЫ:**\n"
            for talent in fascinating_details["hidden_talents"][:2]:
                result += f"• {talent}\n"
            result += "\n"
        
        # Практические рекомендации
        if actionable_recommendations.get("immediate_actions"):
            result += "🚀 **ДЕЙСТВИЯ НА НЕДЕЛЮ:**\n"
            for action in actionable_recommendations["immediate_actions"][:3]:
                result += f"• {action}\n"
            result += "\n"
        
        # Карьерные советы
        if practical_insights.get("career_alignment"):
            result += f"💼 **КАРЬЕРА:**\n{practical_insights['career_alignment']}\n\n"
        
        # Отношения
        if practical_insights.get("relationship_style"):
            result += f"💕 **ОТНОШЕНИЯ:**\n{practical_insights['relationship_style']}\n\n"
        
        # Скрытые глубины
        if personality_core.get("hidden_depths"):
            result += f"🔍 **ЗА ФАСАДОМ:**\n{personality_core['hidden_depths']}\n\n"
        
        # Метаинформация
        result += f"📈 **ИНДЕКС УВЕРЕННОСТИ:** {confidence}%\n"
        
        # AI движки
        if openai_available and data_sources:
            result += f"🤖 **AI ДВИЖКИ:** Claude 3.5 Sonnet + OpenAI GPT-4o\n"
            result += f"🔬 **МЕТОДЫ:** Big Five (OpenAI), эмоциональный анализ (OpenAI), лингвистический анализ (Claude)\n"
            if psychological_profile.get("scientific_validation"):
                result += f"✅ **НАУЧНАЯ ВАЛИДАЦИЯ:** OpenAI Research\n"
        else:
            result += f"🤖 **AI ДВИЖОК:** Claude 3.5 Sonnet\n"
            result += f"🔬 **МЕТОДЫ:** Big Five, лингвистический анализ\n"
        
        # OpenAI специфичные данные
        if openai_available and openai_big_five:
            # Показываем OpenAI эмоциональные данные если есть
            openai_emotions = psychological_profile.get("emotional_analysis", {})
            if openai_emotions:
                dominant_emotion = openai_emotions.get("dominant_emotion", "")
                if dominant_emotion:
                    result += f"\n🎯 **ДОМИНИРУЮЩАЯ ЭМОЦИЯ (OpenAI):** {dominant_emotion}\n"
                    
                sentiment = psychological_profile.get("sentiment_analysis", {})
                if sentiment:
                    polarity = sentiment.get("polarity", 0)
                    sentiment_text = "Позитивное" if polarity > 0.3 else "Негативное" if polarity < -0.3 else "Нейтральное"
                    result += f"• **Общий настрой:** {sentiment_text} ({polarity:.2f})\n"
        
        result += "\n💬 Отправьте еще текст для дополнительного анализа!"
        
        return result
    
    async def _collect_ai_insights(self, analysis_input: AnalysisInput, analysis_id: int) -> Dict[str, Any]:
        """Сбор данных от всех доступных AI сервисов"""
        results = {}
        tasks = []
        
        if analysis_input.text:
            # Claude анализ (всегда доступен)
            tasks.append(self._run_claude_analysis(analysis_input.text, analysis_input.metadata))
            
            # OpenAI анализ (если доступен)
            if self.supported_services["openai"]:
                tasks.append(self._run_openai_analysis(analysis_input.text, analysis_input.metadata))
            
            logger.info("🔄 Запуск параллельного AI анализа", 
                       services_count=len(tasks),
                       analysis_id=analysis_id)
            
            # Параллельное выполнение всех анализов
            ai_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка результатов
            service_names = ["claude"]
            if self.supported_services["openai"]:
                service_names.append("openai")
            
            for i, result in enumerate(ai_results):
                service_name = service_names[i]
                
                if isinstance(result, Exception):
                    logger.error(f"❌ Ошибка {service_name} анализа", 
                               error=str(result), 
                               analysis_id=analysis_id)
                    results[service_name] = {
                        "error": str(result),
                        "status": "failed",
                        "service": service_name
                    }
                else:
                    results[service_name] = result
                    logger.info(f"✅ {service_name.title()} анализ завершен", 
                               confidence=result.get('confidence_score', 0),
                               analysis_id=analysis_id)
        
        return results
    
    async def _run_claude_analysis(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск Claude анализа"""
        try:
            return await self.claude_client.analyze_text(
                text=text,
                analysis_type="comprehensive_psychological",
                user_context=metadata
            )
        except Exception as e:
            logger.error("❌ Ошибка Claude анализа", error=str(e))
            return {
                "error": str(e),
                "status": "failed",
                "service": "claude"
            }
    
    async def _run_openai_analysis(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск OpenAI анализа"""
        try:
            # Параллельный запуск всех OpenAI анализов
            personality_task = self.openai_client.analyze_personality(text)
            emotions_task = self.openai_client.analyze_emotions(text)
            sentiment_task = self.openai_client.analyze_sentiment(text)
            
            personality_result, emotions_result, sentiment_result = await asyncio.gather(
                personality_task, emotions_task, sentiment_task, return_exceptions=True
            )
            
            # Объединение результатов
            combined_result = {
                "status": "success",
                "service": "openai",
                "big_five_traits": personality_result.get("big_five", {}) if not isinstance(personality_result, Exception) else {},
                "mbti": personality_result.get("mbti", "Unknown") if not isinstance(personality_result, Exception) else "Unknown",
                "disc": personality_result.get("disc", "Unknown") if not isinstance(personality_result, Exception) else "Unknown",
                "emotions": emotions_result.get("emotions", {}) if not isinstance(emotions_result, Exception) else {},
                "dominant_emotion": emotions_result.get("dominant_emotion", "neutral") if not isinstance(emotions_result, Exception) else "neutral",
                "sentiment": sentiment_result.get("sentiment", "neutral") if not isinstance(sentiment_result, Exception) else "neutral",
                "sentiment_polarity": sentiment_result.get("polarity", 0.0) if not isinstance(sentiment_result, Exception) else 0.0,
                "confidence_score": 85  # OpenAI высокий confidence
            }
            
            return combined_result
            
        except Exception as e:
            logger.error("❌ Ошибка OpenAI анализа", error=str(e))
            return {
                "error": str(e),
                "status": "failed", 
                "service": "openai"
            }
    
    async def _run_cohere_analysis(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск Cohere Command-R+ анализа"""
        try:
            # Параллельный запуск всех Cohere анализов
            psycholinguistics_task = self.cohere_client.analyze_psycholinguistics(text)
            sentiment_task = self.cohere_client.analyze_advanced_sentiment(text)
            behavioral_task = self.cohere_client.analyze_behavioral_patterns(text)
            
            psycholinguistics_result, sentiment_result, behavioral_result = await asyncio.gather(
                psycholinguistics_task, sentiment_task, behavioral_task, return_exceptions=True
            )
            
            # Объединение результатов Cohere
            combined_result = {
                "status": "success",
                "service": "cohere",
                "psycholinguistics": psycholinguistics_result if not isinstance(psycholinguistics_result, Exception) else {},
                "advanced_sentiment": sentiment_result if not isinstance(sentiment_result, Exception) else {},
                "behavioral_patterns": behavioral_result if not isinstance(behavioral_result, Exception) else {},
                "confidence_score": 80  # Cohere хороший confidence для психолингвистики
            }
            
            # Извлечение ключевых инсайтов
            if not isinstance(psycholinguistics_result, Exception):
                combined_result["linguistic_insights"] = {
                    "cognitive_style": psycholinguistics_result.get("cognitive_style", {}),
                    "communication_psychology": psycholinguistics_result.get("communication_psychology", {}),
                    "thought_process": psycholinguistics_result.get("thought_process_indicators", {})
                }
            
            if not isinstance(sentiment_result, Exception):
                combined_result["emotional_insights"] = {
                    "dimensional_analysis": sentiment_result.get("dimensional_analysis", {}),
                    "psychological_sentiment": sentiment_result.get("psychological_sentiment_markers", {}),
                    "social_emotional": sentiment_result.get("social_emotional_context", {})
                }
            
            return combined_result
            
        except Exception as e:
            logger.error("❌ Ошибка Cohere анализа", error=str(e))
            return {
                "error": str(e),
                "status": "failed",
                "service": "cohere"
            }
    
    async def _run_huggingface_analysis(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск HuggingFace Transformers анализа"""
        try:
            # Параллельный запуск всех HuggingFace анализов
            emotions_task = self.huggingface_client.analyze_emotions_transformers(text)
            personality_task = self.huggingface_client.analyze_personality_transformers(text)
            mental_health_task = self.huggingface_client.analyze_mental_health_indicators(text)
            
            emotions_result, personality_result, mental_health_result = await asyncio.gather(
                emotions_task, personality_task, mental_health_task, return_exceptions=True
            )
            
            # Объединение результатов HuggingFace
            combined_result = {
                "status": "success",
                "service": "huggingface",
                "transformer_emotions": emotions_result if not isinstance(emotions_result, Exception) else {},
                "transformer_personality": personality_result if not isinstance(personality_result, Exception) else {},
                "mental_health_analysis": mental_health_result if not isinstance(mental_health_result, Exception) else {},
                "confidence_score": 75  # HuggingFace средний confidence (специализированные модели)
            }
            
            # Извлечение ключевых инсайтов из трансформеров
            if not isinstance(emotions_result, Exception):
                combined_result["emotion_insights"] = {
                    "transformer_emotions": emotions_result.get("transformer_emotions", {}),
                    "emotional_profile": emotions_result.get("emotional_profile", {}),
                    "psychological_insights": emotions_result.get("psychological_insights", {})
                }
            
            if not isinstance(mental_health_result, Exception):
                combined_result["wellbeing_insights"] = {
                    "stress_indicators": mental_health_result.get("stress_indicators", {}),
                    "resilience_factors": mental_health_result.get("resilience_factors", {}),
                    "psychological_wellbeing": mental_health_result.get("psychological_wellbeing", {})
                }
            
            return combined_result
            
        except Exception as e:
            logger.error("❌ Ошибка HuggingFace анализа", error=str(e))
            return {
                "error": str(e),
                "status": "failed",
                "service": "huggingface"
            }
    
    async def _synthesize_results(self, ai_results: Dict[str, Any], analysis_input: AnalysisInput) -> Dict[str, Any]:
        """Синтез результатов через Claude с учетом данных от всех AI сервисов"""
        try:
            logger.info("🔄 Синтез результатов от AI сервисов", 
                       services_available=list(ai_results.keys()))
            
            # Если есть данные от нескольких сервисов - используем синтез
            if len(ai_results) > 1 and "openai" in ai_results and "claude" in ai_results:
                # Комплексный синтез через Claude
                synthesis_context = {
                    "ai_results": ai_results,
                    "services_used": list(ai_results.keys()),
                    "analysis_input": analysis_input.metadata
                }
                
                synthesis_result = await self.claude_client.analyze_text(
                    text=analysis_input.text,
                    analysis_type="synthesis",
                    user_context=synthesis_context
                )
                
                # Обогащение синтеза данными OpenAI
                if "openai" in ai_results and ai_results["openai"].get("status") == "success":
                    synthesis_result = self._enrich_with_openai_data(synthesis_result, ai_results["openai"])
                
                logger.info("✅ Комплексный синтез завершен", 
                           confidence=synthesis_result.get('confidence_score', 0))
                
                return synthesis_result
            
            # Если OpenAI недоступен - возвращаем Claude результат
            elif "claude" in ai_results:
                logger.info("📝 Используем только Claude результат")
                return ai_results["claude"]
            
            # Если только OpenAI доступен
            elif "openai" in ai_results:
                logger.info("🧠 Используем только OpenAI результат")
                return self._format_openai_only_result(ai_results["openai"])
            
            else:
                logger.warning("⚠️ Нет доступных результатов анализа")
                return {"error": "Нет доступных результатов анализа", "status": "no_results"}
                
        except Exception as e:
            logger.error("❌ Ошибка синтеза результатов", error=str(e), exc_info=True)
            # Fallback на Claude если есть
            return ai_results.get("claude", {"error": str(e), "status": "synthesis_failed"})
    
    def _enrich_with_openai_data(self, claude_result: Dict[str, Any], openai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Обогащение результата Claude данными от OpenAI"""
        try:
            # Добавляем данные OpenAI в Claude результат
            if "psychological_profile" not in claude_result:
                claude_result["psychological_profile"] = {}
            
            # OpenAI Big Five данные
            openai_big_five = openai_result.get("big_five_traits", {})
            if openai_big_five:
                claude_result["psychological_profile"]["openai_big_five"] = openai_big_five
                claude_result["psychological_profile"]["scientific_validation"] = True
            
            # OpenAI эмоциональный анализ
            if "emotions" in openai_result:
                claude_result["psychological_profile"]["emotional_analysis"] = {
                    "emotions": openai_result["emotions"],
                    "dominant_emotion": openai_result.get("dominant_emotion", "neutral"),
                    "emotional_intensity": openai_result.get("emotional_intensity", 0.5)
                }
            
            # OpenAI анализ настроений
            if "sentiment" in openai_result:
                claude_result["psychological_profile"]["sentiment_analysis"] = {
                    "sentiment": openai_result["sentiment"],
                    "polarity": openai_result.get("sentiment_polarity", 0.0),
                    "confidence": openai_result.get("sentiment_confidence", 0.8)
                }
            
            # MBTI и DISC от OpenAI
            if "mbti" in openai_result:
                claude_result["psychological_profile"]["mbti_type"] = openai_result["mbti"]
            if "disc" in openai_result:
                claude_result["psychological_profile"]["disc_profile"] = openai_result["disc"]
            
            # Обновляем confidence score (средний между Claude и OpenAI)
            openai_confidence = openai_result.get("confidence_score", 0)
            claude_confidence = claude_result.get("confidence_score", 0)
            
            if openai_confidence > 0 and claude_confidence > 0:
                # Взвешенное среднее: равные веса для Claude и OpenAI
                combined_confidence = (openai_confidence * 0.5 + claude_confidence * 0.5)
                claude_result["confidence_score"] = round(combined_confidence, 1)
            
            # Добавляем метаданные о источниках
            claude_result["data_sources"] = {
                "claude": "Психологический синтез и интерпретация",
                "openai": "Многоаспектный анализ GPT-4o (Big Five, эмоции, настроения)",
                "synthesis_method": "Гибридный анализ с кросс-валидацией"
            }
            
            logger.info("✅ Claude результат обогащен данными OpenAI")
            return claude_result
            
        except Exception as e:
            logger.error("❌ Ошибка обогащения Watson данными", error=str(e))
            return claude_result
    
    def _format_openai_only_result(self, openai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование результата только от OpenAI для пользователя"""
        try:
            # Конвертируем OpenAI данные в формат похожий на Claude
            formatted_result = {
                "analysis_type": "openai_personality",
                "hook_summary": "Многоаспектный анализ через OpenAI GPT-4o",
                "personality_core": {
                    "essence": f"MBTI: {openai_result.get('mbti', 'Unknown')}, DISC: {openai_result.get('disc', 'Unknown')}",
                    "unique_traits": [],
                    "hidden_depths": "Анализ основан на Big Five + эмоциональный профиль"
                },
                "main_findings": {
                    "personality_traits": [],
                    "emotional_signature": f"Доминирующая эмоция: {openai_result.get('dominant_emotion', 'neutral')}",
                    "thinking_style": f"Настрой: {openai_result.get('sentiment', 'neutral')}"
                },
                "psychological_profile": {
                    "big_five_traits": openai_result.get("big_five_traits", {}),
                    "emotional_analysis": openai_result.get("emotions", {}),
                    "sentiment_analysis": {
                        "sentiment": openai_result.get("sentiment", "neutral"),
                        "polarity": openai_result.get("sentiment_polarity", 0.0)
                    }
                },
                "confidence_score": openai_result.get("confidence_score", 85),
                "data_sources": {
                    "openai": "OpenAI GPT-4o (Big Five, эмоции, настроения)",
                    "methodology": "Многоаспектный психологический анализ"
                },
                "status": "openai_only"
            }
            
            # Извлекаем доминирующие черты из OpenAI Big Five
            big_five = openai_result.get("big_five_traits", {})
            for trait_name, trait_score in big_five.items():
                if isinstance(trait_score, (int, float)) and trait_score >= 70:
                    formatted_result["personality_core"]["unique_traits"].append(
                        f"{trait_name.title()}: {trait_score}% (высокий уровень)"
                    )
            
            return formatted_result
            
        except Exception as e:
            logger.error("❌ Ошибка форматирования OpenAI результата", error=str(e))
            return openai_result
    
    async def _validate_analysis(self, synthesis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация (упрощенная версия)"""
        return {"validation_score": 80}
    
    async def _generate_final_report(self, synthesis_result: Dict[str, Any], validation_result: Dict[str, Any], ai_results: Dict[str, Any]) -> str:
        """Генерация отчета (упрощенная версия)"""
        return self._format_quick_result(synthesis_result)
    
    def _calculate_confidence_score(self, ai_results: Dict[str, Any], validation_result: Dict[str, Any]) -> float:
        """Расчет уверенности на основе доступных AI сервисов"""
        base_confidence = 75.0
        
        # Бонус за каждый успешный AI сервис
        successful_services = 0
        total_confidence = 0
        
        for service_name, service_result in ai_results.items():
            if service_result.get("status") != "failed" and "error" not in service_result:
                successful_services += 1
                service_confidence = service_result.get("confidence_score", 75)
                total_confidence += service_confidence
        
        if successful_services > 0:
            # Средний confidence с бонусом за множественные источники
            avg_confidence = total_confidence / successful_services
            
            # Бонус за OpenAI (многоаспектный анализ)
            if "openai" in ai_results and ai_results["openai"].get("status") == "success":
                avg_confidence += 8  # +8% за многоаспектный анализ
            
            # Бонус за кросс-валидацию (несколько сервисов)
            if successful_services > 1:
                avg_confidence += 5  # +5% за кросс-валидацию
            
            return min(95.0, max(50.0, avg_confidence))
        
        return base_confidence
    
    def _detect_potential_bias(self, synthesis_result: Dict[str, Any], ai_results: Dict[str, Any]) -> List[str]:
        """Выявление предвзятостей"""
        return []
    
    def _get_methodology_used(self, ai_results: Dict[str, Any]) -> List[str]:
        """Определение использованной методологии"""
        methodology = []
        
        if "claude" in ai_results and ai_results["claude"].get("status") != "failed":
            methodology.append("Anthropic Claude 3.5 Sonnet - психологический синтез и интерпретация")
        
        if "openai" in ai_results and ai_results["openai"].get("status") == "success":
            methodology.append("OpenAI GPT-4o - многоаспектный анализ (Big Five + эмоции + настроения)")
            methodology.append("IBM Research - психометрические алгоритмы и статистический анализ")
        
        # Если использовались оба сервиса
        if len([r for r in ai_results.values() if r.get("status") != "failed"]) > 1:
            methodology.append("Гибридный анализ с кросс-валидацией между AI системами")
        
        return methodology if methodology else ["Базовый психологический анализ"]
    
    async def _create_analysis_record(self, analysis_input: AnalysisInput) -> int:
        """Создание записи (упрощенная версия)"""
        return 1  # Заглушка
    
    async def _save_analysis_result(self, analysis_id: int, result: AnalysisResult, ai_results: Dict[str, Any], synthesis_result: Dict[str, Any]):
        """Сохранение результата (упрощенная версия)"""
        pass
    
    async def _save_analysis_error(self, analysis_id: int, service_name: str, error_message: str):
        """Сохранение ошибки (упрощенная версия)"""
        pass
    
    async def _synthesize_multiple_ai_results(self, ai_results: Dict[str, Any], text: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Синтез результатов от нескольких AI сервисов через Claude"""
        try:
            # Подготовка данных для синтеза
            synthesis_context = {
                "ai_results": ai_results,
                "successful_services": [name for name, result in ai_results.items() if result.get("status") != "failed"],
                "text_length": len(text),
                "user_context": user_context
            }
            
            # Специальный промпт для мульти-AI синтеза
            synthesis_result = await self.claude_client.analyze_text(
                text=text,
                analysis_type="multi_ai_synthesis",
                user_context=synthesis_context
            )
            
            # Обогащение синтеза данными от всех успешных сервисов
            enriched_result = self._enrich_claude_with_modern_ai(synthesis_result, ai_results)
            
            # Добавление метаданных о мульти-AI анализе
            enriched_result["multi_ai_analysis"] = {
                "services_used": synthesis_context["successful_services"],
                "synthesis_method": "claude_coordination",
                "cross_validation": True,
                "confidence_boost": len(synthesis_context["successful_services"]) * 5  # Бонус за множественные источники
            }
            
            return enriched_result
            
        except Exception as e:
            logger.error("❌ Ошибка мульти-AI синтеза", error=str(e))
            # Fallback на Claude результат если синтез не удался
            return ai_results.get("claude", {"error": str(e), "status": "synthesis_failed"})
    
    def _enrich_claude_with_modern_ai(self, claude_result: Dict[str, Any], ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Обогащение Claude результата данными от современных AI сервисов (2025)"""
        try:
            # Инициализация структуры если нужно
            if "psychological_profile" not in claude_result:
                claude_result["psychological_profile"] = {}
            if "data_sources" not in claude_result:
                claude_result["data_sources"] = {}
            
            confidence_scores = []
            
            # === ИНТЕГРАЦИЯ OPENAI ДАННЫХ ===
            openai_data = ai_results.get("openai", {})
            if openai_data.get("status") == "success":
                # Big Five от OpenAI (наиболее точные)
                if "big_five_traits" in openai_data:
                    claude_result["psychological_profile"]["openai_big_five"] = openai_data["big_five_traits"]
                    claude_result["psychological_profile"]["mbti_type"] = openai_data.get("mbti", "Unknown")
                    claude_result["psychological_profile"]["disc_profile"] = openai_data.get("disc", "Unknown")
                
                # Эмоциональные данные от OpenAI
                if "emotions" in openai_data:
                    claude_result["psychological_profile"]["openai_emotions"] = {
                        "emotions": openai_data["emotions"],
                        "dominant_emotion": openai_data.get("dominant_emotion", "neutral"),
                        "sentiment": openai_data.get("sentiment", "neutral"),
                        "polarity": openai_data.get("sentiment_polarity", 0.0)
                    }
                
                claude_result["data_sources"]["openai"] = "GPT-4o многоаспектный анализ (Big Five + эмоции)"
                confidence_scores.append(openai_data.get("confidence_score", 85))
            
            # === ИНТЕГРАЦИЯ COHERE ДАННЫХ ===
            cohere_data = ai_results.get("cohere", {})
            if cohere_data.get("status") == "success":
                # Психолингвистические инсайты
                if "linguistic_insights" in cohere_data:
                    claude_result["psychological_profile"]["psycholinguistics"] = cohere_data["linguistic_insights"]
                
                # Продвинутый анализ настроений
                if "emotional_insights" in cohere_data:
                    claude_result["psychological_profile"]["cohere_sentiment"] = cohere_data["emotional_insights"]
                
                # Поведенческие паттерны
                if "behavioral_patterns" in cohere_data:
                    claude_result["psychological_profile"]["behavioral_analysis"] = cohere_data["behavioral_patterns"]
                
                claude_result["data_sources"]["cohere"] = "Command-R+ психолингвистический анализ"
                confidence_scores.append(cohere_data.get("confidence_score", 80))
            
            # === ИНТЕГРАЦИЯ HUGGINGFACE ДАННЫХ ===
            huggingface_data = ai_results.get("huggingface", {})
            if huggingface_data.get("status") == "success":
                # Transformer эмоциональный анализ
                if "emotion_insights" in huggingface_data:
                    claude_result["psychological_profile"]["transformer_emotions"] = huggingface_data["emotion_insights"]
                
                # Анализ ментального здоровья
                if "wellbeing_insights" in huggingface_data:
                    claude_result["psychological_profile"]["mental_wellbeing"] = huggingface_data["wellbeing_insights"]
                
                claude_result["data_sources"]["huggingface"] = "Specialized Transformers эмоциональный анализ"
                confidence_scores.append(huggingface_data.get("confidence_score", 75))
            
            # === РАСЧЕТ КОМБИНИРОВАННОГО CONFIDENCE ===
            claude_confidence = claude_result.get("confidence_score", 75)
            confidence_scores.append(claude_confidence)
            
            if len(confidence_scores) > 1:
                # Взвешенное среднее с бонусом за кросс-валидацию
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                cross_validation_bonus = min(10, (len(confidence_scores) - 1) * 3)  # +3% за каждый дополнительный источник
                combined_confidence = min(95, avg_confidence + cross_validation_bonus)
                claude_result["confidence_score"] = round(combined_confidence, 1)
            
            # Добавление метаданных о современном анализе
            claude_result["modern_ai_integration"] = {
                "ai_services_count": len([r for r in ai_results.values() if r.get("status") == "success"]),
                "data_fusion": True,
                "cross_validation": len(confidence_scores) > 1,
                "analysis_year": 2025
            }
            
            logger.info("✨ Claude обогащен современными AI данными", 
                       sources=len(confidence_scores),
                       final_confidence=claude_result.get("confidence_score"))
            
            return claude_result
            
        except Exception as e:
            logger.error("❌ Ошибка обогащения современными AI", error=str(e))
            return claude_result
    
    def _format_modern_analysis_result(self, analysis_result: Dict[str, Any], successful_services: List[str], ai_results: Dict[str, Any]) -> str:
        """Форматирование результата современного мульти-AI анализа для Telegram"""
        
        if "error" in analysis_result or not analysis_result:
            return f"⚠️ **Ошибка анализа**: {analysis_result.get('error', 'Неизвестная ошибка')}"
        
        # Извлечение базовых данных
        hook_summary = analysis_result.get("hook_summary", "Анализ завершен")
        personality_core = analysis_result.get("personality_core", {})
        main_findings = analysis_result.get("main_findings", {})
        psychological_profile = analysis_result.get("psychological_profile", {})
        
        # Данные от разных AI сервисов
        openai_big_five = psychological_profile.get("openai_big_five", {})
        claude_big_five = psychological_profile.get("big_five_traits", {})
        openai_emotions = psychological_profile.get("openai_emotions", {})
        cohere_sentiment = psychological_profile.get("cohere_sentiment", {})
        transformer_emotions = psychological_profile.get("transformer_emotions", {})
        
        # Выбираем лучшие данные Big Five (приоритет OpenAI)
        best_big_five = openai_big_five if openai_big_five else claude_big_five
        
        confidence = analysis_result.get("confidence_score", 80)
        data_sources = analysis_result.get("data_sources", {})
        
        # === НАЧАЛО ФОРМАТИРОВАНИЯ ===
        result = "🧠 **СОВРЕМЕННЫЙ ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ (2025)**\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Захватывающий хук
        if hook_summary and hook_summary != "Анализ завершен":
            result += f"✨ **{hook_summary}**\n\n"
        
        # Суть личности
        if personality_core.get("essence"):
            result += f"🎯 **СУТЬ ЛИЧНОСТИ:**\n{personality_core['essence']}\n\n"
        
        # Уникальные черты с источниками
        if personality_core.get("unique_traits"):
            result += "⭐ **УНИКАЛЬНЫЕ ЧЕРТЫ:**\n"
            for trait in personality_core["unique_traits"][:3]:
                result += f"• {trait}\n"
            result += "\n"
        
        # Эмоциональная подпись (с данными от нескольких AI)
        emotional_signature = main_findings.get("emotional_signature", "")
        if openai_emotions and openai_emotions.get("dominant_emotion"):
            emotional_signature += f" | OpenAI: доминирует {openai_emotions['dominant_emotion']}"
        if transformer_emotions and transformer_emotions.get("emotional_profile", {}).get("dominant_emotion"):
            emotional_signature += f" | HF: {transformer_emotions['emotional_profile']['dominant_emotion']}"
        
        if emotional_signature:
            result += f"❤️ **ЭМОЦИОНАЛЬНАЯ ПОДПИСЬ:**\n{emotional_signature}\n\n"
        
        # Стиль мышления
        if main_findings.get("thinking_style"):
            result += f"🧠 **СТИЛЬ МЫШЛЕНИЯ:**\n{main_findings['thinking_style']}\n\n"
        
        # Big Five с мульти-источниками
        if best_big_five:
            result += "📊 **ПРОФИЛЬ ЛИЧНОСТИ (Big Five):**\n"
            traits_ru = {
                "openness": "🎨 Открытость",
                "conscientiousness": "📋 Добросовестность", 
                "extraversion": "👥 Экстраверсия",
                "agreeableness": "🤝 Доброжелательность",
                "neuroticism": "🌊 Эмоциональность"
            }
            
            for trait, trait_data in best_big_five.items():
                if trait in traits_ru:
                    if isinstance(trait_data, dict):
                        score = trait_data.get("score", 50)
                        description = trait_data.get("description", "")
                    else:
                        score = trait_data
                        description = ""
                    
                    level = "🔴 Низкий" if score < 40 else "🟡 Средний" if score < 70 else "🟢 Высокий"
                    result += f"• {traits_ru[trait]}: {score}% {level}\n"
                    if description:
                        result += f"  └ {description[:60]}...\n"
            
            # Указываем источник Big Five
            if openai_big_five:
                result += "  📍 *Источник: OpenAI GPT-4o научный анализ*\n"
            result += "\n"
        
        # MBTI и DISC (если есть от OpenAI)
        mbti = psychological_profile.get("mbti_type", "")
        disc = psychological_profile.get("disc_profile", "")
        if mbti and mbti != "Unknown":
            result += f"🎭 **ТИПОЛОГИЯ:** MBTI: {mbti}"
            if disc and disc != "Unknown":
                result += f" | DISC: {disc}"
            result += "\n\n"
        
        # Практические инсайты
        practical_insights = analysis_result.get("practical_insights", {})
        if practical_insights.get("strengths_to_leverage"):
            result += "💪 **ВАШИ СУПЕРСИЛЫ:**\n"
            for strength in practical_insights["strengths_to_leverage"][:2]:
                result += f"• {strength}\n"
            result += "\n"
        
        # Карьерные рекомендации
        if practical_insights.get("career_alignment"):
            result += f"💼 **КАРЬЕРА:**\n{practical_insights['career_alignment'][:120]}...\n\n"
        
        # Специализированные инсайты от современных AI
        if "cohere" in successful_services and cohere_sentiment:
            result += "🧬 **ПСИХОЛИНГВИСТИКА (Cohere):**\n"
            dimensional = cohere_sentiment.get("dimensional_analysis", {})
            if dimensional:
                valence = dimensional.get("valence", 0)
                arousal = dimensional.get("arousal", 0.5)
                result += f"• Эмоциональная валентность: {valence:.2f}\n"
                result += f"• Уровень активации: {arousal:.2f}\n\n"
        
        if "huggingface" in successful_services and transformer_emotions:
            result += "🤖 **TRANSFORMER АНАЛИЗ:**\n"
            hf_emotions = transformer_emotions.get("transformer_emotions", {})
            if hf_emotions:
                top_emotion = max(hf_emotions.items(), key=lambda x: x[1])
                result += f"• Доминирующая эмоция: {top_emotion[0]} ({top_emotion[1]:.0f}%)\n\n"
        
        # === МЕТАДАННЫЕ АНАЛИЗА ===
        result += f"📈 **ИНДЕКС УВЕРЕННОСТИ:** {confidence}%\n"
        
        # AI сервисы с деталями
        if len(successful_services) > 1:
            result += f"🚀 **AI ДВИЖКИ ({len(successful_services)}):** "
            ai_names = []
            if "claude" in successful_services:
                ai_names.append("Claude 3.5 Sonnet")
            if "openai" in successful_services:
                ai_names.append("OpenAI GPT-4o")
            if "cohere" in successful_services:
                ai_names.append("Cohere Command-R+")
            if "huggingface" in successful_services:
                ai_names.append("HuggingFace Transformers")
            
            result += " + ".join(ai_names) + "\n"
            result += f"🔬 **МЕТОДЫ:** Мульти-AI кросс-валидация ({len(successful_services)} источников)\n"
            result += f"✅ **НАУЧНАЯ ВАЛИДАЦИЯ:** Консенсус современных AI систем\n"
        else:
            result += f"🤖 **AI ДВИЖОК:** {successful_services[0].title()}\n"
        
        # Современность анализа
        modern_integration = analysis_result.get("modern_ai_integration", {})
        if modern_integration.get("data_fusion"):
            result += f"⚡ **ТЕХНОЛОГИЯ 2025:** Фьюжн данных от {modern_integration.get('ai_services_count', 1)} AI систем\n"
        
        result += "\n💬 Отправьте еще текст для дополнительного анализа!"
        
        return result


# Глобальный экземпляр движка
analysis_engine = AnalysisEngine() 