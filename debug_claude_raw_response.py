#!/usr/bin/env python3
"""
Debug Claude's raw response structure for storytelling analysis
"""

import asyncio
import json
from app.services.ai_service import AIService
from app.utils.helpers import extract_json_from_text, safe_json_loads

async def debug_claude_response():
    """Debug Claude's structured response"""
    
    # Test data
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
        }
    ]
    
    ai_service = AIService()
    
    try:
        print("🔍 Генерирую анализ с storytelling техникой...")
        result = await ai_service.profile_partner_advanced(
            answers=test_answers,
            user_id=999,
            partner_name="Алексей",
            partner_description="Муж, 35 лет",
            technique="storytelling",
            use_cache=False
        )
        
        print("\n" + "="*60)
        print("🧠 РЕЗУЛЬТАТ АНАЛИЗА:")
        print("="*60)
        
        print(f"📊 Размер профиля: {len(result.get('psychological_profile', ''))}")
        print(f"📊 Метод парсинга: {result.get('parsing_method', 'unknown')}")
        print(f"📊 Red flags: {len(result.get('red_flags', []))}")
        print(f"📊 Персонализированные инсайты: {len(result.get('personalized_insights', []))}")
        
        # Проверяем структурированные данные
        if 'structured_analysis' in result:
            structured = result['structured_analysis']
            print(f"\n🏗️ СТРУКТУРИРОВАННЫЕ ДАННЫЕ:")
            print(f"   Core traits: {len(structured.get('core_traits', []))}")
            print(f"   Behavioral patterns: {len(structured.get('behavioral_patterns', []))}")
            print(f"   Relationship dynamics: {len(structured.get('relationship_dynamics', []))}")
            
            # Детали каждого элемента
            print(f"\n📝 ДЕТАЛИ СТРУКТУРИРОВАННЫХ ДАННЫХ:")
            for trait in structured.get('core_traits', []):
                print(f"   - Core trait: {trait}")
            
            for pattern in structured.get('behavioral_patterns', []):
                print(f"   - Behavioral pattern: {pattern}")
                
            for dynamic in structured.get('relationship_dynamics', []):
                print(f"   - Relationship dynamic: {dynamic}")
        
        print(f"\n📖 ПРЕВЬЮ STORYTELLING ПРОФИЛЯ:")
        print("-" * 60)
        profile_text = result.get('psychological_profile', '')
        print(profile_text[:1000])
        if len(profile_text) > 1000:
            print("...")
        print("-" * 60)
        
        # Проверяем наличие ключевых элементов
        print(f"\n🎭 ПРОВЕРКА STORYTELLING ЭЛЕМЕНТОВ:")
        profile_text = result.get('psychological_profile', '')
        
        has_dialogues = '**' in profile_text and ':' in profile_text
        has_emotions = any(word in profile_text.lower() for word in ['чувствуете', 'эмоци', 'настроение', 'переживаете'])
        has_scenarios = any(word in profile_text.lower() for word in ['сценарий', 'представьте', 'ситуация'])
        has_partner_name = 'Алексей' in profile_text
        
        print(f"   📢 Есть диалоги: {'✅' if has_dialogues else '❌'}")
        print(f"   😊 Есть эмоции: {'✅' if has_emotions else '❌'}")
        print(f"   🎬 Есть сценарии: {'✅' if has_scenarios else '❌'}")
        print(f"   👤 Есть имя партнера: {'✅' if has_partner_name else '❌'}")
        
        # Статистика слов
        word_count = len(profile_text.split())
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   Символов: {len(profile_text)}")
        print(f"   Слов: {word_count}")
        print(f"   Качество: {'✅ ХОРОШО' if word_count >= 1000 else '❌ МАЛО'}")
        
    except Exception as e:
        print(f"❌ Ошибка при генерации анализа: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_claude_response()) 