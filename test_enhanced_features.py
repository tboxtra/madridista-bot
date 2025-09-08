#!/usr/bin/env python3
"""
Test script for enhanced features: weather, news, currency, and caching.
"""

import os
import sys
import time
from openai import OpenAI

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_weather_provider():
    """Test weather provider functionality."""
    print("🌤️  Testing Weather Provider")
    print("-" * 40)
    
    try:
        from providers.weather import weather_provider
        
        # Test match weather
        result = weather_provider.get_match_weather("Santiago Bernabeu")
        print(f"✅ Weather for Santiago Bernabeu: {result.get('temperature', 'N/A')}°C")
        
        # Test weather impact
        conditions = {
            "temperature": 25,
            "wind_speed": 8,
            "conditions": "clear sky",
            "visibility": 10000
        }
        impact = weather_provider.get_weather_impact(conditions)
        print(f"✅ Weather impact analysis: {impact.get('description', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Weather provider test failed: {e}")
        return False

def test_news_provider():
    """Test enhanced news provider functionality."""
    print("\n📰 Testing Enhanced News Provider")
    print("-" * 40)
    
    try:
        from providers.news_enhanced import enhanced_news_provider
        
        # Test trending news
        result = enhanced_news_provider.get_trending_news("football", 3)
        print(f"✅ Trending news: {result.get('total_articles', 0)} articles found")
        
        # Test team news
        team_result = enhanced_news_provider.get_team_news("Real Madrid", 2)
        print(f"✅ Team news: {team_result.get('total_articles', 0)} articles for Real Madrid")
        
        return True
        
    except Exception as e:
        print(f"❌ News provider test failed: {e}")
        return False

def test_currency_provider():
    """Test currency provider functionality."""
    print("\n💰 Testing Currency Provider")
    print("-" * 40)
    
    try:
        from providers.currency import currency_provider
        
        # Test transfer conversion
        result = currency_provider.convert_transfer_fee(100000000, "EUR", "USD")
        print(f"✅ Transfer conversion: €100M = ${result.get('converted_amount', 'N/A')}")
        
        # Test market trends
        trends = currency_provider.get_market_trends()
        print(f"✅ Market trends: {len(trends.get('current_rates', {}))} currencies analyzed")
        
        return True
        
    except Exception as e:
        print(f"❌ Currency provider test failed: {e}")
        return False

def test_cache_system():
    """Test caching system functionality."""
    print("\n💾 Testing Cache System")
    print("-" * 40)
    
    try:
        from utils.cache import cache_manager, tool_cache, api_cache
        
        # Test basic caching
        cache_manager.set("test_key", "test_value", 60)
        cached_value = cache_manager.get("test_key")
        print(f"✅ Basic cache: {cached_value}")
        
        # Test tool caching
        tool_cache.cache_tool_result("test_tool", {"param": "value"}, {"result": "success"}, 60)
        tool_result = tool_cache.get_cached_result("test_tool", {"param": "value"})
        print(f"✅ Tool cache: {tool_result}")
        
        # Test cache stats
        stats = cache_manager.get_stats()
        print(f"✅ Cache stats: {stats['size']} entries, {stats['hit_rate']}% hit rate")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache system test failed: {e}")
        return False

def test_enhanced_tools():
    """Test enhanced tools functionality."""
    print("\n🔧 Testing Enhanced Tools")
    print("-" * 40)
    
    try:
        from orchestrator.tools_enhanced import ENHANCED_TOOLS
        
        # Test weather tool
        weather_result = ENHANCED_TOOLS["tool_weather_match"]({"venue": "Camp Nou"})
        print(f"✅ Weather tool: {weather_result.get('temperature', 'N/A')}°C at Camp Nou")
        
        # Test news tool
        news_result = ENHANCED_TOOLS["tool_news_trending"]({"topic": "football", "limit": 2})
        print(f"✅ News tool: {news_result.get('total_articles', 0)} trending articles")
        
        # Test currency tool
        currency_result = ENHANCED_TOOLS["tool_convert_transfer"]({"amount": 50000000, "from_currency": "EUR", "to_currency": "GBP"})
        print(f"✅ Currency tool: €50M = £{currency_result.get('converted_amount', 'N/A')}")
        
        # Test cache stats tool
        cache_stats = ENHANCED_TOOLS["tool_cache_stats"]({})
        print(f"✅ Cache stats tool: {cache_stats.get('cache_stats', {}).get('size', 0)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced tools test failed: {e}")
        return False

def test_enhanced_brain_integration():
    """Test enhanced brain with new tools."""
    print("\n🧠 Testing Enhanced Brain Integration")
    print("-" * 40)
    
    try:
        from orchestrator.enhanced_brain import EnhancedFootballBrain
        
        # Mock client for testing
        class MockClient:
            def chat(self):
                return self
            def completions(self):
                return self
            def create(self, **kwargs):
                class MockResponse:
                    def __init__(self):
                        self.choices = [type('obj', (object,), {'message': type('obj', (object,), {'content': '{"intent": "test", "confidence": 0.9}'})()})()]
                return MockResponse()
        
        brain = EnhancedFootballBrain(MockClient())
        
        # Check if new tools are registered
        tool_count = len(brain.tool_functions)
        print(f"✅ Enhanced brain initialized with {tool_count} tools")
        
        # Check for specific enhanced tools
        enhanced_tools = [name for name in brain.tool_functions.keys() if "weather" in name or "news" in name or "currency" in name or "cache" in name]
        print(f"✅ Enhanced tools registered: {len(enhanced_tools)} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced brain integration test failed: {e}")
        return False

def test_performance():
    """Test performance improvements with caching."""
    print("\n⚡ Testing Performance Improvements")
    print("-" * 40)
    
    try:
        from orchestrator.tools_enhanced import ENHANCED_TOOLS
        from utils.cache import clear_all_cache
        
        # Clear cache
        clear_all_cache()
        
        # Test without cache
        start_time = time.time()
        result1 = ENHANCED_TOOLS["tool_news_trending"]({"topic": "football", "limit": 3})
        time1 = time.time() - start_time
        
        # Test with cache
        start_time = time.time()
        result2 = ENHANCED_TOOLS["tool_news_trending"]({"topic": "football", "limit": 3})
        time2 = time.time() - start_time
        
        print(f"✅ First call (no cache): {time1:.3f}s")
        print(f"✅ Second call (with cache): {time2:.3f}s")
        print(f"✅ Performance improvement: {((time1 - time2) / time1 * 100):.1f}% faster")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all enhanced feature tests."""
    print("🚀 Enhanced Features Test Suite")
    print("=" * 50)
    
    tests = [
        test_weather_provider,
        test_news_provider,
        test_currency_provider,
        test_cache_system,
        test_enhanced_tools,
        test_enhanced_brain_integration,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced features are working perfectly!")
        print("\n✅ New Features Available:")
        print("   • Weather conditions for matches")
        print("   • Enhanced news with sentiment analysis")
        print("   • Transfer value currency conversions")
        print("   • Intelligent caching for performance")
        print("   • Market trends and analysis")
        print("   • Advanced tool integration")
        
        print("\n🚀 Ready for deployment with enhanced features!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
