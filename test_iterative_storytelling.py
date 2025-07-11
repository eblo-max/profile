#!/usr/bin/env python3
"""
Тест итеративного подхода storytelling
Этап 1: Структурированные данные
Этап 2: Storytelling narrative
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import AIService

async def test_iterative_storytelling():
    """Тест итеративного storytelling подхода"""
    
    print("🚀 ТЕСТ ИТЕРАТИВНОГО STORYTELLING ПОДХОДА")
    print("=" * 60)
    
    # Тестовые данные
    test_answers = [
        {
            "question": "Как ваш партнер реагирует на критику?",
            "answer": "Он очень злится и начинает кричать. Говорит, что я всегда всё делаю не так.",
            "question_id": 1
        },
        {
            "question": "Контролирует ли он ваши финансы?",
            "answer": "Да, он забирает всю зарплату и дает мне только на самое необходимое.",
            "question_id": 2
        },
        {
            "question": "Как он относится к вашим друзьям?",
            "answer": "Он говорит, что они плохо влияют на меня, и я почти не общаюсь с ними.",
            "question_id": 3
        },
        {
            "question": "Извиняется ли он после ссор?",
            "answer": "Никогда. Говорит, что это я виновата во всем.",
            "question_id": 4
        },
        {
            "question": "Проверяет ли он ваш телефон?",
            "answer": "Постоянно. Читает все сообщения и требует объяснений.",
            "question_id": 5
        }
    ]
    
    ai_service = AIService()
    
    try:
        print("🔄 Запускаю итеративный storytelling...")
        print("   Этап 1: Получение структурированных данных")
        print("   Этап 2: Генерация storytelling narrative")
        print()
        
        result = await ai_service.profile_partner_advanced(
            answers=test_answers,
            user_id=999,
            partner_name="Михаил",
            partner_description="Партнер, 32 года",
            technique="storytelling",
            use_cache=False
        )
        
        print("✅ ИТЕРАТИВНЫЙ АНАЛИЗ ЗАВЕРШЕН!")
        print("=" * 60)
        
        # Проверяем метаданные
        print(f"📊 МЕТАДАННЫЕ:")
        print(f"   Метод генерации: {result.get('generation_method', 'unknown')}")
        print(f"   Символов в narrative: {result.get('narrative_length', 0)}")
        print(f"   Слов в narrative: {result.get('narrative_words', 0)}")
        print(f"   Red flags: {len(result.get('red_flags', []))}")
        print(f"   Персональные инсайты: {len(result.get('personalized_insights', []))}")
        print()
        
        # Проверяем структурированные данные
        if 'structured_analysis' in result:
            structured = result['structured_analysis']
            print(f"🏗️ СТРУКТУРИРОВАННЫЕ ДАННЫЕ:")
            print(f"   Тип личности: {structured.get('personality_type', 'N/A')}")
            print(f"   Риск манипуляций: {structured.get('manipulation_risk', 'N/A')}")
            print(f"   Уровень срочности: {structured.get('urgency_level', 'N/A')}")
            print()
        
        # Проверяем storytelling контент
        profile_text = result.get('psychological_profile', '')
        word_count = len(profile_text.split())
        
        print(f"📖 STORYTELLING АНАЛИЗ:")
        print(f"   Символов: {len(profile_text)}")
        print(f"   Слов: {word_count}")
        print(f"   Целевое количество: 1500+ слов")
        print(f"   Качество: {'✅ ОТЛИЧНО' if word_count >= 1500 else '⚠️ МАЛО' if word_count >= 1000 else '❌ ПЛОХО'}")
        print()
        
        # Проверяем ключевые элементы storytelling
        has_partner_name = 'Михаил' in profile_text
        has_dialogues = profile_text.count('**') >= 4 and ':' in profile_text
        has_scenarios = any(word in profile_text.lower() for word in ['сценарий', 'история', 'ситуация', 'представьте'])
        has_emotions = any(word in profile_text.lower() for word in ['чувствуете', 'эмоци', 'переживаете', 'ощущаете'])
        has_details = any(word in profile_text.lower() for word in ['детали', 'конкретн', 'например', 'мимика', 'жесты'])
        
        print(f"🎭 КАЧЕСТВО STORYTELLING:")
        print(f"   👤 Имя партнера (Михаил): {'✅' if has_partner_name else '❌'}")
        print(f"   💬 Диалоги и цитаты: {'✅' if has_dialogues else '❌'}")
        print(f"   🎬 Сценарии и истории: {'✅' if has_scenarios else '❌'}")
        print(f"   😊 Эмоциональные описания: {'✅' if has_emotions else '❌'}")
        print(f"   🔍 Детализация: {'✅' if has_details else '❌'}")
        print()
        
        quality_score = sum([has_partner_name, has_dialogues, has_scenarios, has_emotions, has_details])
        print(f"🎯 ОБЩАЯ ОЦЕНКА: {quality_score}/5")
        
        if quality_score >= 4:
            print("🏆 ОТЛИЧНО! Итеративный подход работает!")
        elif quality_score >= 3:
            print("✅ ХОРОШО! Есть потенциал для улучшения")
        else:
            print("❌ ПЛОХО! Нужны доработки")
        
        print()
        print("📖 ПРЕВЬЮ STORYTELLING ТЕКСТА:")
        print("-" * 60)
        print(profile_text[:1000])
        if len(profile_text) > 1000:
            print("...")
            print()
            print("(Показаны первые 1000 символов)")
        print("-" * 60)
        
        # Сравнение с требованиями
        print()
        print("📊 СРАВНЕНИЕ С ТРЕБОВАНИЯМИ:")
        print(f"   Требуется: 1500+ слов")
        print(f"   Получено: {word_count} слов")
        print(f"   Выполнение: {round(word_count/1500*100, 1)}%")
        
        if word_count >= 1500:
            print("🎉 ЦЕЛЬ ДОСТИГНУТА! Итеративный подход решил проблему с объемом!")
        else:
            print("⚠️ Требуется доработка промпта для увеличения объема")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_iterative_storytelling()) 