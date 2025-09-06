#!/usr/bin/env python3
"""
Test script to verify Wikipedia-first routing with dynamic parsing
"""
import os
import sys

# Set up environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['STRICT_FACTS'] = 'true'
os.environ['HISTORY_ENABLE'] = 'true'
os.environ['LOG_TOOL_CALLS'] = 'true'

def test_wikipedia_tools():
    """Test Wikipedia tools directly"""
    print("=== WIKIPEDIA TOOLS TEST ===")
    
    from orchestrator.tools_history import tool_history_lookup, tool_ucl_last_n_winners
    
    # Test history lookup
    print("1. Testing tool_history_lookup:")
    result1 = tool_history_lookup({'query': 'Real Madrid Champions League'})
    print(f"   Success: {result1.get('ok', False)}")
    if result1.get('ok'):
        print(f"   Source: {result1.get('__source', 'N/A')}")
        print(f"   Title: {result1.get('title', 'N/A')}")
        print(f"   Extract length: {len(result1.get('extract', ''))}")
    
    # Test UCL winners
    print("\n2. Testing tool_ucl_last_n_winners:")
    result2 = tool_ucl_last_n_winners({'n': 5})
    print(f"   Success: {result2.get('ok', False)}")
    if result2.get('ok'):
        print(f"   Source: {result2.get('__source', 'N/A')}")
        items = result2.get('items', [])
        print(f"   Found {len(items)} winners:")
        for item in items:
            print(f"     {item.get('season', 'N/A')}: {item.get('winner', 'N/A')}")

def test_intent_detection():
    """Test intent detection for various query types"""
    print("\n=== INTENT DETECTION TEST ===")
    
    from orchestrator.brain import _looks_factual, _looks_historical, _pre_hint
    
    test_cases = [
        # UCL winners queries
        ("What are the last 5 UCL winners?", True, True, "ucl_winners"),
        ("Give me the last 5 Champions League winners.", False, True, "ucl_winners"),
        ("last 10 champions league winners please", False, True, "ucl_winners"),
        
        # Historical queries
        ("Who won the UCL in 2020?", True, True, "history"),
        ("Real Madrid Champions League history", True, True, "history"),
        ("Show me the 1950 World Cup final details.", True, True, "history"),
        
        # Current queries
        ("Madrid vs Barca next match", True, False, "fixture"),
        ("Any Madrid news today?", True, False, "news"),
        
        # Conceptual queries
        ("What is offside?", False, False, "concept")
    ]
    
    for query, expected_factual, expected_historical, expected_type in test_cases:
        is_factual = _looks_factual(query)
        is_historical = _looks_historical(query)
        hint = _pre_hint(query)
        
        print(f"Query: '{query}'")
        print(f"  Expected: Factual={expected_factual}, Historical={expected_historical}, Type={expected_type}")
        print(f"  Actual: Factual={is_factual}, Historical={is_historical}")
        print(f"  Hint: {hint}")
        
        # Check if detection matches expectations
        factual_match = is_factual == expected_factual
        historical_match = bool(is_historical) == expected_historical
        
        if factual_match and historical_match:
            print("  ✅ Detection correct")
        else:
            print("  ❌ Detection incorrect")
        print()

def test_tool_registration():
    """Test if all required tools are registered"""
    print("=== TOOL REGISTRATION TEST ===")
    
    from orchestrator.brain import FUNCTIONS, NAME_TO_FUNC
    
    # Check for key tools
    required_tools = [
        'tool_history_lookup',
        'tool_rm_ucl_titles',
        'tool_ucl_last_n_winners',
        'tool_af_next_fixture',
        'tool_news_top'
    ]
    
    for tool in required_tools:
        in_functions = any(f['name'] == tool for f in FUNCTIONS)
        in_name_to_func = tool in NAME_TO_FUNC
        
        print(f"{tool}:")
        print(f"  In FUNCTIONS: {in_functions}")
        print(f"  In NAME_TO_FUNC: {in_name_to_func}")
        
        if in_functions and in_name_to_func:
            print("  ✅ Properly registered")
        else:
            print("  ❌ Missing registration")
        print()

def test_environment_flags():
    """Test environment flags"""
    print("=== ENVIRONMENT FLAGS TEST ===")
    
    from orchestrator.brain import STRICT_FACTS, HISTORY_ON, LOG_TOOL_CALLS
    
    print(f"STRICT_FACTS: {STRICT_FACTS}")
    print(f"HISTORY_ON: {HISTORY_ON}")
    print(f"LOG_TOOL_CALLS: {LOG_TOOL_CALLS}")
    
    if STRICT_FACTS and HISTORY_ON and LOG_TOOL_CALLS:
        print("✅ All flags set correctly")
    else:
        print("❌ Some flags not set correctly")

def main():
    print("Madridista Bot - Wikipedia-First Routing Test")
    print("=" * 50)
    
    test_wikipedia_tools()
    test_intent_detection()
    test_tool_registration()
    test_environment_flags()
    
    print("\n" + "=" * 50)
    print("Wikipedia-First Routing Test Complete!")
    print("\nExpected behavior:")
    print("- UCL winners queries → tool_ucl_last_n_winners (dynamic parsing)")
    print("- Historical queries → tool_history_lookup (Wikipedia)")
    print("- Current queries → appropriate current data tools")
    print("- AI thinks first, then selects tools, then composes response")
    print("- Tool calls logged for debugging")

if __name__ == "__main__":
    main()
