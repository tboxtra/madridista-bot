#!/usr/bin/env python3
"""
Diagnostic test harness for query processing
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['LOG_TOOL_CALLS'] = 'true'
os.environ['STRICT_FACTS'] = 'true'
os.environ['HISTORY_ENABLE'] = 'true'
os.environ['CITATIONS'] = 'true'

def test_query_processing():
    """Test query processing with debug logging"""
    print("=== QUERY PROCESSING TEST ===")
    
    from orchestrator.brain import answer_nl_question
    
    test_queries = [
        "What was the last score between Real Madrid and Arsenal?",
        "Madrid vs Arsenal head to head?",
        "Any Madrid news today?",
        "Who won the UCL in 2020?",
        "When is Real Madrid's next match?",
        "Compare Real Madrid and Barcelona"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        try:
            result = answer_nl_question(query)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        print("-" * 50)

def test_tool_direct_calls():
    """Test tools directly to verify they work"""
    print("\n=== DIRECT TOOL TEST ===")
    
    try:
        from orchestrator.tools_ext import tool_af_last_result_vs
        from orchestrator.tools_history import tool_h2h_officialish
        
        print("Testing tool_af_last_result_vs:")
        result1 = tool_af_last_result_vs({'team_a': 'Real Madrid', 'team_b': 'Arsenal'})
        print(f"  Success: {result1.get('ok', False)}")
        print(f"  Message: {result1.get('message', 'N/A')}")
        
        print("\nTesting tool_h2h_officialish:")
        result2 = tool_h2h_officialish({'team_a': 'Real Madrid', 'team_b': 'Arsenal'})
        print(f"  Success: {result2.get('ok', False)}")
        print(f"  Message: {result2.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"Tool test error: {e}")
        import traceback
        traceback.print_exc()

def test_arbiter_planning():
    """Test arbiter planning for H2H queries"""
    print("\n=== ARBITER PLANNING TEST ===")
    
    from orchestrator.arbiter import plan_tools, _looks_compare
    
    h2h_queries = [
        "What was the last score between Real Madrid and Arsenal?",
        "Madrid vs Arsenal head to head?",
        "Compare Real Madrid and Barcelona"
    ]
    
    for query in h2h_queries:
        plan = plan_tools(query)
        is_compare = _looks_compare(query)
        has_opponent_tools = any(tool in plan for tool in ['tool_af_last_result_vs', 'tool_h2h_officialish'])
        
        print(f"Query: {query}")
        print(f"  Compare intent: {is_compare}")
        print(f"  Has opponent tools: {has_opponent_tools}")
        print(f"  Plan: {plan}")
        print()

def test_team_id_resolution():
    """Test team name to ID resolution"""
    print("\n=== TEAM ID RESOLUTION TEST ===")
    
    from providers.ids import af_id
    
    test_teams = [
        ("Real Madrid", 541),
        ("Arsenal", 42),
        ("madrid", 541),
        ("barca", 529)
    ]
    
    for team_name, expected_id in test_teams:
        actual_id = af_id(team_name)
        print(f"Team: '{team_name}' → ID: {actual_id} (expected: {expected_id}) {'✅' if actual_id == expected_id else '❌'}")

def main():
    print("Madridista Bot - Diagnostic Test Harness")
    print("=" * 60)
    
    test_query_processing()
    test_tool_direct_calls()
    test_arbiter_planning()
    test_team_id_resolution()
    
    print("\n" + "=" * 60)
    print("Diagnostic Test Complete!")
    print("\nExpected logs:")
    print("- [text_router] got: <query>")
    print("- [brain] Forcing tool retry for factual query: <query>")
    print("- [tools] calling tool_af_last_result_vs args={...}")
    print("- [tools] calling tool_h2h_officialish args={...}")

if __name__ == "__main__":
    main()
