#!/usr/bin/env python3
"""
Simple test script for Phase 1 features to identify specific issues.
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality of each Phase 1 component."""
    print("🧪 Testing basic Phase 1 functionality...")
    
    # Test 1: Match Prediction Engine
    try:
        from analytics.predictions import MatchPredictionEngine
        print("✅ MatchPredictionEngine imported")
        
        # Test basic initialization
        class MockClient:
            pass
        engine = MatchPredictionEngine(MockClient())
        print("✅ MatchPredictionEngine initialized")
        
    except Exception as e:
        print(f"❌ MatchPredictionEngine failed: {e}")
    
    # Test 2: Personalization Engine
    try:
        from orchestrator.personalization import PersonalizationEngine
        print("✅ PersonalizationEngine imported")
        
        class MockClient:
            pass
        engine = PersonalizationEngine(MockClient())
        print("✅ PersonalizationEngine initialized")
        
    except Exception as e:
        print(f"❌ PersonalizationEngine failed: {e}")
    
    # Test 3: Interactive Features
    try:
        from features.interactive import InteractiveFeatures
        print("✅ InteractiveFeatures imported")
        
        interactive = InteractiveFeatures()
        print("✅ InteractiveFeatures initialized")
        
        # Test basic functionality
        match_data = {"home_team": "Real Madrid", "away_team": "Barcelona", "match_id": "test"}
        keyboard = interactive.create_match_prediction_poll(match_data)
        print("✅ Match prediction poll created")
        
    except Exception as e:
        print(f"❌ InteractiveFeatures failed: {e}")
    
    # Test 4: Achievement System
    try:
        from gamification.achievements import AchievementSystem
        print("✅ AchievementSystem imported")
        
        system = AchievementSystem()
        print("✅ AchievementSystem initialized")
        
        # Test basic functionality
        user_stats = system.get_user_stats("test_user")
        print("✅ User stats retrieved")
        
    except Exception as e:
        print(f"❌ AchievementSystem failed: {e}")
    
    # Test 5: Phase 1 Tools
    try:
        from orchestrator.tools_phase1 import PHASE1_TOOLS
        print("✅ Phase 1 tools imported")
        
        print(f"✅ {len(PHASE1_TOOLS)} Phase 1 tools available")
        
    except Exception as e:
        print(f"❌ Phase 1 tools failed: {e}")
    
    # Test 6: Enhanced Brain Integration
    try:
        from orchestrator.enhanced_brain import EnhancedFootballBrain
        print("✅ EnhancedFootballBrain imported")
        
        class MockClient:
            pass
        brain = EnhancedFootballBrain(MockClient())
        print("✅ EnhancedFootballBrain initialized")
        
        # Check Phase 1 tools are registered
        phase1_tools = [name for name in brain.tool_functions.keys() if "predict" in name or "personalize" in name or "achievement" in name]
        print(f"✅ {len(phase1_tools)} Phase 1 tools registered in enhanced brain")
        
    except Exception as e:
        print(f"❌ EnhancedFootballBrain failed: {e}")

if __name__ == "__main__":
    test_basic_functionality()
