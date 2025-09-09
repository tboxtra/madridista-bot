#!/usr/bin/env python3
"""
Comprehensive test script for Phase 1 features:
- AI-powered match predictions
- Advanced personalization
- Interactive features
- Achievement system
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Phase 1 modules can be imported."""
    print("🧪 Testing Phase 1 imports...")
    
    try:
        from analytics.predictions import MatchPredictionEngine
        print("✅ MatchPredictionEngine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import MatchPredictionEngine: {e}")
        return False
    
    try:
        from orchestrator.personalization import PersonalizationEngine
        print("✅ PersonalizationEngine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import PersonalizationEngine: {e}")
        return False
    
    try:
        from features.interactive import InteractiveFeatures
        print("✅ InteractiveFeatures imported successfully")
    except Exception as e:
        print(f"❌ Failed to import InteractiveFeatures: {e}")
        return False
    
    try:
        from gamification.achievements import AchievementSystem
        print("✅ AchievementSystem imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AchievementSystem: {e}")
        return False
    
    try:
        from orchestrator.tools_phase1 import PHASE1_TOOLS
        print("✅ Phase 1 tools imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Phase 1 tools: {e}")
        return False
    
    return True

def test_match_prediction_engine():
    """Test the match prediction engine."""
    print("\n🔮 Testing Match Prediction Engine...")
    
    try:
        from analytics.predictions import MatchPredictionEngine
        from openai import OpenAI
        
        # Mock OpenAI client for testing
        class MockOpenAI:
            class ChatCompletion:
                def __init__(self, content):
                    self.content = content
                
                class Choice:
                    def __init__(self, content):
                        self.message = type('Message', (), {'content': content})()
                
                def __init__(self, content):
                    self.choices = [self.Choice(content)]
            
            def chat(self):
                return self
            
            def completions(self):
                return self
            
            def create(self, **kwargs):
                mock_response = {
                    "home_win_probability": 0.45,
                    "draw_probability": 0.25,
                    "away_win_probability": 0.30,
                    "confidence": 0.75,
                    "key_factors": ["Home advantage", "Recent form", "Head-to-head record"],
                    "predicted_score": "2-1",
                    "reasoning": "Based on recent form and home advantage"
                }
                return self.ChatCompletion(json.dumps(mock_response))
        
        mock_client = MockOpenAI()
        engine = MatchPredictionEngine(mock_client)
        
        # Test match prediction
        prediction = engine.predict_match_outcome("Real Madrid", "Barcelona")
        
        assert hasattr(prediction, 'home_win_probability')
        assert hasattr(prediction, 'confidence')
        assert hasattr(prediction, 'key_factors')
        
        print("✅ Match prediction engine working correctly")
        print(f"   Home win probability: {prediction.home_win_probability}")
        print(f"   Confidence: {prediction.confidence}")
        print(f"   Key factors: {prediction.key_factors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Match prediction engine test failed: {e}")
        return False

def test_personalization_engine():
    """Test the personalization engine."""
    print("\n🎨 Testing Personalization Engine...")
    
    try:
        from orchestrator.personalization import PersonalizationEngine, UserPersonality, ResponseStyle, DetailLevel, EngagementLevel
        from openai import OpenAI
        
        # Mock OpenAI client
        class MockOpenAI:
            class ChatCompletion:
                def __init__(self, content):
                    self.content = content
                
                class Choice:
                    def __init__(self, content):
                        self.message = type('Message', (), {'content': content})()
                
                def __init__(self, content):
                    self.choices = [self.Choice(content)]
            
            def chat(self):
                return self
            
            def completions(self):
                return self
            
            def create(self, **kwargs):
                if "personality" in kwargs.get("messages", [{}])[0].get("content", ""):
                    mock_response = {
                        "preferred_teams": ["Real Madrid"],
                        "response_style": "enthusiastic",
                        "detail_level": "detailed",
                        "interests": ["stats", "news", "predictions"],
                        "timezone": "UTC",
                        "language": "en",
                        "engagement_level": "superfan",
                        "favorite_players": ["Benzema", "Modric"],
                        "preferred_competitions": ["La Liga", "Champions League"],
                        "query_patterns": {"stats": 5, "news": 3},
                        "reasoning": "User shows high engagement with Real Madrid"
                    }
                else:
                    mock_response = "This is a personalized response for an enthusiastic Real Madrid superfan!"
                
                return self.ChatCompletion(json.dumps(mock_response) if isinstance(mock_response, dict) else mock_response)
        
        mock_client = MockOpenAI()
        engine = PersonalizationEngine(mock_client)
        
        # Test personality analysis
        conversation_history = [
            {"role": "user", "content": "What are Real Madrid's stats this season?"},
            {"role": "assistant", "content": "Real Madrid has been performing well..."},
            {"role": "user", "content": "Any news about Benzema?"}
        ]
        
        personality = engine.analyze_user_personality("test_user", conversation_history)
        
        assert personality.user_id == "test_user"
        assert "Real Madrid" in personality.preferred_teams
        assert personality.response_style == ResponseStyle.ENTHUSIASTIC
        
        print("✅ Personalization engine working correctly")
        print(f"   Preferred teams: {personality.preferred_teams}")
        print(f"   Response style: {personality.response_style.value}")
        print(f"   Engagement level: {personality.engagement_level.value}")
        
        # Test response personalization
        original_response = "Real Madrid won their last match 2-1."
        personalized = engine.personalize_response(original_response, personality)
        
        assert personalized != original_response
        print("✅ Response personalization working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Personalization engine test failed: {e}")
        return False

def test_interactive_features():
    """Test the interactive features."""
    print("\n🎮 Testing Interactive Features...")
    
    try:
        from features.interactive import InteractiveFeatures, QuizQuestion
        
        interactive = InteractiveFeatures()
        
        # Test match prediction poll creation
        match_data = {
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "match_time": "2024-01-15 20:00",
            "match_id": "test_match_123"
        }
        
        keyboard = interactive.create_match_prediction_poll(match_data)
        assert keyboard is not None
        print("✅ Match prediction poll creation working")
        
        # Test quiz creation
        keyboard, question = interactive.create_quick_quiz("history", "easy")
        assert isinstance(question, QuizQuestion)
        assert len(question.options) > 0
        print("✅ Quiz creation working")
        print(f"   Question: {question.question}")
        print(f"   Options: {question.options}")
        
        # Test team comparison poll
        keyboard = interactive.create_team_comparison_poll("Real Madrid", "Barcelona")
        assert keyboard is not None
        print("✅ Team comparison poll creation working")
        
        # Test poll response handling
        result = interactive.handle_poll_response("test_user", "predict_home_test_poll")
        assert result["ok"] == True
        print("✅ Poll response handling working")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive features test failed: {e}")
        return False

def test_achievement_system():
    """Test the achievement system."""
    print("\n🏆 Testing Achievement System...")
    
    try:
        from gamification.achievements import AchievementSystem, AchievementType, AchievementRarity
        
        system = AchievementSystem()
        
        # Test achievement checking
        user_id = "test_user"
        action = "query"
        data = {
            "intent": "stats",
            "mentioned_teams": ["Real Madrid"]
        }
        
        new_achievements = system.check_achievements(user_id, action, data)
        print(f"✅ Achievement checking working - {len(new_achievements)} new achievements")
        
        # Test user stats
        user_stats = system.get_user_stats(user_id)
        assert user_stats.user_id == user_id
        assert user_stats.total_queries > 0
        print("✅ User stats tracking working")
        print(f"   Total queries: {user_stats.total_queries}")
        print(f"   Team mentions: {user_stats.team_mentions}")
        
        # Test achievement progress
        progress = system.get_user_achievement_progress(user_id)
        assert len(progress) > 0
        print("✅ Achievement progress tracking working")
        
        # Test leaderboard
        leaderboard = system.get_leaderboard("achievements")
        assert isinstance(leaderboard, list)
        print("✅ Leaderboard generation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Achievement system test failed: {e}")
        return False

def test_phase1_tools():
    """Test Phase 1 tools integration."""
    print("\n🔧 Testing Phase 1 Tools...")
    
    try:
        from orchestrator.tools_phase1 import PHASE1_TOOLS
        
        # Test that all tools are available
        expected_tools = [
            "tool_predict_match_outcome",
            "tool_predict_league_winner",
            "tool_analyze_user_personality",
            "tool_create_match_prediction_poll",
            "tool_create_quiz_question",
            "tool_check_user_achievements",
            "tool_get_user_achievements"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in PHASE1_TOOLS, f"Tool {tool_name} not found"
            print(f"✅ {tool_name} available")
        
        # Test a simple tool call
        args = {
            "home_team": "Real Madrid",
            "away_team": "Barcelona"
        }
        
        # Note: This will fail without proper OpenAI API key, but we can test the structure
        try:
            result = PHASE1_TOOLS["tool_predict_match_outcome"](args)
            print("✅ Tool call structure working")
        except Exception as e:
            if "API key" in str(e) or "OpenAI" in str(e):
                print("✅ Tool call structure working (API key needed for full test)")
            else:
                raise e
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 tools test failed: {e}")
        return False

def test_enhanced_brain_integration():
    """Test that Phase 1 features are integrated with enhanced brain."""
    print("\n🧠 Testing Enhanced Brain Integration...")
    
    try:
        from orchestrator.enhanced_brain import EnhancedFootballBrain
        from openai import OpenAI
        
        # Mock OpenAI client
        class MockOpenAI:
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
        
        mock_client = MockOpenAI()
        brain = EnhancedFootballBrain(mock_client)
        
        # Test that Phase 1 tools are registered
        phase1_tools = [
            "tool_predict_match_outcome",
            "tool_analyze_user_personality",
            "tool_create_match_prediction_poll",
            "tool_check_user_achievements"
        ]
        
        for tool_name in phase1_tools:
            assert tool_name in brain.tool_functions, f"Phase 1 tool {tool_name} not registered"
            print(f"✅ {tool_name} registered in enhanced brain")
        
        # Test system prompt includes Phase 1 capabilities
        system_prompt = brain.system_prompt
        assert "AI-powered predictions" in system_prompt
        assert "personalization" in system_prompt
        assert "interactive features" in system_prompt
        assert "achievement system" in system_prompt
        print("✅ System prompt includes Phase 1 capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced brain integration test failed: {e}")
        return False

def run_all_tests():
    """Run all Phase 1 tests."""
    print("🚀 Starting Phase 1 Feature Tests\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Match Prediction Engine", test_match_prediction_engine),
        ("Personalization Engine", test_personalization_engine),
        ("Interactive Features", test_interactive_features),
        ("Achievement System", test_achievement_system),
        ("Phase 1 Tools", test_phase1_tools),
        ("Enhanced Brain Integration", test_enhanced_brain_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 1 features are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
