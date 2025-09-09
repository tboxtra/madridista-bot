#!/usr/bin/env python3
"""
Bot Diagnostics Script
Quick diagnostic tool to check bot status and identify issues.
"""

import os
import sys
import traceback
from typing import Dict, Any

def check_environment_variables() -> Dict[str, Any]:
    """Check if required environment variables are set."""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "OPENAI_API_KEY"
    ]
    
    optional_vars = [
        "OPENWEATHER_API_KEY",
        "NEWS_API_KEY",
        "EXCHANGE_RATE_API_KEY",
        "FOOTBALL_DATA_API_KEY",
        "API_FOOTBALL_KEY",
        "RAPIDAPI_KEY"
    ]
    
    results = {
        "required": {},
        "optional": {},
        "status": "ok"
    }
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            results["required"][var] = "✅ Set"
        else:
            results["required"][var] = "❌ Missing"
            results["status"] = "error"
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            results["optional"][var] = "✅ Set"
        else:
            results["optional"][var] = "⚠️ Not set"
    
    return results

def check_imports() -> Dict[str, Any]:
    """Check if all required modules can be imported."""
    modules_to_check = [
        ("telegram", "python-telegram-bot"),
        ("openai", "openai"),
        ("requests", "requests"),
        ("numpy", "numpy"),
        ("pandas", "pandas")
    ]
    
    results = {
        "modules": {},
        "status": "ok"
    }
    
    for module_name, package_name in modules_to_check:
        try:
            __import__(module_name)
            results["modules"][module_name] = f"✅ {package_name}"
        except ImportError as e:
            results["modules"][module_name] = f"❌ {package_name} - {str(e)}"
            results["status"] = "error"
    
    return results

def check_bot_modules() -> Dict[str, Any]:
    """Check if bot-specific modules can be imported."""
    bot_modules = [
        "orchestrator.enhanced_brain",
        "orchestrator.tools",
        "orchestrator.tools_ext",
        "orchestrator.tools_history",
        "orchestrator.tools_enhanced",
        "orchestrator.tools_enhanced_v2",
        "orchestrator.tools_phase1",
        "utils.memory",
        "utils.relevance",
        "utils.cooldown",
        "utils.user_manager",
        "utils.api_manager",
        "features.telegram_interactive",
        "features.realtime_updates"
    ]
    
    results = {
        "modules": {},
        "status": "ok"
    }
    
    for module_name in bot_modules:
        try:
            __import__(module_name)
            results["modules"][module_name] = "✅ OK"
        except ImportError as e:
            results["modules"][module_name] = f"❌ {str(e)}"
            results["status"] = "error"
        except Exception as e:
            results["modules"][module_name] = f"⚠️ {str(e)}"
    
    return results

def check_enhanced_brain_initialization() -> Dict[str, Any]:
    """Check if enhanced brain can be initialized."""
    try:
        # Set test environment variables
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
        os.environ['OPENAI_API_KEY'] = 'test_key'
        
        from openai import OpenAI
        from orchestrator.enhanced_brain import EnhancedFootballBrain
        
        client = OpenAI(api_key="test_key")
        brain = EnhancedFootballBrain(client)
        
        return {
            "status": "ok",
            "message": "✅ Enhanced brain initializes successfully",
            "tool_count": len(brain.tool_functions)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Enhanced brain initialization failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

def check_main_module() -> Dict[str, Any]:
    """Check if main module can be imported."""
    try:
        # Set test environment variables
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
        os.environ['OPENAI_API_KEY'] = 'test_key'
        
        import main
        return {
            "status": "ok",
            "message": "✅ Main module imports successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Main module import failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

def run_diagnostics() -> Dict[str, Any]:
    """Run all diagnostic checks."""
    print("🔍 Running Bot Diagnostics...")
    print("=" * 50)
    
    results = {
        "environment": check_environment_variables(),
        "imports": check_imports(),
        "bot_modules": check_bot_modules(),
        "enhanced_brain": check_enhanced_brain_initialization(),
        "main_module": check_main_module()
    }
    
    # Print results
    print("\n📋 Environment Variables:")
    print("-" * 30)
    for var, status in results["environment"]["required"].items():
        print(f"  {var}: {status}")
    
    print("\n📦 Optional Environment Variables:")
    print("-" * 30)
    for var, status in results["environment"]["optional"].items():
        print(f"  {var}: {status}")
    
    print("\n📚 External Dependencies:")
    print("-" * 30)
    for module, status in results["imports"]["modules"].items():
        print(f"  {module}: {status}")
    
    print("\n🤖 Bot Modules:")
    print("-" * 30)
    for module, status in results["bot_modules"]["modules"].items():
        print(f"  {module}: {status}")
    
    print("\n🧠 Enhanced Brain:")
    print("-" * 30)
    print(f"  {results['enhanced_brain']['message']}")
    if "tool_count" in results["enhanced_brain"]:
        print(f"  Tools registered: {results['enhanced_brain']['tool_count']}")
    
    print("\n🚀 Main Module:")
    print("-" * 30)
    print(f"  {results['main_module']['message']}")
    
    # Overall status
    overall_status = "ok"
    for check_name, check_result in results.items():
        if check_result.get("status") == "error":
            overall_status = "error"
            break
    
    print("\n" + "=" * 50)
    if overall_status == "ok":
        print("✅ All diagnostics passed! Bot should be working.")
    else:
        print("❌ Some diagnostics failed. Check the issues above.")
    
    return results

if __name__ == "__main__":
    run_diagnostics()
