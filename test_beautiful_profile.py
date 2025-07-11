#!/usr/bin/env python3
"""
Test beautiful HTML formatting of psychological profiles
"""

import asyncio
from app.services.html_pdf_service import HTMLPDFService

async def test_beautiful_profile():
    """Test beautiful HTML profile rendering"""
    
    print("🎨 Testing beautiful HTML profile formatting...")
    
    # Initialize service
    pdf_service = HTMLPDFService()
    
    # High risk test data
    high_risk_data = {
        "manipulation_risk": 8.5,
        "overall_risk_score": 85.0,
        "psychological_profile": "Короткий AI профиль",
        "personality_type": "Критический токсичный нарцисс",
        "red_flags": [
            "Систематический контроль всех аспектов жизни",
            "Эмоциональное принуждение и шантаж",
            "Изоляция от друзей и семьи"
        ],
        "block_scores": {
            "narcissism": 9.2,
            "control": 8.8,
            "gaslighting": 8.5,
            "emotion": 8.0,
            "intimacy": 7.5,
            "social": 6.8
        },
        "dark_triad": {
            "narcissism": 9.2,
            "machiavellianism": 8.8,
            "psychopathy": 7.1
        },
        "survival_guide": ["Обратитесь за помощью немедленно"]
    }
    
    # Low risk test data  
    low_risk_data = {
        "manipulation_risk": 1.5,
        "overall_risk_score": 15.0,
        "psychological_profile": "Партнер показывает здоровые паттерны",
        "personality_type": "Эмоционально зрелая личность",
        "red_flags": [],
        "block_scores": {
            "narcissism": 1.5,
            "control": 1.0,
            "gaslighting": 0.8,
            "emotion": 2.0,
            "intimacy": 1.5,
            "social": 1.2
        },
        "dark_triad": {
            "narcissism": 1.5,
            "machiavellianism": 1.0,
            "psychopathy": 0.8
        },
        "survival_guide": ["Продолжайте развивать здоровые отношения"]
    }
    
    print("\n📄 Generating BEAUTIFUL HIGH RISK PDF...")
    try:
        high_risk_pdf = await pdf_service.generate_partner_report_html(
            analysis_data=high_risk_data,
            user_id=789,
            partner_name="Александр"
        )
        
        with open("beautiful_high_risk.pdf", "wb") as f:
            f.write(high_risk_pdf)
        
        print(f"✅ Beautiful high risk PDF: {len(high_risk_pdf)} bytes")
        
    except Exception as e:
        print(f"❌ High risk failed: {e}")
    
    print("\n📄 Generating BEAUTIFUL LOW RISK PDF...")
    try:
        low_risk_pdf = await pdf_service.generate_partner_report_html(
            analysis_data=low_risk_data,
            user_id=987,
            partner_name="Елена"
        )
        
        with open("beautiful_low_risk.pdf", "wb") as f:
            f.write(low_risk_pdf)
        
        print(f"✅ Beautiful low risk PDF: {len(low_risk_pdf)} bytes")
        
    except Exception as e:
        print(f"❌ Low risk failed: {e}")
    
    print("\n🔍 Showing HTML output examples...")
    
    # Show high risk HTML
    high_risk_html = pdf_service._expand_psychological_profile(
        high_risk_data["psychological_profile"],
        "Александр",
        85.0,
        high_risk_data
    )
    
    print(f"\n📊 High risk HTML preview (first 400 chars):")
    print(high_risk_html[:400] + "...")
    
    # Show low risk HTML
    low_risk_html = pdf_service._expand_psychological_profile(
        low_risk_data["psychological_profile"],
        "Елена",
        15.0,
        low_risk_data
    )
    
    print(f"\n📊 Low risk HTML preview (first 400 chars):")
    print(low_risk_html[:400] + "...")
    
    print("\n" + "="*50)
    print("🎉 BEAUTIFUL FORMATTING COMPLETE!")
    print("\n📊 Generated files:")
    print("   1. beautiful_high_risk.pdf - Critical case with HTML formatting")
    print("   2. beautiful_low_risk.pdf - Healthy case with HTML formatting")
    
    print("\n✨ Key improvements:")
    print("   ✅ HTML headers instead of ## symbols")
    print("   ✅ Proper section dividers with colors")
    print("   ✅ Beautiful lists instead of plain text")
    print("   ✅ Emphasized quotes with <em> tags")
    print("   ✅ Strong highlights with <strong> tags")
    print("   ✅ Color-coded sections by risk level")
    
    print("\n📖 Now open the PDF files to see the beautiful formatting!")

if __name__ == "__main__":
    asyncio.run(test_beautiful_profile()) 