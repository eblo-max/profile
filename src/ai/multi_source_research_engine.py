#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Мульти-источниковая поисковая система для научных исследований
Интеграция с реальными API академических баз данных
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from ..config.settings import settings
except ImportError:
    from src.config.settings import settings

from .academic_api_implementations import (
    MultiSourceSearchEngine,
    ResearchPaper,
    search_academic_papers
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """Структура поискового запроса"""
    text: str
    language: str = "ru"
    max_results: int = 50
    sources: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    document_types: Optional[List[str]] = None
    open_access_only: bool = False
    sort_by: str = "relevance"  # relevance, date, citations

@dataclass
class SearchResult:
    """Результат поиска"""
    query: SearchQuery
    papers: List[ResearchPaper]
    total_found: int
    sources_used: List[str]
    search_time: float
    errors: List[str] = None

class EnhancedMultiSourceEngine:
    """Улучшенная мульти-источниковая поисковая система"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or settings.get_api_config_dict()
        self.engine = MultiSourceSearchEngine(self.config)
        self.cache = {}  # Простой кэш в памяти
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "cached_searches": 0,
            "source_usage": {}
        }
    
    async def search(self, query: SearchQuery) -> SearchResult:
        """Основной метод поиска"""
        start_time = time.time()
        self.search_stats["total_searches"] += 1
        
        errors = []
        papers = []
        sources_used = []
        
        try:
            # Выполнение поиска
            results = await self.engine.search_all_sources(
                query.text, 
                max_results_per_source=max(query.max_results // 5, 5)
            )
            
            # Обработка результатов
            for source, source_papers in results.items():
                if source_papers:
                    sources_used.append(source)
                    papers.extend(source_papers)
                    
                    # Обновление статистики
                    if source not in self.search_stats["source_usage"]:
                        self.search_stats["source_usage"][source] = 0
                    self.search_stats["source_usage"][source] += len(source_papers)
            
            # Ограничение количества результатов
            papers = papers[:query.max_results]
            
            search_time = time.time() - start_time
            
            result = SearchResult(
                query=query,
                papers=papers,
                total_found=len(papers),
                sources_used=sources_used,
                search_time=search_time,
                errors=errors if errors else None
            )
            
            self.search_stats["successful_searches"] += 1
            logger.info(f"Поиск завершен: найдено {len(papers)} статей из {len(sources_used)} источников за {search_time:.2f}с")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            errors.append(str(e))
            
            return SearchResult(
                query=query,
                papers=[],
                total_found=0,
                sources_used=[],
                search_time=time.time() - start_time,
                errors=errors
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики поиска"""
        return {
            "search_stats": self.search_stats.copy(),
            "cache_size": len(self.cache),
            "enabled_sources": settings.get_enabled_sources(),
            "available_sources": list(self.engine.clients.keys())
        }

# Создание глобального экземпляра
research_engine = EnhancedMultiSourceEngine()

# Вспомогательные функции для простого использования
async def search_papers(query_text: str, **kwargs) -> SearchResult:
    """Простой поиск статей"""
    query = SearchQuery(text=query_text, **kwargs)
    return await research_engine.search(query)

async def analyze_research_topic(topic: str, language: str = "ru") -> Dict[str, Any]:
    """Простой анализ темы исследования"""
    query = SearchQuery(text=topic, language=language, max_results=50)
    result = await research_engine.search(query)
    
    return {
        "topic": topic,
        "total_papers": result.total_found,
        "sources_used": result.sources_used,
        "search_time": result.search_time,
        "errors": result.errors
    }

# Экспорт основных компонентов
__all__ = [
    'EnhancedMultiSourceEngine',
    'SearchQuery',
    'SearchResult',
    'ResearchPaper',
    'research_engine',
    'search_papers',
    'analyze_research_topic'
]
