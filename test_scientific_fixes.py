#!/usr/bin/env python3
"""
Тест исправлений научной системы
"""
import asyncio
import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.scientific_research_engine import PersonData, ScientificResearchEngine
from src.ai.multi_ai_research_analyzer import MultiAIResearchAnalyzer
from src.config.settings import settings

async def test_person_data_parsing():
    """Тест парсинга данных об IT-разработчике"""
    print("🧪 Тест 1: Парсинг данных об IT-разработчике")
    
    test_text = """
    Имя: Алексей
    Возраст: 28 лет
    Профессия: IT-разработчик
    Поведение: Очень организованный, любит порядок, предпочитает работать в одиночку. 
    Часто анализирует детали. В общении сдержан, но дружелюбен.
    Тексты: "Мне нравится, когда все по плану. Хаос меня раздражает."
    """
    
    # Импортируем функцию парсинга
    from src.bot.handlers.main_handler import parse_person_data_from_text
    
    parsed_data = parse_person_data_from_text(test_text)
    
    print(f"📊 Результат парсинга:")
    print(f"   Имя: {parsed_data['name']}")
    print(f"   Возраст: {parsed_data['age']}")
    print(f"   Профессия: '{parsed_data['occupation']}'")
    print(f"   Эмоциональные маркеры: {parsed_data['emotional_markers']}")
    print(f"   Социальные паттерны: {parsed_data['social_patterns']}")
    
    # Создаем PersonData объект
    person_data = PersonData(
        name=parsed_data.get("name", "Неизвестно"),
        age=parsed_data.get("age"),
        occupation=parsed_data.get("occupation", ""),
        behavior_description=parsed_data.get("behavior_description", ""),
        text_samples=parsed_data.get("text_samples", []),
        emotional_markers=parsed_data.get("emotional_markers", []),
        social_patterns=parsed_data.get("social_patterns", []),
        cognitive_traits=parsed_data.get("cognitive_traits", []),
        country="Russia"
    )
    
    print(f"✅ PersonData создан: {person_data.name}, {person_data.age}, '{person_data.occupation}'")
    return person_data

async def test_query_generation(person_data: PersonData):
    """Тест генерации поисковых запросов"""
    print("\n🧪 Тест 2: Генерация поисковых запросов")
    
    engine = ScientificResearchEngine(settings)
    queries = await engine._generate_smart_queries(person_data)
    
    print(f"📊 Сгенерировано {len(queries)} запросов:")
    for i, query in enumerate(queries[:10], 1):  # Показываем первые 10
        print(f"   {i}. {query}")
    
    # Проверяем наличие IT-специфичных запросов
    it_queries = [q for q in queries if any(term in q.lower() for term in ['it', 'software', 'developer', 'programmer'])]
    print(f"🔍 IT-специфичных запросов: {len(it_queries)}")
    for q in it_queries[:3]:
        print(f"   • {q}")
    
    return queries

async def test_ai_clients():
    """Тест инициализации AI клиентов"""
    print("\n🧪 Тест 3: Проверка AI клиентов")
    
    analyzer = MultiAIResearchAnalyzer(settings)
    
    print(f"📊 Статус AI клиентов:")
    print(f"   Claude: {'✅' if analyzer.claude_client else '❌'}")
    print(f"   OpenAI: {'✅' if analyzer.openai_client else '❌'}")
    print(f"   Gemini: {'✅' if analyzer.gemini_client else '❌'}")
    print(f"   Cohere: {'✅' if analyzer.cohere_client else '❌'}")
    
    # Проверяем API ключи
    print(f"\n🔑 API ключи:")
    print(f"   ANTHROPIC_API_KEY: {'✅' if settings.anthropic_api_key else '❌'}")
    print(f"   OPENAI_API_KEY: {'✅' if hasattr(settings, 'openai_api_key') and settings.openai_api_key else '❌'}")
    print(f"   SERPAPI_API_KEY: {'✅' if hasattr(settings, 'serpapi_api_key') and settings.serpapi_api_key else '❌'}")

async def test_pubmed_parsing():
    """Тест парсинга PubMed"""
    print("\n🧪 Тест 4: PubMed XML парсинг")
    
    # Создаем простой XML для тестирования
    test_xml = '''<?xml version="1.0" ?>
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <Article>
                    <ArticleTitle>Personality Psychology in Software Development</ArticleTitle>
                    <AuthorList>
                        <Author>
                            <LastName>Smith</LastName>
                            <ForeName>John</ForeName>
                        </Author>
                        <Author>
                            <LastName>Doe</LastName>
                            <ForeName>Jane</ForeName>
                        </Author>
                    </AuthorList>
                    <Journal>
                        <Title>Journal of Applied Psychology</Title>
                    </Journal>
                    <Abstract>
                        <AbstractText>This study examines personality traits in software developers...</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
            <PubmedData>
                <History>
                    <PubMedPubDate PubStatus="pubmed">
                        <Year>2024</Year>
                    </PubMedPubDate>
                </History>
                <ArticleIdList>
                    <ArticleId IdType="pubmed">12345678</ArticleId>
                </ArticleIdList>
            </PubmedData>
        </PubmedArticle>
    </PubmedArticleSet>'''
    
    from src.ai.scientific_research_engine import PubMedResearcher
    
    researcher = PubMedResearcher(settings)
    sources = researcher._parse_pubmed_xml(test_xml)
    
    print(f"📊 Парсинг результат:")
    if sources:
        source = sources[0]
        print(f"   Заголовок: {source.title}")
        print(f"   Авторы: {source.authors}")
        print(f"   Журнал: {source.publication}")
        print(f"   Год: {source.year}")
        print(f"   PMID: {source.pmid}")
        print(f"   ✅ Парсинг работает!")
    else:
        print(f"   ❌ Парсинг не вернул результатов")

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов исправлений научной системы\n")
    
    try:
        # Тест 1: Парсинг PersonData
        person_data = await test_person_data_parsing()
        
        # Тест 2: Генерация запросов
        queries = await test_query_generation(person_data)
        
        # Тест 3: AI клиенты
        await test_ai_clients()
        
        # Тест 4: PubMed парсинг
        await test_pubmed_parsing()
        
        print("\n✅ Все тесты завершены!")
        
        # Проверяем критические проблемы
        print("\n🔍 АНАЛИЗ ПРОБЛЕМ:")
        
        if person_data.occupation and 'it' in person_data.occupation.lower():
            print("✅ IT-профессия корректно извлечена")
        else:
            print("❌ Проблема с извлечением IT-профессии")
            
        it_queries = [q for q in queries if 'software' in q.lower() or 'developer' in q.lower()]
        if it_queries:
            print("✅ IT-специфичные запросы генерируются")
        else:
            print("❌ Проблема с генерацией IT-запросов")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 