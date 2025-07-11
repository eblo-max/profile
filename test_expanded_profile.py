#!/usr/bin/env python3
"""
Test expanded psychological profile generation
"""

import asyncio
from app.services.html_pdf_service import HTMLPDFService

async def test_expanded_profile():
    """Test the expanded psychological profile generation"""
    
    # Create service
    pdf_service = HTMLPDFService()
    
    # High risk test data
    analysis_data = {
        "manipulation_risk": 8.5,
        "overall_risk_score": 85,
        "psychological_profile": "Короткий профиль от AI",
        "red_flags": [
            "Контролирует финансы",
            "Изолирует от друзей",
            "Эмоциональные вспышки",
            "Никогда не извиняется"
        ],
        "block_scores": {
            "narcissism": 8.5,
            "control": 9.0,
            "gaslighting": 7.5,
            "emotion": 8.0,
            "intimacy": 7.0,
            "social": 6.5
        },
        "dark_triad": {
            "narcissism": 8.5,
            "machiavellianism": 9.0,
            "psychopathy": 6.5
        }
    }
    
    # Generate expanded profile
    expanded_profile = pdf_service._expand_psychological_profile(
        analysis_data.get("psychological_profile", ""),
        "Дмитрий",
        85.0,
        analysis_data
    )
    
    print(f"📊 Expanded profile length: {len(expanded_profile)} characters")
    print(f"📊 Word count: ~{len(expanded_profile.split())} words")
    
    # Show first part
    print("\n🔍 First 500 characters:")
    print(expanded_profile[:500])
    
    # Generate full HTML
    html_content = pdf_service._generate_beautiful_html_report(
        analysis_data,
        "Дмитрий",
        123
    )
    
    print(f"\n📄 Full HTML length: {len(html_content)} characters")
    
    # Save HTML for inspection
    with open("expanded_profile_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ Test completed! Check expanded_profile_test.html")

if __name__ == "__main__":
    asyncio.run(test_expanded_profile()) 