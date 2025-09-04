#!/usr/bin/env python3
"""
Diagnostic script to identify why the bot isn't working
"""

import os
import sys
import requests

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return False
    
    if token == "your_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN is still placeholder")
        return False
    
    if len(token) < 40:
        print("❌ TELEGRAM_BOT_TOKEN too short")
        return False
    
    print(f"✅ TELEGRAM_BOT_TOKEN: {token[:10]}...{token[-10:]}")
    return True

def check_telegram_api():
    """Check if bot token is valid with Telegram API"""
    print("\n🔍 Checking Telegram API...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ No token to test")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot is valid: @{bot_info.get('username')} ({bot_info.get('first_name')})")
                return True
            else:
                print(f"❌ Telegram API error: {data.get('description')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'telegram',
        'openai',
        'requests',
        'pytz'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        return False
    
    return True

def check_code_compilation():
    """Check if the bot code compiles"""
    print("\n🔍 Checking code compilation...")
    
    try:
        from main import MadridistaBot
        print("✅ Main module compiles")
        return True
    except Exception as e:
        print(f"❌ Compilation error: {e}")
        return False

def check_features():
    """Check if features work without API keys"""
    print("\n🔍 Checking features...")
    
    try:
        from features.live import live_handler
        result = live_handler()
        print(f"✅ Live handler: {result[:50]}...")
        
        from features.matches import matches_handler
        print("✅ Matches handler imported")
        
        return True
    except Exception as e:
        print(f"❌ Feature error: {e}")
        return False

def main():
    """Run all diagnostics"""
    print("🔧 MadridistaAI Bot Diagnostics")
    print("=" * 50)
    
    checks = [
        check_environment,
        check_telegram_api,
        check_dependencies,
        check_code_compilation,
        check_features
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Bot should work.")
        print("\n💡 If bot still doesn't respond, check:")
        print("   - Railway deployment status")
        print("   - Bot privacy mode in @BotFather")
        print("   - Bot is actually running on Railway")
    else:
        print("❌ Some checks failed. Fix the issues above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
