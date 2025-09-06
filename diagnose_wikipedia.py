#!/usr/bin/env python3
"""
Diagnostic script to check Wikipedia integration and environment setup
"""
import os
import sys
import requests

def check_environment():
    """Check if all required environment variables are set"""
    print("=== ENVIRONMENT VARIABLES CHECK ===")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        'API_FOOTBALL_KEY',
        'RAPIDAPI_KEY',
        'YOUTUBE_API_KEY',
        'ODDS_API_KEY'
    ]
    
    optional_vars = [
        'STRICT_FACTS',
        'FAN_CREATIVE',
        'FAN_SPICE',
        'HISTORY_ENABLE',
        'CITATIONS',
        'AUTO_REPLY',
        'AUTO_REPLY_PROB',
        'BOT_NAME',
        'TZ'
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_required:
        print(f"❌ Missing required variables: {missing_required}")
    else:
        print("✅ All required environment variables are set")
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var, "Not set")
        print(f"   {var}: {value}")

def test_wikipedia_direct():
    """Test Wikipedia API directly"""
    print("\n=== WIKIPEDIA API DIRECT TEST ===")
    
    headers = {
        "User-Agent": "MadridistaBot/1.0 (https://github.com/tboxtra/madridista-bot; football bot for Real Madrid fans)"
    }
    
    try:
        # Test direct Wikipedia API
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/Real_Madrid"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wikipedia API working")
            print(f"   Title: {data.get('title', 'N/A')}")
            print(f"   Summary length: {len(data.get('extract', ''))}")
        else:
            print(f"❌ Wikipedia API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Wikipedia API exception: {e}")

def test_wikipedia_provider():
    """Test our Wikipedia provider"""
    print("\n=== WIKIPEDIA PROVIDER TEST ===")
    
    try:
        from providers.wiki import wiki_lookup
        
        # Test basic lookup
        result = wiki_lookup('Real Madrid')
        if result:
            print(f"✅ wiki_lookup working")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Summary length: {len(result.get('summary', ''))}")
        else:
            print("❌ wiki_lookup returned None")
            
    except Exception as e:
        print(f"❌ Wikipedia provider exception: {e}")

def test_history_tools():
    """Test history tools"""
    print("\n=== HISTORY TOOLS TEST ===")
    
    try:
        from orchestrator.tools_history import tool_history_lookup, tool_rm_ucl_titles
        
        # Test history lookup
        result1 = tool_history_lookup({'query': 'Real Madrid Champions League'})
        if result1.get('ok'):
            print(f"✅ tool_history_lookup working")
            print(f"   Source: {result1.get('__source', 'N/A')}")
        else:
            print(f"❌ tool_history_lookup failed: {result1.get('message', 'Unknown error')}")
        
        # Test UCL titles
        result2 = tool_rm_ucl_titles({})
        if result2.get('ok'):
            print(f"✅ tool_rm_ucl_titles working")
            print(f"   Source: {result2.get('__source', 'N/A')}")
        else:
            print(f"❌ tool_rm_ucl_titles failed: {result2.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ History tools exception: {e}")

def test_brain_integration():
    """Test brain integration"""
    print("\n=== BRAIN INTEGRATION TEST ===")
    
    try:
        # Set mock OpenAI key for testing
        os.environ['OPENAI_API_KEY'] = 'sk-test'
        
        from orchestrator.brain import _looks_factual, _pre_hint, FUNCTIONS, NAME_TO_FUNC
        
        # Test factual detection
        test_query = 'Who won the European Cup in 1960?'
        is_factual = _looks_factual(test_query)
        hint = _pre_hint(test_query)
        
        print(f"✅ Factual detection working")
        print(f"   Query: '{test_query}'")
        print(f"   Is factual: {is_factual}")
        print(f"   Hint: {hint}")
        
        # Check tool registration
        history_tools = [f for f in FUNCTIONS if 'history' in f['name'] or 'ucl' in f['name']]
        print(f"✅ History tools registered: {len(history_tools)}")
        for tool in history_tools:
            print(f"   - {tool['name']}")
            
    except Exception as e:
        print(f"❌ Brain integration exception: {e}")

def main():
    print("Madridista Bot - Wikipedia Integration Diagnostic")
    print("=" * 50)
    
    check_environment()
    test_wikipedia_direct()
    test_wikipedia_provider()
    test_history_tools()
    test_brain_integration()
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()
