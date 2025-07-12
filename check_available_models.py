#!/usr/bin/env python3
"""
Проверка доступных моделей Claude
"""

import asyncio
from anthropic import AsyncAnthropic
from app.core.config import settings

async def check_models():
    """Проверяем доступные модели"""
    
    client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
    
    # Список моделей для проверки
    models_to_test = [
        "claude-3-5-sonnet-20241022",      # Текущая рабочая
        "claude-3-7-sonnet-20250201",      # Предполагаемая 3.7
        "claude-3-5-sonnet-20250115",      # Возможная новая версия
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229"
    ]
    
    print("🔍 ПРОВЕРКА ДОСТУПНЫХ МОДЕЛЕЙ CLAUDE")
    print("=" * 50)
    
    for model in models_to_test:
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            print(f"✅ {model} - РАБОТАЕТ")
        except Exception as e:
            if "not_found_error" in str(e):
                print(f"❌ {model} - НЕ НАЙДЕНА")
            else:
                print(f"⚠️  {model} - ОШИБКА: {str(e)[:100]}")
    
    print("\n" + "=" * 50)
    print("💡 РЕКОМЕНДАЦИЯ:")
    print("Используй claude-3-5-sonnet-20241022 с увеличенными токенами")
    print("Claude 3.7 пока недоступна через API")

if __name__ == "__main__":
    asyncio.run(check_models()) 