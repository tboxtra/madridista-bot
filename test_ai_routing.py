#!/usr/bin/env python3
"""
Test script to verify AI-first routing and tool selection
"""
import os
import sys

# Set up environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['STRICT_FACTS'] = 'true'

def test_intent_detection():
    """Test intent detection for various query types"""
    print("=== INTENT DETECTION TEST ===")
    
    from orchestrator.brain import _looks_factual, _looks_historical, _pre_hint
    
    test_cases = [
        # Historical queries
        ("Who won the UCL in 2020?", True, True, "history"),
        ("Give me the last 5 Champions League winners.", False, True, "history"),
        ("When did Real Madrid last win the UCL?", True, True, "history"),
        ("Show me the 1950 World Cup final details.", True, True, "history"),
        ("What are the last 5 UCL winners?", False, True, "history"),
        ("Real Madrid Champions League history", True, True, "history"),
        ("Who were the winners of the 1960 European Cup?", True, True, "history"),
        
        # Current/factual queries
        ("Madrid vs Barca next match", True, False, "fixture"),
        ("Any Madrid news today?", True, False, "news"),
        ("Real Madrid current form", True, False, "form"),
        ("Madrid vs Barca last match", True, False, "result"),
        
        # Conceptual queries
        ("What is offside?", False, False, "concept"),
        ("How does high pressing work?", False, False, "concept"),
        ("Explain 4-3-3 formation", False, False, "concept"),
        
        # Non-football
        ("Hello world", False, False, "none"),
        ("What's the weather?", False, False, "none")
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
        'tool_af_next_fixture',
        'tool_news_top',
        'tool_glossary'
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

def test_system_prompt():
    """Test if system prompt enforces AI thinking"""
    print("=== SYSTEM PROMPT TEST ===")
    
    from orchestrator.brain import SYSTEM
    
    required_elements = [
        "think about the question FIRST",
        "SELECT the best tool",
        "never allowed to make up data",
        "tool_history_lookup",
        "tool_af_next_fixture",
        "step by step"
    ]
    
    for element in required_elements:
        present = element in SYSTEM
        print(f"'{element}': {'✅' if present else '❌'}")
    
    print(f"\nSystem prompt length: {len(SYSTEM)} characters")

def test_wikipedia_tools():
    """Test Wikipedia tools directly"""
    print("\n=== WIKIPEDIA TOOLS TEST ===")
    
    try:
        from orchestrator.tools_history import tool_history_lookup, tool_rm_ucl_titles
        
        # Test history lookup
        result1 = tool_history_lookup({'query': 'Real Madrid Champions League'})
        print(f"tool_history_lookup: {result1.get('ok', False)}")
        if result1.get('ok'):
            print(f"  Source: {result1.get('__source', 'N/A')}")
            print(f"  Title: {result1.get('title', 'N/A')}")
        
        # Test UCL titles
        result2 = tool_rm_ucl_titles({})
        print(f"tool_rm_ucl_titles: {result2.get('ok', False)}")
        if result2.get('ok'):
            print(f"  Source: {result2.get('__source', 'N/A')}")
            print(f"  Title: {result2.get('title', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Wikipedia tools error: {e}")

def main():
    print("Madridista Bot - AI-First Routing Test")
    print("=" * 50)
    
    test_intent_detection()
    test_tool_registration()
    test_system_prompt()
    test_wikipedia_tools()
    
    print("\n" + "=" * 50)
    print("AI-First Routing Test Complete!")
    print("\nExpected behavior:")
    print("- Historical queries → tool_history_lookup or tool_rm_ucl_titles")
    print("- Current queries → appropriate current data tools")
    print("- Conceptual queries → tool_glossary or direct answer")
    print("- AI thinks first, then selects tools, then composes response")

if __name__ == "__main__":
    main()
