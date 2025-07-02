"""
📦 ПРОФЕССИОНАЛЬНЫЙ КЭШИРУЮЩИЙ МЕНЕДЖЕР
Система интеллектуального кэширования для экономии на AI запросах
"""
import asyncio
import structlog
import hashlib
import json
import redis.asyncio as redis
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from src.config.settings import settings

logger = structlog.get_logger()


@dataclass
class CacheEntry:
    """Запись в кэше"""
    key: str
    data: Any
    timestamp: datetime
    ttl_hours: int
    access_count: int
    cost_saved_usd: float


class IntelligentCacheManager:
    """Интеллектуальный менеджер кэширования для экономии средств"""
    
    def __init__(self):
        """Инициализация кэш-менеджера"""
        self.redis_client: Optional[redis.Redis] = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "savings_usd": 0.0,
            "entries_count": 0
        }
        
        # Конфигурация кэширования по типам
        self.cache_configs = {
            "analysis_basic": {
                "ttl_hours": settings.analysis_cache_ttl_hours,
                "prefix": "analysis:basic:",
                "cost_per_miss": 1.99
            },
            "analysis_advanced": {
                "ttl_hours": settings.analysis_cache_ttl_hours,
                "prefix": "analysis:advanced:",
                "cost_per_miss": 4.99
            },
            "scientific_research": {
                "ttl_hours": settings.scientific_cache_ttl_hours,
                "prefix": "research:scientific:",
                "cost_per_miss": 9.99
            },
            "ai_response": {
                "ttl_hours": 6,  # AI ответы кэшируем на 6 часов
                "prefix": "ai:response:",
                "cost_per_miss": 0.50
            },
            "user_profile": {
                "ttl_hours": 24,
                "prefix": "user:profile:",
                "cost_per_miss": 0.0
            }
        }
        
        logger.info("📦 IntelligentCacheManager инициализирован",
                   cache_types=len(self.cache_configs),
                   default_ttl_hours=settings.analysis_cache_ttl_hours)
    
    async def initialize(self) -> None:
        """Инициализация подключения к Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
            
            # Проверяем подключение
            await self.redis_client.ping()
            logger.info("✅ Подключение к Redis установлено", 
                       redis_url=settings.redis_url[:20] + "...")
            
        except Exception as e:
            logger.error("❌ Ошибка подключения к Redis", 
                        error=str(e), 
                        exc_info=True)
            self.redis_client = None
    
    def _generate_cache_key(
        self, 
        cache_type: str, 
        identifier: str,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Генерация умного ключа кэша"""
        config = self.cache_configs.get(cache_type, {"prefix": f"{cache_type}:"})
        
        # Базовый ключ
        base_key = f"{config['prefix']}{identifier}"
        
        # Добавляем дополнительные параметры в хэш
        if extra_params:
            params_str = json.dumps(extra_params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            base_key += f":{params_hash}"
        
        return base_key
    
    def _generate_content_hash(self, content: Union[str, Dict[str, Any]]) -> str:
        """Генерация хэша контента для семантического кэширования"""
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    async def get_cached_analysis(
        self, 
        text: str, 
        analysis_level: str,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получение кэшированного анализа по тексту
        
        Args:
            text: Текст для анализа
            analysis_level: Уровень анализа (basic, advanced, research)
            user_id: ID пользователя (опционально)
            
        Returns:
            Кэшированный результат или None
        """
        if not self.redis_client:
            return None
        
        try:
            # Генерируем хэш контента
            content_hash = self._generate_content_hash(text)
            
            # Формируем ключ кэша
            cache_key = self._generate_cache_key(
                f"analysis_{analysis_level}",
                content_hash,
                {"user_id": user_id} if user_id else None
            )
            
            # Получаем данные из Redis
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                result = json.loads(cached_data)
                
                # Обновляем статистику
                self.cache_stats["hits"] += 1
                cost_saved = self.cache_configs.get(
                    f"analysis_{analysis_level}", 
                    {"cost_per_miss": 1.0}
                )["cost_per_miss"]
                self.cache_stats["savings_usd"] += cost_saved
                
                # Обновляем счетчик доступа
                await self._increment_access_count(cache_key)
                
                logger.info("🎯 Кэш попадание",
                           cache_key=cache_key[:50] + "...",
                           analysis_level=analysis_level,
                           cost_saved_usd=cost_saved)
                
                return result
            else:
                self.cache_stats["misses"] += 1
                logger.debug("❌ Кэш промах", 
                           cache_key=cache_key[:50] + "...",
                           analysis_level=analysis_level)
                return None
                
        except Exception as e:
            logger.error("❌ Ошибка получения из кэша", 
                        analysis_level=analysis_level,
                        error=str(e), 
                        exc_info=True)
            return None
    
    async def cache_analysis_result(
        self, 
        text: str,
        level: str,
        result: str,
        user_id: Optional[int] = None,
        custom_ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Кэширование результата анализа (строка)
        
        Args:
            text: Исходный текст
            level: Уровень анализа
            result: Результат для кэширования (строка)
            user_id: ID пользователя
            custom_ttl_hours: Кастомное время жизни кэша
            
        Returns:
            True если успешно закэшировано
        """
        if not self.redis_client:
            return False
        
        try:
            # Генерируем хэш контента
            content_hash = self._generate_content_hash(text)
            
            # Формируем ключ кэша
            cache_key = self._generate_cache_key(
                f"analysis_{level}",
                content_hash,
                {"user_id": user_id} if user_id else None
            )
            
            # Определяем TTL
            cache_config = self.cache_configs.get(f"analysis_{level}")
            ttl_hours = custom_ttl_hours or (cache_config["ttl_hours"] if cache_config else 24)
            ttl_seconds = ttl_hours * 3600
            
            # Добавляем метаданные к результату
            cached_result = {
                "data": result,  # Строка с результатом
                "metadata": {
                    "cached_at": datetime.utcnow().isoformat(),
                    "analysis_level": level,
                    "content_hash": content_hash,
                    "user_id": user_id,
                    "ttl_hours": ttl_hours
                }
            }
            
            # Сохраняем в Redis
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cached_result)
            )
            
            self.cache_stats["entries_count"] += 1
            
            logger.info("💾 Результат закэширован",
                       cache_key=cache_key[:50] + "...",
                       analysis_level=level,
                       ttl_hours=ttl_hours)
            
            return True
            
        except Exception as e:
            logger.error("❌ Ошибка кэширования результата",
                        analysis_level=level,
                        error=str(e), 
                        exc_info=True)
            return False
    
    async def get_analysis_result(
        self, 
        text: str, 
        level: str,
        user_id: Optional[int] = None
    ) -> Optional[str]:
        """
        АЛИАС для get_cached_analysis с возвратом только результата анализа
        
        Args:
            text: Исходный текст для анализа
            level: Уровень анализа
            user_id: ID пользователя
            
        Returns:
            Строка с результатом анализа или None если не найден
        """
        cached_analysis = await self.get_cached_analysis(text, level, user_id)
        
        if cached_analysis and "data" in cached_analysis:
            # Извлекаем результат анализа из кэшированных данных
            analysis_data = cached_analysis["data"]
            
            # Если это строка - возвращаем как есть
            if isinstance(analysis_data, str):
                return analysis_data
            
            # Если это словарь - ищем поле с результатом
            if isinstance(analysis_data, dict):
                # Пробуем разные возможные ключи
                for key in ["result", "analysis", "text", "content", "output"]:
                    if key in analysis_data:
                        return str(analysis_data[key])
                
                # Если не нашли - конвертируем весь словарь в строку
                return str(analysis_data)
        
        return None
    
    async def get_cached_scientific_research(
        self, 
        query_terms: List[str],
        max_sources: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Получение кэшированного научного исследования"""
        if not self.redis_client:
            return None
        
        try:
            # Создаем хэш от поисковых терминов
            query_hash = self._generate_content_hash({
                "terms": sorted(query_terms),
                "max_sources": max_sources
            })
            
            cache_key = self._generate_cache_key("scientific_research", query_hash)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                result = json.loads(cached_data)
                self.cache_stats["hits"] += 1
                self.cache_stats["savings_usd"] += 9.99  # Экономия на научном поиске
                
                logger.info("🎯 Научный кэш попадание",
                           query_terms=query_terms,
                           cost_saved_usd=9.99)
                
                return result["data"]
            
            return None
            
        except Exception as e:
            logger.error("❌ Ошибка получения научного кэша", error=str(e))
            return None
    
    async def cache_scientific_research(
        self, 
        query_terms: List[str],
        research_result: Dict[str, Any],
        max_sources: int = 30
    ) -> bool:
        """Кэширование результата научного исследования"""
        if not self.redis_client:
            return False
        
        try:
            query_hash = self._generate_content_hash({
                "terms": sorted(query_terms),
                "max_sources": max_sources
            })
            
            cache_key = self._generate_cache_key("scientific_research", query_hash)
            ttl_seconds = settings.scientific_cache_ttl_hours * 3600
            
            cached_result = {
                "data": research_result,
                "metadata": {
                    "cached_at": datetime.utcnow().isoformat(),
                    "query_terms": query_terms,
                    "max_sources": max_sources,
                    "sources_found": len(research_result.get("sources", []))
                }
            }
            
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cached_result)
            )
            
            logger.info("💾 Научное исследование закэшировано",
                       query_terms=query_terms,
                       sources_count=len(research_result.get("sources", [])),
                       ttl_hours=settings.scientific_cache_ttl_hours)
            
            return True
            
        except Exception as e:
            logger.error("❌ Ошибка кэширования научного исследования", error=str(e))
            return False
    
    async def _increment_access_count(self, cache_key: str) -> None:
        """Увеличение счетчика доступа к кэш-записи"""
        try:
            access_key = f"access_count:{cache_key}"
            await self.redis_client.incr(access_key)
            # Устанавливаем TTL для счетчика доступа
            await self.redis_client.expire(access_key, 7 * 24 * 3600)  # 7 дней
        except Exception as e:
            logger.warning("⚠️ Ошибка обновления счетчика доступа", error=str(e))
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Получение статистики кэширования"""
        if not self.redis_client:
            return {"status": "Redis недоступен"}
        
        try:
            # Общая статистика Redis
            redis_info = await self.redis_client.info("memory")
            
            # Подсчет записей по типам
            type_stats = {}
            for cache_type, config in self.cache_configs.items():
                pattern = f"{config['prefix']}*"
                keys = await self.redis_client.keys(pattern)
                type_stats[cache_type] = len(keys)
            
            hit_rate = (
                self.cache_stats["hits"] / 
                (self.cache_stats["hits"] + self.cache_stats["misses"])
                if (self.cache_stats["hits"] + self.cache_stats["misses"]) > 0 
                else 0
            )
            
            return {
                "hit_rate": round(hit_rate, 3),
                "total_hits": self.cache_stats["hits"],
                "total_misses": self.cache_stats["misses"],
                "total_savings_usd": round(self.cache_stats["savings_usd"], 2),
                "entries_by_type": type_stats,
                "redis_memory_used": redis_info.get("used_memory_human", "N/A"),
                "cache_efficiency": "Высокая" if hit_rate > 0.7 else "Средняя" if hit_rate > 0.4 else "Низкая"
            }
            
        except Exception as e:
            logger.error("❌ Ошибка получения статистики кэша", error=str(e))
            return {"error": str(e)}
    
    async def clear_cache_by_pattern(self, pattern: str) -> int:
        """Очистка кэша по паттерну"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted_count = await self.redis_client.delete(*keys)
                logger.info("🗑️ Кэш очищен", 
                           pattern=pattern, 
                           deleted_keys=deleted_count)
                return deleted_count
            return 0
            
        except Exception as e:
            logger.error("❌ Ошибка очистки кэша", pattern=pattern, error=str(e))
            return 0
    
    async def warm_up_cache(self, popular_queries: List[str]) -> None:
        """Предварительный прогрев кэша популярными запросами"""
        logger.info("🔥 Начинаю прогрев кэша", queries_count=len(popular_queries))
        
        for query in popular_queries:
            # Тут можно было бы запустить анализ популярных запросов
            # Но пока просто логируем
            logger.debug("🔥 Прогрев кэша для запроса", query=query[:50] + "...")
    
    async def close(self) -> None:
        """Закрытие подключения к Redis"""
        if self.redis_client:
            await self.redis_client.aclose()
            logger.info("📦 Подключение к Redis закрыто")


# Глобальный экземпляр кэш-менеджера
cache_manager = IntelligentCacheManager() 