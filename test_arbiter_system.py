#!/usr/bin/env python3
"""
Test script to verify the complete arbiter system
"""
import os
import sys

# Set up environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['STRICT_FACTS'] = 'true'
os.environ['HISTORY_ENABLE'] = 'true'
os.environ['LOG_TOOL_CALLS'] = 'true'

def test_arbiter_planning():
    """Test arbiter tool planning"""
    print("=== ARBITER PLANNING TEST ===")
    
    from orchestrator.arbiter import plan_tools, _looks_live, _looks_next, _looks_last, _looks_news, _looks_history, _looks_players, _looks_compare
    
    test_cases = [
        ("What is Madrid vs Arsenal head to head?", "compare"),
        ("Any Madrid news today?", "news"),
        ("When is Real Madrid next match?", "next"),
        ("What was the last score between Madrid and Arsenal?", "last"),
        ("Who has better recent form, Madrid or Barcelona?", "compare"),
        ("What year did Zidane score that UCL final volley?", "history"),
        ("Show me Madrid live score", "live"),
        ("Bellingham player stats", "players")
    ]
    
    for query, expected_type in test_cases:
        plan = plan_tools(query)
        print(f"Query: '{query}'")
        print(f"  Expected type: {expected_type}")
        print(f"  Plan: {plan}")
        print(f"  Live: {_looks_live(query)}, Next: {_looks_next(query)}, Last: {_looks_last(query)}")
        print(f"  News: {_looks_news(query)}, History: {_looks_history(query)}, Players: {_looks_players(query)}, Compare: {_looks_compare(query)}")
        print()

def test_arbiter_validation():
    """Test arbiter validation logic"""
    print("=== ARBITER VALIDATION TEST ===")
    
    from orchestrator.arbiter import validate_recency, _is_empty
    
    # Test validation with different payloads
    test_cases = [
        ("What was the last score?", {"ok": True, "home": "Madrid", "away": "Barca", "when": "2024-01-15"}, True, "valid_last"),
        ("What was the last score?", {"ok": True, "message": "No data"}, False, "empty_last"),
        ("When is the next match?", {"ok": True, "when": "2024-01-20", "home": "Madrid", "away": "Barca"}, True, "valid_next"),
        ("When is the next match?", {"ok": True, "message": "No fixtures"}, False, "empty_next"),
        ("Any news today?", {"ok": True, "items": [{"title": "Breaking news"}]}, True, "valid_news"),
        ("Any news today?", {"ok": True, "message": "No news"}, False, "empty_news")
    ]
    
    for query, payload, expected_valid, description in test_cases:
        is_empty = _is_empty(payload)
        is_valid, reason = validate_recency(query, payload)
        print(f"Query: '{query}'")
        print(f"  Payload: {payload}")
        print(f"  Is empty: {is_empty}")
        print(f"  Is valid: {is_valid} (reason: {reason})")
        print(f"  Expected: {expected_valid} - {description}")
        print()

def test_arbiter_integration():
    """Test arbiter integration with brain"""
    print("=== ARBITER INTEGRATION TEST ===")
    
    from orchestrator.brain import _looks_factual, _looks_historical, _pre_hint
    
    test_queries = [
        "What are the last 5 UCL winners?",
        "What was the last score between Madrid and Arsenal?",
        "What's Madrid vs Arsenal head to head?",
        "Any Madrid news today?",
        "When is Real Madrid's next match?",
        "Who has better recent form, Madrid or Barcelona?",
        "What year did Zidane score that UCL final volley?"
    ]
    
    for query in test_queries:
        is_factual = _looks_factual(query)
        is_historical = _looks_historical(query)
        hint = _pre_hint(query)
        
        print(f"Query: '{query}'")
        print(f"  Factual: {is_factual}")
        print(f"  Historical: {is_historical}")
        print(f"  Hint: {hint}")
        print()

def test_tool_coverage():
    """Test that all arbiter tools are available"""
    print("=== TOOL COVERAGE TEST ===")
    
    from orchestrator.arbiter import plan_tools
    from orchestrator.brain import NAME_TO_FUNC
    
    # Get all tools that arbiter might try
    all_queries = [
        "live score now",
        "next match",
        "last result", 
        "news today",
        "player stats",
        "compare teams",
        "history query"
    ]
    
    all_tools = set()
    for query in all_queries:
        plan = plan_tools(query)
        all_tools.update(plan)
    
    print(f"All tools arbiter might use: {sorted(all_tools)}")
    
    missing_tools = [tool for tool in all_tools if tool not in NAME_TO_FUNC]
    if missing_tools:
        print(f"❌ Missing tools: {missing_tools}")
    else:
        print("✅ All arbiter tools are registered")
    
    print()

def main():
    print("Madridista Bot - Arbiter System Test")
    print("=" * 50)
    
    test_arbiter_planning()
    test_arbiter_validation()
    test_arbiter_integration()
    test_tool_coverage()
    
    print("=" * 50)
    print("Arbiter System Test Complete!")
    print("\nExpected behavior:")
    print("- Arbiter plans tools based on query intent")
    print("- Validates data freshness and completeness")
    print("- Retries with alternate tools if first fails")
    print("- Logs all tool attempts for debugging")
    print("- Only composes response after getting valid data")

if __name__ == "__main__":
    main()
