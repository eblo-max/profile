#!/usr/bin/env python3
"""
Отладочный скрипт для проверки полного текста storytelling
"""

import asyncio
from app.services.ai_service import ai_service

async def debug_storytelling_text():
    """Отладка полного текста storytelling"""
    
    try:
        # Тестовые данные
        test_answers = [
            {"question": "Как партнер реагирует на ваши успехи?", "answer": "Михаил всегда находит способ принизить мои достижения. Когда я получила повышение, он сказал: 'Ну конечно, тебе просто повезло'. А когда я выиграла конкурс, он отозвался: 'Наверное, жюри просто пожалело тебя'."},
            {"question": "Проверяет ли он ваш телефон?", "answer": "Да, постоянно. Он говорит, что это нормально для пар, которые доверяют друг другу. Но если я отказываюсь показать телефон, он начинает кричать и обвинять меня в измене."},
            {"question": "Как он контролирует финансы?", "answer": "Он забрал мою карту и говорит, что будет сам распоряжаться деньгами. На каждую покупку нужно его разрешение. Даже за продукты не могу пойти одна - он дает точную сумму и требует чек."},
            {"question": "Изолирует ли он вас от друзей?", "answer": "Постепенно я перестала видеться с друзьями. Михаил всегда находил повод не отпускать: то у него были планы, то мои подруги 'плохо на меня влияют'. Теперь я почти никого не вижу."},
            {"question": "Как он реагирует на критику?", "answer": "Очень агрессивно. Если я пытаюсь высказать недовольство, он кричит, что я неблагодарная, что все женщины одинаковые. Может несколько дней не разговаривать или уйти из дома."}
        ]
        
        print("🚀 ОТЛАДКА STORYTELLING ТЕКСТА")
        print("=" * 60)
        
        # Запускаем анализ
        print("📡 Запускаю анализ...")
        result = await ai_service.profile_partner_advanced(
            answers=test_answers,
            user_id=999,
            partner_name="Михаил",
            technique="storytelling"
        )
        
        print("✅ Анализ завершен!")
        
        # Выводим полный текст
        storytelling_text = result.get("psychological_profile", "")
        print(f"📖 ПОЛНЫЙ STORYTELLING ТЕКСТ:")
        print("-" * 60)
        print(storytelling_text)
        print("-" * 60)
        
        # Анализируем структуру
        print(f"\n📊 АНАЛИЗ СТРУКТУРЫ:")
        print(f"   Символов: {len(storytelling_text)}")
        print(f"   Слов: {len(storytelling_text.split())}")
        double_newline = '\n\n'
        print(f"   Абзацев: {len(storytelling_text.split(double_newline))}")
        
        # Проверяем наличие ключевых элементов
        has_dialogues = "–" in storytelling_text or ":" in storytelling_text
        has_emotions = any(word in storytelling_text.lower() for word in ["чувствует", "переживает", "боится", "волнует"])
        has_scenarios = any(word in storytelling_text.lower() for word in ["утром", "вечером", "когда", "ситуация"])
        has_name = "Михаил" in storytelling_text
        
        print(f"\n🎭 КАЧЕСТВЕННЫЕ ПОКАЗАТЕЛИ:")
        print(f"   Диалоги: {'✅' if has_dialogues else '❌'}")
        print(f"   Эмоции: {'✅' if has_emotions else '❌'}")
        print(f"   Сценарии: {'✅' if has_scenarios else '❌'}")
        print(f"   Имя партнера: {'✅' if has_name else '❌'}")
        
        # Проверяем red flags
        red_flags = result.get("red_flags", [])
        print(f"\n🚨 RED FLAGS: {len(red_flags)}")
        for i, flag in enumerate(red_flags, 1):
            print(f"   {i}. {flag}")
        
        # Персональные инсайты
        insights = result.get("personalized_insights", [])
        print(f"\n💡 ПЕРСОНАЛЬНЫЕ ИНСАЙТЫ: {len(insights)}")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_storytelling_text()) 