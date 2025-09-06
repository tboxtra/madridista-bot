#!/usr/bin/env python3
"""
Test script to verify opponent-specific query handling
"""
import os
import sys

# Set up environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['STRICT_FACTS'] = 'true'
os.environ['HISTORY_ENABLE'] = 'true'
os.environ['LOG_TOOL_CALLS'] = 'true'

def test_tool_registration():
    """Test that opponent-specific tools are registered"""
    print("=== TOOL REGISTRATION TEST ===")
    
    from orchestrator.brain import FUNCTIONS, NAME_TO_FUNC
    
    required_tools = [
        'tool_af_last_result_vs',
        'tool_h2h_officialish'
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

def test_team_id_mapping():
    """Test team name to ID mapping"""
    print("=== TEAM ID MAPPING TEST ===")
    
    from providers.ids import af_id
    
    test_teams = [
        ("Real Madrid", 541),
        ("Arsenal", 42),
        ("Barcelona", 529),
        ("madrid", 541),  # lowercase
        ("barca", 529),   # alias
        ("Unknown Team", 0)  # not found
    ]
    
    for team_name, expected_id in test_teams:
        actual_id = af_id(team_name)
        print(f"Team: '{team_name}'")
        print(f"  Expected ID: {expected_id}")
        print(f"  Actual ID: {actual_id}")
        print(f"  Match: {'✅' if actual_id == expected_id else '❌'}")
        print()

def test_arbiter_planning():
    """Test arbiter planning for opponent queries"""
    print("=== ARBITER PLANNING TEST ===")
    
    from orchestrator.arbiter import plan_tools, _looks_compare
    
    test_queries = [
        ("What was the last score between Real Madrid and Arsenal?", True),
        ("Madrid vs Arsenal head to head summary?", True),
        ("What is Madrid vs Arsenal head to head?", True),
        ("Compare Real Madrid and Barcelona", True),
        ("Real Madrid next match", False),
        ("Any Madrid news today?", False)
    ]
    
    for query, expected_compare in test_queries:
        plan = plan_tools(query)
        is_compare = _looks_compare(query)
        
        print(f"Query: '{query}'")
        print(f"  Expected compare: {expected_compare}")
        print(f"  Actual compare: {is_compare}")
        print(f"  Plan: {plan}")
        
        # Check if opponent tools are in plan for compare queries
        if expected_compare:
            has_opponent_tools = any(tool in plan for tool in ['tool_af_last_result_vs', 'tool_h2h_officialish'])
            print(f"  Has opponent tools: {has_opponent_tools}")
            print(f"  Planning: {'✅' if has_opponent_tools else '❌'}")
        else:
            print(f"  Planning: {'✅' if not is_compare else '❌'}")
        print()

def test_intent_detection():
    """Test intent detection for opponent queries"""
    print("=== INTENT DETECTION TEST ===")
    
    from orchestrator.brain import _pre_hint
    
    test_queries = [
        "What was the last score between Real Madrid and Arsenal?",
        "Madrid vs Arsenal head to head summary?",
        "What is Madrid vs Arsenal head to head?",
        "Compare Real Madrid and Barcelona",
        "Real Madrid next match",
        "Any Madrid news today?"
    ]
    
    for query in test_queries:
        hint = _pre_hint(query)
        print(f"Query: '{query}'")
        print(f"  Hint: {hint}")
        
        # Check if hint suggests opponent tools
        has_opponent_hint = hint and any(tool in hint for tool in ['tool_af_last_result_vs', 'tool_h2h_officialish'])
        print(f"  Suggests opponent tools: {has_opponent_hint}")
        print()

def test_tool_parameters():
    """Test tool parameter schemas"""
    print("=== TOOL PARAMETERS TEST ===")
    
    from orchestrator.brain import FUNCTIONS
    
    # Find the opponent tools in FUNCTIONS
    opponent_tools = [f for f in FUNCTIONS if f['name'] in ['tool_af_last_result_vs', 'tool_h2h_officialish']]
    
    for tool in opponent_tools:
        print(f"Tool: {tool['name']}")
        print(f"  Description: {tool['description']}")
        params = tool.get('parameters', {}).get('properties', {})
        print(f"  Parameters: {list(params.keys())}")
        
        # Check for required parameters
        if tool['name'] == 'tool_af_last_result_vs':
            has_team_params = all(p in params for p in ['team_a', 'team_b'])
            print(f"  Has team parameters: {has_team_params}")
        elif tool['name'] == 'tool_h2h_officialish':
            has_team_params = all(p in params for p in ['team_a', 'team_b'])
            print(f"  Has team parameters: {has_team_params}")
        print()

def main():
    print("Madridista Bot - Opponent Query Test")
    print("=" * 50)
    
    test_tool_registration()
    test_team_id_mapping()
    test_arbiter_planning()
    test_intent_detection()
    test_tool_parameters()
    
    print("=" * 50)
    print("Opponent Query Test Complete!")
    print("\nExpected behavior:")
    print("- 'What was the last score between X and Y?' → tool_af_last_result_vs")
    print("- 'X vs Y head to head?' → tool_af_last_result_vs + tool_h2h_officialish")
    print("- Arbiter tries opponent tools first for H2H queries")
    print("- Team names resolve to API-Football IDs")
    print("- No more generic banter for H2H queries")

if __name__ == "__main__":
    main()
