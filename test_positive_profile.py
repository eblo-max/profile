#!/usr/bin/env python3
"""
Test positive psychological profile for low risk
"""

import asyncio
from app.services.html_pdf_service import HTMLPDFService

async def test_positive_profile():
    """Test positive profile for low risk case"""
    
    # Create service
    pdf_service = HTMLPDFService()
    
    # Low risk test data
    analysis_data = {
        "manipulation_risk": 1.5,
        "overall_risk_score": 15,
        "psychological_profile": "Партнер показывает здоровые паттерны",
        "red_flags": [],
        "positive_traits": [
            "Эмоциональная поддержка",
            "Уважение границ",
            "Открытое общение",
            "Готовность к компромиссам"
        ],
        "block_scores": {
            "narcissism": 2.0,
            "control": 1.5,
            "gaslighting": 1.0,
            "emotion": 2.5,
            "intimacy": 2.0,
            "social": 1.5
        },
        "dark_triad": {
            "narcissism": 2.0,
            "machiavellianism": 1.5,
            "psychopathy": 1.0
        }
    }
    
    # Generate expanded profile
    expanded_profile = pdf_service._expand_psychological_profile(
        analysis_data.get("psychological_profile", ""),
        "Анна",
        15.0,
        analysis_data
    )
    
    print(f"📊 Positive profile length: {len(expanded_profile)} characters")
    print(f"📊 Word count: ~{len(expanded_profile.split())} words")
    
    # Show first part
    print("\n🔍 First 500 characters:")
    print(expanded_profile[:500])
    
    # Generate full HTML
    html_content = pdf_service._generate_beautiful_html_report(
        analysis_data,
        "Анна",
        456
    )
    
    print(f"\n📄 Full HTML length: {len(html_content)} characters")
    
    # Save HTML for inspection
    with open("positive_profile_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ Test completed! Check positive_profile_test.html")

if __name__ == "__main__":
    asyncio.run(test_positive_profile()) 