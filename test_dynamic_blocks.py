#!/usr/bin/env python3
"""
Тест динамических блоков PDF с персонализацией на основе ответов пользователя
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService

async def test_dynamic_blocks():
    """Тест динамических блоков с реальными ответами"""
    
    print("🔄 Тестируем динамические блоки PDF...")
    
    # Создаем реалистичные ответы пользователя
    test_answers = [
        {
            "question": "Опишите конкретную ситуацию за последние 2 недели, когда вы дали партнеру критическую обратную связь о его поведении или действиях. Что именно вы сказали и как он отреагировал в первые 10 секунд?",
            "answer": "Я сказала ему, что мне не нравится, как он кричит на детей. В первые секунды он покраснел, сжал кулаки и сказал: 'Ты вообще понимаешь, как тяжело мне на работе? А ты еще и дома меня критикуешь!' Потом начал перечислять все мои недостатки.",
            "block": "narcissism"
        },
        {
            "question": "Вспомните последний раз, когда вы сказали 'нет' на просьбу партнера. Опишите его реакцию в следующие 10 минут. Какие именно слова он использовал?",
            "answer": "Я отказалась идти к его друзьям, сказав что устала. Он сначала молчал, потом сказал: 'Ты всегда находишь отговорки. Мои друзья уже думают, что ты меня не любишь.' Потом весь вечер демонстративно молчал и хлопал дверями.",
            "block": "control"
        },
        {
            "question": "Вспомните конкретную ситуацию, когда вы напомнили партнеру о его действии или словах, а он отрицал, что это происходило. Опишите, что именно он сказал и как вы себя почувствовали.",
            "answer": "Я напомнила ему, что он вчера обещал забрать ребенка из садика. Он сказал: 'Я такого не говорил, ты все выдумываешь. У тебя плохая память.' Я почувствовала себя сумасшедшей, начала сомневаться в себе.",
            "block": "gaslighting"
        },
        {
            "question": "Опишите последний случай, когда ваш партнер очень разозлился. Что именно он делал и говорил в первые 5 минут? Приведите его точные слова.",
            "answer": "Он злился из-за того, что ужин был не готов. Кричал: 'Ты вообще ничего не умеешь! Я весь день работаю, а ты даже поесть нормально не можешь приготовить!' Швырнул тарелку в раковину, хлопнул дверью и ушел.",
            "block": "emotion"
        },
        {
            "question": "Опишите последний раз, когда вы отказались от интимной близости. Как именно отреагировал партнер? Что он сказал или сделал?",
            "answer": "Я сказала, что не в настроении. Он ответил: 'Ты никогда не в настроении. Наверное, у тебя кто-то есть.' Потом всю неделю был холодным и говорил, что я его не люблю.",
            "block": "intimacy"
        },
        {
            "question": "Опишите недавнее событие, где вы были с партнером среди других людей. Как он вел себя с вами при свидетелях vs дома после?",
            "answer": "На дне рождения у друзей он был очень внимательным, обнимал меня, говорил комплименты. А дома сразу сказал: 'Ты опять много болтала, всех раздражала своими историями. Мне было стыдно за тебя.'",
            "block": "social"
        }
    ]
    
    # Инициализируем сервисы
    ai_service = AIService()
    pdf_service = HTMLPDFService()
    
    # Выполняем анализ
    print("🤖 Выполняем AI анализ...")
    analysis_result = await ai_service.profile_partner_free_form(
        text_answers=test_answers,
        user_id=123,
        partner_name="Дмитрий",
        partner_description="Муж, 35 лет, работает менеджером",
        partner_basic_info="Женат 8 лет, двое детей"
    )
    
    print(f"✅ Анализ завершен! Риск: {analysis_result['overall_risk_score']}%")
    print(f"🔍 Тип: {analysis_result['personality_type']}")
    
    # Показываем динамические данные
    print("\n📊 Динамические блоки:")
    for block, score in analysis_result['block_scores'].items():
        print(f"  {block}: {score}/10")
    
    print(f"\n🚩 Красные флаги ({len(analysis_result['red_flags'])}):")
    for i, flag in enumerate(analysis_result['red_flags'][:5], 1):
        print(f"  {i}. {flag}")
    
    # Генерируем PDF
    print("\n📄 Генерируем динамический PDF отчет...")
    pdf_bytes = await pdf_service.generate_partner_report_html(
        analysis_data=analysis_result,
        user_id=123,
        partner_name="Дмитрий"
    )
    
    # Сохраняем PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"dynamic_test_report_{timestamp}.pdf"
    
    with open(pdf_filename, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ PDF сохранен: {pdf_filename}")
    print(f"📊 Размер файла: {len(pdf_bytes)} байт")
    
    # Показываем извлеченные Dark Triad данные
    dark_triad = pdf_service._extract_dark_triad_scores(analysis_result, analysis_result['overall_risk_score'])
    print(f"\n🎭 Dark Triad оценки:")
    print(f"  Нарциссизм: {dark_triad['narcissism']}/10")
    print(f"  Макиавеллизм: {dark_triad['machiavellianism']}/10") 
    print(f"  Психопатия: {dark_triad['psychopathy']}/10")
    
    # Показываем персонализированные инсайты
    insights = pdf_service._generate_personalized_insights(analysis_result, "Дмитрий", analysis_result['overall_risk_score'])
    print(f"\n💡 Персонализированные инсайты:")
    print(f"  Предупреждающие знаки: {len(insights['warning_signs'])}")
    print(f"  Поведенческие паттерны: {len(insights['behavioral_patterns'])}")
    print(f"  Защитные механизмы: {len(insights['protective_mechanisms'])}")
    print(f"  Ресурсы помощи: {len(insights['help_resources'])}")
    
    print(f"\n🎉 Тест завершен! Все блоки теперь динамические и персонализированные!")
    
    # Сохраняем результаты анализа для изучения
    results_filename = f"dynamic_analysis_result_{timestamp}.json"
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Результаты анализа сохранены: {results_filename}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_blocks()) 