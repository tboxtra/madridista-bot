"""
Phase 1 Tools Integration
New tools that integrate match predictions, personalization, interactive features, and achievements.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

# Import Phase 1 modules
from analytics.predictions import MatchPredictionEngine
from orchestrator.personalization import PersonalizationEngine
from features.interactive import InteractiveFeatures
from gamification.achievements import AchievementSystem

def tool_predict_match_outcome(args: Dict[str, Any]) -> Dict[str, Any]:
    """Predict match outcome with AI analysis."""
    home_team = args.get("home_team", "")
    away_team = args.get("away_team", "")
    context = args.get("context", {})
    
    if not home_team or not away_team:
        return {"ok": False, "message": "Both teams required for prediction"}
    
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        engine = MatchPredictionEngine(openai_client)
        prediction = engine.predict_match_outcome(home_team, away_team, context)
        
        return {
            "ok": True,
            "prediction": {
                "home_win_probability": prediction.home_win_probability,
                "draw_probability": prediction.draw_probability,
                "away_win_probability": prediction.away_win_probability,
                "confidence": prediction.confidence,
                "key_factors": prediction.key_factors,
                "predicted_score": prediction.predicted_score,
                "reasoning": prediction.reasoning
            },
            "__source": "AI Prediction Engine"
        }
    except Exception as e:
        return {"ok": False, "message": f"Prediction failed: {str(e)}"}

def tool_predict_league_winner(args: Dict[str, Any]) -> Dict[str, Any]:
    """Predict league winner with remaining matches."""
    league = args.get("league", "")
    remaining_matches = args.get("remaining_matches", 10)
    
    if not league:
        return {"ok": False, "message": "League name required"}
    
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        engine = MatchPredictionEngine(openai_client)
        prediction = engine.predict_league_winner(league, remaining_matches)
        
        return prediction
    except Exception as e:
        return {"ok": False, "message": f"League prediction failed: {str(e)}"}

def tool_predict_transfer_probability(args: Dict[str, Any]) -> Dict[str, Any]:
    """Predict transfer probability using AI analysis."""
    player = args.get("player", "")
    target_team = args.get("target_team", "")
    
    if not player or not target_team:
        return {"ok": False, "message": "Player and target team required"}
    
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        engine = MatchPredictionEngine(openai_client)
        prediction = engine.predict_transfer_probability(player, target_team)
        
        return prediction
    except Exception as e:
        return {"ok": False, "message": f"Transfer prediction failed: {str(e)}"}

def tool_analyze_user_personality(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze user personality from conversation history."""
    user_id = args.get("user_id", "")
    conversation_history = args.get("conversation_history", [])
    
    if not user_id:
        return {"ok": False, "message": "User ID required"}
    
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        engine = PersonalizationEngine(openai_client)
        personality = engine.analyze_user_personality(user_id, conversation_history)
        
        return {
            "ok": True,
            "personality": {
                "user_id": personality.user_id,
                "preferred_teams": personality.preferred_teams,
                "response_style": personality.response_style.value,
                "detail_level": personality.detail_level.value,
                "interests": personality.interests,
                "engagement_level": personality.engagement_level.value,
                "favorite_players": personality.favorite_players,
                "preferred_competitions": personality.preferred_competitions
            },
            "__source": "Personalization Engine"
        }
    except Exception as e:
        return {"ok": False, "message": f"Personality analysis failed: {str(e)}"}

def tool_personalize_response(args: Dict[str, Any]) -> Dict[str, Any]:
    """Personalize response based on user personality."""
    response = args.get("response", "")
    user_personality = args.get("user_personality", {})
    query_context = args.get("query_context", {})
    
    if not response or not user_personality:
        return {"ok": False, "message": "Response and user personality required"}
    
    try:
        from openai import OpenAI
        from orchestrator.personalization import UserPersonality, ResponseStyle, DetailLevel, EngagementLevel
        
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Reconstruct UserPersonality object
        personality = UserPersonality(
            user_id=user_personality.get("user_id", ""),
            preferred_teams=user_personality.get("preferred_teams", []),
            response_style=ResponseStyle(user_personality.get("response_style", "casual")),
            detail_level=DetailLevel(user_personality.get("detail_level", "detailed")),
            interests=user_personality.get("interests", []),
            timezone=user_personality.get("timezone", "UTC"),
            language=user_personality.get("language", "en"),
            engagement_level=EngagementLevel(user_personality.get("engagement_level", "regular")),
            favorite_players=user_personality.get("favorite_players", []),
            preferred_competitions=user_personality.get("preferred_competitions", []),
            query_patterns=user_personality.get("query_patterns", {}),
            last_updated=user_personality.get("last_updated", datetime.now().isoformat())
        )
        
        engine = PersonalizationEngine(openai_client)
        personalized_response = engine.personalize_response(response, personality, query_context)
        
        return {
            "ok": True,
            "personalized_response": personalized_response,
            "__source": "Personalization Engine"
        }
    except Exception as e:
        return {"ok": False, "message": f"Response personalization failed: {str(e)}"}

def tool_create_match_prediction_poll(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create interactive prediction poll for upcoming match."""
    match_data = args.get("match_data", {})
    
    if not match_data:
        return {"ok": False, "message": "Match data required"}
    
    try:
        interactive = InteractiveFeatures()
        keyboard = interactive.create_match_prediction_poll(match_data)
        
        return {
            "ok": True,
            "poll_created": True,
            "match_data": match_data,
            "keyboard_data": str(keyboard),
            "__source": "Interactive Features"
        }
    except Exception as e:
        return {"ok": False, "message": f"Poll creation failed: {str(e)}"}

def tool_create_quiz_question(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create quick football trivia quiz."""
    category = args.get("category", None)
    difficulty = args.get("difficulty", None)
    
    try:
        interactive = InteractiveFeatures()
        keyboard, question = interactive.create_quick_quiz(category, difficulty)
        
        return {
            "ok": True,
            "quiz_created": True,
            "question": {
                "question": question.question,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "difficulty": question.difficulty,
                "category": question.category
            },
            "keyboard_data": str(keyboard),
            "__source": "Interactive Features"
        }
    except Exception as e:
        return {"ok": False, "message": f"Quiz creation failed: {str(e)}"}

def tool_create_team_comparison_poll(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create team comparison poll."""
    team_a = args.get("team_a", "")
    team_b = args.get("team_b", "")
    
    if not team_a or not team_b:
        return {"ok": False, "message": "Both teams required for comparison"}
    
    try:
        interactive = InteractiveFeatures()
        keyboard = interactive.create_team_comparison_poll(team_a, team_b)
        
        return {
            "ok": True,
            "poll_created": True,
            "team_a": team_a,
            "team_b": team_b,
            "keyboard_data": str(keyboard),
            "__source": "Interactive Features"
        }
    except Exception as e:
        return {"ok": False, "message": f"Team comparison poll creation failed: {str(e)}"}

def tool_check_user_achievements(args: Dict[str, Any]) -> Dict[str, Any]:
    """Check if user earned any new achievements."""
    user_id = args.get("user_id", "")
    action = args.get("action", "")
    data = args.get("data", {})
    
    if not user_id or not action:
        return {"ok": False, "message": "User ID and action required"}
    
    try:
        achievement_system = AchievementSystem()
        new_achievements = achievement_system.check_achievements(user_id, action, data)
        
        return {
            "ok": True,
            "new_achievements": [
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "rarity": achievement.rarity.value,
                    "points": achievement.points,
                    "reward": achievement.reward
                }
                for achievement in new_achievements
            ],
            "total_new": len(new_achievements),
            "__source": "Achievement System"
        }
    except Exception as e:
        return {"ok": False, "message": f"Achievement check failed: {str(e)}"}

def tool_get_user_achievements(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get user's earned achievements and progress."""
    user_id = args.get("user_id", "")
    
    if not user_id:
        return {"ok": False, "message": "User ID required"}
    
    try:
        achievement_system = AchievementSystem()
        earned_achievements = achievement_system.get_user_achievements(user_id)
        progress = achievement_system.get_user_achievement_progress(user_id)
        user_stats = achievement_system.get_user_stats(user_id)
        
        return {
            "ok": True,
            "earned_achievements": [
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "rarity": achievement.rarity.value,
                    "points": achievement.points
                }
                for achievement in earned_achievements
            ],
            "progress": {
                achievement_id: {
                    "name": progress_data["achievement"].name,
                    "description": progress_data["achievement"].description,
                    "icon": progress_data["achievement"].icon,
                    "completed": progress_data["completed"],
                    "progress": progress_data["progress"]
                }
                for achievement_id, progress_data in progress.items()
            },
            "user_stats": {
                "total_queries": user_stats.total_queries,
                "accurate_predictions": user_stats.accurate_predictions,
                "stats_queries": user_stats.stats_queries,
                "news_queries": user_stats.news_queries,
                "consecutive_days": user_stats.consecutive_days,
                "quiz_accuracy": (user_stats.quiz_correct / user_stats.quiz_total * 100) if user_stats.quiz_total > 0 else 0,
                "prediction_streak": user_stats.prediction_streak
            },
            "__source": "Achievement System"
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to get user achievements: {str(e)}"}

def tool_get_leaderboard(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get leaderboard for achievements or stats."""
    category = args.get("category", "achievements")  # achievements, predictions, quiz, queries
    
    try:
        achievement_system = AchievementSystem()
        leaderboard = achievement_system.get_leaderboard(category)
        
        return {
            "ok": True,
            "leaderboard": leaderboard,
            "category": category,
            "__source": "Achievement System"
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to get leaderboard: {str(e)}"}

def tool_get_personalized_suggestions(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get personalized suggestions based on user profile."""
    user_personality = args.get("user_personality", {})
    current_query = args.get("current_query", "")
    
    if not user_personality:
        return {"ok": False, "message": "User personality required"}
    
    try:
        from openai import OpenAI
        from orchestrator.personalization import UserPersonality, ResponseStyle, DetailLevel, EngagementLevel
        
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Reconstruct UserPersonality object
        personality = UserPersonality(
            user_id=user_personality.get("user_id", ""),
            preferred_teams=user_personality.get("preferred_teams", []),
            response_style=ResponseStyle(user_personality.get("response_style", "casual")),
            detail_level=DetailLevel(user_personality.get("detail_level", "detailed")),
            interests=user_personality.get("interests", []),
            timezone=user_personality.get("timezone", "UTC"),
            language=user_personality.get("language", "en"),
            engagement_level=EngagementLevel(user_personality.get("engagement_level", "regular")),
            favorite_players=user_personality.get("favorite_players", []),
            preferred_competitions=user_personality.get("preferred_competitions", []),
            query_patterns=user_personality.get("query_patterns", {}),
            last_updated=user_personality.get("last_updated", datetime.now().isoformat())
        )
        
        engine = PersonalizationEngine(openai_client)
        suggestions = engine.get_personalized_suggestions(personality, current_query)
        
        return {
            "ok": True,
            "suggestions": suggestions,
            "__source": "Personalization Engine"
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to get personalized suggestions: {str(e)}"}

def tool_handle_poll_response(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user response to interactive poll."""
    user_id = args.get("user_id", "")
    callback_data = args.get("callback_data", "")
    
    if not user_id or not callback_data:
        return {"ok": False, "message": "User ID and callback data required"}
    
    try:
        interactive = InteractiveFeatures()
        result = interactive.handle_poll_response(user_id, callback_data)
        
        return {
            "ok": True,
            "poll_response": result,
            "__source": "Interactive Features"
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to handle poll response: {str(e)}"}

def tool_get_poll_results(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get results for a specific poll."""
    poll_id = args.get("poll_id", "")
    
    if not poll_id:
        return {"ok": False, "message": "Poll ID required"}
    
    try:
        interactive = InteractiveFeatures()
        results = interactive.get_poll_results(poll_id)
        
        return {
            "ok": True,
            "poll_results": results,
            "__source": "Interactive Features"
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to get poll results: {str(e)}"}

# Phase 1 tool registry
PHASE1_TOOLS = {
    "tool_predict_match_outcome": tool_predict_match_outcome,
    "tool_predict_league_winner": tool_predict_league_winner,
    "tool_predict_transfer_probability": tool_predict_transfer_probability,
    "tool_analyze_user_personality": tool_analyze_user_personality,
    "tool_personalize_response": tool_personalize_response,
    "tool_create_match_prediction_poll": tool_create_match_prediction_poll,
    "tool_create_quiz_question": tool_create_quiz_question,
    "tool_create_team_comparison_poll": tool_create_team_comparison_poll,
    "tool_check_user_achievements": tool_check_user_achievements,
    "tool_get_user_achievements": tool_get_user_achievements,
    "tool_get_leaderboard": tool_get_leaderboard,
    "tool_get_personalized_suggestions": tool_get_personalized_suggestions,
    "tool_handle_poll_response": tool_handle_poll_response,
    "tool_get_poll_results": tool_get_poll_results
}
