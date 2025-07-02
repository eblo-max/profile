#!/usr/bin/env python3
"""
Тест Claude анализа для отладки проблемы "Использовано AI моделей: 0"
"""
import asyncio
import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.scientific_research_engine import PersonData
from src.ai.multi_ai_research_analyzer import MultiAIResearchAnalyzer, AIAnalysisResult
from src.config.settings import settings

async def test_claude_direct():
    """Прямой тест Claude API"""
    print("🧪 Тест Claude анализа")
    
    # Создаем тестовые данные
    person_data = PersonData(
        name="Алексей",
        age=28,
        occupation="IT-разработчик",
        behavior_description="Организованный, аналитический, интроверт",
        country="Russia"
    )
    
    # Создаем фиктивные источники для тестирования
    from src.ai.scientific_research_engine import ScientificSource
    
    test_sources = [
        ScientificSource(
            title="Personality Traits in Software Developers",
            authors=["Smith J.", "Doe A."],
            publication="Journal of Applied Psychology",
            year=2024,
            abstract="This study examines personality traits common among software developers...",
            quality_score=85.0,
            source_type="academic"
        )
    ]
    
    print(f"📊 Тестовые данные:")
    print(f"   Человек: {person_data.name}, {person_data.age}, {person_data.occupation}")
    print(f"   Источники: {len(test_sources)}")
    
    # Инициализируем анализатор
    analyzer = MultiAIResearchAnalyzer(settings)
    
    print(f"\n🔑 Проверка клиента:")
    print(f"   Claude клиент: {'✅ Есть' if analyzer.claude_client else '❌ Нет'}")
    
    if not analyzer.claude_client:
        print("❌ Claude клиент не инициализирован - проверьте ANTHROPIC_API_KEY")
        return
    
    try:
        print("\n🚀 Запускаю Claude анализ...")
        
        # Тестируем прямой вызов Claude анализа
        result = await analyzer._claude_general_analysis(person_data, test_sources)
        
        print(f"✅ Claude анализ завершен!")
        print(f"   Модель: {result.ai_model}")
        print(f"   Тип: {result.analysis_type}")
        print(f"   Уверенность: {result.confidence_score}")
        print(f"   Статус: {'✅ Успех' if result.findings.get('status') != 'failed' else '❌ Ошибка'}")
        
        if result.findings.get('status') == 'failed':
            print(f"   Ошибка: {result.findings.get('error', 'Unknown error')}")
        else:
            print(f"   Ключи результата: {list(result.findings.keys())[:5]}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка Claude анализа: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_comprehensive_analysis():
    """Тест полного мультимодального анализа"""
    print("\n🧪 Тест комплексного анализа")
    
    person_data = PersonData(
        name="Алексей",
        age=28,
        occupation="IT-разработчик",
        behavior_description="Организованный, аналитический, интроверт",
        country="Russia"
    )
    
    from src.ai.scientific_research_engine import ScientificSource
    test_sources = [
        ScientificSource(
            title="IT Professional Personality Research",
            authors=["Research Team"],
            publication="Tech Psychology Journal",
            year=2024,
            abstract="Research on IT professional personality traits...",
            quality_score=75.0,
            source_type="academic"
        )
    ]
    
    analyzer = MultiAIResearchAnalyzer(settings)
    
    try:
        print("🚀 Запускаю комплексный анализ...")
        
        result = await analyzer.comprehensive_research_analysis(person_data, test_sources)
        
        print(f"✅ Комплексный анализ завершен!")
        print(f"   AI моделей использовано: {result['analysis_metadata']['total_ai_models']}")
        print(f"   Источников: {result['analysis_metadata']['research_sources_used']}")
        print(f"   Индивидуальных анализов: {len(result['individual_analyses'])}")
        
        # Проверяем наличие профиля
        if result.get('comprehensive_profile'):
            profile_length = len(result['comprehensive_profile'])
            print(f"   Профиль создан: {profile_length} символов")
            print(f"   Начало профиля: {result['comprehensive_profile'][:100]}...")
        else:
            print(f"   ❌ Профиль не создан")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка комплексного анализа: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Главная функция тестирования"""
    print("🚀 Тест Claude AI анализа\n")
    
    # Тест 1: Прямой Claude анализ
    claude_result = await test_claude_direct()
    
    # Тест 2: Комплексный анализ (как в боте)
    comprehensive_result = await test_comprehensive_analysis()
    
    print("\n🔍 ИТОГОВЫЙ АНАЛИЗ:")
    
    if claude_result and claude_result.findings.get('status') != 'failed':
        print("✅ Claude анализ работает")
    else:
        print("❌ Проблема с Claude анализом")
    
    if comprehensive_result and comprehensive_result['analysis_metadata']['total_ai_models'] > 0:
        print("✅ Комплексный анализ работает")
    else:
        print("❌ Проблема с комплексным анализом")

if __name__ == "__main__":
    asyncio.run(main()) 