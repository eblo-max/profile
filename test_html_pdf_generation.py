#!/usr/bin/env python3
"""Test HTML to PDF generation using Claude"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.append(str(Path(__file__).parent))

from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService


async def test_html_pdf_generation():
    """Test HTML PDF generation with Claude"""
    
    print("🎨 ТЕСТ HTML-PDF ГЕНЕРАЦИИ ЧЕРЕЗ CLAUDE")
    print("=" * 50)
    
    # Test data
    partner_name = "Александр Петров"
    user_id = 12345
    
    # Mock analysis data
    analysis_data = {
        "partner_name": partner_name,
        "overall_risk_score": 85.5,
        "urgency_level": "CRITICAL",
        "block_scores": {
            "narcissism": 8.2,
            "control": 9.1,
            "gaslighting": 7.8,
            "emotion": 8.9,
            "intimacy": 9.3,
            "social": 8.5
        },
        "dark_triad": {
            "narcissism": 8.1,
            "psychopathy": 7.9,
            "machiavellianism": 8.4
        },
        "red_flags": [
            "Постоянно контролирует телефон и социальные сети",
            "Изолирует от друзей и семьи",
            "Применяет эмоциональное давление",
            "Обесценивает достижения и мнения",
            "Использует газлайтинг в конфликтах"
        ],
        "survival_guide": [
            "Сохраняйте связь с доверенными людьми",
            "Ведите дневник событий для объективности",
            "Изучите признаки эмоционального абьюза",
            "Обратитесь к психологу за поддержкой",
            "Создайте план безопасности на случай эскалации"
        ],
        "psychological_profile": "Партнер демонстрирует выраженные нарциссические черты с тенденциями к контролю и манипуляциям. Высокий риск эмоционального абьюза.",
        "analysis_blocks": [
            {
                "title": "Нарциссические черты",
                "content": "Завышенная самооценка, потребность в восхищении, отсутствие эмпатии",
                "risk_level": "HIGH"
            },
            {
                "title": "Контролирующее поведение", 
                "content": "Ограничение свободы, контроль финансов и социальных контактов",
                "risk_level": "CRITICAL"
            }
        ]
    }
    
    try:
        print(f"👤 Партнер: {partner_name}")
        print(f"📊 Риск: {analysis_data['overall_risk_score']}%")
        print(f"⚠️ Уровень: {analysis_data['urgency_level']}")
        print()
        
        # Step 1: Initialize HTML PDF service
        print("🔧 Инициализация HTML-PDF сервиса...")
        html_pdf_service = HTMLPDFService()
        print("✅ Сервис инициализирован")
        print()
        
        # Step 2: Generate HTML with Claude
        print("🤖 Генерация HTML через Claude...")
        html_content = await html_pdf_service._generate_html_with_claude(
            analysis_data, partner_name
        )
        
        print(f"✅ HTML сгенерирован ({len(html_content)} символов)")
        
        # Save HTML for inspection
        html_file = Path(f"partner_report_{partner_name.replace(' ', '_')}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📁 HTML сохранен: {html_file}")
        print()
        
        # Step 3: Convert to PDF
        print("📄 Конвертация HTML в PDF...")
        try:
            pdf_bytes = await html_pdf_service._convert_html_to_pdf_playwright(html_content)
            
            # Save PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_file = Path(f"html_partner_report_{partner_name.replace(' ', '_')}_{timestamp}.pdf")
            
            with open(pdf_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✅ PDF создан: {pdf_file}")
            print(f"📊 Размер: {len(pdf_bytes)} байт ({len(pdf_bytes)/1024:.1f} KB)")
            
            # Verify PDF
            if pdf_file.exists() and pdf_file.stat().st_size > 1000:
                print("✅ PDF файл создан успешно")
                
                # Check if it's valid PDF
                with open(pdf_file, 'rb') as f:
                    header = f.read(8)
                    if header.startswith(b'%PDF-'):
                        print("✅ PDF файл валиден")
                    else:
                        print("❌ PDF файл поврежден")
                        return False
            else:
                print("❌ PDF файл не создан или слишком мал")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка конвертации в PDF: {e}")
            print("💡 Возможно, нужно установить Playwright:")
            print("   pip install playwright")
            print("   playwright install chromium")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 HTML-PDF ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("✅ Claude сгенерировал красивый HTML")
        print("✅ HTML успешно конвертирован в PDF")
        print(f"📖 Откройте {pdf_file} для просмотра")
        print(f"🌐 Также можете открыть {html_file} в браузере")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_html_pdf_generation())
    
    if result:
        print("\n🏆 HTML-PDF СИСТЕМА РАБОТАЕТ ОТЛИЧНО!")
        print("🚀 Готова заменить ReportLab!")
    else:
        print("\n💥 ТЕСТ ПРОВАЛЕН - НУЖНЫ ДОРАБОТКИ") 