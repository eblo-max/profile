#!/usr/bin/env python3
"""
Тест трехэтапного storytelling подхода
"""

import asyncio
from app.services.ai_service import ai_service

async def test_triple_storytelling():
    """Тест трехэтапного storytelling анализа"""
    
    # Тестовые данные
    test_answers = [
        {"question": "Как партнер реагирует на ваши успехи?", "answer": "Михаил всегда находит способ принизить мои достижения. Когда я получила повышение, он сказал: 'Ну конечно, тебе просто повезло'. А когда я выиграла конкурс, он отозвался: 'Наверное, жюри просто пожалело тебя'."},
        {"question": "Проверяет ли он ваш телефон?", "answer": "Да, постоянно. Он говорит, что это нормально для пар, которые доверяют друг другу. Но если я отказываюсь показать телефон, он начинает кричать и обвинять меня в измене."},
        {"question": "Как он контролирует финансы?", "answer": "Он забрал мою карту и говорит, что будет сам распоряжаться деньгами. На каждую покупку нужно его разрешение. Даже за продукты не могу пойти одна - он дает точную сумму и требует чек."},
        {"question": "Изолирует ли он вас от друзей?", "answer": "Постепенно я перестала видеться с друзьями. Михаил всегда находил повод не отпускать: то у него были планы, то мои подруги 'плохо на меня влияют'. Теперь я почти никого не вижу."},
        {"question": "Как он реагирует на критику?", "answer": "Очень агрессивно. Если я пытаюсь высказать недовольство, он кричит, что я неблагодарная, что все женщины одинаковые. Может несколько дней не разговаривать или уйти из дома."}
    ]
    
    print("🚀 ТЕСТ ТРЕХЭТАПНОГО STORYTELLING ПОДХОДА")
    print("=" * 60)
    print("🔄 Запускаю трехэтапный storytelling...")
    print("   Этап 1: Получение структурированных данных")
    print("   Этап 2: Генерация первой половины narrative")
    print("   Этап 3: Генерация второй половины narrative")
    print()
    
    # Запускаем анализ
    result = await ai_service.profile_partner_advanced(
        answers=test_answers,
        user_id=999,
        partner_name="Михаил",
        technique="storytelling"
    )
    
    print("✅ ТРЕХЭТАПНЫЙ АНАЛИЗ ЗАВЕРШЕН!")
    print("=" * 60)
    
    # Получаем метаданные
    generation_method = result.get("generation_method", "unknown")
    narrative_words = result.get("narrative_words", 0)
    first_half_words = result.get("first_half_words", 0)
    second_half_words = result.get("second_half_words", 0)
    red_flags = result.get("red_flags", [])
    insights = result.get("personalized_insights", [])
    
    print(f"📊 МЕТАДАННЫЕ:")
    print(f"   Метод генерации: {generation_method}")
    print(f"   Общее количество слов: {narrative_words}")
    print(f"   Первая половина: {first_half_words} слов")
    print(f"   Вторая половина: {second_half_words} слов")
    print(f"   Red flags: {len(red_flags)}")
    print(f"   Персональные инсайты: {len(insights)}")
    
    # Анализируем результаты
    personality_type = result.get("personality_type", "N/A")
    manipulation_risk = result.get("manipulation_risk", "N/A")
    urgency_level = result.get("urgency_level", "N/A")
    
    print(f"\n🏗️ СТРУКТУРИРОВАННЫЕ ДАННЫЕ:")
    print(f"   Тип личности: {personality_type}")
    print(f"   Риск манипуляций: {manipulation_risk}")
    print(f"   Уровень срочности: {urgency_level}")
    
    # Проверяем storytelling
    storytelling_text = result.get("psychological_profile", "")
    words_count = len(storytelling_text.split())
    chars_count = len(storytelling_text)
    
    print(f"\n📖 STORYTELLING АНАЛИЗ:")
    print(f"   Символов: {chars_count}")
    print(f"   Слов: {words_count}")
    print(f"   Целевое количество: 1500+ слов")
    
    # Определяем качество по объему
    if words_count >= 1500:
        quality = "✅ ОТЛИЧНО"
    elif words_count >= 1000:
        quality = "🟡 ХОРОШО"
    elif words_count >= 500:
        quality = "🟠 УДОВЛЕТВОРИТЕЛЬНО"
    else:
        quality = "❌ ПЛОХО"
    
    print(f"   Качество: {quality}")
    
    # Проверяем элементы качества
    has_name = "Михаил" in storytelling_text
    has_dialogues = "–" in storytelling_text or ":" in storytelling_text
    has_scenarios = any(word in storytelling_text.lower() for word in ["утром", "вечером", "когда", "ситуация", "сцена"])
    has_emotions = any(word in storytelling_text.lower() for word in ["чувствует", "переживает", "боится", "волнует", "эмоци"])
    has_details = len(storytelling_text) > 3000
    
    print(f"\n🎭 КАЧЕСТВО STORYTELLING:")
    print(f"   👤 Имя партнера (Михаил): {'✅' if has_name else '❌'}")
    print(f"   💬 Диалоги и цитаты: {'✅' if has_dialogues else '❌'}")
    print(f"   🎬 Сценарии и истории: {'✅' if has_scenarios else '❌'}")
    print(f"   😊 Эмоциональные описания: {'✅' if has_emotions else '❌'}")
    print(f"   🔍 Детализация: {'✅' if has_details else '❌'}")
    
    # Общая оценка
    quality_score = sum([has_name, has_dialogues, has_scenarios, has_emotions, has_details])
    print(f"\n🎯 ОБЩАЯ ОЦЕНКА: {quality_score}/5")
    
    if quality_score >= 4:
        print("✅ ОТЛИЧНО! Высокое качество storytelling")
    elif quality_score >= 3:
        print("🟡 ХОРОШО! Есть потенциал для улучшения")
    else:
        print("❌ ПЛОХО! Нужны доработки")
    
    # Превью storytelling
    preview = storytelling_text[:1000] + "..." if len(storytelling_text) > 1000 else storytelling_text
    print(f"\n📖 ПРЕВЬЮ STORYTELLING ТЕКСТА:")
    print("-" * 60)
    print(preview)
    print("-" * 60)
    
    # Сравнение с требованиями
    print(f"\n📊 СРАВНЕНИЕ С ТРЕБОВАНИЯМИ:")
    print(f"   Требуется: 1500+ слов")
    print(f"   Получено: {words_count} слов")
    print(f"   Выполнение: {words_count / 1500 * 100:.1f}%")
    
    if words_count >= 1500:
        print("✅ Требования выполнены!")
    else:
        print("⚠️ Требуется доработка промпта для увеличения объема")
    
    # Проверяем red flags
    if red_flags:
        print(f"\n🚨 RED FLAGS ({len(red_flags)}):")
        for i, flag in enumerate(red_flags, 1):
            print(f"   {i}. {flag}")
    
    # Проверяем инсайты
    if insights:
        print(f"\n💡 ПЕРСОНАЛЬНЫЕ ИНСАЙТЫ ({len(insights)}):")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_triple_storytelling()) 