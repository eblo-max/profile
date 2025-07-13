#!/usr/bin/env python3
"""
Тест обновленного форматирования анализа
"""
import asyncio
import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import ai_service
from app.services.html_pdf_service import HTMLPDFService

async def test_updated_formatting():
    """Тестируем обновленное форматирование с центрированным заголовком и красными заголовками"""
    
    # Тестовые данные - реалистичные ответы про абьюзера
    test_answers = [
        {
            "question": "Опишите конкретную ситуацию за последние 2 недели, когда вы дали партнеру критическую обратную связь о его поведении или действиях. Какими были его первые слова и реакция в первые 10 секунд?",
            "answer": "Когда я сказала Дмитрию, что он слишком грубо разговаривает с официантами, он сразу повысил голос: 'Ты что, совсем дура? Я просто требую нормального сервиса!' Потом добавил: 'Ты всегда защищаешь чужих людей больше, чем меня'. Лицо покраснело, кулаки сжались."
        },
        {
            "question": "Вспомните последний раз, когда ваш партнер очень сильно разозлился. Что именно он делал и говорил в первые 5 минут?",
            "answer": "Дмитрий кричал: 'Ты специально меня бесишь! Ты знаешь, что я ненавижу, когда ты опаздываешь!' Швырнул телефон об стену, пинал стул. Потом схватил меня за плечи и тряс: 'Смотри на меня, когда я с тобой разговариваю!' Глаза были красные от злости."
        },
        {
            "question": "Опишите конкретную ситуацию, когда вы напомнили партнеру о его действии или словах, а он отрицал, что это происходило. Воспроизведите точный диалог.",
            "answer": "Я: 'Дмитрий, вчера ты сказал, что я толстая корова'. Он: 'Я такого никогда не говорил! У тебя проблемы с памятью'. Я: 'Но ты же сказал это при Ане'. Он: 'Аня ничего не слышала, ты все выдумываешь. Может тебе к врачу сходить проверить голову?'"
        }
    ]
    
    print("🧪 Тестируем обновленное форматирование анализа...")
    
    try:
        # Получаем анализ от AI
        result = await ai_service.profile_partner_free_form(
            text_answers=test_answers,
            user_id=12345,
            partner_name="Дмитрий",
            partner_description="Мой парень, с которым встречаюсь 2 года",
            partner_basic_info="Дмитрий, 28 лет, работает менеджером"
        )
        
        print("✅ AI анализ получен")
        print("📝 Проверяем форматирование...")
        
        # Проверяем наличие HTML стилей в анализе
        analysis_text = result.get('psychological_profile', '')
        
        if 'analysis-main-title' in analysis_text:
            print("✅ Основной заголовок с центрированием найден")
        else:
            print("❌ Основной заголовок с центрированием НЕ найден")
            
        if 'analysis-section-header' in analysis_text:
            print("✅ Красные заголовки разделов найдены")
        else:
            print("❌ Красные заголовки разделов НЕ найдены")
        
        # Показываем фрагмент анализа
        print("\n📄 Фрагмент анализа:")
        print("=" * 60)
        print(analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text)
        print("=" * 60)
        
        # Генерируем PDF для проверки
        pdf_data = {
            'partner_name': 'Дмитрий',
            'date': datetime.now().strftime('%d.%m.%Y'),
            'report_id': 'TEST-001',
            'risk_score': result.get('risk_score', 85),
            'personality_type': result.get('personality_type', 'Манипулятивный нарцисс'),
            'red_flags': result.get('red_flags', []),
            'psychological_profile': analysis_text
        }
        
        html_pdf_service = HTMLPDFService()
        pdf_content = await html_pdf_service.generate_partner_report_html(
            pdf_data, user_id=12345, partner_name="Дмитрий"
        )
        
        # Сохраняем PDF
        with open('test_updated_formatting.pdf', 'wb') as f:
            f.write(pdf_content)
        
        print("✅ PDF сгенерирован: test_updated_formatting.pdf")
        print("🎯 Проверьте PDF на:")
        print("   - Центрированный основной заголовок")
        print("   - Красные заголовки разделов с тенью")
        print("   - Отсутствие лишних пустых страниц")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_updated_formatting()) 