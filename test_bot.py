#!/usr/bin/env python3
"""
Simple test script to check if the bot can run without errors
"""

import os
import sys

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        from main import MadridistaBot
        from features.matches import matches_handler
        from features.live import live_handler
        from live.monitor_providers import monitor_tick, POLL_SECONDS
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_bot_creation():
    """Test if bot can be created (with dummy token)"""
    try:
        print("Testing bot creation...")
        os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'
        from main import MadridistaBot
        bot = MadridistaBot()
        print("✅ Bot created successfully")
        return True
    except Exception as e:
        print(f"❌ Bot creation error: {e}")
        return False

def test_features():
    """Test if features work without API keys"""
    try:
        print("Testing features...")
        from features.live import live_handler
        result = live_handler()
        print(f"✅ Live handler works: {result[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Feature error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing MadridistaAI Bot...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_bot_creation,
        test_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot should work.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
