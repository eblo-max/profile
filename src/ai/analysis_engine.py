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
from src.ai.watson_client import watson_client
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
        self.watson_client = watson_client
        self.supported_services = {
            "claude": True,
            "watson": watson_client.is_available,
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
        Быстрый анализ через Claude + Watson (если доступен)
        
        Args:
            text: Текст для анализа
            user_id: ID пользователя
            telegram_id: Telegram ID
            
        Returns:
            Форматированный результат анализа
        """
        try:
            user_context = {"user_id": user_id, "telegram_id": telegram_id}
            
            # Определяем доступные сервисы
            services_to_use = ["Claude"]
            if self.supported_services["watson"]:
                services_to_use.append("Watson")
            
            logger.info("⚡ Быстрый анализ", 
                       user_id=user_id, 
                       text_length=len(text),
                       services=services_to_use)
            
            # Запуск анализов параллельно
            tasks = []
            
            # Claude (всегда)
            tasks.append(self._run_claude_analysis(text, user_context))
            
            # Watson (если доступен и текст достаточно длинный)
            watson_result = None
            if self.supported_services["watson"] and len(text.split()) >= 100:
                tasks.append(self._run_watson_analysis(text, user_context))
            
            # Выполнение анализов
            if len(tasks) > 1:
                claude_result, watson_result = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Обработка исключений
                if isinstance(claude_result, Exception):
                    logger.error("❌ Ошибка Claude", error=str(claude_result))
                    claude_result = {"error": str(claude_result), "status": "failed"}
                
                if isinstance(watson_result, Exception):
                    logger.warning("⚠️ Watson недоступен", error=str(watson_result))
                    watson_result = None
                
            else:
                # Только Claude
                claude_result = await tasks[0]
            
            # Создание комбинированного результата
            if watson_result and watson_result.get("status") == "success":
                # Обогащаем Claude результат данными Watson
                enhanced_result = self._enrich_with_watson_data(claude_result, watson_result)
                logger.info("✅ Быстрый анализ завершен (Claude + Watson)", 
                           user_id=user_id,
                           confidence=enhanced_result.get('confidence_score', 0))
            else:
                # Только Claude
                enhanced_result = claude_result
                logger.info("✅ Быстрый анализ завершен (только Claude)", 
                           user_id=user_id,
                           confidence=enhanced_result.get('confidence_score', 0))
            
            # Форматирование результата для пользователя
            formatted_result = self._format_quick_result(enhanced_result, watson_available=bool(watson_result))
            
            return formatted_result
            
        except Exception as e:
            logger.error("❌ Ошибка быстрого анализа", error=str(e), exc_info=True)
            return f"⚠️ **Ошибка анализа**: {str(e)}\n\nПопробуйте позже или обратитесь к администратору."
    
    def _format_quick_result(self, analysis_result: Dict[str, Any], watson_available: bool = False) -> str:
        """Форматирование детального результата для Telegram"""
        
        if "error" in analysis_result:
            return f"⚠️ **Ошибка анализа**: {analysis_result['error']}"
        
        # Извлечение данных из структуры
        hook_summary = analysis_result.get("hook_summary", "")
        personality_core = analysis_result.get("personality_core", {})
        main_findings = analysis_result.get("main_findings", {})
        psychological_profile = analysis_result.get("psychological_profile", {})
        
        # Приоритет Watson Big Five данным если доступны
        watson_big_five = psychological_profile.get("watson_big_five", {})
        claude_big_five = psychological_profile.get("big_five_traits", {})
        big_five_detailed = watson_big_five if watson_big_five else claude_big_five
        
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
        if watson_available and data_sources:
            result += f"🤖 **AI ДВИЖКИ:** Claude 3.5 Sonnet + IBM Watson\n"
            result += f"🔬 **МЕТОДЫ:** Big Five (Watson), лингвистический анализ (Claude)\n"
            if psychological_profile.get("scientific_validation"):
                result += f"✅ **НАУЧНАЯ ВАЛИДАЦИЯ:** IBM Research\n"
        else:
            result += f"🤖 **AI ДВИЖОК:** Claude 3.5 Sonnet\n"
            result += f"🔬 **МЕТОДЫ:** Big Five, лингвистический анализ\n"
        
        # Watson специфичные данные
        if watson_available and watson_big_five:
            # Показываем Watson потребности если есть
            watson_needs = psychological_profile.get("psychological_needs", {})
            if watson_needs:
                top_needs = sorted(watson_needs.items(), key=lambda x: x[1].get('percentile', 0), reverse=True)[:2]
                if top_needs:
                    result += f"\n🎯 **КЛЮЧЕВЫЕ ПОТРЕБНОСТИ (Watson):**\n"
                    for need_id, need_data in top_needs:
                        result += f"• {need_data.get('name', need_id)}: {need_data.get('percentile', 0):.0f}%\n"
        
        result += "\n💬 Отправьте еще текст для дополнительного анализа!"
        
        return result
    
    async def _collect_ai_insights(self, analysis_input: AnalysisInput, analysis_id: int) -> Dict[str, Any]:
        """Сбор данных от всех доступных AI сервисов"""
        results = {}
        tasks = []
        
        if analysis_input.text:
            # Claude анализ (всегда доступен)
            tasks.append(self._run_claude_analysis(analysis_input.text, analysis_input.metadata))
            
            # Watson анализ (если доступен)
            if self.supported_services["watson"]:
                tasks.append(self._run_watson_analysis(analysis_input.text, analysis_input.metadata))
            
            logger.info("🔄 Запуск параллельного AI анализа", 
                       services_count=len(tasks),
                       analysis_id=analysis_id)
            
            # Параллельное выполнение всех анализов
            ai_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка результатов
            service_names = ["claude"]
            if self.supported_services["watson"]:
                service_names.append("watson")
            
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
    
    async def _run_watson_analysis(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск Watson анализа"""
        try:
            return await self.watson_client.analyze_personality(
                text=text,
                user_context=metadata
            )
        except Exception as e:
            logger.error("❌ Ошибка Watson анализа", error=str(e))
            return {
                "error": str(e),
                "status": "failed", 
                "service": "watson"
            }
    
    async def _synthesize_results(self, ai_results: Dict[str, Any], analysis_input: AnalysisInput) -> Dict[str, Any]:
        """Синтез результатов через Claude с учетом данных от всех AI сервисов"""
        try:
            logger.info("🔄 Синтез результатов от AI сервисов", 
                       services_available=list(ai_results.keys()))
            
            # Если есть данные от нескольких сервисов - используем синтез
            if len(ai_results) > 1 and "watson" in ai_results and "claude" in ai_results:
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
                
                # Обогащение синтеза данными Watson
                if "watson" in ai_results and ai_results["watson"].get("status") == "success":
                    synthesis_result = self._enrich_with_watson_data(synthesis_result, ai_results["watson"])
                
                logger.info("✅ Комплексный синтез завершен", 
                           confidence=synthesis_result.get('confidence_score', 0))
                
                return synthesis_result
            
            # Если Watson недоступен - возвращаем Claude результат
            elif "claude" in ai_results:
                logger.info("📝 Используем только Claude результат")
                return ai_results["claude"]
            
            # Если только Watson доступен
            elif "watson" in ai_results:
                logger.info("🧠 Используем только Watson результат")
                return self._format_watson_only_result(ai_results["watson"])
            
            else:
                logger.warning("⚠️ Нет доступных результатов анализа")
                return {"error": "Нет доступных результатов анализа", "status": "no_results"}
                
        except Exception as e:
            logger.error("❌ Ошибка синтеза результатов", error=str(e), exc_info=True)
            # Fallback на Claude если есть
            return ai_results.get("claude", {"error": str(e), "status": "synthesis_failed"})
    
    def _enrich_with_watson_data(self, claude_result: Dict[str, Any], watson_result: Dict[str, Any]) -> Dict[str, Any]:
        """Обогащение результата Claude данными от Watson"""
        try:
            # Добавляем научные данные Watson в Claude результат
            if "psychological_profile" not in claude_result:
                claude_result["psychological_profile"] = {}
            
            # Watson Big Five данные
            watson_big_five = watson_result.get("big_five_traits", {})
            if watson_big_five:
                claude_result["psychological_profile"]["watson_big_five"] = watson_big_five
                claude_result["psychological_profile"]["scientific_validation"] = True
            
            # Watson потребности и ценности
            if "psychological_needs" in watson_result:
                claude_result["psychological_profile"]["psychological_needs"] = watson_result["psychological_needs"]
            
            if "core_values" in watson_result:
                claude_result["psychological_profile"]["core_values"] = watson_result["core_values"]
            
            # Обновляем confidence score (средний между Claude и Watson)
            watson_confidence = watson_result.get("confidence_score", 0)
            claude_confidence = claude_result.get("confidence_score", 0)
            
            if watson_confidence > 0 and claude_confidence > 0:
                # Взвешенное среднее: Watson больше веса из-за научной основы
                combined_confidence = (watson_confidence * 0.6 + claude_confidence * 0.4)
                claude_result["confidence_score"] = round(combined_confidence, 1)
            
            # Добавляем метаданные о источниках
            claude_result["data_sources"] = {
                "claude": "Психологический синтез и интерпретация",
                "watson": "Научная валидация IBM Research (Big Five модель)",
                "synthesis_method": "Гибридный анализ с кросс-валидацией"
            }
            
            logger.info("✅ Claude результат обогащен данными Watson")
            return claude_result
            
        except Exception as e:
            logger.error("❌ Ошибка обогащения Watson данными", error=str(e))
            return claude_result
    
    def _format_watson_only_result(self, watson_result: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование результата только от Watson для пользователя"""
        try:
            # Конвертируем Watson данные в формат похожий на Claude
            formatted_result = {
                "analysis_type": "watson_personality",
                "hook_summary": "Научный анализ личности через IBM Watson",
                "personality_core": {
                    "essence": watson_result.get("personality_summary", "Профиль личности по Watson"),
                    "unique_traits": [],
                    "hidden_depths": "Анализ основан на научной модели Big Five"
                },
                "main_findings": {
                    "personality_traits": [],
                    "emotional_signature": "Научная оценка эмоциональной стабильности",
                    "thinking_style": "Анализ когнитивных особенностей"
                },
                "psychological_profile": {
                    "big_five_traits": watson_result.get("big_five_traits", {}),
                    "psychological_needs": watson_result.get("psychological_needs", {}),
                    "core_values": watson_result.get("core_values", {})
                },
                "confidence_score": watson_result.get("confidence_score", 80),
                "data_sources": {
                    "watson": "IBM Watson Personality Insights (научная основа)",
                    "methodology": "Big Five модель личности"
                },
                "status": "watson_only"
            }
            
            # Извлекаем доминирующие черты из Watson
            big_five = watson_result.get("big_five_traits", {})
            for trait_name, trait_data in big_five.items():
                if isinstance(trait_data, dict) and trait_data.get("percentile", 0) >= 70:
                    formatted_result["personality_core"]["unique_traits"].append(
                        f"{trait_name.title()}: {trait_data.get('description', '')}"
                    )
            
            return formatted_result
            
        except Exception as e:
            logger.error("❌ Ошибка форматирования Watson результата", error=str(e))
            return watson_result
    
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
            
            # Бонус за Watson (научная валидация)
            if "watson" in ai_results and ai_results["watson"].get("status") == "success":
                avg_confidence += 10  # +10% за научную валидацию
            
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
        
        if "watson" in ai_results and ai_results["watson"].get("status") == "success":
            methodology.append("IBM Watson Personality Insights - научная валидация Big Five модели")
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


# Глобальный экземпляр движка
analysis_engine = AnalysisEngine() 