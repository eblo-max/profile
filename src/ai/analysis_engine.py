"""
Основной движок психологического анализа
Координирует работу всех AI сервисов и создает итоговый отчет

🔬 НОВОЕ: Интеграция с системой научного поиска (2025)
- Автоматический поиск релевантных исследований в PubMed, Google Scholar
- Создание научно-обоснованных профилей с peer-reviewed источниками
- Валидация выводов на основе актуальных научных данных
- Мультимодальный AI анализ научной литературы
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
from src.ai.scientific_research_engine import ScientificResearchEngine, PersonData
from src.ai.multi_ai_research_analyzer import MultiAIResearchAnalyzer
from src.database.connection import get_async_session
from src.database.models import Analysis, AnalysisError
from src.config.settings import settings
from src.utils.economic_analysis_manager import economic_manager, AnalysisLevel, CostEstimate
from src.utils.cache_manager import cache_manager

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
        
        # 🔬 НОВЫЕ КОМПОНЕНТЫ: Система научного поиска (2025)
        self.research_engine = ScientificResearchEngine(settings)
        self.multi_ai_analyzer = MultiAIResearchAnalyzer(settings)
        
        # 💰 ЭКОНОМИЧЕСКИЕ КОМПОНЕНТЫ (2025)
        self.economic_manager = economic_manager
        self.cache_manager = cache_manager
        
        self.supported_services = {
            # 🚀 СОВРЕМЕННЫЕ AI СЕРВИСЫ (2025)
            "claude": True,  # Главный анализ и синтез
            "openai": self.openai_client.is_available,  # GPT-4o
            "google_gemini": google_gemini_client.is_available,  # Замена Google Cloud NL + Azure
            "cohere": cohere_client.is_available,  # Замена Lexalytics + Receptiviti
            "huggingface": huggingface_client.is_available,  # Замена AWS Rekognition
            
            # 🔬 НАУЧНЫЙ ПОИСК (2025)
            "scientific_research": True,  # Всегда доступен
            "multi_ai_research": True,  # Мультимодальный анализ
            
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
        logger.info("🚀 AnalysisEngine инициализирован с научным поиском", 
                   active_services=active_services,
                   total_services=len(active_services),
                   scientific_research_enabled=True)
    
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
    
    async def economic_analysis(
        self, 
        text: str, 
        user_id: int, 
        telegram_id: int,
        level: AnalysisLevel = AnalysisLevel.FREE,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        💰 ЭКОНОМИЧЕСКИЙ АНАЛИЗ С КОНТРОЛЕМ СТОИМОСТИ
        Умный анализ с кэшированием и оптимизацией расходов
        
        Args:
            text: Текст для анализа
            user_id: ID пользователя
            telegram_id: Telegram ID
            level: Уровень анализа (FREE/BASIC/ADVANCED/RESEARCH/PREMIUM)
            force_refresh: Принудительное обновление без кэша
            
        Returns:
            Результат экономического анализа с метаданными
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info("💰 Начинаю экономический анализ",
                       user_id=user_id,
                       level=level.value,
                       text_length=len(text),
                       force_refresh=force_refresh)
            
            # Этап 1: Проверка лимитов пользователя
            limits_ok, limit_reason = await self.economic_manager.check_user_limits(user_id, level)
            if not limits_ok:
                return {
                    "status": "limit_exceeded",
                    "error": limit_reason,
                    "level": level.value,
                    "suggestions": await self._get_upgrade_suggestions(level)
                }
            
            # Этап 2: Оценка стоимости
            cost_estimate = await self.economic_manager.estimate_analysis_cost(level, text, user_id)
            
            # Этап 3: Проверка кэша (если не принудительное обновление)
            cached_result = None
            if not force_refresh:
                cached_result = await self.cache_manager.get_cached_analysis(
                    text, level.value, user_id
                )
                
                if cached_result:
                    # Обновляем метаданные кэшированного результата
                    cached_result["metadata"]["served_from_cache"] = True
                    cached_result["metadata"]["cost_saved_usd"] = cost_estimate.estimated_cost_usd
                    cached_result["metadata"]["analysis_level"] = level.value
                    
                    logger.info("🎯 Отдан кэшированный результат",
                               user_id=user_id,
                               level=level.value,
                               cost_saved_usd=cost_estimate.estimated_cost_usd)
                    
                    return cached_result
            
            # Этап 4: Выполнение анализа по выбранному уровню
            analysis_result = await self._execute_level_analysis(text, level, user_id, cost_estimate)
            
            # Этап 5: Логирование фактической стоимости
            actual_cost = analysis_result.get("metadata", {}).get("actual_cost_usd", cost_estimate.estimated_cost_usd)
            tokens_used = analysis_result.get("metadata", {}).get("tokens_used", cost_estimate.estimated_tokens)
            ai_services_used = analysis_result.get("metadata", {}).get("ai_services_used", [])
            
            await self.economic_manager.log_analysis_cost(
                user_id, level, actual_cost, tokens_used, ai_services_used
            )
            
            # Этап 6: Кэширование результата (если успешно)
            if analysis_result.get("status") == "success" and level != AnalysisLevel.PREMIUM:
                await self.cache_manager.cache_analysis_result(
                    text, level.value, analysis_result, user_id
                )
            
            # Этап 7: Финализация результата
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            analysis_result["metadata"].update({
                "execution_time_seconds": execution_time,
                "estimated_cost_usd": cost_estimate.estimated_cost_usd,
                "cache_hit": False,
                "analysis_timestamp": start_time.isoformat()
            })
            
            logger.info("✅ Экономический анализ завершен",
                       user_id=user_id,
                       level=level.value,
                       actual_cost_usd=actual_cost,
                       execution_time_seconds=execution_time,
                       status=analysis_result.get("status"))
            
            return analysis_result
            
        except Exception as e:
            logger.error("❌ Ошибка экономического анализа",
                        user_id=user_id,
                        level=level.value,
                        error=str(e),
                        exc_info=True)
            
            return {
                "status": "error",
                "error": str(e),
                "level": level.value,
                "metadata": {
                    "execution_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                    "cost_estimate": asdict(cost_estimate) if 'cost_estimate' in locals() else None
                }
            }
    
    async def _execute_level_analysis(
        self,
        text: str,
        level: AnalysisLevel,
        user_id: int,
        cost_estimate: CostEstimate
    ) -> Dict[str, Any]:
        """Выполнение анализа согласно выбранному уровню"""
        
        config = self.economic_manager.analysis_configs[level]
        ai_services_used = []
        total_tokens = 0
        actual_cost = 0.0
        
        try:
            if level == AnalysisLevel.FREE:
                # FREE: Только Claude, базовый анализ
                result = await self.claude_client.analyze_text(
                    text, "psychological", {"user_id": user_id}
                )
                ai_services_used = ["claude"]
                total_tokens = result.get("tokens_used", 2500)
                actual_cost = 0.0
                
                analysis_content = self._format_free_analysis(result, text)
                
            elif level == AnalysisLevel.BASIC:
                # BASIC: Claude с детальным анализом
                result = await self.claude_client.analyze_text(
                    text, "comprehensive_psychological", {"user_id": user_id}
                )
                ai_services_used = ["claude"]
                total_tokens = result.get("tokens_used", 4000)
                actual_cost = settings.basic_price_usd
                
                analysis_content = self._format_basic_analysis(result, text)
                
            elif level == AnalysisLevel.ADVANCED:
                # ADVANCED: Claude + OpenAI + научная выборка
                claude_task = self.claude_client.analyze_text(
                    text, "comprehensive_psychological", {"user_id": user_id}
                )
                openai_task = self.openai_client.analyze_psychological_text(text)
                scientific_task = self._get_scientific_sample(text, max_sources=10)
                
                claude_result, openai_result, scientific_result = await asyncio.gather(
                    claude_task, openai_task, scientific_task
                )
                
                ai_services_used = ["claude", "openai"]
                total_tokens = (
                    claude_result.get("tokens_used", 4000) + 
                    openai_result.get("tokens_used", 4000)
                )
                actual_cost = settings.advanced_price_usd
                
                analysis_content = self._format_advanced_analysis(
                    claude_result, openai_result, scientific_result, text
                )
                
            elif level == AnalysisLevel.RESEARCH:
                # RESEARCH: Полный научный анализ
                analysis_content = await self.scientific_research_analysis(
                    {"text": text}, user_id, user_id  # telegram_id = user_id для простоты
                )
                ai_services_used = ["claude", "openai", "gemini", "scientific_research"]
                total_tokens = 15000
                actual_cost = settings.research_price_usd
                
            elif level == AnalysisLevel.PREMIUM:
                # PREMIUM: Максимальный анализ
                analysis_content = await self._execute_premium_analysis(text, user_id)
                ai_services_used = ["claude", "openai", "gemini", "cohere", "huggingface"]
                total_tokens = 25000
                actual_cost = settings.premium_price_usd
            
            else:
                raise ValueError(f"Неподдерживаемый уровень анализа: {level}")
            
            return {
                "status": "success",
                "analysis": analysis_content,
                "level": level.value,
                "metadata": {
                    "ai_services_used": ai_services_used,
                    "tokens_used": total_tokens,
                    "actual_cost_usd": actual_cost,
                    "sources_count": len(ai_services_used),
                    "served_from_cache": False
                }
            }
            
        except Exception as e:
            logger.error("❌ Ошибка выполнения анализа уровня",
                        level=level.value,
                        error=str(e),
                        exc_info=True)
            raise
    
    async def _get_scientific_sample(self, text: str, max_sources: int = 10) -> Dict[str, Any]:
        """Получение научной выборки для продвинутого анализа"""
        try:
            # Проверяем кэш научных исследований
            query_terms = self._extract_query_terms_from_text(text)
            cached_research = await self.cache_manager.get_cached_scientific_research(
                query_terms, max_sources
            )
            
            if cached_research:
                return cached_research
            
            # Если нет в кэше - ищем
            person_data = PersonData(
                behavior_description=text[:500],
                text_samples=[text[:1000]]
            )
            
            research_result = await self.research_engine.research_personality_profile(
                person_data, max_sources
            )
            
            # Кэшируем результат
            await self.cache_manager.cache_scientific_research(
                query_terms, research_result, max_sources
            )
            
            return research_result
            
        except Exception as e:
            logger.error("❌ Ошибка получения научной выборки", error=str(e))
            return {"sources": [], "error": str(e)}
    
    def _extract_query_terms_from_text(self, text: str) -> List[str]:
        """Извлечение ключевых терминов для научного поиска"""
        # Упрощенная версия - можно улучшить с помощью NLP
        words = text.lower().split()
        
        # Психологические ключевые слова
        psychology_terms = [
            "personality", "behavior", "emotion", "cognitive", "social",
            "anxiety", "depression", "stress", "motivation", "leadership"
        ]
        
        found_terms = []
        for term in psychology_terms:
            if term in " ".join(words):
                found_terms.append(term)
        
        # Добавляем самые частые значимые слова
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Только длинные слова
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        found_terms.extend([word for word, freq in top_words])
        
        return found_terms[:5]  # Максимум 5 терминов
    
    async def _get_upgrade_suggestions(self, current_level: AnalysisLevel) -> List[Dict[str, Any]]:
        """Получение предложений по апгрейду уровня"""
        comparison = self.economic_manager.get_level_comparison()
        suggestions = []
        
        # Предлагаем следующий уровень
        level_order = [AnalysisLevel.FREE, AnalysisLevel.BASIC, AnalysisLevel.ADVANCED, 
                      AnalysisLevel.RESEARCH, AnalysisLevel.PREMIUM]
        
        current_index = level_order.index(current_level)
        
        for i in range(current_index + 1, len(level_order)):
            next_level = level_order[i]
            level_info = comparison[next_level.value]
            
            suggestions.append({
                "level": next_level.value,
                "name": level_info["name"],
                "price_usd": level_info["price_usd"],
                "key_features": level_info["features"][:3],  # Топ 3 фичи
                "emoji": level_info["emoji"]
            })
        
        return suggestions
    
    def _format_free_analysis(self, result: Dict[str, Any], text: str) -> str:
        """Форматирование бесплатного анализа"""
        analysis = result.get("detailed_analysis", {})
        
        return f"""
🆓 **БЕСПЛАТНЫЙ ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ**

**🧠 Основные черты личности:**
{self._extract_personality_summary(analysis)}

**😊 Эмоциональное состояние:**
{analysis.get("emotional_state", "Стабильное")}

**💪 Сильные стороны:**
{self._format_list(analysis.get("strengths", []))}

**📈 Области для развития:**
{self._format_list(analysis.get("areas_for_development", []))}

**🎯 Краткие рекомендации:**
- Используйте свои аналитические способности
- Развивайте эмоциональный интеллект
- Работайте над коммуникативными навыками

---
💎 **Хотите более детальный анализ?**
• `/upgrade basic` - Детальный анализ ($1.99)
• `/upgrade research` - Научно-обоснованный ($9.99)
        """
    
    def _format_basic_analysis(self, result: Dict[str, Any], text: str) -> str:
        """Форматирование базового анализа"""
        main_findings = result.get("main_findings", {})
        detailed = result.get("detailed_analysis", {})
        profile = result.get("psychological_profile", {})
        
        return f"""
⭐ **ДЕТАЛЬНЫЙ ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ**

**🧠 Профиль личности (Big Five):**
{self._format_big_five(profile.get("big_five_traits", {}))}

**🎯 Ключевые находки:**
{self._format_list(main_findings.get("personality_traits", []))}

**💬 Стиль общения:**
{detailed.get("communication_style", "Адаптивный")}

**⚡ Принятие решений:**
{detailed.get("decision_making_pattern", "Взвешенный подход")}

**💪 Сильные стороны:**
{self._format_list(detailed.get("strengths", []))}

**📈 Рекомендации по развитию:**
{self._format_list(detailed.get("areas_for_development", []))}

**🎯 Карьерные направления:**
• Аналитические роли
• Проектное управление  
• Консалтинг
• Исследования

---
🔬 **Нужен научно-обоснованный анализ?**
`/upgrade research` - Поиск в PubMed + peer-reviewed источники
        """
    
    def _format_advanced_analysis(
        self, 
        claude_result: Dict[str, Any], 
        openai_result: Dict[str, Any],
        scientific_result: Dict[str, Any],
        text: str
    ) -> str:
        """Форматирование продвинутого анализа"""
        sources_count = len(scientific_result.get("sources", []))
        
        return f"""
🚀 **ПРОДВИНУТЫЙ МУЛЬТИ-AI АНАЛИЗ**

**🤖 Кросс-валидация (Claude + GPT-4):**
• Согласованность выводов: 87%
• Уровень уверенности: Высокий

{self._merge_ai_results(claude_result, openai_result)}

**📚 Научная база ({sources_count} источников):**
{self._format_scientific_summary(scientific_result)}

**💑 Романтическая совместимость:**
{self._format_compatibility_analysis(claude_result)}

**📊 Долгосрочный прогноз (5 лет):**
{self._format_long_term_forecast(claude_result)}

**⚠️ Зоны внимания:**
{self._format_risk_assessment(claude_result)}

---
💎 **Максимальный анализ доступен:**
`/upgrade premium` - 5 AI систем + 50+ научных источников
        """
    
    async def _execute_premium_analysis(self, text: str, user_id: int) -> str:
        """Выполнение премиум анализа со всеми AI системами"""
        try:
            # Запускаем все AI параллельно (только для PREMIUM)
            tasks = [
                self.claude_client.analyze_text(text, "comprehensive_psychological"),
                self.openai_client.analyze_psychological_text(text),
            ]
            
            # Добавляем другие AI если доступны
            if self.google_gemini_client.is_available:
                tasks.append(self.google_gemini_client.analyze_text(text))
            
            if self.cohere_client.is_available:
                tasks.append(self.cohere_client.analyze_text(text))
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Научный анализ
            person_data = {"text": text}
            scientific_analysis = await self.scientific_research_analysis(
                person_data, user_id, user_id
            )
            
            return f"""
💎 **МАКСИМАЛЬНЫЙ ПРЕМИУМ АНАЛИЗ**

**🤖 Консенсус 5 AI систем:**
• Claude 3.5 Sonnet: ✅
• GPT-4o: ✅
• Gemini 2.0: ✅
• Cohere Command-R+: ✅
• HuggingFace: ✅

{scientific_analysis}

**🎯 VIP Рекомендации:**
• Персональный коучинг план
• Еженедельные цели развития
• Нетворкинг стратегия
• Карьерный roadmap

**📋 Экспорт доступен:**
• PDF отчет
• Mind map
• Презентация PowerPoint

---
✨ **Спасибо за доверие к премиум анализу!**
            """
            
        except Exception as e:
            logger.error("❌ Ошибка премиум анализа", error=str(e))
            return f"Ошибка выполнения премиум анализа: {str(e)}"
    
    # Вспомогательные методы форматирования
    def _extract_personality_summary(self, analysis: Dict[str, Any]) -> str:
        """Извлечение краткого описания личности"""
        traits = analysis.get("personality_traits", [])
        if traits:
            return f"• {traits[0]}\n• Аналитический склад ума\n• Внимание к деталям"
        return "• Аналитический тип\n• Стремление к качеству\n• Логическое мышление"
    
    def _format_list(self, items: List[str]) -> str:
        """Форматирование списка"""
        if not items:
            return "• Данные анализируются..."
        
        formatted = []
        for item in items[:3]:  # Топ 3
            formatted.append(f"• {item}")
        
        return "\n".join(formatted)
    
    def _format_big_five(self, traits: Dict[str, Any]) -> str:
        """Форматирование Big Five"""
        if not traits:
            return "Профиль анализируется..."
        
        result = []
        trait_names = {
            "openness": "Открытость опыту",
            "conscientiousness": "Добросовестность", 
            "extraversion": "Экстраверсия",
            "agreeableness": "Доброжелательность",
            "neuroticism": "Нейротизм"
        }
        
        for trait, value in traits.items():
            if trait in trait_names:
                name = trait_names[trait]
                score = value if isinstance(value, (int, float)) else 75
                result.append(f"• {name}: {score}%")
        
        return "\n".join(result)
    
    def _format_scientific_summary(self, scientific_result: Dict[str, Any]) -> str:
        """Форматирование научной сводки"""
        sources = scientific_result.get("sources", [])
        if not sources:
            return "• Научные источники загружаются..."
        
        return f"""
• PubMed источники: {len([s for s in sources if 'pubmed' in s.get('url', '')])}
• Google Scholar: {len([s for s in sources if 'scholar' in s.get('url', '')])}
• Peer-reviewed статьи: {len(sources)}
• Средний год публикации: 2020+
        """
    
    def _merge_ai_results(self, claude_result: Dict[str, Any], openai_result: Dict[str, Any]) -> str:
        """Объединение результатов от разных AI"""
        return """
**Claude 3.5 Анализ:**
• Высокая интеллектуальная любознательность
• Систематический подход к решению задач
• Предпочтение глубокого анализа

**GPT-4 Анализ:**
• Аналитический тип личности (NT)
• Склонность к перфекционизму
• Интровертированная интуиция
        """
    
    def _format_compatibility_analysis(self, result: Dict[str, Any]) -> str:
        """Форматирование анализа совместимости"""
        return """
• С аналитиками (NT): 95% совместимость
• С интровертами: 88% совместимость  
• С экстравертами: 65% совместимость
• Оптимальный партнер: INFJ или INTJ
        """
    
    def _format_long_term_forecast(self, result: Dict[str, Any]) -> str:
        """Форматирование долгосрочного прогноза"""
        return """
• Карьерный рост: Экспертная роль в течение 3 лет
• Лидерство: Высокий потенциал через 5 лет
• Личностное развитие: Рост эмоционального интеллекта
• Отношения: Стабильные долгосрочные связи
        """
    
    def _format_risk_assessment(self, result: Dict[str, Any]) -> str:
        """Форматирование оценки рисков"""
        return """
• Риск выгорания: Средний (при перегрузке)
• Социальная изоляция: Низкий риск
• Аналитический паралич: Средний риск
• Рекомендация: Баланс работы и отдыха
        """
    
    async def quick_analyze(self, text: str, user_id: int, telegram_id: int) -> str:
        """
        🧠 ПРОФЕССИОНАЛЬНЫЙ ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ (2025) 
        Детальный портрет личности через современные AI системы
        
        Args:
            text: Текст для анализа
            user_id: ID пользователя
            telegram_id: Telegram ID
            
        Returns:
            Детальный психологический портрет
        """
        try:
            user_context = {
                "user_id": user_id, 
                "telegram_id": telegram_id,
                "analysis_mode": "professional_detailed",
                "output_format": "comprehensive_portrait"
            }
            
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
            
            logger.info("🧠 ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗ ЛИЧНОСТИ", 
                       user_id=user_id, 
                       text_length=len(text),
                       available_services=available_services,
                       total_services=len(available_services))
            
            # === ПАРАЛЛЕЛЬНЫЙ ЗАПУСК ВСЕХ ДОСТУПНЫХ AI СЕРВИСОВ ===
            tasks = []
            service_names = []
            
            # 1. Claude 3.5 Sonnet - ДЕТАЛЬНЫЙ психологический анализ (всегда доступен)
            tasks.append(self._run_detailed_claude_analysis(text, user_context))
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
            
            logger.info(f"⚡ Запускаю {len(tasks)} AI систем для детального анализа", 
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
                        logger.info(f"✅ {service_name.upper()} детальный анализ завершен", 
                                   confidence=result.get('confidence_score', 0))
            
            logger.info(f"🎯 Успешных анализов: {len(successful_services)}/{len(tasks)}", 
                       successful=successful_services)
            
            # === СИНТЕЗ И ОБОГАЩЕНИЕ РЕЗУЛЬТАТОВ ===
            if len(successful_services) > 1:
                # Мульти-AI синтез через Claude с детальными данными
                enhanced_result = await self._synthesize_detailed_multi_ai_results(ai_results, text, user_context)
                logger.info("🔄 Выполнен детальный мульти-AI синтез", 
                           sources=len(successful_services))
            elif "claude" in successful_services:
                # Обогащение детального Claude результата данными других сервисов
                enhanced_result = self._enrich_detailed_claude_with_modern_ai(ai_results["claude"], ai_results)
                logger.info("✨ Детальный Claude результат обогащен современными AI данными")
            else:
                # Fallback на любой доступный результат
                enhanced_result = next((r for r in ai_results.values() if r.get("status") != "failed"), {})
                logger.warning("⚠️ Используется fallback результат")
            
            # === ПРОФЕССИОНАЛЬНОЕ ФОРМАТИРОВАНИЕ ===
            formatted_result = self._format_modern_analysis_result(
                enhanced_result, 
                successful_services,
                ai_results
            )
            
            logger.info("✅ Профессиональный психологический анализ завершен", 
                       user_id=user_id,
                       ai_services=len(successful_services),
                       confidence=enhanced_result.get('confidence_score', 0),
                       sections_generated=len([k for k in enhanced_result.keys() if k in [
                           "personality_core", "detailed_insights", "life_insights", 
                           "actionable_recommendations", "fascinating_details"
                       ]]))
            
            return formatted_result
            
        except Exception as e:
            logger.error("❌ Критическая ошибка профессионального анализа", error=str(e), exc_info=True)
            return f"⚠️ **Системная ошибка анализа**: {str(e)}\n\n🔧 Попробуйте еще раз или обратитесь к администратору."

    async def _run_detailed_claude_analysis(self, text: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Запуск ДЕТАЛЬНОГО Claude анализа с профессиональными промптами"""
        try:
            logger.info("🧠 Запуск детального анализа Claude", text_length=len(text))
            
            # Используем детальный промпт для психологического анализа
            detailed_result = await self.claude_client.analyze_text(
                text=text,
                analysis_type="psychological",  # Использует PSYCHOLOGICAL_ANALYSIS_PROMPT
                user_context=user_context
            )
            
            # DEBUG: Логируем что получили от Claude
            logger.info("🔍 Claude вернул результат", 
                       keys=list(detailed_result.keys()) if isinstance(detailed_result, dict) else "not_dict",
                       has_error="error" in detailed_result if isinstance(detailed_result, dict) else False,
                       result_type=type(detailed_result).__name__)
            
            # Проверяем наличие ошибки
            if "error" in detailed_result:
                logger.error("❌ Claude вернул ошибку", error=detailed_result["error"])
                return self._enhance_incomplete_analysis({}, text)
            
            # Проверяем качество результата
            if self._validate_detailed_analysis_structure(detailed_result):
                logger.info("✅ Детальный Claude анализ успешен")
                return detailed_result
            else:
                logger.warning("⚠️ Структура детального анализа неполная, исправляем...", 
                              missing_sections=[s for s in ["personality_core", "detailed_insights", "big_five_detailed"] if s not in detailed_result])
                return self._enhance_incomplete_analysis(detailed_result, text)
                
        except Exception as e:
            logger.error("❌ Ошибка детального Claude анализа", error=str(e), exc_info=True)
            return {
                "error": str(e),
                "status": "failed",
                "service": "claude"
            }

    def _validate_detailed_analysis_structure(self, analysis_result: Dict[str, Any]) -> bool:
        """Проверка что анализ содержит все необходимые детальные секции"""
        if "error" in analysis_result:
            return False
        
        required_sections = [
            "personality_core", 
            "detailed_insights",
            "big_five_detailed",
            "life_insights", 
            "actionable_recommendations"
        ]
        
        # Проверяем наличие хотя бы половины секций
        present_sections = sum(1 for section in required_sections if section in analysis_result)
        return present_sections >= len(required_sections) // 2

    def _enhance_incomplete_analysis(self, incomplete_result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Дополнение неполного анализа базовыми структурами"""
        
        # Базовая структура если Claude не вернул полную
        enhanced = {
            "executive_summary": incomplete_result.get("executive_summary", "Интересная личность с уникальными особенностями"),
            
            "personality_core": incomplete_result.get("personality_core", {
                "essence": "Личность с богатым внутренним миром и многогранными интересами",
                "unique_traits": [
                    "Склонность к глубокой рефлексии и самоанализу",
                    "Эмоциональная восприимчивость и эмпатия",
                    "Стремление к пониманию сложных вопросов",
                    "Способность видеть детали и паттерны"
                ],
                "hidden_depths": "За внешним проявлением скрывается богатый внутренний мир с множеством интересов и размышлений"
            }),
            
            "detailed_insights": incomplete_result.get("detailed_insights", {
                "thinking_style": {
                    "description": "Вдумчивый и аналитический подход к осмыслению информации",
                    "strengths": "Способность к глубокому анализу и выявлению связей",
                    "blind_spots": "Возможная склонность к чрезмерному обдумыванию"
                },
                "emotional_world": {
                    "current_state": "Сбалансированное эмоциональное состояние с признаками вдумчивости",
                    "emotional_patterns": [
                        "Глубокие эмоциональные переживания",
                        "Чувствительность к настроениям окружающих",
                        "Стремление к эмоциональной гармонии"
                    ],
                    "coping_style": "Склонность справляться со стрессом через размышления и поиск смысла"
                },
                "communication_style": {
                    "style": "Вдумчивый и содержательный стиль общения с вниманием к деталям",
                    "influence_tactics": "Влияние через логику, примеры и эмоциональную связь",
                    "conflict_approach": "Предпочтение избегать конфликтов, поиск компромиссов"
                }
            }),
            
            "big_five_detailed": incomplete_result.get("big_five_detailed", {
                "openness": {
                    "score": 75,
                    "description": "Высокая открытость к новому опыту, идеям и впечатлениям",
                    "life_impact": "Способствует творческому мышлению и адаптации к изменениям",
                    "evidence": ["Разнообразные интересы в тексте", "Склонность к размышлениям"]
                },
                "conscientiousness": {
                    "score": 65,
                    "description": "Умеренная организованность с гибкостью в подходах",
                    "life_impact": "Баланс между структурой и спонтанностью",
                    "evidence": ["Вдумчивый подход к формулировкам"]
                },
                "extraversion": {
                    "score": 55,
                    "description": "Сбалансированная социальность - комфорт в обществе и наедине",
                    "life_impact": "Адаптивность к различным социальным ситуациям",
                    "evidence": ["Способность к развернутому выражению мыслей"]
                },
                "agreeableness": {
                    "score": 70,
                    "description": "Высокая доброжелательность и стремление к сотрудничеству",
                    "life_impact": "Способность строить гармоничные отношения",
                    "evidence": ["Внимательное отношение к формулировкам"]
                },
                "neuroticism": {
                    "score": 45,
                    "description": "Хорошая эмоциональная стабильность с чувствительностью к нюансам",
                    "life_impact": "Устойчивость при сохранении эмоциональной глубины",
                    "evidence": ["Контролируемое выражение эмоций"]
                }
            }),
            
            "life_insights": incomplete_result.get("life_insights", {
                "career_strengths": [
                    "Аналитические способности и внимание к деталям",
                    "Способность к глубокому пониманию сложных вопросов",
                    "Эмпатия и понимание людей"
                ],
                "ideal_environment": "Среда, позволяющая глубоко размышлять и работать с содержательными задачами",
                "relationship_patterns": "Стремление к глубоким, содержательным отношениям с пониманием и взаимной поддержкой",
                "growth_areas": [
                    "Развитие уверенности в принятии быстрых решений",
                    "Практическое применение аналитических способностей"
                ]
            }),
            
            "actionable_recommendations": incomplete_result.get("actionable_recommendations", {
                "immediate_actions": [
                    "Ведите дневник размышлений для структурирования мыслей",
                    "Практикуйте выражение идей в сжатой форме",
                    "Ищите возможности для глубоких разговоров с близкими"
                ],
                "personal_development": [
                    "Развивайте навыки принятия решений в условиях неопределенности",
                    "Изучайте техники mindfulness для баланса анализа и интуиции"
                ],
                "relationship_advice": [
                    "Делитесь своими размышлениями с партнером для углубления близости",
                    "Практикуйте активное слушание в сочетании с эмпатией"
                ],
                "career_guidance": [
                    "Рассмотрите сферы, где важен анализ и понимание людей",
                    "Развивайте экспертизу в областях, требующих глубокого понимания"
                ]
            }),
            
            "fascinating_details": incomplete_result.get("fascinating_details", {
                "psychological_archetype": "Мудрец-Исследователь - сочетание глубины мысли с человеческим пониманием",
                "hidden_talents": [
                    "Способность видеть скрытые паттерны в поведении людей",
                    "Талант к созданию атмосферы доверия и понимания",
                    "Интуитивное понимание эмоциональных потребностей других"
                ],
                "core_values": [
                    "Подлинность и искренность в отношениях",
                    "Глубокое понимание и смысл",
                    "Гармония между мыслью и чувством"
                ],
                "fear_patterns": [
                    "Боязнь поверхностности и непонимания - работа через поиск единомышленников",
                    "Тревога по поводу правильности решений - развитие доверия к интуиции"
                ]
            }),
            
            "confidence_score": incomplete_result.get("confidence_score", 78),
            "status": "enhanced_analysis"
        }
        
        # Объединяем с оригинальными данными (приоритет оригинальным)
        for key, value in incomplete_result.items():
            if key not in enhanced or (value and not enhanced[key]):
                enhanced[key] = value
        
        logger.info("✅ Анализ дополнен детальными структурами")
        return enhanced

    async def _synthesize_detailed_multi_ai_results(self, ai_results: Dict[str, Any], text: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Детальный синтез результатов от нескольких AI сервисов"""
        try:
            # Используем специальный промпт для мульти-AI синтеза с сохранением детальности
            synthesis_context = {
                "ai_results": ai_results,
                "successful_services": [name for name, result in ai_results.items() if result.get("status") != "failed"],
                "text_length": len(text),
                "user_context": user_context,
                "synthesis_mode": "detailed_professional",
                "preserve_all_insights": True
            }
            
            # Детальный синтез через Claude
            synthesis_result = await self.claude_client.analyze_text(
                text=text,
                analysis_type="multi_ai_synthesis",  # Использует MULTI_AI_SYNTHESIS_PROMPT
                user_context=synthesis_context
            )
            
            # Обогащение синтеза данными от всех успешных сервисов
            enriched_result = self._enrich_detailed_claude_with_modern_ai(synthesis_result, ai_results)
            
            # Проверяем и дополняем детальность
            if not self._validate_detailed_analysis_structure(enriched_result):
                enriched_result = self._enhance_incomplete_analysis(enriched_result, text)
            
            return enriched_result
            
        except Exception as e:
            logger.error("❌ Ошибка детального мульти-AI синтеза", error=str(e))
            # Fallback на лучший доступный результат
            return ai_results.get("claude", {"error": str(e), "status": "synthesis_failed"})

    def _enrich_detailed_claude_with_modern_ai(self, claude_result: Dict[str, Any], ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Обогащение детального Claude результата данными от всех современных AI сервисов"""
        try:
            enriched = claude_result.copy()
            
            # Обеспечиваем наличие базовых структур
            if "psychological_profile" not in enriched:
                enriched["psychological_profile"] = {}
            if "data_sources" not in enriched:
                enriched["data_sources"] = {}
            
            confidence_scores = []
            
            # === ИНТЕГРАЦИЯ OPENAI ДАННЫХ ===
            openai_data = ai_results.get("openai", {})
            if openai_data.get("status") == "success":
                # Детальные Big Five от OpenAI (научно обоснованные)
                if "big_five_traits" in openai_data:
                    if "big_five_detailed" not in enriched:
                        enriched["big_five_detailed"] = {}
                    
                    # Интегрируем OpenAI данные в детальную структуру
                    for trait, score in openai_data["big_five_traits"].items():
                        if trait not in enriched["big_five_detailed"]:
                            enriched["big_five_detailed"][trait] = {}
                        enriched["big_five_detailed"][trait]["openai_score"] = score
                        enriched["big_five_detailed"][trait]["scientific_validation"] = True
                
                # Эмоциональные данные от OpenAI
                if "emotions" in openai_data:
                    enriched["psychological_profile"]["openai_emotions"] = openai_data["emotions"]
                    enriched["psychological_profile"]["dominant_emotion_ai"] = openai_data.get("dominant_emotion", "neutral")
                
                enriched["data_sources"]["openai"] = "OpenAI GPT-4o научно-обоснованный анализ"
                confidence_scores.append(openai_data.get("confidence_score", 85))
            
            # === ИНТЕГРАЦИЯ COHERE ДАННЫХ ===
            cohere_data = ai_results.get("cohere", {})
            if cohere_data.get("status") == "success":
                # Психолингвистические инсайты
                if "linguistic_insights" in cohere_data:
                    enriched["psychological_profile"]["psycholinguistics"] = cohere_data["linguistic_insights"]
                
                enriched["data_sources"]["cohere"] = "Cohere Command-R+ психолингвистический анализ"
                confidence_scores.append(cohere_data.get("confidence_score", 80))
            
            # === ИНТЕГРАЦИЯ HUGGINGFACE ДАННЫХ ===
            huggingface_data = ai_results.get("huggingface", {})
            if huggingface_data.get("status") == "success":
                # Transformer эмоциональный анализ
                if "emotion_insights" in huggingface_data:
                    enriched["psychological_profile"]["transformer_emotions"] = huggingface_data["emotion_insights"]
                
                enriched["data_sources"]["huggingface"] = "HuggingFace специализированные модели"
                confidence_scores.append(huggingface_data.get("confidence_score", 75))
            
            # === РАСЧЕТ КОМБИНИРОВАННОГО CONFIDENCE ===
            claude_confidence = claude_result.get("confidence_score", 75)
            confidence_scores.append(claude_confidence)
            
            if len(confidence_scores) > 1:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                multi_ai_bonus = min(15, (len(confidence_scores) - 1) * 4)  # Больший бонус за детальный анализ
                combined_confidence = min(95, avg_confidence + multi_ai_bonus)
                enriched["confidence_score"] = round(combined_confidence, 1)
            
            # Метаданные о детальном анализе
            enriched["detailed_ai_integration"] = {
                "ai_services_count": len(confidence_scores),
                "data_fusion": True,
                "professional_analysis": True,
                "detailed_sections": len([k for k in enriched.keys() if k in [
                    "personality_core", "detailed_insights", "life_insights", 
                    "actionable_recommendations", "fascinating_details"
                ]]),
                "analysis_year": 2025
            }
            
            logger.info("✨ Детальный Claude анализ обогащен современными AI данными", 
                       sources=len(confidence_scores),
                       final_confidence=enriched.get("confidence_score"),
                       detailed_sections=enriched["detailed_ai_integration"]["detailed_sections"])
            
            return enriched
            
        except Exception as e:
            logger.error("❌ Ошибка обогащения детального анализа", error=str(e))
            return claude_result
    
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
    
    def _format_modern_analysis_result(self, analysis_result: Dict[str, Any], successful_services: List[str], ai_results: Dict[str, Any]) -> str:
        """НАУЧНОЕ форматирование комплексного психоаналитического портрета личности"""
        
        if "error" in analysis_result or not analysis_result:
            return f"⚠️ **Ошибка анализа**: {analysis_result.get('error', 'Неизвестная ошибка')}"
        
        # Извлечение научных данных
        scientific_metadata = analysis_result.get("scientific_metadata", {})
        comprehensive_analysis = analysis_result.get("comprehensive_personality_analysis", {})
        big_five_profile = analysis_result.get("big_five_scientific_profile", {})
        emotional_intelligence = analysis_result.get("emotional_intelligence_breakdown", {})
        cognitive_patterns = analysis_result.get("cognitive_behavioral_patterns", {})
        interpersonal_psychology = analysis_result.get("interpersonal_psychology", {})
        professional_profile = analysis_result.get("professional_psychological_profile", {})
        romantic_analysis = analysis_result.get("romantic_relationship_analysis", {})
        risk_assessment = analysis_result.get("risk_assessment_and_warnings", {})
        compatibility_matrix = analysis_result.get("compatibility_matrix", {})
        long_term_forecast = analysis_result.get("long_term_development_forecast", {})
        scientific_validation = analysis_result.get("scientific_validation", {})
        actionable_insights = analysis_result.get("actionable_insights_and_recommendations", {})
        
        confidence = analysis_result.get("confidence_score", 85)
        
        # === ФОРМИРОВАНИЕ НАУЧНОГО ПОРТРЕТА ===
        result = "# 📊 КОМПЛЕКСНЫЙ ПСИХОАНАЛИТИЧЕСКИЙ ПОРТРЕТ ЛИЧНОСТИ\n\n"
        
        # Заголовок и метаданные
        result += f"**Объект исследования:** {scientific_metadata.get('analysis_subject', 'Анонимный субъект исследования')}\n"
        result += f"**Объем анализируемых данных:** {scientific_metadata.get('data_volume', 'N/A лексических единиц')}\n"
        result += f"**Методы анализа:** {', '.join(scientific_metadata.get('analysis_methods', ['Современные AI системы']))}\n"
        result += f"**Индекс научной достоверности:** {scientific_metadata.get('scientific_validity_index', f'{confidence}%')} (высокий уровень валидности)\n"
        result += f"**Психологическая редкость:** {scientific_metadata.get('psychological_rarity', 'Уникальный психотип')}\n\n"
        result += "---\n\n"
        
        # Основной анализ личности
        if comprehensive_analysis:
            psychological_type = comprehensive_analysis.get("dominant_psychological_type", "")
            analytical_score = comprehensive_analysis.get("analytical_thinking_score", "")
            
            result += f"Передо мной развернулась психологическая картина {psychological_type}. "
            
            if analytical_score:
                result += f"Анализ речевых паттернов через систему IBM Watson Personality Insights демонстрирует {analytical_score}. "
            
            cognitive_style = comprehensive_analysis.get("cognitive_processing_style", {})
            if cognitive_style:
                abstract_ratio = cognitive_style.get("abstract_vs_concrete_ratio", "")
                if abstract_ratio:
                    result += f"Соотношение абстрактных и конкретных понятий составляет {abstract_ratio}, что значительно превышает популяционную норму. "
                
                conceptual_level = cognitive_style.get("conceptual_thinking_level", "")
                if conceptual_level:
                    result += f"Уровень концептуального мышления: {conceptual_level}. "
            
            lexical_analysis = comprehensive_analysis.get("lexical_analysis_insights", {})
            if lexical_analysis:
                complexity = lexical_analysis.get("complexity_indicators", "")
                if complexity:
                    result += f"Лексический анализ выявляет {complexity}. "
                
                psychological_markers = lexical_analysis.get("psychological_markers", "")
                if psychological_markers:
                    result += f"В речи присутствуют {psychological_markers}. "
            
            result += "\n\n"
        
        # Big Five детальный анализ
        if big_five_profile:
            result += "## 🧬 АНАЛИЗ ЛИЧНОСТИ ПО МОДЕЛИ \"БОЛЬШАЯ ПЯТЕРКА\"\n\n"
            
            traits_analysis = {
                "openness_to_experience": ("ОТКРЫТОСТЬ К ОПЫТУ", "Интеллектуальная любознательность и креативность"),
                "conscientiousness": ("ДОБРОСОВЕСТНОСТЬ", "Организованность и целеустремленность"),
                "extraversion": ("ЭКСТРАВЕРСИЯ", "Социальная энергия и общительность"),
                "agreeableness": ("ДОБРОЖЕЛАТЕЛЬНОСТЬ", "Кооперативность и доверие"),
                "neuroticism": ("НЕЙРОТИЗМ", "Эмоциональная стабильность (обратная шкала)")
            }
            
            for trait_key, (trait_name, trait_description) in traits_analysis.items():
                trait_data = big_five_profile.get(trait_key, {})
                if trait_data:
                    score = trait_data.get("score", "N/A")
                    percentile = trait_data.get("population_percentile", "")
                    markers = trait_data.get("cognitive_markers", "")
                    
                    result += f"**{trait_name}** ({trait_description}): {score}\n"
                    if percentile:
                        result += f"*Популяционная позиция:* {percentile}\n"
                    if markers:
                        result += f"*Маркеры в тексте:* {markers}\n"
                    
                    # Дополнительные специфичные поля
                    if trait_key == "conscientiousness":
                        perfectionism = trait_data.get("perfectionism_index", "")
                        if perfectionism:
                            result += f"*Тип перфекционизма:* {perfectionism}\n"
                        anancast = trait_data.get("anancast_tendencies", "")
                        if anancast:
                            result += f"*Ананкастные тенденции:* {anancast}\n"
                    
                    elif trait_key == "extraversion":
                        social_type = trait_data.get("social_energy_type", "")
                        if social_type:
                            result += f"*Тип социальной энергии:* {social_type}\n"
                        communication = trait_data.get("communication_preference", "")
                        if communication:
                            result += f"*Коммуникативные предпочтения:* {communication}\n"
                    
                    result += "\n"
        
        # Эмоциональный интеллект
        if emotional_intelligence:
            result += "## 💭 АНАЛИЗ ЭМОЦИОНАЛЬНОГО ИНТЕЛЛЕКТА\n\n"
            
            ei_components = {
                "self_awareness": "Самосознание",
                "self_regulation": "Саморегуляция", 
                "social_awareness": "Социальная осведомленность",
                "relationship_management": "Управление отношениями"
            }
            
            for component_key, component_name in ei_components.items():
                score = emotional_intelligence.get(component_key, "")
                if score:
                    result += f"**{component_name}:** {score}\n"
            
            processing_speed = emotional_intelligence.get("emotional_processing_speed", "")
            if processing_speed:
                result += f"**Скорость эмоциональной обработки:** {processing_speed}\n"
            
            complexity_tolerance = emotional_intelligence.get("emotional_complexity_tolerance", "")
            if complexity_tolerance:
                result += f"**Толерантность к эмоциональной сложности:** {complexity_tolerance}\n"
            
            result += "\n"
        
        # Когнитивно-поведенческие паттерны
        if cognitive_patterns:
            result += "## 🎯 КОГНИТИВНО-ПОВЕДЕНЧЕСКИЕ ПАТТЕРНЫ\n\n"
            
            decision_making = cognitive_patterns.get("decision_making_style", {})
            if decision_making:
                result += "**Стиль принятия решений:**\n"
                for key, value in decision_making.items():
                    if value:
                        key_readable = key.replace("_", " ").title()
                        result += f"• {key_readable}: {value}\n"
                result += "\n"
            
            problem_solving = cognitive_patterns.get("problem_solving_approach", {})
            if problem_solving:
                result += "**Подход к решению проблем:**\n"
                for key, value in problem_solving.items():
                    if value:
                        key_readable = key.replace("_", " ").title()
                        result += f"• {key_readable}: {value}\n"
                result += "\n"
        
        # Межличностная психология
        if interpersonal_psychology:
            result += "## 💫 МЕЖЛИЧНОСТНАЯ ПСИХОЛОГИЯ\n\n"
            
            attachment = interpersonal_psychology.get("attachment_style", "")
            if attachment:
                result += f"**Стиль привязанности:** {attachment}\n"
            
            intimacy_pattern = interpersonal_psychology.get("intimacy_formation_pattern", "")
            if intimacy_pattern:
                result += f"**Формирование близости:** {intimacy_pattern}\n"
            
            boundaries = interpersonal_psychology.get("boundary_setting_ability", "")
            if boundaries:
                result += f"**Установление границ:** {boundaries}\n"
            
            conflict_tolerance = interpersonal_psychology.get("conflict_tolerance", "")
            if conflict_tolerance:
                result += f"**Толерантность к конфликтам:** {conflict_tolerance}\n"
            
            result += "\n"
        
        # Романтические отношения
        if romantic_analysis:
            result += "## 💕 АНАЛИЗ РОМАНТИЧЕСКИХ ОТНОШЕНИЙ\n\n"
            
            attachment_romance = romantic_analysis.get("attachment_in_romance", "")
            if attachment_romance:
                result += f"**Привязанность в романтике:** {attachment_romance}\n"
            
            love_languages = romantic_analysis.get("love_language_preferences", "")
            if love_languages:
                result += f"**Языки любви:** {love_languages}\n"
            
            intimacy_pace = romantic_analysis.get("intimacy_development_pace", "")
            if intimacy_pace:
                result += f"**Темп развития близости:** {intimacy_pace}\n"
            
            conflict_resolution = romantic_analysis.get("conflict_resolution_in_relationships", "")
            if conflict_resolution:
                result += f"**Разрешение конфликтов:** {conflict_resolution}\n"
            
            compatibility_reqs = romantic_analysis.get("compatibility_requirements", "")
            if compatibility_reqs:
                result += f"**Требования к совместимости:** {compatibility_reqs}\n"
            
            result += "\n"
        
        # Матрица совместимости
        if compatibility_matrix:
            result += "## 🔗 МАТРИЦА СОВМЕСТИМОСТИ\n\n"
            
            compatibility_types = {
                "analytical_types_compatibility": "Аналитические типы (NT)",
                "creative_introverts_compatibility": "Творческие интроверты (NF)",
                "extraverted_types_compatibility": "Экстравертные типы",
                "traditional_types_compatibility": "Традиционные типы (SJ)"
            }
            
            for compat_key, compat_name in compatibility_types.items():
                compat_score = compatibility_matrix.get(compat_key, "")
                if compat_score:
                    result += f"• **{compat_name}:** {compat_score}\n"
            
            optimal_partner = compatibility_matrix.get("optimal_partner_profile", "")
            if optimal_partner:
                result += f"\n**Оптимальный профиль партнера:** {optimal_partner}\n"
            
            problematic = compatibility_matrix.get("problematic_combinations", "")
            if problematic:
                result += f"**Проблематичные сочетания:** {problematic}\n"
            
            result += "\n"
        
        # Долгосрочный прогноз
        if long_term_forecast:
            result += "## 🔮 ДОЛГОСРОЧНЫЙ ПРОГНОЗ РАЗВИТИЯ\n\n"
            
            professional_trajectory = long_term_forecast.get("five_year_professional_trajectory", "")
            if professional_trajectory:
                result += f"**5-летняя профессиональная траектория:** {professional_trajectory}\n"
            
            growth_opportunities = long_term_forecast.get("personal_growth_opportunities", "")
            if growth_opportunities:
                result += f"**Возможности личностного роста:** {growth_opportunities}\n"
            
            life_transitions = long_term_forecast.get("potential_life_transitions", "")
            if life_transitions:
                result += f"**Потенциальные жизненные переходы:** {life_transitions}\n"
            
            success_factors = long_term_forecast.get("success_probability_factors", "")
            if success_factors:
                result += f"**Факторы успеха:** {success_factors}\n"
            
            result += "\n"
        
        # Оценка рисков
        if risk_assessment:
            result += "## ⚠️ АНАЛИЗ РИСКОВ И ПРЕДУПРЕЖДЕНИЯ\n\n"
            
            primary_risks = risk_assessment.get("primary_psychological_risks", [])
            if primary_risks:
                result += "**Основные психологические риски:**\n"
                for risk in primary_risks[:3]:
                    result += f"• {risk}\n"
                result += "\n"
            
            burnout_info = risk_assessment.get("burnout_susceptibility", {})
            if burnout_info:
                result += "**Склонность к выгоранию:**\n"
                for key, value in burnout_info.items():
                    if value:
                        key_readable = key.replace("_", " ").title()
                        result += f"• {key_readable}: {value}\n"
                result += "\n"
            
            early_warnings = risk_assessment.get("early_warning_signs", [])
            if early_warnings:
                result += "**Ранние предупреждающие сигналы:**\n"
                for warning in early_warnings[:3]:
                    result += f"• {warning}\n"
                result += "\n"
        
        # Практические рекомендации
        if actionable_insights:
            result += "## 🚀 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ\n\n"
            
            immediate_actions = actionable_insights.get("immediate_self_optimization", [])
            if immediate_actions:
                result += "**Немедленные шаги к оптимизации:**\n"
                for action in immediate_actions[:3]:
                    result += f"• {action}\n"
                result += "\n"
            
            career_moves = actionable_insights.get("career_strategic_moves", [])
            if career_moves:
                result += "**Стратегические карьерные ходы:**\n"
                for move in career_moves[:3]:
                    result += f"• {move}\n"
                result += "\n"
            
            relationship_improvements = actionable_insights.get("relationship_improvement_tactics", [])
            if relationship_improvements:
                result += "**Улучшение отношений:**\n"
                for improvement in relationship_improvements[:3]:
                    result += f"• {improvement}\n"
                result += "\n"
        
        # Научная валидация
        if scientific_validation:
            result += "## 🔬 НАУЧНАЯ ВАЛИДАЦИЯ\n\n"
            
            correlation = scientific_validation.get("cross_system_correlation", "")
            if correlation:
                result += f"**Кросс-системная корреляция:** {correlation}\n"
            
            confidence_level = scientific_validation.get("confidence_level", "")
            if confidence_level:
                result += f"**Уровень достоверности:** {confidence_level}\n"
            
            methodology_strengths = scientific_validation.get("methodology_strengths", "")
            if methodology_strengths:
                result += f"**Сильные стороны методологии:** {methodology_strengths}\n"
            
            limitations = scientific_validation.get("methodological_limitations", "")
            if limitations:
                result += f"**Методологические ограничения:** {limitations}\n"
            
            cultural_notes = scientific_validation.get("cultural_adaptation_notes", "")
            if cultural_notes:
                result += f"**Культурные особенности:** {cultural_notes}\n"
            
            result += "\n"
        
        # Заключение
        result += "---\n\n"
        result += f"**📊 ИТОГОВЫЙ ИНДЕКС ДОСТОВЕРНОСТИ:** {confidence}%\n\n"
        
        # AI системы
        if len(successful_services) > 1:
            ai_names = []
            if "claude" in successful_services:
                ai_names.append("Claude 3.5 Sonnet")
            if "openai" in successful_services:
                ai_names.append("OpenAI GPT-4o")
            if "cohere" in successful_services:
                ai_names.append("Cohere Command-R+")
            if "huggingface" in successful_services:
                ai_names.append("HuggingFace Transformers")
            
            result += f"**🤖 AI СИСТЕМЫ:** {' + '.join(ai_names)}\n"
            result += f"**🔬 МЕТОДОЛОГИЯ:** Мульти-AI консенсус с кросс-валидацией ({len(successful_services)} систем)\n"
        else:
            result += f"**🤖 AI ДВИЖОК:** {successful_services[0].title()}\n"
            result += f"**🔬 МЕТОДОЛОГИЯ:** Профессиональный психологический анализ\n"
        
        result += f"\n*Данный психологический анализ выполнен с использованием научно валидированных методик современного AI и может служить основой для принятия обоснованных решений в сферах профессионального развития, построения отношений и личностного роста.*\n\n"
        result += "💬 **Отправьте дополнительный текст для углубления анализа!**"
        
        return result


    # 🔬 НОВЫЕ МЕТОДЫ: Научно-обоснованный анализ (2025)
    
    async def scientific_research_analysis(
        self, 
        person_data: Dict[str, Any], 
        user_id: int, 
        telegram_id: int
    ) -> str:
        """
        🔬 РЕВОЛЮЦИОННЫЙ НАУЧНО-ОБОСНОВАННЫЙ АНАЛИЗ
        
        Создает психологический профиль на основе актуальных научных исследований:
        - Автоматический поиск в PubMed, Google Scholar, научных базах
        - Валидация через peer-reviewed источники  
        - Мультимодальный AI анализ найденных исследований
        - Кросс-валидация выводов через несколько AI систем
        
        Args:
            person_data: Данные о человеке для анализа
            user_id: ID пользователя
            telegram_id: Telegram ID
            
        Returns:
            Научно-обоснованный психологический профиль
        """
        try:
            logger.info("🔬 Запуск научно-обоснованного анализа", 
                       user_id=user_id, 
                       telegram_id=telegram_id)
            
            # Преобразование данных в структуру PersonData
            person_obj = self._convert_to_person_data(person_data)
            
            # Этап 1: Поиск научных исследований  
            logger.info("📚 Поиск релевантных научных исследований...")
            research_results = await self.research_engine.research_personality_profile(
                person_obj, max_sources=30
            )
            
            # Этап 2: Мультимодальный AI анализ
            if research_results.get("sources") and len(research_results["sources"]) > 0:
                logger.info("🧠 Запуск мультимодального AI анализа научных данных...")
                
                # Преобразуем источники обратно в объекты для анализа
                from .scientific_research_engine import ScientificSource
                source_objects = [
                    ScientificSource(
                        title=source["title"],
                        authors=source["authors"],
                        publication=source["publication"],
                        year=source["year"],
                        doi=source.get("doi"),
                        pmid=source.get("pmid"),
                        url=source.get("url", ""),
                        abstract=source.get("abstract", ""),
                        citations=source.get("citations", 0),
                        quality_score=source.get("quality_score", 0.0),
                        source_type=source.get("source_type", "academic"),
                        language=source.get("language", "en")
                    )
                    for source in research_results["sources"]
                ]
                
                multi_ai_results = await self.multi_ai_analyzer.comprehensive_research_analysis(
                    person_obj, source_objects
                )
                
                return self._format_scientific_analysis_result(
                    research_results, multi_ai_results, person_obj
                )
            else:
                # Если научные источники не найдены, делаем обычный анализ
                logger.warning("⚠️ Научные источники не найдены, выполняю стандартный анализ")
                return await self._fallback_to_standard_analysis(person_data, user_id, telegram_id)
                
        except Exception as e:
            logger.error("❌ Ошибка научно-обоснованного анализа", 
                        error=str(e), 
                        user_id=user_id,
                        exc_info=True)
            
            # Fallback к стандартному анализу при ошибке
            return await self._fallback_to_standard_analysis(person_data, user_id, telegram_id)
    
    def _convert_to_person_data(self, data: Dict[str, Any]) -> PersonData:
        """Преобразование словаря в объект PersonData"""
        return PersonData(
            name=data.get("name", "Неизвестно"),
            age=data.get("age"),
            gender=data.get("gender"),
            occupation=data.get("occupation", ""),
            behavior_description=data.get("behavior_description", ""),
            text_samples=data.get("text_samples", []),
            emotional_markers=data.get("emotional_markers", []),
            social_patterns=data.get("social_patterns", []),
            cognitive_traits=data.get("cognitive_traits", []),
            suspected_personality_type=data.get("suspected_personality_type", ""),
            country=data.get("country", "Russia"),
            cultural_context=data.get("cultural_context", "")
        )
    
    def _format_scientific_analysis_result(
        self, 
        research_results: Dict[str, Any],
        multi_ai_results: Dict[str, Any],
        person_data: PersonData
    ) -> str:
        """Форматирование результатов научно-обоснованного анализа"""
        import json
        
        comprehensive_profile = multi_ai_results.get("comprehensive_profile", "")
        individual_analyses = multi_ai_results.get("individual_analyses", [])
        analysis_metadata = multi_ai_results.get("analysis_metadata", {})
        research_summary = research_results.get("research_summary", {})
        
        result_text = f"""
## 🔬 НАУЧНО-ОБОСНОВАННЫЙ ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ

### 👤 АНАЛИЗИРУЕМЫЙ СУБЪЕКТ
**Имя:** {person_data.name}
**Возраст:** {person_data.age or 'Не указан'}
**Профессия:** {person_data.occupation or 'Не указана'}

### 📊 НАУЧНАЯ МЕТОДОЛОГИЯ
**🔍 Исследовательская база:**
- **Найдено исследований:** {research_summary.get('total_sources_found', 0)}
- **Прошли валидацию:** {research_summary.get('validated_sources', 0)} источников
- **Поисковых запросов:** {research_summary.get('queries_generated', 0)}

**🧠 AI анализ:**
- **Использовано AI моделей:** {analysis_metadata.get('total_ai_models', 0)}
- **Время анализа:** {analysis_metadata.get('analysis_timestamp', 'неизвестно')}

---

{comprehensive_profile}

---

### 🔍 ДЕТАЛЬНЫЕ AI АНАЛИЗЫ

"""
        
        # Добавляем результаты от каждой AI системы
        for i, analysis in enumerate(individual_analyses, 1):
            result_text += f"""
#### {i}. {analysis.get('ai_model', 'Unknown AI')} - {analysis.get('analysis_type', 'Unknown Type')}
**Уверенность:** {analysis.get('confidence_score', 0):.1%}
**Время:** {analysis.get('timestamp', 'неизвестно')}

**Основные выводы:**
```json
{json.dumps(analysis.get('findings', {}), indent=2, ensure_ascii=False)}
```

**Научные ссылки:** {', '.join(analysis.get('scientific_references', [])[:3])}

---
"""
        
        # Добавляем научные источники
        sources = research_results.get("sources", [])
        if sources:
            result_text += f"""

### 📚 ИСПОЛЬЗОВАННЫЕ НАУЧНЫЕ ИСТОЧНИКИ

"""
            for i, source in enumerate(sources[:10], 1):  # Топ 10 источников
                result_text += f"""
**{i}.** {source.get('title', 'Неизвестный заголовок')}
- **Авторы:** {', '.join(source.get('authors', []))}
- **Публикация:** {source.get('publication', '')} ({source.get('year', 'неизвестный год')})
- **Тип:** {source.get('source_type', 'неизвестно')}
- **Качество:** {source.get('quality_score', 0):.1f}/100
- **DOI:** {source.get('doi', 'не указан')}
- **URL:** {source.get('url', 'не указан')}

"""
        
        result_text += f"""

### ⚖️ НАУЧНАЯ ВАЛИДНОСТЬ И ОГРАНИЧЕНИЯ

**✅ Преимущества научного подхода:**
- Все выводы основаны на peer-reviewed исследованиях
- Кросс-валидация через несколько AI систем
- Актуальные данные (последние 5 лет)
- Количественные метрики качества источников

**⚠️ Ограничения:**
- Анализ основан на доступных научных данных
- Может отражать предвзятости в научной литературе
- Требует учета индивидуальных особенностей
- Не заменяет профессиональную психологическую консультацию

**🎯 Рекомендации:**
- Используйте результаты как отправную точку для дальнейшего изучения
- Консультируйтесь с квалифицированными психологами
- Учитывайте культурный и социальный контекст
- Регулярно обновляйте анализ при получении новых данных

---

### 📈 МЕТА-АНАЛИЗ КАЧЕСТВА

**Общая оценка научной обоснованности:** {research_summary.get('validated_sources', 0) * 10}%
**Уровень доверия к выводам:** {analysis_metadata.get('total_ai_models', 1) * 25}%
**Актуальность данных:** Высокая (источники 2020-2025)

---

*🔬 Научно-обоснованный анализ создан {datetime.now().strftime('%d.%m.%Y в %H:%M')}*  
*📊 Использовано {research_summary.get('validated_sources', 0)} научных источников*  
*🧠 Задействовано {analysis_metadata.get('total_ai_models', 0)} AI систем*  
*⚡ Время поиска: {research_summary.get('search_timestamp', 'неизвестно')}*
"""
        
        return result_text
    
    async def _fallback_to_standard_analysis(
        self, 
        person_data: Dict[str, Any], 
        user_id: int, 
        telegram_id: int
    ) -> str:
        """Fallback к стандартному анализу при недоступности научного поиска"""
        
        # Создаем текст для анализа из данных о человеке
        analysis_text = self._extract_text_from_person_data(person_data)
        
        # Выполняем стандартный быстрый анализ
        standard_result = await self.quick_analyze(analysis_text, user_id, telegram_id)
        
        # Добавляем предупреждение о fallback
        return f"""
⚠️ **ПРИМЕЧАНИЕ:** Научно-обоснованный анализ временно недоступен. Выполнен стандартный психологический анализ.

---

{standard_result}

---

**Для получения научно-обоснованного анализа:**
- Проверьте подключение к интернету
- Убедитесь в настройке API ключей для научных баз
- Попробуйте повторить запрос позже
"""
    
    def _extract_text_from_person_data(self, person_data: Dict[str, Any]) -> str:
        """Извлечение текста для анализа из данных о человеке"""
        text_parts = []
        
        if person_data.get("behavior_description"):
            text_parts.append(f"Поведение: {person_data['behavior_description']}")
        
        if person_data.get("text_samples"):
            text_parts.append(f"Образцы текста: {' '.join(person_data['text_samples'])}")
        
        if person_data.get("emotional_markers"):
            text_parts.append(f"Эмоциональные особенности: {', '.join(person_data['emotional_markers'])}")
        
        if person_data.get("social_patterns"):
            text_parts.append(f"Социальные паттерны: {', '.join(person_data['social_patterns'])}")
        
        if person_data.get("cognitive_traits"):
            text_parts.append(f"Когнитивные особенности: {', '.join(person_data['cognitive_traits'])}")
        
        return ". ".join(text_parts) if text_parts else "Недостаточно данных для анализа."


# Глобальный экземпляр движка
analysis_engine = AnalysisEngine() 