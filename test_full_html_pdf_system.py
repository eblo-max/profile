#!/usr/bin/env python3
"""Test complete HTML-PDF system with full professional report"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.html_pdf_service import HTMLPDFService
from app.services.ai_service import AIService
from app.prompts.profiler_full_questions import get_all_questions


async def test_full_html_pdf_system():
    """Test complete HTML-PDF system with real AI analysis"""
    
    print("🔍 Starting full HTML-PDF system test...")
    
    # Initialize services
    ai_service = AIService()
    html_pdf_service = HTMLPDFService()
    
    # Get test questions
    all_questions = get_all_questions()
    question_keys = list(all_questions.keys())
    
    # Create realistic test answers using actual question format
    test_answers = [
        {
            'question_id': 0,
            'question': all_questions[question_keys[0]]['text'],
            'answer': 'Мой партнер Дмитрий Соколов постоянно контролирует мои действия. Он всегда спрашивает где я была, с кем общалась, что делала. Когда я прихожу домой, он проверяет мой телефон и требует объяснений по каждому сообщению. Если я задерживаюсь на работе, он звонит каждые 15 минут.'
        },
        {
            'question_id': 1, 
            'question': all_questions[question_keys[1]]['text'],
            'answer': 'Да, он часто говорит что я неправильно помню события. Когда я напоминаю ему о его обещаниях или словах, он говорит что я все выдумываю. Недавно он сказал что никогда не кричал на меня, хотя это было вчера. Он убеждает меня что у меня плохая память.'
        },
        {
            'question_id': 2,
            'question': all_questions[question_keys[2]]['text'], 
            'answer': 'Он не разрешает мне встречаться с подругами. Говорит что они плохо на меня влияют и настраивают против него. Когда я хочу пойти к маме, он устраивает скандал и говорит что я его не люблю. Я уже почти не общаюсь с друзьями.'
        },
        {
            'question_id': 3,
            'question': all_questions[question_keys[3]]['text'],
            'answer': 'Он очень вспыльчивый. Может накричать из-за любой мелочи - если ужин не готов, если я не так поставила обувь, если забыла что-то купить. Когда злится, может не разговаривать со мной несколько дней. Я всегда хожу на цыпочках.'
        },
        {
            'question_id': 4,
            'question': all_questions[question_keys[4]]['text'],
            'answer': 'Он считает себя самым умным и успешным. Постоянно рассказывает какой он хороший, а все остальные глупые. Говорит что без него я бы ничего не добилась. Никогда не извиняется, даже когда неправ. Всегда находит оправдания.'
        },
        {
            'question_id': 5,
            'question': all_questions[question_keys[5]]['text'],
            'answer': 'В интимной близости он думает только о себе. Не интересуется моими желаниями и потребностями. Если я не в настроении, он обижается и говорит что я его не люблю. Принуждает к близости через чувство вины.'
        },
        {
            'question_id': 6,
            'question': all_questions[question_keys[6]]['text'],
            'answer': 'Он изолирует меня от семьи и друзей. Говорит что они плохо влияют на наши отношения. Когда я общаюсь с кем-то, он устраивает скандалы и обвиняет меня в измене. Из-за этого я почти ни с кем не общаюсь.'
        },
        {
            'question_id': 7,
            'question': all_questions[question_keys[7]]['text'],
            'answer': 'Да, он часто унижает меня публично. Может высмеять мои слова при друзьях, критиковать мою внешность или поведение. Говорит что это шутки, но мне больно и стыдно. Я стараюсь не появляться с ним в обществе.'
        }
    ]
    
    print(f"📝 Using {len(test_answers)} test answers")
    print(f"📋 Total questions available: {len(all_questions)}")
    
    # Step 1: Get AI analysis
    print("🤖 Getting AI analysis...")
    try:
        analysis_result = await ai_service.profile_partner(test_answers, user_id=12345)
        print(f"✅ AI analysis completed")
        print(f"📊 Overall risk: {analysis_result.get('overall_risk_score', 0):.1f}%")
        print(f"⚠️ Urgency: {analysis_result.get('urgency_level', 'UNKNOWN')}")
        
        # Print block scores
        block_scores = analysis_result.get('block_scores', {})
        print("📈 Block scores:")
        for block, score in block_scores.items():
            print(f"  • {block}: {score:.1f}/10")
            
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return False
    
    # Step 2: Generate HTML-PDF report
    print("📄 Generating HTML-PDF report...")
    try:
        partner_name = "Дмитрий Соколов"
        pdf_bytes = await html_pdf_service.generate_partner_report_html(
            analysis_result,
            user_id=12345,
            partner_name=partner_name
        )
        
        print(f"✅ HTML-PDF generated successfully")
        print(f"📦 PDF size: {len(pdf_bytes)} bytes ({len(pdf_bytes) / 1024:.1f} KB)")
        
        # Save PDF file
        pdf_path = f"test_html_report_{partner_name.replace(' ', '_')}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"💾 PDF saved as: {pdf_path}")
        
        # Verify PDF content
        if len(pdf_bytes) > 50000:  # Should be substantial
            print("✅ PDF appears to contain substantial content")
        else:
            print("⚠️ PDF seems small, might have issues")
            
    except Exception as e:
        print(f"❌ HTML-PDF generation failed: {e}")
        return False
    
    # Step 3: Display analysis summary
    print("\n📋 ANALYSIS SUMMARY:")
    print("=" * 50)
    
    overall_risk = analysis_result.get('overall_risk_score', 0)
    urgency = analysis_result.get('urgency_level', 'UNKNOWN')
    
    print(f"👤 Partner: {partner_name}")
    print(f"🎯 Overall Risk: {overall_risk:.1f}% ({urgency})")
    
    # Block scores
    print(f"\n📊 Detailed Scores:")
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
    
    # Red flags count
    red_flags = analysis_result.get('red_flags', [])
    print(f"\n🚩 Red flags detected: {len(red_flags)}")
    
    # Recommendations count
    survival_guide = analysis_result.get('survival_guide', [])
    print(f"💡 Recommendations provided: {len(survival_guide)}")
    
    print("\n✅ FULL HTML-PDF SYSTEM TEST COMPLETED SUCCESSFULLY!")
    print(f"📄 Professional report generated: {pdf_path}")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_full_html_pdf_system())
    if success:
        print("\n🎉 All tests passed! HTML-PDF system is working correctly.")
    else:
        print("\n❌ Tests failed! Check the error messages above.")
        sys.exit(1) 