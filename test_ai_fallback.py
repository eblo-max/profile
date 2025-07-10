#!/usr/bin/env python3
"""
Test AI fallback analysis system
"""

import asyncio
from app.services.ai_service import ai_service
from app.prompts.profiler_full_questions import QUESTION_ORDER

async def test_fallback_analysis():
    """Test fallback analysis without AI services"""
    print("🔍 Тестирование fallback-анализа...")
    
    # Create test answers (medium risk)
    test_answers = {}
    for i, question_id in enumerate(QUESTION_ORDER):
        # Simulate medium risk answers (index 2 out of 0-4)
        test_answers[question_id] = 2
    
    try:
        # Test profile analysis
        result = await ai_service.profile_partner(
            answers=test_answers,
            user_id=1,
            partner_name="Тест",
            partner_description="Тестовый партнер",
            use_cache=False
        )
        
        print("✅ Fallback-анализ выполнен успешно!")
        print(f"📊 Общий риск: {result['overall_risk_score']}%")
        print(f"⚠️ Уровень срочности: {result['urgency_level']}")
        print(f"📝 Длина анализа: {len(result['analysis'])} символов")
        
        # Check if it's fallback
        if result.get('ai_available') == False:
            print("🤖 Используется автоматический анализ (AI недоступен)")
        else:
            print("🤖 Используется AI-анализ")
            
        # Show first part of analysis
        print("\n📋 Начало анализа:")
        print(result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis'])
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка fallback-анализа: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fallback_analysis())
    if success:
        print("\n🎉 Тест fallback-анализа пройден успешно!")
    else:
        print("\n💥 Тест fallback-анализа провален!") 