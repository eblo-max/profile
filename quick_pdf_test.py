#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService

# Высокий риск - токсичный партнер
HIGH_RISK_ANSWERS = [
    {"question": "Контроль", "answer": "Да, он контролирует все мои действия"},
    {"question": "Критика", "answer": "Да, он постоянно критикует меня"},
    {"question": "Изоляция", "answer": "Да, он запрещает мне видеться с друзьями"},
    {"question": "Манипуляции", "answer": "Да, он использует эмоциональный шантаж"},
    {"question": "Агрессия", "answer": "Да, он может кричать и угрожать"},
    {"question": "Ревность", "answer": "Да, он патологически ревнив"},
    {"question": "Унижение", "answer": "Да, он унижает меня публично"},
    {"question": "Финансовый контроль", "answer": "Да, он контролирует все деньги"},
    {"question": "Газлайтинг", "answer": "Да, он заставляет меня сомневаться в себе"},
    {"question": "Изоляция от семьи", "answer": "Да, он настроил меня против семьи"}
]

# Низкий риск - здоровые отношения
LOW_RISK_ANSWERS = [
    {"question": "Поддержка", "answer": "Да, он всегда меня поддерживает"},
    {"question": "Уважение", "answer": "Да, он уважает мои границы"},
    {"question": "Общение", "answer": "Да, мы открыто обсуждаем проблемы"},
    {"question": "Доверие", "answer": "Да, между нами полное доверие"},
    {"question": "Независимость", "answer": "Да, я свободна в своих решениях"},
    {"question": "Друзья", "answer": "Да, он рад моим дружеским отношениям"},
    {"question": "Семья", "answer": "Да, он хорошо ладит с моей семьей"},
    {"question": "Финансы", "answer": "Да, мы совместно планируем бюджет"},
    {"question": "Эмоции", "answer": "Да, он понимает мои чувства"},
    {"question": "Развитие", "answer": "Да, он поддерживает мои цели"}
]

async def test_different_risk_levels():
    """Тестируем разные уровни риска"""
    print("🧪 Тестирую бесшовный PDF дизайн для разных уровней риска...")
    
    ai_service = AIService()
    pdf_service = HTMLPDFService()
    
    # Тест 1: Высокий риск (токсичный партнер)
    print("\n1️⃣ Генерирую высокорисковый отчет...")
    
    high_risk_analysis = await ai_service.profile_partner(
        user_id=999,
        answers=HIGH_RISK_ANSWERS,
        partner_name="Токсичный Партнер"
    )
    
    print(f"✅ Анализ высокого риска: {high_risk_analysis['manipulation_risk']:.1f}%")
    
    # Генерируем PDF
    high_risk_pdf = await pdf_service.generate_partner_report_html(
        analysis_data=high_risk_analysis,
        user_id=999,
        partner_name="Токсичный Партнер"
    )
    
    with open("seamless_high_risk.pdf", "wb") as f:
        f.write(high_risk_pdf)
    
    print(f"✅ Высокорисковый PDF: {len(high_risk_pdf)/(1024*1024):.1f}MB")
    
    # Тест 2: Низкий риск (здоровые отношения)
    print("\n2️⃣ Генерирую низкорисковый отчет...")
    
    low_risk_analysis = await ai_service.profile_partner(
        user_id=998,
        answers=LOW_RISK_ANSWERS,
        partner_name="Здоровый Партнер"
    )
    
    print(f"✅ Анализ низкого риска: {low_risk_analysis['manipulation_risk']:.1f}%")
    
    # Генерируем PDF
    low_risk_pdf = await pdf_service.generate_partner_report_html(
        analysis_data=low_risk_analysis,
        user_id=998,
        partner_name="Здоровый Партнер"
    )
    
    with open("seamless_low_risk.pdf", "wb") as f:
        f.write(low_risk_pdf)
    
    print(f"✅ Низкорисковый PDF: {len(low_risk_pdf)/(1024*1024):.1f}MB")
    
    print("\n🎉 Бесшовные PDF готовы!")
    print("🔴 seamless_high_risk.pdf - критический риск с красным оформлением")
    print("🟢 seamless_low_risk.pdf - здоровые отношения с зеленым оформлением")
    print("\n📋 Основные улучшения:")
    print("   • Бесшовный дизайн без разрывов страниц")
    print("   • Цветовая дифференциация по уровню риска")
    print("   • Современная типографика и layout")
    print("   • Адаптивные секции и правильные отступы")
    print("   • Профессиональное оформление заголовков")

if __name__ == "__main__":
    asyncio.run(test_different_risk_levels()) 