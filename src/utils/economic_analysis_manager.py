"""
💰 ЭКОНОМИЧЕСКИЙ МЕНЕДЖЕР АНАЛИЗА
Профессиональная система управления стоимостью и уровнями анализа
"""
import asyncio
import structlog
import time
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import json

from src.config.settings import settings
from src.database.connection import get_async_session
from src.database.models import User, Analysis, ApiUsage

logger = structlog.get_logger()


class AnalysisLevel(Enum):
    """Уровни психологического анализа с экономической оптимизацией"""
    
    FREE = "free"           # Бесплатный (3 раза в день, только Claude)
    BASIC = "basic"         # $1.99 - Claude + быстрая валидация
    ADVANCED = "advanced"   # $4.99 - Claude + OpenAI + научная выборка
    RESEARCH = "research"   # $9.99 - Полный научный поиск + 2 AI
    PREMIUM = "premium"     # $19.99 - Все AI + полный научный анализ


@dataclass
class AnalysisConfig:
    """Конфигурация для уровня анализа"""
    level: AnalysisLevel
    price_usd: float
    ai_services: List[str]
    scientific_search: bool
    max_sources: int
    cache_enabled: bool
    estimated_tokens: int
    estimated_time_minutes: int
    features: List[str]


@dataclass
class CostEstimate:
    """Оценка стоимости анализа"""
    level: AnalysisLevel
    estimated_cost_usd: float
    estimated_tokens: int
    ai_services_count: int
    cache_hit_probability: float
    estimated_time_minutes: int


class EconomicAnalysisManager:
    """Менеджер экономических уровней психологического анализа"""
    
    def __init__(self):
        """Инициализация экономического менеджера"""
        self.analysis_configs = self._init_analysis_configs()
        self.daily_limits = {
            AnalysisLevel.FREE: settings.free_analyses_per_day,
            AnalysisLevel.BASIC: 50,
            AnalysisLevel.ADVANCED: 20,
            AnalysisLevel.RESEARCH: 10,
            AnalysisLevel.PREMIUM: 5
        }
        logger.info("💰 EconomicAnalysisManager инициализирован", 
                   levels=len(self.analysis_configs),
                   daily_limit_usd=settings.daily_cost_limit_usd)
    
    def _init_analysis_configs(self) -> Dict[AnalysisLevel, AnalysisConfig]:
        """Инициализация конфигураций для всех уровней анализа"""
        return {
            AnalysisLevel.FREE: AnalysisConfig(
                level=AnalysisLevel.FREE,
                price_usd=0.0,
                ai_services=["claude"],
                scientific_search=False,
                max_sources=0,
                cache_enabled=True,
                estimated_tokens=2500,
                estimated_time_minutes=1,
                features=[
                    "Базовый психологический анализ",
                    "Big Five оценка", 
                    "Эмоциональный профиль",
                    "Основные рекомендации"
                ]
            ),
            
            AnalysisLevel.BASIC: AnalysisConfig(
                level=AnalysisLevel.BASIC,
                price_usd=settings.basic_price_usd,
                ai_services=["claude"],
                scientific_search=False,
                max_sources=0,
                cache_enabled=True,
                estimated_tokens=4000,
                estimated_time_minutes=2,
                features=[
                    "Детальный психологический анализ",
                    "Big Five + DISC профиль",
                    "Когнитивные паттерны",
                    "Межличностная совместимость",
                    "Карьерные рекомендации",
                    "Приоритетная обработка"
                ]
            ),
            
            AnalysisLevel.ADVANCED: AnalysisConfig(
                level=AnalysisLevel.ADVANCED,
                price_usd=settings.advanced_price_usd,
                ai_services=["claude", "openai"],
                scientific_search=True,
                max_sources=10,
                cache_enabled=True,
                estimated_tokens=8000,
                estimated_time_minutes=3,
                features=[
                    "Мульти-AI анализ (Claude + GPT-4)",
                    "Научная выборка (10 источников)",
                    "Углубленный эмоциональный интеллект",
                    "Профессиональная психология",
                    "Романтическая совместимость",
                    "Долгосрочные прогнозы (5 лет)",
                    "Кросс-валидация результатов"
                ]
            ),
            
            AnalysisLevel.RESEARCH: AnalysisConfig(
                level=AnalysisLevel.RESEARCH,
                price_usd=settings.research_price_usd,
                ai_services=["claude", "openai", "gemini"],
                scientific_search=True,
                max_sources=30,
                cache_enabled=True,
                estimated_tokens=15000,
                estimated_time_minutes=5,
                features=[
                    "Научно-обоснованный анализ",
                    "Поиск в PubMed + Google Scholar",
                    "Peer-reviewed валидация",
                    "3 AI системы (Claude + GPT-4 + Gemini)",
                    "30+ научных источников",
                    "Статистическая валидность",
                    "Клинические рекомендации",
                    "Долгосрочные прогнозы (10 лет)",
                    "Культурная адаптация"
                ]
            ),
            
            AnalysisLevel.PREMIUM: AnalysisConfig(
                level=AnalysisLevel.PREMIUM,
                price_usd=settings.premium_price_usd,
                ai_services=["claude", "openai", "gemini", "cohere", "huggingface"],
                scientific_search=True,
                max_sources=50,
                cache_enabled=False,  # Всегда свежий анализ
                estimated_tokens=25000,
                estimated_time_minutes=8,
                features=[
                    "Максимальный анализ (5 AI систем)",
                    "Полный научный поиск (50+ источников)",
                    "Мультимодальный анализ",
                    "Нейропсихологический профиль",
                    "Персонализированные интервенции",
                    "Экспертная валидация",
                    "VIP обработка без очереди",
                    "Приватная консультация",
                    "Экспорт в PDF"
                ]
            )
        }
    
    async def estimate_analysis_cost(
        self, 
        level: AnalysisLevel, 
        text: str,
        user_id: int
    ) -> CostEstimate:
        """
        Оценка стоимости анализа для конкретного уровня
        
        Args:
            level: Уровень анализа
            text: Текст для анализа
            user_id: ID пользователя
            
        Returns:
            Детальная оценка стоимости
        """
        try:
            config = self.analysis_configs[level]
            
            # Базовая стоимость уровня
            base_cost = config.price_usd
            
            # Оценка токенов на основе длины текста
            estimated_tokens = self._estimate_tokens(text, config)
            
            # Проверка кэша для снижения стоимости
            cache_hit_probability = await self._calculate_cache_hit_probability(
                text, level, user_id
            )
            
            # Итоговая стоимость с учетом кэша
            final_cost = base_cost * (1 - cache_hit_probability * 0.7)  # 70% скидка за кэш
            
            return CostEstimate(
                level=level,
                estimated_cost_usd=round(final_cost, 2),
                estimated_tokens=estimated_tokens,
                ai_services_count=len(config.ai_services),
                cache_hit_probability=cache_hit_probability,
                estimated_time_minutes=config.estimated_time_minutes
            )
            
        except Exception as e:
            logger.error("❌ Ошибка оценки стоимости", 
                        level=level.value, 
                        error=str(e), 
                        exc_info=True)
            # Возвращаем максимальную оценку в случае ошибки
            return CostEstimate(
                level=level,
                estimated_cost_usd=config.price_usd,
                estimated_tokens=config.estimated_tokens,
                ai_services_count=len(config.ai_services),
                cache_hit_probability=0.0,
                estimated_time_minutes=config.estimated_time_minutes
            )
    
    def _estimate_tokens(self, text: str, config: AnalysisConfig) -> int:
        """Оценка количества токенов для анализа"""
        # Примерная формула: 1 токен ≈ 0.75 слов
        word_count = len(text.split())
        input_tokens = word_count // 0.75
        
        # Умножаем на количество AI сервисов
        total_input_tokens = input_tokens * len(config.ai_services)
        
        # Добавляем выходные токены (обычно 20-40% от входных)
        output_tokens = total_input_tokens * 0.3
        
        return int(total_input_tokens + output_tokens)
    
    async def _calculate_cache_hit_probability(
        self, 
        text: str, 
        level: AnalysisLevel, 
        user_id: int
    ) -> float:
        """Рассчитывает вероятность попадания в кэш"""
        try:
            # Создаем хэш от текста для проверки кэша
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Для научных уровней проверяем кэш научного поиска
            if level in [AnalysisLevel.RESEARCH, AnalysisLevel.PREMIUM]:
                # Научный кэш живет 7 дней
                return 0.3  # 30% вероятность попадания
            
            # Для обычных анализов - проверяем недавние анализы пользователя
            async with get_async_session() as session:
                # Тут бы проверить Redis кэш, но пока симулируем
                recent_analyses_count = 5  # Мок
                
                if recent_analyses_count > 0:
                    return min(0.6, recent_analyses_count * 0.1)  # Максимум 60%
                
                return 0.0
                
        except Exception as e:
            logger.error("❌ Ошибка расчета кэша", error=str(e))
            return 0.0
    
    async def check_user_limits(self, user_id: int, level: AnalysisLevel) -> Tuple[bool, str]:
        """
        Проверка лимитов пользователя
        
        Returns:
            (allowed: bool, reason: str)
        """
        try:
            async with get_async_session() as session:
                # Проверяем дневные лимиты для бесплатного уровня
                if level == AnalysisLevel.FREE:
                    # Подсчитываем анализы сегодня
                    today_analyses = 2  # Мок - в реальности запрос к БД
                    
                    if today_analyses >= self.daily_limits[level]:
                        return False, f"Превышен дневной лимит бесплатных анализов ({self.daily_limits[level]})"
                
                # Проверяем общие дневные расходы
                daily_cost = 45.0  # Мок - в реальности сумма из ApiUsage
                
                if daily_cost >= settings.daily_cost_limit_usd:
                    return False, f"Превышен дневной лимит расходов (${settings.daily_cost_limit_usd})"
                
                return True, "OK"
                
        except Exception as e:
            logger.error("❌ Ошибка проверки лимитов", 
                        user_id=user_id, 
                        level=level.value, 
                        error=str(e))
            return False, "Техническая ошибка при проверке лимитов"
    
    def get_level_comparison(self) -> Dict[str, Any]:
        """Возвращает сравнение всех уровней анализа"""
        comparison = {}
        
        for level, config in self.analysis_configs.items():
            comparison[level.value] = {
                "name": self._get_level_name(level),
                "price_usd": config.price_usd,
                "ai_services": config.ai_services,
                "scientific_search": config.scientific_search,
                "max_sources": config.max_sources,
                "estimated_time_minutes": config.estimated_time_minutes,
                "features": config.features,
                "emoji": self._get_level_emoji(level)
            }
        
        return comparison
    
    def _get_level_name(self, level: AnalysisLevel) -> str:
        """Возвращает человекочитаемое название уровня"""
        names = {
            AnalysisLevel.FREE: "Базовый",
            AnalysisLevel.BASIC: "Стандартный", 
            AnalysisLevel.ADVANCED: "Продвинутый",
            AnalysisLevel.RESEARCH: "Научный",
            AnalysisLevel.PREMIUM: "Максимальный"
        }
        return names.get(level, level.value)
    
    def _get_level_emoji(self, level: AnalysisLevel) -> str:
        """Возвращает эмодзи для уровня"""
        emojis = {
            AnalysisLevel.FREE: "🆓",
            AnalysisLevel.BASIC: "⭐",
            AnalysisLevel.ADVANCED: "🚀", 
            AnalysisLevel.RESEARCH: "🔬",
            AnalysisLevel.PREMIUM: "💎"
        }
        return emojis.get(level, "📊")
    
    async def perform_analysis(
        self, 
        text: str, 
        user_id: int, 
        level: AnalysisLevel,
        telegram_id: int = None
    ) -> str:
        """
        🚀 ОСНОВНОЙ МЕТОД ЭКОНОМИЧЕСКОГО АНАЛИЗА
        
        Выполняет полный цикл экономического анализа:
        1. Проверка лимитов пользователя
        2. Оценка стоимости
        3. Проверка кэша
        4. Выполнение анализа
        5. Логирование стоимости
        """
        start_time = time.time()
        
        try:
            logger.info("🚀 Начало экономического анализа",
                       user_id=user_id,
                       level=level.value,
                       text_length=len(text))
            
            # 1. ПРОВЕРКА ЛИМИТОВ
            allowed, reason = await self.check_user_limits(user_id, level)
            if not allowed:
                return f"❌ **Анализ недоступен**\n\n{reason}\n\n" \
                       f"• `/pricing` - Тарифные планы\n" \
                       f"• `/help` - Справка"
            
            # 2. ОЦЕНКА СТОИМОСТИ
            cost_estimate = await self.estimate_analysis_cost(level, text, user_id)
            
            # 3. ПРОВЕРКА КЭША (если включен)
            config = self.analysis_configs[level]
            cache_result = None
            
            if config.cache_enabled:
                from src.utils.cache_manager import cache_manager
                cache_result = await cache_manager.get_analysis_result(
                    text=text, 
                    level=level.value,
                    user_id=user_id
                )
            
            # 4. ВЫПОЛНЕНИЕ АНАЛИЗА
            if cache_result:
                # ✅ Результат из кэша
                analysis_result = cache_result
                actual_cost = 0.0  # Кэш = бесплатно
                tokens_used = 0
                
                logger.info("💰 Результат получен из кэша (экономия 100%)",
                           user_id=user_id,
                           level=level.value)
            else:
                # 🔄 Новый анализ
                from src.ai.analysis_engine import analysis_engine
                
                analysis_result = await analysis_engine.economic_analysis(
                    text=text,
                    level=level,
                    user_id=user_id,
                    telegram_id=telegram_id or user_id
                )
                
                actual_cost = cost_estimate.estimated_cost_usd
                tokens_used = cost_estimate.estimated_tokens
                
                # Сохранение в кэш
                if config.cache_enabled:
                    await cache_manager.cache_analysis_result(
                        text=text,
                        level=level.value,
                        result=analysis_result,
                        user_id=user_id
                    )
            
            # 5. ЛОГИРОВАНИЕ СТОИМОСТИ
            await self.log_analysis_cost(
                user_id=user_id,
                level=level,
                actual_cost_usd=actual_cost,
                tokens_used=tokens_used,
                ai_services_used=config.ai_services
            )
            
            # 6. ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ
            execution_time = round(time.time() - start_time, 1)
            
            # Добавляем информацию об анализе
            footer = f"\n\n" \
                    f"📊 **Информация об анализе:**\n" \
                    f"🎯 Уровень: {self._get_level_name(level)} {self._get_level_emoji(level)}\n" \
                    f"💰 Стоимость: ${actual_cost:.2f} {'(кэш)' if cache_result else ''}\n" \
                    f"⏱️ Время: {execution_time}с\n" \
                    f"🤖 AI сервисы: {', '.join(config.ai_services)}\n" \
                    f"🔬 Научный поиск: {'✅' if config.scientific_search else '❌'}\n\n" \
                    f"💡 Апгрейд: `/pricing` | Статистика: `/cache`"
            
            logger.info("✅ Экономический анализ завершен",
                       user_id=user_id,
                       level=level.value,
                       cost_usd=actual_cost,
                       execution_time=execution_time,
                       from_cache=bool(cache_result))
            
            return analysis_result + footer
            
        except Exception as e:
            execution_time = round(time.time() - start_time, 1)
            logger.error("❌ Ошибка экономического анализа",
                        user_id=user_id,
                        level=level.value,
                        error=str(e),
                        execution_time=execution_time,
                        exc_info=True)
            
            return f"❌ **Ошибка анализа**\n\n" \
                   f"Произошла техническая ошибка: {str(e)[:100]}...\n\n" \
                   f"• Попробуйте позже\n" \
                   f"• `/help` - Справка\n" \
                   f"• `/pricing` - Другие уровни"

    async def log_analysis_cost(
        self, 
        user_id: int, 
        level: AnalysisLevel,
        actual_cost_usd: float,
        tokens_used: int,
        ai_services_used: List[str]
    ) -> None:
        """Логирование фактической стоимости анализа"""
        try:
            async with get_async_session() as session:
                # Создаем запись об использовании API
                api_usage = ApiUsage(
                    user_id=user_id,
                    service_name=f"analysis_{level.value}",
                    requests_count=1,
                    tokens_used=tokens_used,
                    cost_usd=actual_cost_usd
                )
                session.add(api_usage)
                await session.commit()
                
                logger.info("💰 Зафиксирована стоимость анализа",
                           user_id=user_id,
                           level=level.value,
                           cost_usd=actual_cost_usd,
                           tokens_used=tokens_used,
                           ai_services=ai_services_used)
                
        except Exception as e:
            logger.error("❌ Ошибка логирования стоимости", 
                        error=str(e), 
                        exc_info=True)


# Глобальный экземпляр менеджера
economic_manager = EconomicAnalysisManager() 