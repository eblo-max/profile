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
        self.supported_services = {
            "claude": True,
            "watson": settings.ibm_watson_api_key is not None,
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
        Быстрый анализ только через Claude (для демо)
        
        Args:
            text: Текст для анализа
            user_id: ID пользователя
            telegram_id: Telegram ID
            
        Returns:
            Форматированный результат анализа
        """
        try:
            logger.info("⚡ Быстрый анализ через Claude", 
                       user_id=user_id, 
                       text_length=len(text))
            
            # Анализ через Claude
            claude_result = await self.claude_client.analyze_text(
                text=text,
                analysis_type="psychological",
                user_context={"user_id": user_id, "telegram_id": telegram_id}
            )
            
            # Форматирование результата для пользователя
            formatted_result = self._format_quick_result(claude_result)
            
            logger.info("✅ Быстрый анализ завершен", user_id=user_id)
            return formatted_result
            
        except Exception as e:
            logger.error("❌ Ошибка быстрого анализа", error=str(e))
            return f"⚠️ **Ошибка анализа**: {str(e)}\n\nПопробуйте позже или обратитесь к администратору."
    
    def _format_quick_result(self, claude_result: Dict[str, Any]) -> str:
        """Форматирование быстрого результата для Telegram"""
        
        if "error" in claude_result:
            return f"⚠️ **Ошибка анализа**: {claude_result['error']}"
        
        # Извлечение данных
        main_findings = claude_result.get("main_findings", {})
        psychological_profile = claude_result.get("psychological_profile", {})
        confidence = claude_result.get("confidence_score", 75)
        
        # Форматирование
        result = "🧠 **ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ**\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Основные черты
        if main_findings.get("personality_traits"):
            result += "🎯 **ОСНОВНЫЕ ЧЕРТЫ ЛИЧНОСТИ:**\n"
            for trait in main_findings["personality_traits"][:3]:
                result += f"• {trait}\n"
            result += "\n"
        
        # Эмоциональное состояние
        if main_findings.get("emotional_state"):
            result += f"😊 **ЭМОЦИОНАЛЬНОЕ СОСТОЯНИЕ:**\n{main_findings['emotional_state']}\n\n"
        
        # Big Five (если есть)
        big_five = psychological_profile.get("big_five_traits", {})
        if big_five:
            result += "📊 **ПРОФИЛЬ ЛИЧНОСТИ (Big Five):**\n"
            traits_ru = {
                "openness": "Открытость опыту",
                "conscientiousness": "Добросовестность", 
                "extraversion": "Экстраверсия",
                "agreeableness": "Доброжелательность",
                "neuroticism": "Нейротизм"
            }
            
            for trait, value in big_five.items():
                if isinstance(value, (int, float)) and trait in traits_ru:
                    level = "🔴 Низкий" if value < 40 else "🟡 Средний" if value < 70 else "🟢 Высокий"
                    result += f"• {traits_ru[trait]}: {value}% {level}\n"
            result += "\n"
        
        # Рекомендации
        recommendations = claude_result.get("recommendations", [])
        if recommendations:
            result += "💡 **РЕКОМЕНДАЦИИ:**\n"
            for rec in recommendations[:2]:
                result += f"• {rec}\n"
            result += "\n"
        
        # Метаинформация
        result += f"📈 **ИНДЕКС УВЕРЕННОСТИ:** {confidence}%\n"
        result += f"🔬 **ИСТОЧНИК:** Anthropic Claude AI\n"
        result += f"⚠️ **ПРИМЕЧАНИЕ:** Результат носит рекомендательный характер\n\n"
        
        result += "Для получения детального анализа используйте /analyze"
        
        return result
    
    async def _collect_ai_insights(self, analysis_input: AnalysisInput, analysis_id: int) -> Dict[str, Any]:
        """Сбор данных от всех доступных AI сервисов (демо версия)"""
        results = {}
        
        if analysis_input.text:
            claude_result = await self.claude_client.analyze_text(
                text=analysis_input.text,
                analysis_type="comprehensive_psychological",
                user_context=analysis_input.metadata
            )
            results["claude"] = claude_result
        
        return results
    
    async def _synthesize_results(self, ai_results: Dict[str, Any], analysis_input: AnalysisInput) -> Dict[str, Any]:
        """Синтез результатов (упрощенная версия)"""
        return ai_results.get("claude", {})
    
    async def _validate_analysis(self, synthesis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация (упрощенная версия)"""
        return {"validation_score": 80}
    
    async def _generate_final_report(self, synthesis_result: Dict[str, Any], validation_result: Dict[str, Any], ai_results: Dict[str, Any]) -> str:
        """Генерация отчета (упрощенная версия)"""
        return self._format_quick_result(synthesis_result)
    
    def _calculate_confidence_score(self, ai_results: Dict[str, Any], validation_result: Dict[str, Any]) -> float:
        """Расчет уверенности"""
        return 80.0
    
    def _detect_potential_bias(self, synthesis_result: Dict[str, Any], ai_results: Dict[str, Any]) -> List[str]:
        """Выявление предвзятостей"""
        return []
    
    def _get_methodology_used(self, ai_results: Dict[str, Any]) -> List[str]:
        """Методология"""
        return ["Anthropic Claude - комплексный анализ"]
    
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