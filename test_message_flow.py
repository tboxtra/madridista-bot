#!/usr/bin/env python3
"""
Test script to simulate the message handling flow
"""
from features.router_football import route_football
from features.router_extra import route_related

def test_message_flow():
    """Test the message handling flow"""
    test_messages = [
        "show me the table",
        "madrid last 5",
        "next game",
        "top scorers",
        "show me the squad",
        "who is injured",
        "show goalkeepers",
        "hello there",
        "what's the weather like"
    ]
    
    print("Testing message handling flow:")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\nMessage: '{message}'")
        
        # Try football router first
        football_answer = route_football(message)
        if football_answer:
            print(f"  Football router: {football_answer[:50]}...")
            continue
            
        # Try Madrid router
        madrid_answer = route_related(message)
        if madrid_answer:
            print(f"  Madrid router: {madrid_answer[:50]}...")
            continue
            
        # No router matched
        print("  No router matched - would show generic response")

if __name__ == "__main__":
    test_message_flow()
