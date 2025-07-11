#!/usr/bin/env python3
"""
Скрипт для запуска комплексного теста системы профилирования партнера
"""

import asyncio
import sys
from test_complete_profile_system import main

if __name__ == "__main__":
    print("🚀 Запускаю комплексный тест системы профилирования партнера...")
    print("🔄 Это может занять 30-60 секунд...")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Тест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        sys.exit(1) 