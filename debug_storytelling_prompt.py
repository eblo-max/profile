#!/usr/bin/env python3
"""
Дебаг тест для проверки storytelling промпта
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.prompts.ultra_personalization_prompt import create_storytelling_analysis_prompt, create_simplified_system_prompt

def test_storytelling_prompt():
    """Тест для проверки storytelling промпта"""
    
    # Тестовые данные
    test_answers = """1. Контроль финансов
   Ответ: Да, он полностью контролирует все мои деньги

2. Критика внешности
   Ответ: Да, он постоянно критикует мою внешность

3. Изоляция от друзей
   Ответ: Да, он запрещает мне видеться с друзьями

4. Эмоциональный шантаж
   Ответ: Да, он угрожает уйти если я не подчиняюсь

5. Ревность
   Ответ: Да, он патологически ревнив ко всем мужчинам"""
    
    partner_name = "Тестовый Партнер"
    partner_description = "Тестовый случай для проверки storytelling"
    
    # Создаем промпт
    user_prompt = create_storytelling_analysis_prompt(
        test_answers, partner_name, partner_description
    )
    
    system_prompt = create_simplified_system_prompt()
    
    print("=" * 80)
    print("🎭 DEBUG: STORYTELLING PROMPT TEST")
    print("=" * 80)
    
    print(f"\n📝 SYSTEM PROMPT ({len(system_prompt)} chars):")
    print("-" * 50)
    print(system_prompt)
    print("-" * 50)
    
    print(f"\n📝 USER PROMPT ({len(user_prompt)} chars):")
    print("-" * 50)
    print(user_prompt)
    print("-" * 50)
    
    # Анализируем промпт
    print(f"\n📊 АНАЛИЗ ПРОМПТА:")
    print(f"   📏 Размер системного промпта: {len(system_prompt)} символов")
    print(f"   📏 Размер пользовательского промпта: {len(user_prompt)} символов")
    print(f"   📏 Общий размер: {len(system_prompt) + len(user_prompt)} символов")
    
    # Проверяем ключевые элементы
    storytelling_keywords = [
        "storytelling", "диалоги", "сценарии", "живые", "конкретные",
        "примеры", "цитаты", "механизмы", "детальные", "минимум 1000 слов"
    ]
    
    found_keywords = []
    for keyword in storytelling_keywords:
        if keyword.lower() in user_prompt.lower():
            found_keywords.append(keyword)
    
    print(f"\n🔍 НАЙДЕННЫЕ КЛЮЧЕВЫЕ СЛОВА:")
    for keyword in found_keywords:
        print(f"   ✅ {keyword}")
    
    missing_keywords = [k for k in storytelling_keywords if k not in found_keywords]
    if missing_keywords:
        print(f"\n❌ ОТСУТСТВУЮЩИЕ КЛЮЧЕВЫЕ СЛОВА:")
        for keyword in missing_keywords:
            print(f"   ❌ {keyword}")
    
    # Проверяем структуру JSON
    json_structure_check = [
        "psychological_profile", "personality_type", "red_flags",
        "personalized_insights", "behavioral_evidence", "manipulation_tactics"
    ]
    
    print(f"\n📋 ПРОВЕРКА JSON СТРУКТУРЫ:")
    for field in json_structure_check:
        if field in user_prompt:
            print(f"   ✅ {field}")
        else:
            print(f"   ❌ {field}")
    
    print(f"\n🎯 ВЫВОДЫ:")
    if len(found_keywords) >= 8:
        print("   ✅ Промпт содержит достаточно storytelling инструкций")
    else:
        print("   ❌ Промпт недостаточно детальный для storytelling")
    
    if len(user_prompt) >= 3000:
        print("   ✅ Промпт достаточно детальный")
    else:
        print("   ⚠️ Промпт может быть недостаточно детальным")
    
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print("   1. Проверьте, что промпт содержит конкретные примеры 'плохо' vs 'хорошо'")
    print("   2. Убедитесь, что требуется минимум 1000 слов для психологического профиля")
    print("   3. Проверьте, что указаны конкретные инструкции для диалогов и сценариев")
    
    return user_prompt, system_prompt

if __name__ == "__main__":
    test_storytelling_prompt() 