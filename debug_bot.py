#!/usr/bin/env python3
"""
Debug script to test bot startup and identify issues
"""

import os
import sys
from dotenv import load_dotenv

def debug_environment():
    """Check environment variables and dependencies"""
    print("🔍 Debugging Bot Environment...")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # Load environment
    print("\n📁 Loading environment...")
    load_dotenv(override=False)
    
    # Check required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    print("\n🔑 Environment Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first and last few characters
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    # Check optional environment variables
    optional_vars = [
        'LIVE_PROVIDER', 'SOFA_TEAM_ID', 'POLL_SECONDS',
        'LIVESCORE_RAPIDAPI_KEY', 'SOFA_RAPIDAPI_KEY'
    ]
    print("\n🔑 Optional Environment Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: NOT SET (optional)")
    
    # Test imports
    print("\n📦 Testing imports...")
    try:
        from platforms.telegram_client import MadridistaTelegramBot
        print("   ✅ MadridistaTelegramBot import successful")
    except Exception as e:
        print(f"   ❌ MadridistaTelegramBot import failed: {e}")
        return False
    
    try:
        from live.monitor_providers import monitor_tick, POLL_SECONDS
        print("   ✅ Live monitor import successful")
    except Exception as e:
        print(f"   ❌ Live monitor import failed: {e}")
    
    try:
        from features.news import news_handler
        print("   ✅ News handler import successful")
    except Exception as e:
        print(f"   ❌ News handler import failed: {e}")
    
    try:
        from features.tv import tv_handler
        print("   ✅ TV handler import successful")
    except Exception as e:
        print(f"   ❌ TV handler import failed: {e}")
    
    # Test bot creation
    print("\n🤖 Testing bot creation...")
    try:
        # Set test tokens if not present
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
        if not os.getenv('OPENAI_API_KEY'):
            os.environ['OPENAI_API_KEY'] = 'test_key'
        
        bot = MadridistaTelegramBot()
        print("   ✅ Bot creation successful")
        
        # Test bot properties
        print(f"   📱 Bot token: {bot.token[:10]}..." if len(bot.token) > 10 else "   📱 Bot token: test_token")
        print(f"   🏗️  Application: {type(bot.application).__name__}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Bot creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🚀 MadridistaAI Bot Debug Tool")
    print("=" * 50)
    
    success = debug_environment()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Bot environment looks good!")
        print("💡 If the bot still doesn't work on Railway, check:")
        print("   - Railway logs for specific error messages")
        print("   - Environment variables are set correctly")
        print("   - Railway service is running")
    else:
        print("❌ Bot environment has issues!")
        print("💡 Fix the import/creation errors above")
    
    print("\n🔍 To see Railway logs, go to:")
    print("   Railway Dashboard → Your Service → Logs")

if __name__ == "__main__":
    main()
