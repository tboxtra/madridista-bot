#!/usr/bin/env python3
"""
Quick test script to verify Phase 1 features are working.
Run this to check if all Phase 1 components are properly integrated.
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_phase1_integration():
    """Quick test to verify Phase 1 integration."""
    print("🧪 Quick Phase 1 Integration Test\n")
    
    # Test 1: Check all Phase 1 modules can be imported
    print("1. Testing module imports...")
    try:
        from analytics.predictions import MatchPredictionEngine
        from orchestrator.personalization import PersonalizationEngine
        from features.interactive import InteractiveFeatures
        from gamification.achievements import AchievementSystem
        from orchestrator.tools_phase1 import PHASE1_TOOLS
        print("   ✅ All Phase 1 modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Check Enhanced Brain has Phase 1 tools
    print("2. Testing Enhanced Brain integration...")
    try:
        from orchestrator.enhanced_brain import EnhancedFootballBrain
        from openai import OpenAI
        
        # Mock client for testing
        class MockClient:
            def chat(self):
                return self
            def completions(self):
                return self
            def create(self, **kwargs):
                return type('Response', (), {
                    'choices': [type('Choice', (), {
                        'message': type('Message', (), {
                            'content': 'Mock response',
                            'tool_calls': []
                        })()
                    })()]
                })()
        
        brain = EnhancedFootballBrain(MockClient())
        
        # Check Phase 1 tools are registered
        phase1_tool_names = [
            "tool_predict_match_outcome",
            "tool_analyze_user_personality", 
            "tool_create_match_prediction_poll",
            "tool_check_user_achievements"
        ]
        
        for tool_name in phase1_tool_names:
            if tool_name in brain.tool_functions:
                print(f"   ✅ {tool_name} registered")
            else:
                print(f"   ❌ {tool_name} missing")
                return False
        
        print("   ✅ Enhanced Brain integration working")
    except Exception as e:
        print(f"   ❌ Enhanced Brain test failed: {e}")
        return False
    
    # Test 3: Check system prompt includes Phase 1 features
    print("3. Testing system prompt...")
    try:
        system_prompt = brain.system_prompt
        phase1_keywords = [
            "AI-powered predictions",
            "personalization", 
            "interactive features",
            "Achievement system"
        ]
        
        for keyword in phase1_keywords:
            if keyword in system_prompt:
                print(f"   ✅ System prompt includes '{keyword}'")
            else:
                print(f"   ❌ System prompt missing '{keyword}'")
                return False
        
        print("   ✅ System prompt updated for Phase 1")
    except Exception as e:
        print(f"   ❌ System prompt test failed: {e}")
        return False
    
    # Test 4: Check Phase 1 tools functionality
    print("4. Testing Phase 1 tools...")
    try:
        # Test prediction tool
        args = {"home_team": "Real Madrid", "away_team": "Barcelona"}
        result = PHASE1_TOOLS["tool_predict_match_outcome"](args)
        if result.get("ok") is not None:
            print("   ✅ Prediction tool structure working")
        else:
            print("   ❌ Prediction tool failed")
            return False
        
        # Test achievement tool
        args = {"user_id": "test_user", "action": "query", "data": {"intent": "stats"}}
        result = PHASE1_TOOLS["tool_check_user_achievements"](args)
        if result.get("ok") is not None:
            print("   ✅ Achievement tool structure working")
        else:
            print("   ❌ Achievement tool failed")
            return False
        
        print("   ✅ Phase 1 tools functional")
    except Exception as e:
        print(f"   ❌ Phase 1 tools test failed: {e}")
        return False
    
    # Test 5: Check interactive features
    print("5. Testing interactive features...")
    try:
        interactive = InteractiveFeatures()
        
        # Test poll creation
        match_data = {"home_team": "Real Madrid", "away_team": "Barcelona", "match_id": "test"}
        keyboard = interactive.create_match_prediction_poll(match_data)
        if keyboard:
            print("   ✅ Poll creation working")
        else:
            print("   ❌ Poll creation failed")
            return False
        
        # Test quiz creation
        keyboard, question = interactive.create_quick_quiz()
        if question and hasattr(question, 'question'):
            print("   ✅ Quiz creation working")
        else:
            print("   ❌ Quiz creation failed")
            return False
        
        print("   ✅ Interactive features working")
    except Exception as e:
        print(f"   ❌ Interactive features test failed: {e}")
        return False
    
    print("\n🎉 All Phase 1 features are properly integrated!")
    print("\n📋 Next steps:")
    print("1. Deploy to Railway (already done)")
    print("2. Test with real questions using PHASE1_TESTING_QUESTIONS.md")
    print("3. Monitor user engagement and feedback")
    print("4. Plan Phase 2 based on usage patterns")
    
    return True

if __name__ == "__main__":
    success = test_phase1_integration()
    if success:
        print("\n✅ Phase 1 is ready for production testing!")
    else:
        print("\n❌ Phase 1 has issues that need to be fixed.")
    
    sys.exit(0 if success else 1)
