#!/usr/bin/env python3
"""
Debug script to test H2H query handling
"""
import os
import sys

# Set up environment
os.environ['OPENAI_API_KEY'] = 'test'
os.environ['TELEGRAM_BOT_TOKEN'] = 'test'
os.environ['FOOTBALL_DATA_API_KEY'] = 'test'
os.environ['RAPIDAPI_KEY'] = 'test'
os.environ['API_FOOTBALL_KEY'] = 'test'

from orchestrator.arbiter import plan_tools, _looks_compare, _looks_last
from orchestrator.brain import answer_nl_question
from orchestrator.tools_ext import tool_af_last_result_vs
from providers.ids import af_id

def test_h2h_query():
    query = "What was the last score between Madrid and Arsenal?"
    print(f"Testing query: {query}")
    print("=" * 60)
    
    # Test intent detection
    print("Intent detection:")
    print(f"  _looks_compare: {_looks_compare(query)}")
    print(f"  _looks_last: {_looks_last(query)}")
    print()
    
    # Test arbiter planning
    print("Arbiter planning:")
    plan = plan_tools(query)
    print(f"  Plan: {plan}")
    print()
    
    # Test team ID resolution
    print("Team ID resolution:")
    madrid_id = af_id('Madrid')
    arsenal_id = af_id('Arsenal')
    print(f"  Madrid -> {madrid_id}")
    print(f"  Arsenal -> {arsenal_id}")
    print()
    
    # Test the H2H tool directly
    print("Testing tool_af_last_result_vs:")
    try:
        result = tool_af_last_result_vs({'team_a': 'Madrid', 'team_b': 'Arsenal'})
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test the full brain answer (this will fail due to API key, but we can see the flow)
    print("Testing full brain answer:")
    try:
        result = answer_nl_question(query)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")
        # Don't print full traceback for API key errors
        if "API key" not in str(e):
            import traceback
            traceback.print_exc()
    print()

if __name__ == "__main__":
    test_h2h_query()
