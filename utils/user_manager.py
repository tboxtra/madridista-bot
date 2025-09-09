"""
User Management System
Handles user profiles, achievements, and statistics tracking.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from gamification.achievements import AchievementSystem, UserStats
from orchestrator.personalization import UserPersonality, ResponseStyle, DetailLevel, EngagementLevel

@dataclass
class UserProfile:
    user_id: str
    username: str
    first_name: str
    last_name: str
    created_at: datetime
    last_active: datetime
    total_queries: int
    favorite_teams: List[str]
    favorite_players: List[str]
    preferred_competitions: List[str]
    personality: Optional[UserPersonality]
    achievements: List[str]  # List of achievement IDs
    stats: UserStats
    settings: Dict[str, Any]

class UserManager:
    """Manages user profiles, achievements, and statistics."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.achievement_system = AchievementSystem()
        self.user_profiles = {}
        self._ensure_data_dir()
        self._load_user_data()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_user_data(self):
        """Load user data from storage."""
        try:
            user_file = os.path.join(self.data_dir, "user_profiles.json")
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        # Convert datetime strings back to datetime objects
                        profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
                        profile_data['last_active'] = datetime.fromisoformat(profile_data['last_active'])
                        
                        # Reconstruct UserStats
                        stats_data = profile_data.get('stats', {})
                        profile_data['stats'] = UserStats(**stats_data)
                        
                        # Reconstruct UserPersonality if exists
                        if profile_data.get('personality'):
                            personality_data = profile_data['personality']
                            personality_data['response_style'] = ResponseStyle(personality_data['response_style'])
                            personality_data['detail_level'] = DetailLevel(personality_data['detail_level'])
                            personality_data['engagement_level'] = EngagementLevel(personality_data['engagement_level'])
                            profile_data['personality'] = UserPersonality(**personality_data)
                        
                        self.user_profiles[user_id] = UserProfile(**profile_data)
        except Exception as e:
            print(f"Error loading user data: {e}")
    
    def _save_user_data(self):
        """Save user data to storage."""
        try:
            user_file = os.path.join(self.data_dir, "user_profiles.json")
            data = {}
            for user_id, profile in self.user_profiles.items():
                profile_dict = asdict(profile)
                # Convert datetime objects to strings
                profile_dict['created_at'] = profile.created_at.isoformat()
                profile_dict['last_active'] = profile.last_active.isoformat()
                data[user_id] = profile_dict
            
            with open(user_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def get_or_create_user(self, user_id: str, username: str = "", first_name: str = "", last_name: str = "") -> UserProfile:
        """Get existing user or create new one."""
        
        if user_id in self.user_profiles:
            # Update last active
            self.user_profiles[user_id].last_active = datetime.now()
            return self.user_profiles[user_id]
        
        # Create new user
        new_profile = UserProfile(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.now(),
            last_active=datetime.now(),
            total_queries=0,
            favorite_teams=["Real Madrid"],  # Default
            favorite_players=[],
            preferred_competitions=["La Liga", "Champions League"],
            personality=None,
            achievements=[],
            stats=UserStats(
                user_id=user_id,
                total_queries=0,
                accurate_predictions=0,
                stats_queries=0,
                news_queries=0,
                team_mentions={},
                consecutive_days=0,
                last_active=datetime.now(),
                quiz_correct=0,
                quiz_total=0,
                prediction_streak=0,
                best_prediction_streak=0
            ),
            settings={
                "notifications": True,
                "language": "en",
                "timezone": "UTC"
            }
        )
        
        self.user_profiles[user_id] = new_profile
        self._save_user_data()
        return new_profile
    
    def update_user_activity(self, user_id: str, action: str, data: Dict[str, Any]):
        """Update user activity and check for achievements."""
        
        if user_id not in self.user_profiles:
            return
        
        user_profile = self.user_profiles[user_id]
        
        # Update basic stats
        if action == "query":
            user_profile.total_queries += 1
            user_profile.stats.total_queries += 1
            
            # Update team mentions
            mentioned_teams = data.get("mentioned_teams", [])
            for team in mentioned_teams:
                if team in user_profile.stats.team_mentions:
                    user_profile.stats.team_mentions[team] += 1
                else:
                    user_profile.stats.team_mentions[team] = 1
                
                # Add to favorite teams if mentioned frequently
                if user_profile.stats.team_mentions[team] >= 5 and team not in user_profile.favorite_teams:
                    user_profile.favorite_teams.append(team)
            
            # Update query type counts
            intent = data.get("intent", "general")
            if intent == "stats":
                user_profile.stats.stats_queries += 1
            elif intent == "news":
                user_profile.stats.news_queries += 1
        
        elif action == "prediction_correct":
            user_profile.stats.accurate_predictions += 1
            user_profile.stats.prediction_streak += 1
            if user_profile.stats.prediction_streak > user_profile.stats.best_prediction_streak:
                user_profile.stats.best_prediction_streak = user_profile.stats.prediction_streak
        
        elif action == "prediction_incorrect":
            user_profile.stats.prediction_streak = 0
        
        elif action == "quiz_correct":
            user_profile.stats.quiz_correct += 1
            user_profile.stats.quiz_total += 1
        
        elif action == "quiz_incorrect":
            user_profile.stats.quiz_total += 1
        
        # Check for new achievements
        new_achievements = self.achievement_system.check_achievements(user_id, action, data)
        
        for achievement in new_achievements:
            if achievement.id not in user_profile.achievements:
                user_profile.achievements.append(achievement.id)
        
        # Update last active
        user_profile.last_active = datetime.now()
        user_profile.stats.last_active = datetime.now()
        
        # Save changes
        self._save_user_data()
        
        return new_achievements
    
    def get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get user's achievements and progress."""
        
        if user_id not in self.user_profiles:
            return {"ok": False, "message": "User not found"}
        
        user_profile = self.user_profiles[user_id]
        earned_achievements = self.achievement_system.get_user_achievements(user_id)
        progress = self.achievement_system.get_user_achievement_progress(user_id)
        
        return {
            "ok": True,
            "user_id": user_id,
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
                "total_queries": user_profile.stats.total_queries,
                "accurate_predictions": user_profile.stats.accurate_predictions,
                "stats_queries": user_profile.stats.stats_queries,
                "news_queries": user_profile.stats.news_queries,
                "consecutive_days": user_profile.stats.consecutive_days,
                "quiz_accuracy": (user_profile.stats.quiz_correct / user_profile.stats.quiz_total * 100) if user_profile.stats.quiz_total > 0 else 0,
                "prediction_streak": user_profile.stats.prediction_streak,
                "favorite_teams": user_profile.favorite_teams,
                "favorite_players": user_profile.favorite_players
            }
        }
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile."""
        return self.user_profiles.get(user_id)
    
    def update_user_personality(self, user_id: str, personality: UserPersonality):
        """Update user personality."""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].personality = personality
            self._save_user_data()
    
    def get_leaderboard(self, category: str = "achievements") -> List[Dict]:
        """Get leaderboard for achievements or stats."""
        return self.achievement_system.get_leaderboard(category)
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user insights."""
        
        if user_id not in self.user_profiles:
            return {"ok": False, "message": "User not found"}
        
        user_profile = self.user_profiles[user_id]
        
        return {
            "ok": True,
            "user_id": user_id,
            "profile": {
                "username": user_profile.username,
                "first_name": user_profile.first_name,
                "created_at": user_profile.created_at.isoformat(),
                "last_active": user_profile.last_active.isoformat(),
                "total_queries": user_profile.total_queries,
                "favorite_teams": user_profile.favorite_teams,
                "favorite_players": user_profile.favorite_players,
                "preferred_competitions": user_profile.preferred_competitions
            },
            "personality": {
                "response_style": user_profile.personality.response_style.value if user_profile.personality else "casual",
                "detail_level": user_profile.personality.detail_level.value if user_profile.personality else "detailed",
                "engagement_level": user_profile.personality.engagement_level.value if user_profile.personality else "regular",
                "interests": user_profile.personality.interests if user_profile.personality else []
            },
            "achievements": self.get_user_achievements(user_id),
            "stats": user_profile.stats.__dict__
        }
