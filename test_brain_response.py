#!/usr/bin/env python3
"""
Test script to simulate brain responses for historical queries
"""
import os
import sys

# Set up environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['STRICT_FACTS'] = 'true'

def test_scope_check():
    """Test if historical queries pass the scope check"""
    print("=== SCOPE CHECK TEST ===")
    
    from orchestrator.brain import _in_scope, _looks_factual, _pre_hint
    
    test_queries = [
        "Who won the European Cup in 1960?",
        "Real Madrid Champions League history",
        "What happened in the 1960 final?",
        "Madrid vs Barca last match",
        "What is offside?",
        "Hello world"
    ]
    
    for query in test_queries:
        in_scope = _in_scope(query)
        is_factual = _looks_factual(query)
        hint = _pre_hint(query)
        
        print(f"Query: '{query}'")
        print(f"  In scope: {in_scope}")
        print(f"  Is factual: {is_factual}")
        print(f"  Hint: {hint}")
        print()

def test_tool_registration():
    """Test if history tools are properly registered"""
    print("=== TOOL REGISTRATION TEST ===")
    
    from orchestrator.brain import FUNCTIONS, NAME_TO_FUNC
    
    # Check FUNCTIONS
    history_functions = [f for f in FUNCTIONS if 'history' in f['name'] or 'ucl' in f['name']]
    print(f"History tools in FUNCTIONS: {len(history_functions)}")
    for func in history_functions:
        print(f"  - {func['name']}: {func['description']}")
    
    # Check NAME_TO_FUNC
    history_funcs = [k for k in NAME_TO_FUNC.keys() if 'history' in k or 'ucl' in k]
    print(f"History tools in NAME_TO_FUNC: {len(history_funcs)}")
    for func in history_funcs:
        print(f"  - {func}")
    
    # Test if we can call the functions
    print("\nTesting function calls:")
    try:
        from orchestrator.tools_history import tool_history_lookup, tool_rm_ucl_titles
        
        result1 = tool_history_lookup({'query': 'Real Madrid Champions League'})
        print(f"  tool_history_lookup: {result1.get('ok', False)}")
        
        result2 = tool_rm_ucl_titles({})
        print(f"  tool_rm_ucl_titles: {result2.get('ok', False)}")
        
    except Exception as e:
        print(f"  Error calling functions: {e}")

def test_wikipedia_provider():
    """Test Wikipedia provider directly"""
    print("\n=== WIKIPEDIA PROVIDER TEST ===")
    
    try:
        from providers.wiki import wiki_lookup
        
        # Test various queries
        test_queries = [
            'Real Madrid',
            'Real Madrid CF in international football',
            'Real Madrid Champions League',
            'European Cup 1960'
        ]
        
        for query in test_queries:
            result = wiki_lookup(query)
            if result:
                print(f"✅ '{query}': {result.get('title', 'N/A')}")
            else:
                print(f"❌ '{query}': No result")
                
    except Exception as e:
        print(f"❌ Wikipedia provider error: {e}")

def test_system_prompt():
    """Test if system prompt includes history instructions"""
    print("\n=== SYSTEM PROMPT TEST ===")
    
    from orchestrator.brain import SYSTEM
    
    print("System prompt includes:")
    print(f"  - 'history': {'history' in SYSTEM}")
    print(f"  - 'tools first': {'tools first' in SYSTEM}")
    print(f"  - 'Wikipedia': {'Wikipedia' in SYSTEM}")
    print(f"  - 'STRICT_FACTS': {'STRICT_FACTS' in SYSTEM}")
    
    # Show relevant parts
    lines = SYSTEM.split('.')
    for line in lines:
        if 'history' in line.lower() or 'tool' in line.lower():
            print(f"  Relevant: {line.strip()}")

def main():
    print("Madridista Bot - Brain Response Test")
    print("=" * 50)
    
    test_scope_check()
    test_tool_registration()
    test_wikipedia_provider()
    test_system_prompt()
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    main()
