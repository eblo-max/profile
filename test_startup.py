#!/usr/bin/env python3
"""Minimal startup test"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    print("=== TESTING IMPORTS ===")
    
    try:
        print("1. Testing core imports...")
        from app.core.config import settings
        print(f"✅ Config: Environment={settings.ENVIRONMENT}")
        
        print("2. Testing database...")
        from app.core.database import init_db
        print("✅ Database imports OK")
        
        print("3. Testing Redis...")
        from app.core.redis import init_redis
        print("✅ Redis imports OK")
        
        print("4. Testing bot handlers...")
        from app.bot.handlers import register_all_handlers
        print("✅ Handlers imports OK")
        
        print("5. Testing middlewares...")
        from app.bot.middlewares import register_all_middlewares  
        print("✅ Middlewares imports OK")
        
        print("6. Testing main app...")
        from app.main import create_app
        print("✅ Main app imports OK")
        
        print("=== ALL IMPORTS SUCCESSFUL ===")
        return True
        
    except Exception as e:
        print(f"❌ IMPORT ERROR: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("\n=== TESTING APP CREATION ===")
    
    try:
        from app.main import create_app
        app = create_app()
        print("✅ FastAPI app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ APP CREATION ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 STARTUP DIAGNOSTIC TEST")
    print("="*50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test app creation  
    app_ok = test_app_creation()
    
    if imports_ok and app_ok:
        print("\n🎉 ALL TESTS PASSED - App should start normally")
        sys.exit(0)
    else:
        print("\n💥 TESTS FAILED - Check errors above")
        sys.exit(1) 