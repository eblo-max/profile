#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт тестирования реальных API интеграций
Проверяет работоспособность всех академических источников
"""

import asyncio
import os
import sys
import time
from typing import Dict, List, Any

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import settings
from src.ai.academic_api_implementations import (
    PubMedAPIClient,
    SemanticScholarAPIClient,
    ArxivAPIClient,
    CrossRefAPIClient,
    OpenAlexAPIClient,
    CoreAPIClient,
    IEEEXploreAPIClient,
    SpringerNatureAPIClient,
    MultiSourceSearchEngine,
    search_academic_papers
)
from src.ai.multi_source_research_engine import (
    research_engine,
    SearchQuery,
    search_papers,
    analyze_research_topic
)

class APITester:
    """Тестер API интеграций"""
    
    def __init__(self):
        self.results = {}
        self.test_query = "machine learning psychology"
        self.config = settings.get_api_config_dict()
    
    async def test_all_apis(self) -> Dict[str, Any]:
        """Тестирование всех API"""
        print("🧪 Начинаем тестирование API интеграций...\n")
        
        # Тестирование отдельных клиентов
        await self._test_individual_clients()
        
        # Тестирование мульти-источникового поиска
        await self._test_multi_source_search()
        
        # Тестирование исследовательского движка
        await self._test_research_engine()
        
        # Вывод результатов
        self._print_summary()
        
        return self.results
    
    async def _test_individual_clients(self):
        """Тестирование отдельных API клиентов"""
        print("🔍 Тестирование отдельных API клиентов:\n")
        
        # Бесплатные API
        await self._test_client("PubMed", PubMedAPIClient(
            email=self.config.get('pubmed_email'),
            api_key=self.config.get('pubmed_api_key')
        ))
        
        await self._test_client("arXiv", ArxivAPIClient())
        
        await self._test_client("CrossRef", CrossRefAPIClient(
            email=self.config.get('crossref_email')
        ))
        
        await self._test_client("OpenAlex", OpenAlexAPIClient(
            email=self.config.get('openalex_email')
        ))
        
        # API с регистрацией
        if self.config.get('semantic_scholar_api_key'):
            await self._test_client("Semantic Scholar", SemanticScholarAPIClient(
                api_key=self.config.get('semantic_scholar_api_key')
            ))
        else:
            print("⚠️  Semantic Scholar: API ключ не настроен (пропускаем)")
            self.results['semantic_scholar'] = {'status': 'skipped', 'reason': 'No API key'}
        
        # Платные API
        if self.config.get('core_api_key'):
            await self._test_client("CORE", CoreAPIClient(
                api_key=self.config.get('core_api_key')
            ))
        else:
            print("⚠️  CORE: API ключ не настроен (пропускаем)")
            self.results['core'] = {'status': 'skipped', 'reason': 'No API key'}
        
        if self.config.get('ieee_api_key'):
            await self._test_client("IEEE Xplore", IEEEXploreAPIClient(
                api_key=self.config.get('ieee_api_key')
            ))
        else:
            print("⚠️  IEEE Xplore: API ключ не настроен (пропускаем)")
            self.results['ieee'] = {'status': 'skipped', 'reason': 'No API key'}
        
        if self.config.get('springer_api_key'):
            await self._test_client("Springer Nature", SpringerNatureAPIClient(
                api_key=self.config.get('springer_api_key')
            ))
        else:
            print("⚠️  Springer Nature: API ключ не настроен (пропускаем)")
            self.results['springer'] = {'status': 'skipped', 'reason': 'No API key'}
    
    async def _test_client(self, name: str, client, max_results: int = 5):
        """Тестирование отдельного клиента"""
        start_time = time.time()
        
        try:
            print(f"📡 Тестирование {name}...", end=" ")
            
            papers = await client.search_papers(self.test_query, max_results)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if papers:
                print(f"✅ Успех! Найдено {len(papers)} статей за {duration:.2f}с")
                
                # Показываем первую статью как пример
                if papers[0].title:
                    print(f"   📄 Пример: {papers[0].title[:80]}{'...' if len(papers[0].title) > 80 else ''}")
                
                self.results[name.lower().replace(' ', '_')] = {
                    'status': 'success',
                    'papers_found': len(papers),
                    'duration': duration,
                    'example_title': papers[0].title if papers else None
                }
            else:
                print(f"⚠️  Нет результатов за {duration:.2f}с")
                self.results[name.lower().replace(' ', '_')] = {
                    'status': 'no_results',
                    'papers_found': 0,
                    'duration': duration
                }
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ Ошибка: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}")
            self.results[name.lower().replace(' ', '_')] = {
                'status': 'error',
                'error': str(e),
                'duration': duration
            }
    
    async def _test_multi_source_search(self):
        """Тестирование мульти-источникового поиска"""
        print(f"\n🔄 Тестирование мульти-источникового поиска:\n")
        
        try:
            start_time = time.time()
            print(f"🔍 Поиск '{self.test_query}' по всем источникам...", end=" ")
            
            papers = await search_academic_papers(
                self.test_query,
                config=self.config,
                max_results_per_source=3
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if papers:
                print(f"✅ Успех! Найдено {len(papers)} уникальных статей за {duration:.2f}с")
                
                # Анализ источников
                sources = {}
                for paper in papers:
                    source = paper.source or 'Unknown'
                    sources[source] = sources.get(source, 0) + 1
                
                print(f"   📊 Источники: {dict(sources)}")
                
                # Примеры статей
                print(f"   📄 Примеры статей:")
                for i, paper in enumerate(papers[:3], 1):
                    print(f"      {i}. {paper.title[:60]}{'...' if len(paper.title) > 60 else ''} ({paper.source})")
                
                self.results['multi_source_search'] = {
                    'status': 'success',
                    'total_papers': len(papers),
                    'duration': duration,
                    'sources_used': list(sources.keys()),
                    'source_distribution': sources
                }
            else:
                print(f"⚠️  Нет результатов за {duration:.2f}с")
                self.results['multi_source_search'] = {
                    'status': 'no_results',
                    'duration': duration
                }
                
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            self.results['multi_source_search'] = {
                'status': 'error',
                'error': str(e)
            }
    
    async def _test_research_engine(self):
        """Тестирование исследовательского движка"""
        print(f"\n🧠 Тестирование исследовательского движка:\n")
        
        try:
            # Тест простого поиска
            start_time = time.time()
            print(f"🔍 Простой поиск через движок...", end=" ")
            
            result = await search_papers(
                self.test_query,
                max_results=10,
                sort_by="relevance"
            )
            
            search_duration = time.time() - start_time
            
            print(f"✅ Найдено {result.total_found} статей из {len(result.sources_used)} источников за {search_duration:.2f}с")
            
            # Тест анализа темы
            start_time = time.time()
            print(f"📊 Анализ темы исследования...", end=" ")
            
            analysis = await analyze_research_topic(self.test_query, language="en")
            
            analysis_duration = time.time() - start_time
            
            print(f"✅ Анализ завершен за {analysis_duration:.2f}с")
            
            # Вывод результатов анализа
            print(f"   📈 Всего статей проанализировано: {analysis.get('total_papers', 0)}")
            print(f"   📚 Ключевые авторы: {len(analysis.get('key_authors', []))}")
            print(f"   📖 Ключевые журналы: {len(analysis.get('key_journals', []))}")
            print(f"   💡 Рекомендаций: {len(analysis.get('recommendations', []))}")
            
            self.results['research_engine'] = {
                'status': 'success',
                'search_results': result.total_found,
                'search_duration': search_duration,
                'analysis_duration': analysis_duration,
                'sources_used': result.sources_used,
                'total_analyzed': analysis.get('total_papers', 0)
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            self.results['research_engine'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def _print_summary(self):
        """Вывод итоговой статистики"""
        print(f"\n" + "="*60)
        print(f"📋 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print(f"="*60)
        
        total_tests = len(self.results)
        successful = sum(1 for r in self.results.values() if r.get('status') == 'success')
        errors = sum(1 for r in self.results.values() if r.get('status') == 'error')
        skipped = sum(1 for r in self.results.values() if r.get('status') == 'skipped')
        no_results = sum(1 for r in self.results.values() if r.get('status') == 'no_results')
        
        print(f"📊 Всего тестов: {total_tests}")
        print(f"✅ Успешных: {successful}")
        print(f"❌ Ошибок: {errors}")
        print(f"⚠️  Пропущено (нет ключей): {skipped}")
        print(f"⚠️  Без результатов: {no_results}")
        
        success_rate = (successful / (total_tests - skipped)) * 100 if (total_tests - skipped) > 0 else 0
        print(f"📈 Успешность: {success_rate:.1f}%")
        
        print(f"\n🔍 ДЕТАЛИ ПО ИСТОЧНИКАМ:")
        for name, result in self.results.items():
            status_emoji = {
                'success': '✅',
                'error': '❌',
                'skipped': '⚠️',
                'no_results': '⚠️'
            }.get(result.get('status'), '❓')
            
            print(f"{status_emoji} {name.replace('_', ' ').title()}: {result.get('status')}")
            
            if result.get('papers_found'):
                print(f"   📄 Найдено статей: {result['papers_found']}")
            
            if result.get('duration'):
                print(f"   ⏱️  Время: {result['duration']:.2f}с")
            
            if result.get('error'):
                print(f"   ❌ Ошибка: {result['error'][:100]}{'...' if len(result['error']) > 100 else ''}")
            
            if result.get('reason'):
                print(f"   ℹ️  Причина: {result['reason']}")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if errors > 0:
            print(f"• Проверьте API ключи для источников с ошибками")
            print(f"• Убедитесь в наличии интернет-соединения")
            print(f"• Проверьте лимиты API")
        
        if skipped > 0:
            print(f"• Настройте API ключи для пропущенных источников")
            print(f"• См. API_KEYS_SETUP_GUIDE.md для инструкций")
        
        if successful >= 4:
            print(f"• ✅ Отличный результат! Система готова к работе")
        elif successful >= 2:
            print(f"• ⚠️  Хороший результат, но можно улучшить")
        else:
            print(f"• ❌ Требуется настройка API ключей")
        
        print(f"\n🔗 Полезные ссылки:")
        print(f"• Руководство по API: API_KEYS_SETUP_GUIDE.md")
        print(f"• Документация: README.md")
        print(f"• Настройки: src/config/settings.py")

async def main():
    """Основная функция тестирования"""
    print("🚀 Тестер API интеграций Psychology AI Bot")
    print("=" * 50)
    
    # Проверка базовой конфигурации
    print(f"📋 Проверка конфигурации:")
    enabled_sources = settings.get_enabled_sources()
    print(f"   Доступные источники: {enabled_sources}")
    
    validation = settings.validate_config()
    if validation['errors']:
        print(f"   ❌ Ошибки конфигурации: {validation['errors']}")
    if validation['warnings']:
        print(f"   ⚠️  Предупреждения: {validation['warnings']}")
    
    print()
    
    # Запуск тестов
    tester = APITester()
    results = await tester.test_all_apis()
    
    # Сохранение результатов
    import json
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в test_results.json")

if __name__ == "__main__":
    # Запуск тестирования
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n⚠️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc() 