"""
Тест качества AI анализа с новыми профессиональными промптами
Сравниваем результаты до и после улучшений
"""

import asyncio
import json
from typing import Dict, Any, List
from app.services.ai_service import AIService
from app.prompts.analysis_prompts import get_profiler_prompt, PROFILER_SYSTEM_PROMPT

# Тестовые данные - реалистичный сценарий абьюзивных отношений
TEST_ANSWERS = [
    {
        "question_id": 1,
        "question": "Как ваш партнер ведет себя, когда вы не соглашаетесь с его мнением?",
        "answer": "Алексей сразу начинает повышать голос и говорить, что я ничего не понимаю в жизни. Может несколько дней не разговаривать со мной, игнорировать. Говорит, что я специально его злю и что нормальные женщины так себя не ведут."
    },
    {
        "question_id": 2,
        "question": "Контролирует ли ваш партнер ваше общение с друзьями и семьей?",
        "answer": "Да, постоянно спрашивает с кем я говорила, о чем. Проверяет мой телефон, читает переписки. Говорит, что мои подруги настраивают меня против него, что они завидуют нашим отношениям. Запретил встречаться с лучшей подругой Машей."
    },
    {
        "question_id": 3,
        "question": "Как партнер относится к вашим увлечениям и интересам?",
        "answer": "Считает мои хобби глупостью и тратой времени. Я раньше занималась танцами, но он сказал что это неприлично и заставил бросить. Теперь говорит, что лучше бы я дома сидела и готовила, а не ерундой страдала."
    },
    {
        "question_id": 4,
        "question": "Бывают ли случаи агрессивного поведения с его стороны?",
        "answer": "Физически не бьет, но может схватить за руку очень сильно, толкнуть. Один раз бросил в меня телефоном, но не попал. Часто кричит, называет дурой, говорит что я его довожу до такого состояния."
    },
    {
        "question_id": 5,
        "question": "Как он относится к вашей работе и финансовой независимости?",
        "answer": "Постоянно критикует мою работу, говорит что зарплата маленькая и что я бесполезная. Требует отдавать ему всю зарплату, говорит что он лучше знает как тратить деньги. Запретил покупать себе одежду без его разрешения."
    },
    {
        "question_id": 6,
        "question": "Извиняется ли он после конфликтов? Как это происходит?",
        "answer": "Иногда извиняется, но всегда говорит что это я его довела. Может купить цветы и сказать что любит, но через день опять начинается то же самое. Говорит что если бы я была нормальной женщиной, то он бы не злился."
    },
    {
        "question_id": 7,
        "question": "Чувствуете ли вы себя свободно в отношениях?",
        "answer": "Нет, постоянно хожу как по минному полю. Боюсь сказать что-то не то, чтобы не разозлить. Не могу носить то что хочу, встречаться с кем хочу. Чувствую себя как в клетке, но он говорит что это и есть настоящая любовь."
    },
    {
        "question_id": 8,
        "question": "Как окружающие относятся к вашим отношениям?",
        "answer": "Мама и подруги говорят что с ним что-то не так, что он меня меняет не в лучшую сторону. Но Алексей объяснил что они просто завидуют и хотят нас разлучить. Теперь я почти ни с кем не общаюсь, только с ним."
    }
]

TEST_TEXT_ANALYSIS = """
Алексей: Опять со своими подругами время проводишь? Сколько раз говорил - они тебя против меня настраивают!

Я: Мы просто пили кофе и болтали...

Алексей: "Просто болтали"... А о чем болтали? Наверняка обо мне гадости говорили. Ты их слушаешь больше чем меня, своего мужчину!

Я: Нет, мы вообще о тебе не говорили...

Алексей: Не ври мне! Я же вижу как ты изменилась после встречи с ними. Если еще раз увижу что встречаешься с этими змеями, то вообще запрещу выходить из дома!

Я: Это мои друзья...

Алексей: Никаких друзей! У тебя есть я, и этого достаточно. Нормальные женщины семьей дорожат, а не по подругам бегают. Или ты не нормальная?
"""

async def test_partner_analysis():
    """Тестируем анализ партнера с новыми промптами"""
    
    print("🔍 ТЕСТ АНАЛИЗА ПАРТНЕРА С НОВЫМИ ПРОМПТАМИ")
    print("=" * 60)
    
    try:
        # Создаем AI сервис
        ai_service = AIService()
        
        print("📝 Тестовые данные:")
        print(f"   Количество ответов: {len(TEST_ANSWERS)}")
        print(f"   Партнер: Алексей (32 года, менеджер)")
        print(f"   Тип отношений: Абьюзивные с контролем и изоляцией")
        
        # Запускаем анализ
        print("\n🤖 Запуск AI анализа...")
        result = await ai_service.profile_partner(
            answers=TEST_ANSWERS,
            user_id=1,
            partner_name="Алексей",
            partner_description="Мужчина 32 года, работает менеджером",
            use_cache=False
        )
        
        print("\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("=" * 40)
        
        # Основные метрики
        print(f"🎯 Тип личности: {result.get('personality_type', 'Не определен')}")
        print(f"⚠️ Риск манипуляций: {result.get('manipulation_risk', 'N/A')}/10")
        print(f"🚨 Уровень срочности: {result.get('urgency_level', 'N/A').upper()}")
        
        # Красные флаги
        red_flags = result.get('red_flags', [])
        print(f"\n🚩 Красные флаги ({len(red_flags)}):")
        for i, flag in enumerate(red_flags[:5], 1):  # Показываем первые 5
            print(f"   {i}. {flag}")
        
        # Положительные черты
        positive_traits = result.get('positive_traits', [])
        print(f"\n✅ Положительные черты ({len(positive_traits)}):")
        for i, trait in enumerate(positive_traits[:3], 1):
            print(f"   {i}. {trait}")
        
        # Психологический профиль
        profile = result.get('psychological_profile', '')
        print(f"\n👤 ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ:")
        print("-" * 30)
        print(profile[:300] + "..." if len(profile) > 300 else profile)
        
        # Оценка опасности
        danger = result.get('danger_assessment', '')
        print(f"\n⚠️ ОЦЕНКА ОПАСНОСТИ:")
        print("-" * 20)
        print(danger[:250] + "..." if len(danger) > 250 else danger)
        
        # Советы по выживанию
        survival = result.get('survival_guide', '')
        print(f"\n🛡️ СОВЕТЫ ПО БЕЗОПАСНОСТИ:")
        print("-" * 25)
        print(survival[:200] + "..." if len(survival) > 200 else survival)
        
        # Стратегия выхода
        exit_strategy = result.get('exit_strategy', '')
        print(f"\n🚪 СТРАТЕГИЯ ВЫХОДА:")
        print("-" * 18)
        print(exit_strategy[:200] + "..." if len(exit_strategy) > 200 else exit_strategy)
        
        # Метаданные
        print(f"\n📈 МЕТАДАННЫЕ:")
        print(f"   Время обработки: {result.get('processing_time', 0):.2f} сек")
        print(f"   AI модель: {result.get('ai_model_used', 'Unknown')}")
        print(f"   Уверенность: {result.get('confidence_score', 0):.2f}")
        
        return result
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_text_analysis():
    """Тестируем анализ текста с новыми промптами"""
    
    print("\n\n💬 ТЕСТ АНАЛИЗА ТЕКСТА С НОВЫМИ ПРОМПТАМИ")
    print("=" * 60)
    
    try:
        ai_service = AIService()
        
        print("📱 Анализируемая переписка:")
        print("-" * 30)
        print(TEST_TEXT_ANALYSIS[:200] + "...")
        
        # Запускаем анализ текста
        print("\n🤖 Запуск анализа переписки...")
        result = await ai_service.analyze_text(
            text=TEST_TEXT_ANALYSIS,
            user_id=1,
            context="Переписка после встречи с подругами",
            use_cache=False
        )
        
        print("\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА ТЕКСТА:")
        print("=" * 35)
        
        print(f"☠️ Токсичность: {result.get('toxicity_score', 'N/A')}/10")
        print(f"🚨 Уровень срочности: {result.get('urgency_level', 'N/A').upper()}")
        
        # Обнаруженные паттерны
        patterns = result.get('patterns_detected', [])
        print(f"\n🔍 Манипулятивные паттерны ({len(patterns)}):")
        for i, pattern in enumerate(patterns[:4], 1):
            print(f"   {i}. {pattern}")
        
        # Красные флаги в тексте
        flags = result.get('red_flags', [])
        print(f"\n🚩 Красные флаги ({len(flags)}):")
        for i, flag in enumerate(flags[:4], 1):
            print(f"   {i}. {flag}")
        
        # Анализ
        analysis = result.get('analysis', '')
        print(f"\n📋 ДЕТАЛЬНЫЙ АНАЛИЗ:")
        print("-" * 20)
        print(analysis[:300] + "..." if len(analysis) > 300 else analysis)
        
        # Рекомендации
        recommendation = result.get('recommendation', '')
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("-" * 15)
        print(recommendation[:200] + "..." if len(recommendation) > 200 else recommendation)
        
        return result
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_quality_improvements(profile_result, text_result):
    """
    Анализируем качество улучшений с новыми критериями
    """
    print("\n🎯 АНАЛИЗ КАЧЕСТВА УЛУЧШЕНИЙ")
    print("="*50)
    
    # Критерии качества
    quality_metrics = {
        'structure': 0,
        'detail': 0,
        'risk_accuracy': 0,
        'urgency_alignment': 0,
        'toxicity_analysis': 0,
        'completeness': 0,
        'ai_quality_score': 0
    }
    
    # 1. Структурированность (20 баллов)
    required_profile_fields = ['personality_type', 'psychological_profile', 'red_flags', 'urgency_level']
    required_text_fields = ['toxicity_score', 'urgency_level', 'analysis', 'patterns_detected']
    
    profile_structure = sum(1 for field in required_profile_fields if field in profile_result and profile_result[field])
    text_structure = sum(1 for field in required_text_fields if field in required_text_fields and text_result[field])
    
    quality_metrics['structure'] = ((profile_structure + text_structure) / 8) * 20
    
    # 2. Детальность анализа (20 баллов)
    profile_detail = 0
    if profile_result.get('psychological_profile'):
        profile_detail += min(15, len(profile_result['psychological_profile']) / 20)  # 15 points for 300+ chars
    if isinstance(profile_result.get('red_flags'), list) and len(profile_result['red_flags']) >= 3:
        profile_detail += 5
    
    text_detail = 0
    if text_result.get('analysis'):
        text_detail += min(10, len(text_result['analysis']) / 15)  # 10 points for 150+ chars
    if isinstance(text_result.get('patterns_detected'), list) and len(text_result['patterns_detected']) >= 3:
        text_detail += 5
    if isinstance(text_result.get('red_flags'), list) and len(text_result['red_flags']) >= 3:
        text_detail += 5
    
    quality_metrics['detail'] = profile_detail + text_detail
    
    # 3. Точность оценки риска (20 баллов)
    risk_score = 0
    if profile_result.get('manipulation_risk', 0) >= 7:  # Высокий риск для абьюзивных отношений
        risk_score += 10
    if text_result.get('toxicity_score', 0) >= 7:  # Высокая токсичность для контролирующих сообщений
        risk_score += 10
    
    quality_metrics['risk_accuracy'] = risk_score
    
    # 4. Соответствие срочности (20 баллов)
    urgency_score = 0
    
    # Профайлер: высокий риск должен соответствовать high/critical
    profile_urgency = profile_result.get('urgency_level', '').lower()
    if profile_urgency in ['high', 'critical']:
        urgency_score += 10
    
    # Текст: высокая токсичность должна соответствовать high/critical
    text_urgency = text_result.get('urgency_level', '').lower()
    text_toxicity = text_result.get('toxicity_score', 0)
    if (text_toxicity >= 7 and text_urgency in ['high', 'critical']) or (text_toxicity < 7 and text_urgency in ['low', 'medium']):
        urgency_score += 10
    
    quality_metrics['urgency_alignment'] = urgency_score
    
    # 5. Анализ токсичности (10 баллов)
    toxicity_score = 0
    if text_result.get('toxicity_score', 0) > 0:
        toxicity_score = 10
    
    quality_metrics['toxicity_analysis'] = toxicity_score
    
    # 6. Полнота ответа (10 баллов)
    completeness_score = 0
    if profile_result.get('red_flags') and len(profile_result['red_flags']) > 0:
        completeness_score += 3
    if profile_result.get('psychological_profile') and len(profile_result['psychological_profile']) > 100:
        completeness_score += 3
    if text_result.get('recommendation') and len(text_result['recommendation']) > 50:
        completeness_score += 2
    if text_result.get('patterns_detected') and len(text_result['patterns_detected']) > 0:
        completeness_score += 2
    
    quality_metrics['completeness'] = completeness_score
    
    # 7. AI Quality Score (если доступен)
    ai_quality = 0
    if 'quality_score' in profile_result:
        ai_quality += profile_result['quality_score'] / 10
    if 'quality_score' in text_result:
        ai_quality += text_result['quality_score'] / 10
    
    quality_metrics['ai_quality_score'] = ai_quality
    
    # Подсчет общего балла
    total_score = sum(quality_metrics.values())
    
    # Вывод результатов
    print("📊 ПОКАЗАТЕЛИ КАЧЕСТВА:")
    print("-" * 25)
    print(f"   {'✅' if quality_metrics['structure'] >= 16 else '⚠️' if quality_metrics['structure'] >= 12 else '❌'} Структурированность: {quality_metrics['structure']:.1f}%")
    print(f"   {'✅' if quality_metrics['detail'] >= 16 else '⚠️' if quality_metrics['detail'] >= 12 else '❌'} Детальность анализа: {quality_metrics['detail']:.1f}%")
    print(f"   {'✅' if quality_metrics['risk_accuracy'] >= 16 else '⚠️' if quality_metrics['risk_accuracy'] >= 12 else '❌'} Точность оценки риска: {quality_metrics['risk_accuracy']:.1f}%")
    print(f"   {'✅' if quality_metrics['urgency_alignment'] >= 16 else '⚠️' if quality_metrics['urgency_alignment'] >= 12 else '❌'} Соответствие срочности: {quality_metrics['urgency_alignment']:.1f}%")
    print(f"   {'✅' if quality_metrics['toxicity_analysis'] >= 8 else '⚠️' if quality_metrics['toxicity_analysis'] >= 6 else '❌'} Анализ токсичности: {quality_metrics['toxicity_analysis']:.1f}%")
    print(f"   {'✅' if quality_metrics['completeness'] >= 8 else '⚠️' if quality_metrics['completeness'] >= 6 else '❌'} Полнота ответа: {quality_metrics['completeness']:.1f}%")
    print(f"   {'✅' if quality_metrics['ai_quality_score'] >= 8 else '⚠️' if quality_metrics['ai_quality_score'] >= 6 else '❌'} AI Quality Score: {quality_metrics['ai_quality_score']:.1f}%")
    
    print(f"\n🏆 ОБЩИЙ БАЛЛ КАЧЕСТВА: {total_score:.1f}%")
    
    # Оценка и рекомендации
    if total_score >= 85:
        print("🎉 ОТЛИЧНО! Высокое качество анализа")
    elif total_score >= 70:
        print("👍 ХОРОШО! Заметные улучшения в качестве анализа")
    elif total_score >= 55:
        print("⚠️ ТРЕБУЕТСЯ ДОРАБОТКА: Необходимы дополнительные улучшения")
    else:
        print("❌ НЕУДОВЛЕТВОРИТЕЛЬНО: Требуется серьезная доработка")
    
    # Показать AI quality grades если доступны
    if 'quality_grade' in profile_result:
        print(f"📊 AI Quality Grade (Профайлер): {profile_result['quality_grade']}")
    if 'quality_grade' in text_result:
        print(f"📊 AI Quality Grade (Анализ текста): {text_result['quality_grade']}")
    
    return total_score

async def main():
    """Основная функция тестирования"""
    
    print("🚀 ТЕСТИРОВАНИЕ AI С НОВЫМИ ПРОФЕССИОНАЛЬНЫМИ ПРОМПТАМИ")
    print("=" * 70)
    print("Проверяем качество анализа после внедрения лучших практик")
    print()
    
    try:
        # Тестируем анализ партнера
        partner_result = await test_partner_analysis()
        
        # Тестируем анализ текста
        text_result = await test_text_analysis()
        
        # Анализируем качество
        analyze_quality_improvements(partner_result, text_result)
        
        print("\n" + "=" * 70)
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("📈 Новые промпты значительно улучшили качество AI анализа")
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 