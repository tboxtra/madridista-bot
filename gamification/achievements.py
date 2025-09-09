"""
Achievement & Badge System
Gamification features to increase user engagement and retention.
"""

import json
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

class AchievementType(Enum):
    PREDICTION_MASTER = "prediction_master"
    STATS_EXPERT = "stats_expert"
    NEWS_HUNTER = "news_hunter"
    TEAM_LOYALIST = "team_loyalist"
    QUIZ_CHAMPION = "quiz_champion"
    DAILY_USER = "daily_user"
    SUPERFAN = "superfan"
    KNOWLEDGE_SEEKER = "knowledge_seeker"
    PREDICTION_STREAK = "prediction_streak"
    EARLY_BIRD = "early_bird"

class AchievementRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    rarity: AchievementRarity
    requirement: Dict
    reward: str
    points: int
    category: str

@dataclass
class UserAchievement:
    user_id: str
    achievement_id: str
    earned_at: datetime
    progress: Dict
    is_completed: bool

@dataclass
class UserStats:
    user_id: str
    total_queries: int
    accurate_predictions: int
    stats_queries: int
    news_queries: int
    team_mentions: Dict[str, int]  # team -> count
    consecutive_days: int
    last_active: datetime
    quiz_correct: int
    quiz_total: int
    prediction_streak: int
    best_prediction_streak: int

class AchievementSystem:
    """Achievement and badge system for user engagement."""
    
    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.user_achievements = {}  # user_id -> Set[achievement_id]
        self.user_stats = {}  # user_id -> UserStats
        self.achievement_history = {}  # user_id -> List[UserAchievement]
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize all available achievements."""
        
        return {
            "prediction_master": Achievement(
                id="prediction_master",
                name="🔮 Prediction Master",
                description="Make 10 accurate match predictions",
                icon="🔮",
                rarity=AchievementRarity.RARE,
                requirement={"accurate_predictions": 10},
                reward="Unlock advanced prediction features",
                points=100,
                category="predictions"
            ),
            "stats_expert": Achievement(
                id="stats_expert",
                name="📊 Stats Expert",
                description="Ask 50 statistics-related questions",
                icon="📊",
                rarity=AchievementRarity.COMMON,
                requirement={"stats_queries": 50},
                reward="Access to advanced analytics",
                points=50,
                category="knowledge"
            ),
            "news_hunter": Achievement(
                id="news_hunter",
                name="📰 News Hunter",
                description="Ask 25 news-related questions",
                icon="📰",
                rarity=AchievementRarity.COMMON,
                requirement={"news_queries": 25},
                reward="Priority news updates",
                points=50,
                category="knowledge"
            ),
            "team_loyalist": Achievement(
                id="team_loyalist",
                name="❤️ Team Loyalist",
                description="Ask about the same team 20 times",
                icon="❤️",
                rarity=AchievementRarity.RARE,
                requirement={"team_mentions": 20},
                reward="Personalized team updates",
                points=75,
                category="loyalty"
            ),
            "quiz_champion": Achievement(
                id="quiz_champion",
                name="🧠 Quiz Champion",
                description="Answer 20 quiz questions correctly",
                icon="🧠",
                rarity=AchievementRarity.RARE,
                requirement={"quiz_correct": 20},
                reward="Exclusive quiz categories",
                points=100,
                category="knowledge"
            ),
            "daily_user": Achievement(
                id="daily_user",
                name="📅 Daily User",
                description="Use the bot for 7 consecutive days",
                icon="📅",
                rarity=AchievementRarity.EPIC,
                requirement={"consecutive_days": 7},
                reward="Priority support and features",
                points=150,
                category="engagement"
            ),
            "superfan": Achievement(
                id="superfan",
                name="🔥 Superfan",
                description="Ask 100 questions about football",
                icon="🔥",
                rarity=AchievementRarity.EPIC,
                requirement={"total_queries": 100},
                reward="Superfan badge and exclusive content",
                points=200,
                category="engagement"
            ),
            "knowledge_seeker": Achievement(
                id="knowledge_seeker",
                name="🔍 Knowledge Seeker",
                description="Ask questions in 5 different categories",
                icon="🔍",
                rarity=AchievementRarity.COMMON,
                requirement={"categories_used": 5},
                reward="Access to knowledge base",
                points=75,
                category="knowledge"
            ),
            "prediction_streak": Achievement(
                id="prediction_streak",
                name="⚡ Prediction Streak",
                description="Make 5 correct predictions in a row",
                icon="⚡",
                rarity=AchievementRarity.EPIC,
                requirement={"prediction_streak": 5},
                reward="Prediction streak tracking",
                points=150,
                category="predictions"
            ),
            "early_bird": Achievement(
                id="early_bird",
                name="🐦 Early Bird",
                description="Use the bot before 8 AM for 5 days",
                icon="🐦",
                rarity=AchievementRarity.RARE,
                requirement={"early_morning_usage": 5},
                reward="Early access to new features",
                points=100,
                category="engagement"
            )
        }
    
    def check_achievements(self, user_id: str, action: str, data: Dict) -> List[Achievement]:
        """Check if user earned any new achievements."""
        
        # Update user stats
        self._update_user_stats(user_id, action, data)
        
        user_stats = self._get_user_stats(user_id)
        new_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id in self.user_achievements.get(user_id, set()):
                continue  # Already earned
            
            if self._check_achievement_requirement(achievement, user_stats, action, data):
                new_achievements.append(achievement)
                self._award_achievement(user_id, achievement_id)
        
        return new_achievements
    
    def _update_user_stats(self, user_id: str, action: str, data: Dict):
        """Update user statistics based on action."""
        
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(
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
            )
        
        stats = self.user_stats[user_id]
        current_time = datetime.now()
        
        # Update last active
        stats.last_active = current_time
        
        # Update based on action
        if action == "query":
            stats.total_queries += 1
            
            # Check for consecutive days
            if self._is_new_day(stats.last_active, current_time):
                stats.consecutive_days += 1
            else:
                stats.consecutive_days = 1
            
            # Update team mentions
            mentioned_teams = data.get("mentioned_teams", [])
            for team in mentioned_teams:
                if team in stats.team_mentions:
                    stats.team_mentions[team] += 1
                else:
                    stats.team_mentions[team] = 1
            
            # Update query type counts
            intent = data.get("intent", "general")
            if intent == "stats":
                stats.stats_queries += 1
            elif intent == "news":
                stats.news_queries += 1
        
        elif action == "prediction_correct":
            stats.accurate_predictions += 1
            stats.prediction_streak += 1
            if stats.prediction_streak > stats.best_prediction_streak:
                stats.best_prediction_streak = stats.prediction_streak
        
        elif action == "prediction_incorrect":
            stats.prediction_streak = 0
        
        elif action == "quiz_correct":
            stats.quiz_correct += 1
            stats.quiz_total += 1
        
        elif action == "quiz_incorrect":
            stats.quiz_total += 1
    
    def _check_achievement_requirement(self, achievement: Achievement, 
                                     user_stats: UserStats, action: str, data: Dict) -> bool:
        """Check if achievement requirement is met."""
        
        requirement = achievement.requirement
        
        if "accurate_predictions" in requirement:
            return user_stats.accurate_predictions >= requirement["accurate_predictions"]
        
        if "stats_queries" in requirement:
            return user_stats.stats_queries >= requirement["stats_queries"]
        
        if "news_queries" in requirement:
            return user_stats.news_queries >= requirement["news_queries"]
        
        if "team_mentions" in requirement:
            max_team_mentions = max(user_stats.team_mentions.values()) if user_stats.team_mentions else 0
            return max_team_mentions >= requirement["team_mentions"]
        
        if "consecutive_days" in requirement:
            return user_stats.consecutive_days >= requirement["consecutive_days"]
        
        if "total_queries" in requirement:
            return user_stats.total_queries >= requirement["total_queries"]
        
        if "quiz_correct" in requirement:
            return user_stats.quiz_correct >= requirement["quiz_correct"]
        
        if "prediction_streak" in requirement:
            return user_stats.prediction_streak >= requirement["prediction_streak"]
        
        if "categories_used" in requirement:
            # Count unique intents used
            unique_intents = set()
            for achievement_history in self.achievement_history.get(user_stats.user_id, []):
                if hasattr(achievement_history, 'intent'):
                    unique_intents.add(achievement_history.intent)
            return len(unique_intents) >= requirement["categories_used"]
        
        if "early_morning_usage" in requirement:
            # Check if user used bot before 8 AM
            current_hour = datetime.now().hour
            return current_hour < 8
        
        return False
    
    def _award_achievement(self, user_id: str, achievement_id: str):
        """Award achievement to user."""
        
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = set()
        
        self.user_achievements[user_id].add(achievement_id)
        
        # Add to achievement history
        if user_id not in self.achievement_history:
            self.achievement_history[user_id] = []
        
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            earned_at=datetime.now(),
            progress={},
            is_completed=True
        )
        
        self.achievement_history[user_id].append(user_achievement)
    
    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Get user's earned achievements."""
        
        earned_ids = self.user_achievements.get(user_id, set())
        return [self.achievements[aid] for aid in earned_ids if aid in self.achievements]
    
    def get_user_achievement_progress(self, user_id: str) -> Dict:
        """Get user's progress towards all achievements."""
        
        user_stats = self._get_user_stats(user_id)
        progress = {}
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id in self.user_achievements.get(user_id, set()):
                progress[achievement_id] = {
                    "achievement": achievement,
                    "completed": True,
                    "progress": 100
                }
            else:
                progress_percentage = self._calculate_progress_percentage(achievement, user_stats)
                progress[achievement_id] = {
                    "achievement": achievement,
                    "completed": False,
                    "progress": progress_percentage
                }
        
        return progress
    
    def _calculate_progress_percentage(self, achievement: Achievement, user_stats: UserStats) -> int:
        """Calculate progress percentage for an achievement."""
        
        requirement = achievement.requirement
        
        if "accurate_predictions" in requirement:
            return min(100, (user_stats.accurate_predictions / requirement["accurate_predictions"]) * 100)
        
        if "stats_queries" in requirement:
            return min(100, (user_stats.stats_queries / requirement["stats_queries"]) * 100)
        
        if "news_queries" in requirement:
            return min(100, (user_stats.news_queries / requirement["news_queries"]) * 100)
        
        if "team_mentions" in requirement:
            max_team_mentions = max(user_stats.team_mentions.values()) if user_stats.team_mentions else 0
            return min(100, (max_team_mentions / requirement["team_mentions"]) * 100)
        
        if "consecutive_days" in requirement:
            return min(100, (user_stats.consecutive_days / requirement["consecutive_days"]) * 100)
        
        if "total_queries" in requirement:
            return min(100, (user_stats.total_queries / requirement["total_queries"]) * 100)
        
        if "quiz_correct" in requirement:
            return min(100, (user_stats.quiz_correct / requirement["quiz_correct"]) * 100)
        
        if "prediction_streak" in requirement:
            return min(100, (user_stats.prediction_streak / requirement["prediction_streak"]) * 100)
        
        return 0
    
    def get_user_stats(self, user_id: str) -> UserStats:
        """Get user statistics."""
        return self._get_user_stats(user_id)
    
    def _get_user_stats(self, user_id: str) -> UserStats:
        """Get or create user statistics."""
        
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(
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
            )
        
        return self.user_stats[user_id]
    
    def _is_new_day(self, last_active: datetime, current_time: datetime) -> bool:
        """Check if current time is a new day compared to last active."""
        return current_time.date() > last_active.date()
    
    def get_leaderboard(self, category: str = None):
        """Get leaderboard for achievements or stats."""
        
        leaderboard = []
        
        for user_id, stats in self.user_stats.items():
            user_data = {
                "user_id": user_id,
                "total_queries": stats.total_queries,
                "accurate_predictions": stats.accurate_predictions,
                "achievements_earned": len(self.user_achievements.get(user_id, set())),
                "quiz_accuracy": (stats.quiz_correct / stats.quiz_total * 100) if stats.quiz_total > 0 else 0,
                "prediction_streak": stats.prediction_streak,
                "consecutive_days": stats.consecutive_days
            }
            
            if category == "achievements":
                user_data["score"] = user_data["achievements_earned"]
            elif category == "predictions":
                user_data["score"] = user_data["accurate_predictions"]
            elif category == "quiz":
                user_data["score"] = user_data["quiz_accuracy"]
            else:
                user_data["score"] = user_data["total_queries"]
            
            leaderboard.append(user_data)
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return leaderboard[:10]  # Top 10
    
    def get_achievement_by_rarity(self, rarity: AchievementRarity) -> List[Achievement]:
        """Get achievements by rarity."""
        return [achievement for achievement in self.achievements.values() 
                if achievement.rarity == rarity]
    
    def export_data(self) -> Dict:
        """Export achievement system data."""
        return {
            "user_achievements": {user_id: list(achievements) 
                                for user_id, achievements in self.user_achievements.items()},
            "user_stats": {user_id: asdict(stats) 
                          for user_id, stats in self.user_stats.items()},
            "achievement_history": {user_id: [asdict(history) for history in histories]
                                  for user_id, histories in self.achievement_history.items()}
        }
    
    def import_data(self, data: Dict):
        """Import achievement system data."""
        self.user_achievements = {user_id: set(achievements) 
                                for user_id, achievements in data.get("user_achievements", {}).items()}
        
        # Import user stats
        for user_id, stats_data in data.get("user_stats", {}).items():
            self.user_stats[user_id] = UserStats(**stats_data)
        
        # Import achievement history
        for user_id, history_data in data.get("achievement_history", {}).items():
            self.achievement_history[user_id] = [
                UserAchievement(**history) for history in history_data
            ]
