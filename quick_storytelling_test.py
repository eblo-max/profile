#!/usr/bin/env python3
"""
Быстрый тест storytelling техники
Проверяет использование новых промптов без генерации PDF
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import AIService

async def quick_storytelling_test():
    """Быстрый тест storytelling техники"""
    print("⚡ БЫСТРЫЙ ТЕСТ STORYTELLING ТЕХНИКИ")
    print("=" * 50)
    
    ai_service = AIService()
    
    # Быстрый тест на высоком риске
    test_answers = [
        {"question": "Контроль финансов", "answer": "Да, он полностью контролирует все мои деньги"},
        {"question": "Критика", "answer": "Да, он постоянно критикует мою внешность"},
        {"question": "Изоляция", "answer": "Да, он запрещает мне видеться с друзьями"},
        {"question": "Эмоциональный шантаж", "answer": "Да, он угрожает уйти если я не подчиняюсь"},
        {"question": "Ревность", "answer": "Да, он патологически ревнив ко всем мужчинам"}
    ]
    
    print("🧠 Генерирую анализ с storytelling техникой...")
    
    try:
        # Тест storytelling техники
        analysis = await ai_service.profile_partner_advanced(
            answers=test_answers,
            user_id=999,
            partner_name="Тестовый Партнер",
            partner_description="Тестовый случай для проверки storytelling",
            technique="storytelling",
            use_cache=False
        )
        
        # Проверяем результат
        profile_text = analysis.get("psychological_profile", "")
        
        print(f"✅ Анализ сгенерирован!")
        print(f"📊 Размер: {len(profile_text)} символов")
        
        # Безопасная проверка слов
        if isinstance(profile_text, str):
            word_count = len(profile_text.split())
            print(f"📊 Слов: {word_count} слов")
        else:
            word_count = 0
            print(f"📊 Слов: ERROR - profile_text не является строкой: {type(profile_text)}")
            print(f"📊 Содержимое: {profile_text}")
        
        # Проверяем качество storytelling
        print("\n🎭 АНАЛИЗ КАЧЕСТВА STORYTELLING:")
        
        # Проверяем наличие диалогов
        has_dialogue = any(marker in profile_text for marker in ['"', '«', '»', "говорит", "сказал"])
        print(f"   📢 Диалоги: {'✅' if has_dialogue else '❌'}")
        
        # Проверяем наличие сценариев
        has_scenarios = any(marker in profile_text.lower() for marker in ["когда", "например", "ситуация"])
        print(f"   🎬 Сценарии: {'✅' if has_scenarios else '❌'}")
        
        # Проверяем эмоциональность
        has_emotions = any(marker in profile_text.lower() for marker in ["чувствует", "испытывает", "переживает"])
        print(f"   😊 Эмоции: {'✅' if has_emotions else '❌'}")
        
        # Проверяем использование имени
        has_name = "Тестовый Партнер" in profile_text
        print(f"   👤 Имя партнера: {'✅' if has_name else '❌'}")
        
        # Проверяем детализацию (1000+ слов)
        if isinstance(profile_text, str):
            is_detailed = len(profile_text.split()) >= 1000
        else:
            is_detailed = False
        print(f"   📝 Детализация: {'✅' if is_detailed else '❌'}")
        
        # Показываем превью
        print(f"\n📖 ПРЕВЬЮ АНАЛИЗА (первые 500 символов):")
        print("-" * 50)
        print(profile_text[:500])
        if len(profile_text) > 500:
            print("...")
        print("-" * 50)
        
        # Проверяем, что это не статичный шаблон
        is_dynamic = "статичный" not in profile_text.lower() and "шаблон" not in profile_text.lower()
        print(f"\n🔄 Динамический контент: {'✅' if is_dynamic else '❌'}")
        
        # Общая оценка
        quality_score = sum([has_dialogue, has_scenarios, has_emotions, has_name, is_detailed, is_dynamic])
        print(f"\n🎯 ОБЩАЯ ОЦЕНКА: {quality_score}/6")
        
        if quality_score >= 5:
            print("🎉 ОТЛИЧНО! Storytelling техника работает!")
        elif quality_score >= 3:
            print("⚠️ ХОРОШО, но есть проблемы")
        else:
            print("❌ ПЛОХО! Storytelling техника не работает")
            
        print(f"\n📊 ДЕТАЛИ:")
        if isinstance(profile_text, str):
            print(f"   Слов в профиле: {len(profile_text.split())}")
            print(f"   Символов в профиле: {len(profile_text)}")
        else:
            print(f"   Слов в профиле: ERROR - не строка")
            print(f"   Символов в профиле: ERROR - не строка")
        print(f"   Требуется минимум: 1000 слов")
        print(f"   Ожидается минимум: ~5000 символов")
            
        return analysis
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(quick_storytelling_test()) 