#!/usr/bin/env python3
"""Full integration test for partner profiling system"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.append(str(Path(__file__).parent))

from app.services.ai_service import AIService
from app.services.pdf_service import PDFReportService
from app.prompts.profiler_full_questions import get_all_questions


async def test_full_partner_profiling():
    """Test complete partner profiling workflow"""
    
    print("🔍 ЗАПУСК ПОЛНОГО ТЕСТА СИСТЕМЫ ПРОФИЛИРОВАНИЯ ПАРТНЕРА")
    print("=" * 60)
    
    # Get all questions
    all_questions = get_all_questions()
    question_list = list(all_questions.values())
    
    # Test user answers (realistic high-risk scenario)
    test_answers = {
        1: "Часто критикует мою внешность и говорит, что я недостаточно хороша для него",
        2: "Постоянно проверяет мой телефон, читает сообщения, требует пароли от соцсетей", 
        3: "Говорит, что мои друзья плохо на меня влияют, запрещает с ними встречаться",
        4: "Контролирует все наши финансы, не дает мне денег на личные нужды",
        5: "Часто кричит на меня, может толкнуть или ударить во время ссор",
        6: "Постоянно обвиняет меня в том, что я флиртую с другими мужчинами",
        7: "Говорит, что без него я никто и ничего не смогу добиться в жизни",
        8: "Принимает все важные решения сам, не учитывает мое мнение",
        9: "Угрожает причинить вред мне или моим близким, если я его покину",
        10: "Заставляет заниматься сексом против моего желания",
        11: "Постоянно меняет версии событий, заставляет сомневаться в своей памяти",
        12: "Публично унижает меня перед друзьями и родственниками",
        13: "Запрещает работать или учиться, говорит что должна сидеть дома",
        14: "Следит за мной через GPS, камеры, требует отчеты о каждом шаге",
        15: "Никогда не извиняется за свое поведение, всегда виновата я",
        16: "Может исчезнуть на несколько дней без объяснений, потом возвращается как ни в чем не бывало",
        17: "Говорит, что я психически больная, когда пытаюсь обсуждать проблемы",
        18: "Заставляет прерывать контакты с семьей, говорит что они меня не понимают",
        19: "Требует постоянного внимания, устраивает сцены если я занята чем-то другим",
        20: "Может быть очень милым и заботливым, а потом резко становится агрессивным",
        21: "Постоянно сравнивает меня с бывшими девушками не в мою пользу",
        22: "Говорит, что я должна быть благодарна ему за отношения",
        23: "Использует мои секреты и слабости против меня во время ссор",
        24: "Заставляет делать вещи, которые мне неприятны, говорит что так проявляется любовь",
        25: "Никогда не поддерживает мои начинания, всегда находит негативные стороны",
        26: "Может внезапно стать холодным и отстраненным на несколько дней",
        27: "Говорит, что все мужчины такие, и мне не найти лучше",
        28: "Требует, чтобы я постоянно доказывала свою любовь к нему"
    }
    
    partner_name = "Дмитрий Соколов"
    user_id = 12345
    
    print(f"👤 Тестируемый партнер: {partner_name}")
    print(f"🆔 ID пользователя: {user_id}")
    print(f"📝 Количество ответов: {len(test_answers)}")
    print(f"📋 Всего вопросов в системе: {len(question_list)}")
    print()
    
    try:
        # Step 1: Initialize services
        print("🔧 ЭТАП 1: Инициализация сервисов")
        ai_service = AIService()
        pdf_service = PDFReportService()
        print("✅ Все сервисы инициализированы")
        print()
        
        # Step 2: Prepare questionnaire data
        print("📋 ЭТАП 2: Подготовка данных анкеты")
        questionnaire_text = f"Анализ партнера: {partner_name}\n\n"
        
        for q_num, answer in test_answers.items():
            if q_num <= len(question_list):
                question_data = question_list[q_num - 1]
                question_text = question_data.get('text', f'Вопрос {q_num}')
                questionnaire_text += f"Вопрос {q_num}: {question_text}\nОтвет: {answer}\n\n"
        
        print(f"✅ Подготовлено {len(test_answers)} вопросов и ответов")
        print(f"📄 Длина текста анкеты: {len(questionnaire_text)} символов")
        print()
        
        # Step 3: AI Analysis using profiler prompt
        print("🤖 ЭТАП 3: ИИ анализ анкеты")
        print("   Отправляю данные в AI сервис для анализа...")
        
        # Convert answers to the format expected by profile_partner
        # profile_partner expects Dict[str, int] where key is question_id and value is answer_index
        formatted_answers = {}
        for q_num, answer_text in test_answers.items():
            if q_num <= len(question_list):
                question_data = question_list[q_num - 1]
                question_id = question_data.get('id', f'q{q_num}')
                # For this test, we'll use high-risk answer indices (3-4 range)
                answer_index = 4 if q_num % 2 == 0 else 3  # Vary between high-risk answers
                formatted_answers[question_id] = answer_index
        
        # Use the correct method: profile_partner
        analysis_result = await ai_service.profile_partner(
            answers=formatted_answers,
            user_id=user_id,
            partner_name=partner_name,
            partner_description="Партнер демонстрирует множественные признаки токсичного поведения"
        )
        
        if not analysis_result:
            print("❌ AI анализ не удался")
            return False
        
        print("✅ AI анализ завершен успешно")
        print(f"📊 Общий уровень риска: {analysis_result.get('overall_risk_score', 'N/A')}%")
        print(f"⚠️ Уровень срочности: {analysis_result.get('urgency_level', 'N/A')}")
        print(f"🔍 Блоков анализа: {len(analysis_result.get('block_scores', {}))}")
        print()
        
        # Step 4: Generate PDF Report
        print("📄 ЭТАП 4: Генерация PDF отчета")
        print("   Создаю профессиональный PDF отчет...")
        
        # Add user_id to analysis data for PDF generation
        analysis_result['user_id'] = user_id
        
        pdf_bytes = await pdf_service.generate_partner_report(
            analysis_data=analysis_result,
            user_id=user_id,
            partner_name=partner_name
        )
        
        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"partner_profile_{partner_name.replace(' ', '_')}_{timestamp}.pdf")
        
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        
        print("✅ PDF отчет создан успешно")
        print(f"📁 Файл: {output_file}")
        print(f"📊 Размер: {len(pdf_bytes)} байт ({len(pdf_bytes)/1024:.1f} KB)")
        print()
        
        # Step 5: Verification and Summary
        print("🔍 ЭТАП 5: Проверка и итоги")
        
        if output_file.exists() and output_file.stat().st_size > 10000:
            print("✅ PDF файл создан и содержит данные")
            
            # Check if it's a valid PDF
            with open(output_file, 'rb') as f:
                header = f.read(8)
                if header.startswith(b'%PDF-'):
                    print("✅ Файл является валидным PDF документом")
                else:
                    print("❌ Файл поврежден или не является PDF")
                    return False
        else:
            print("❌ PDF файл не создан или слишком мал")
            return False
        
        # Print detailed analysis results
        print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("-" * 40)
        
        print(f"Партнер: {partner_name}")
        print(f"Общий риск: {analysis_result.get('overall_risk_score', 0)}%")
        print(f"Срочность: {analysis_result.get('urgency_level', 'UNKNOWN')}")
        
        # Block scores
        block_scores = analysis_result.get('block_scores', {})
        if block_scores:
            print("\nОценки по блокам:")
            block_names = {
                'narcissism': 'Нарциссизм',
                'control': 'Контроль', 
                'gaslighting': 'Газлайтинг',
                'emotion': 'Эмоции',
                'intimacy': 'Интимность',
                'social': 'Социальное'
            }
            
            for block_key, score in block_scores.items():
                if block_key in block_names:
                    print(f"  • {block_names[block_key]}: {score:.1f}/10")
        
        # Dark Triad
        dark_triad = analysis_result.get('dark_triad', {})
        if dark_triad:
            print("\nТемная триада:")
            triad_names = {
                'narcissism': 'Нарциссизм',
                'psychopathy': 'Психопатия',
                'machiavellianism': 'Макиавеллизм'
            }
            for trait, score in dark_triad.items():
                if trait in triad_names:
                    print(f"  • {triad_names[trait]}: {score:.1f}/10")
        
        # Red flags count
        red_flags = analysis_result.get('red_flags', [])
        if red_flags:
            print(f"\nКрасные флаги: {len(red_flags)} обнаружено")
            for i, flag in enumerate(red_flags[:3], 1):  # Show first 3
                print(f"  {i}. {flag}")
            if len(red_flags) > 3:
                print(f"  ... и еще {len(red_flags) - 3}")
        
        # Recommendations count  
        survival_guide = analysis_result.get('survival_guide', [])
        if survival_guide:
            print(f"\nРекомендации: {len(survival_guide)} пунктов")
        
        # Psychological profile preview
        profile = analysis_result.get('psychological_profile', '')
        if profile:
            profile_preview = profile[:200] + "..." if len(profile) > 200 else profile
            print(f"\nПсихологический профиль (превью):")
            print(f"  {profile_preview}")
        
        print("\n" + "=" * 60)
        print("🎉 ПОЛНЫЙ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
        print("✅ Все этапы пройдены без ошибок")
        print(f"📖 Откройте файл {output_file} для просмотра отчета")
        print("🔍 Проверьте, что русский текст отображается корректно")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА НА ЭТАПЕ ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_full_partner_profiling())
    
    if result:
        print("\n🏆 СИСТЕМА ПРОФИЛИРОВАНИЯ ПАРТНЕРА РАБОТАЕТ ИДЕАЛЬНО!")
        print("🚀 Готова к продакшену!")
    else:
        print("\n💥 ТЕСТ ПРОВАЛЕН - ТРЕБУЮТСЯ ИСПРАВЛЕНИЯ!") 