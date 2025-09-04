#!/usr/bin/env python3
"""
Test script for MadridistaAI Telegram Bot
This script tests if the bot can be imported and configured correctly
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from platforms.telegram_client import MadridistaTelegramBot
        print("✅ Telegram client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Telegram client: {e}")
        return False
    
    try:
        from ai_engine.gpt_engine import generate_short_post
        print("✅ AI engine imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI engine: {e}")
        return False
    
    try:
        from prompts.fan_prompts import PROMPTS
        print("✅ Prompts imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import prompts: {e}")
        return False
    
    return True

def test_environment():
    """Test if required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    load_dotenv(override=False)
    
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    return True

def test_bot_creation():
    """Test if the bot can be created (without running it)"""
    print("\n🔍 Testing bot creation...")
    
    try:
        from platforms.telegram_client import MadridistaTelegramBot
        
        # This will fail if TELEGRAM_BOT_TOKEN is not set, but that's expected
        bot = MadridistaTelegramBot()
        print("✅ Bot created successfully")
        return True
    except ValueError as e:
        if "TELEGRAM_BOT_TOKEN" in str(e):
            print("✅ Bot creation test passed (token validation working)")
            return True
        else:
            print(f"❌ Unexpected error creating bot: {e}")
            return False
    except Exception as e:
        print(f"❌ Failed to create bot: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 MadridistaAI Telegram Bot Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("Bot Creation Test", test_bot_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("\nTo start the bot, run:")
        print("  python main_telegram.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCheck the setup guide: TELEGRAM_SETUP.md")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
