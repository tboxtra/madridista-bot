"""
Context-aware conversation memory system for football bot.
Tracks user interests, mentioned teams/players, and conversation history.
"""

import json
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime, timedelta

@dataclass
class ConversationEntry:
    """Represents a single conversation entry."""
    timestamp: float
    user_id: str
    query: str
    response: str
    intent: str
    entities: List[Dict]
    tools_used: List[str]
    satisfaction_score: Optional[float] = None

@dataclass
class UserProfile:
    """Represents a user's football interests and preferences."""
    user_id: str
    favorite_teams: Set[str]
    favorite_players: Set[str]
    preferred_competitions: Set[str]
    query_patterns: Dict[str, int]  # intent -> count
    active_time: List[float]  # timestamps of activity
    last_interaction: float
    total_queries: int

@dataclass
class ContextSummary:
    """Represents current conversation context."""
    recent_queries: List[str]
    mentioned_teams: Set[str]
    mentioned_players: Set[str]
    current_topic: str
    conversation_flow: List[str]
    user_mood: str  # interested, casual, frustrated, etc.

class ConversationMemory:
    """Context-aware conversation memory system."""
    
    def __init__(self, max_history: int = 50, max_user_profiles: int = 1000):
        self.max_history = max_history
        self.max_user_profiles = max_user_profiles
        
        # Core storage
        self.conversation_history: deque = deque(maxlen=max_history)
        self.user_profiles: Dict[str, UserProfile] = {}
        self.team_mentions: Dict[str, int] = defaultdict(int)
        self.player_mentions: Dict[str, int] = defaultdict(int)
        self.competition_mentions: Dict[str, int] = defaultdict(int)
        
        # Context tracking
        self.current_context: Dict[str, ContextSummary] = {}
        
        # Learning parameters
        self.interest_decay_factor = 0.95
        self.context_window_hours = 24
        
    def add_conversation(self, user_id: str, query: str, response: str, 
                        intent: str, entities: List[Dict], tools_used: List[str]) -> None:
        """Add a new conversation entry to memory."""
        
        entry = ConversationEntry(
            timestamp=time.time(),
            user_id=user_id,
            query=query,
            response=response,
            intent=intent,
            entities=entities,
            tools_used=tools_used
        )
        
        self.conversation_history.append(entry)
        self._update_user_profile(user_id, entry)
        self._update_global_mentions(entities)
        self._update_context(user_id, entry)
    
    def get_user_context(self, user_id: str) -> ContextSummary:
        """Get current context for a user."""
        if user_id not in self.current_context:
            self.current_context[user_id] = ContextSummary(
                recent_queries=[],
                mentioned_teams=set(),
                mentioned_players=set(),
                current_topic="",
                conversation_flow=[],
                user_mood="neutral"
            )
        
        return self.current_context[user_id]
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                favorite_teams=set(),
                favorite_players=set(),
                preferred_competitions=set(),
                query_patterns=defaultdict(int),
                active_time=[],
                last_interaction=time.time(),
                total_queries=0
            )
        
        return self.user_profiles[user_id]
    
    def get_recent_context(self, user_id: str, hours: int = 2) -> Dict[str, Any]:
        """Get recent conversation context for a user."""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_entries = [
            entry for entry in self.conversation_history
            if entry.user_id == user_id and entry.timestamp > cutoff_time
        ]
        
        if not recent_entries:
            return {"recent_queries": [], "mentioned_entities": [], "context": "No recent context"}
        
        # Extract recent entities
        recent_teams = set()
        recent_players = set()
        recent_competitions = set()
        
        for entry in recent_entries:
            for entity in entry.entities:
                if entity.get("type") == "team":
                    recent_teams.add(entity.get("value", ""))
                elif entity.get("type") == "player":
                    recent_players.add(entity.get("value", ""))
                elif entity.get("type") == "competition":
                    recent_competitions.add(entity.get("value", ""))
        
        return {
            "recent_queries": [entry.query for entry in recent_entries[-5:]],  # Last 5 queries
            "mentioned_teams": list(recent_teams),
            "mentioned_players": list(recent_players),
            "mentioned_competitions": list(recent_competitions),
            "recent_intents": [entry.intent for entry in recent_entries[-3:]],  # Last 3 intents
            "tools_used": list(set([tool for entry in recent_entries for tool in entry.tools_used])),
            "context": f"User has been asking about {', '.join(recent_teams)} recently" if recent_teams else "No specific team focus"
        }
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's football preferences based on history."""
        profile = self.get_user_profile(user_id)
        
        # Calculate favorite teams based on mentions
        team_scores = defaultdict(float)
        for entry in self.conversation_history:
            if entry.user_id == user_id:
                for entity in entry.entities:
                    if entity.get("type") == "team":
                        team = entity.get("value", "")
                        # Decay older mentions
                        age_factor = self.interest_decay_factor ** ((time.time() - entry.timestamp) / 86400)
                        team_scores[team] += age_factor
        
        favorite_teams = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate preferred query types
        intent_scores = defaultdict(int)
        for entry in self.conversation_history:
            if entry.user_id == user_id:
                intent_scores[entry.intent] += 1
        
        preferred_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "favorite_teams": [team for team, score in favorite_teams if score > 0.1],
            "preferred_query_types": [intent for intent, count in preferred_intents],
            "total_queries": profile.total_queries,
            "most_active_time": self._get_most_active_time(user_id),
            "engagement_level": self._calculate_engagement_level(user_id)
        }
    
    def suggest_follow_up_questions(self, user_id: str, current_query: str, 
                                  current_response: str) -> List[str]:
        """Suggest follow-up questions based on context and preferences."""
        context = self.get_recent_context(user_id)
        preferences = self.get_user_preferences(user_id)
        
        suggestions = []
        
        # Based on recent teams mentioned
        if context.get("mentioned_teams"):
            teams = context["mentioned_teams"]
            if len(teams) >= 2:
                suggestions.append(f"How do {teams[0]} and {teams[1]} compare this season?")
            else:
                team = teams[0]
                suggestions.extend([
                    f"What's {team}'s next fixture?",
                    f"How is {team} performing recently?",
                    f"Any news about {team}?"
                ])
        
        # Based on query patterns
        if "match_result" in context.get("recent_intents", []):
            suggestions.extend([
                "What about their head-to-head record?",
                "How have they been performing recently?",
                "When do they play next?"
            ])
        
        # Based on user preferences
        if preferences.get("favorite_teams"):
            favorite_team = preferences["favorite_teams"][0]
            suggestions.append(f"What's the latest news about {favorite_team}?")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def update_satisfaction(self, user_id: str, query: str, satisfaction_score: float) -> None:
        """Update satisfaction score for a conversation."""
        for entry in self.conversation_history:
            if (entry.user_id == user_id and 
                entry.query == query and 
                entry.satisfaction_score is None):
                entry.satisfaction_score = satisfaction_score
                break
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        """Get insights about conversation patterns."""
        if not self.conversation_history:
            return {"message": "No conversation history available"}
        
        # Most mentioned teams
        team_mentions = defaultdict(int)
        player_mentions = defaultdict(int)
        intent_counts = defaultdict(int)
        
        for entry in self.conversation_history:
            intent_counts[entry.intent] += 1
            for entity in entry.entities:
                if entity.get("type") == "team":
                    team_mentions[entity.get("value", "")] += 1
                elif entity.get("type") == "player":
                    player_mentions[entity.get("value", "")] += 1
        
        return {
            "total_conversations": len(self.conversation_history),
            "most_mentioned_teams": sorted(team_mentions.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_mentioned_players": sorted(player_mentions.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_common_intents": sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "active_users": len(set(entry.user_id for entry in self.conversation_history)),
            "average_queries_per_user": len(self.conversation_history) / max(1, len(set(entry.user_id for entry in self.conversation_history)))
        }
    
    def _update_user_profile(self, user_id: str, entry: ConversationEntry) -> None:
        """Update user profile with new conversation entry."""
        profile = self.get_user_profile(user_id)
        
        profile.total_queries += 1
        profile.last_interaction = entry.timestamp
        profile.active_time.append(entry.timestamp)
        profile.query_patterns[entry.intent] += 1
        
        # Update favorite teams/players based on entities
        for entity in entry.entities:
            if entity.get("type") == "team":
                profile.favorite_teams.add(entity.get("value", ""))
            elif entity.get("type") == "player":
                profile.favorite_players.add(entity.get("value", ""))
            elif entity.get("type") == "competition":
                profile.preferred_competitions.add(entity.get("value", ""))
        
        # Keep only recent active times (last 30 days)
        cutoff_time = time.time() - (30 * 24 * 3600)
        profile.active_time = [t for t in profile.active_time if t > cutoff_time]
    
    def _update_global_mentions(self, entities: List[Dict]) -> None:
        """Update global mention counts."""
        for entity in entities:
            if entity.get("type") == "team":
                self.team_mentions[entity.get("value", "")] += 1
            elif entity.get("type") == "player":
                self.player_mentions[entity.get("value", "")] += 1
            elif entity.get("type") == "competition":
                self.competition_mentions[entity.get("value", "")] += 1
    
    def _update_context(self, user_id: str, entry: ConversationEntry) -> None:
        """Update current context for user."""
        context = self.get_user_context(user_id)
        
        # Update recent queries
        context.recent_queries.append(entry.query)
        if len(context.recent_queries) > 10:
            context.recent_queries.pop(0)
        
        # Update mentioned entities
        for entity in entry.entities:
            if entity.get("type") == "team":
                context.mentioned_teams.add(entity.get("value", ""))
            elif entity.get("type") == "player":
                context.mentioned_players.add(entity.get("value", ""))
        
        # Update conversation flow
        context.conversation_flow.append(entry.intent)
        if len(context.conversation_flow) > 5:
            context.conversation_flow.pop(0)
        
        # Determine current topic
        if context.mentioned_teams:
            context.current_topic = f"Discussion about {', '.join(list(context.mentioned_teams)[:2])}"
        else:
            context.current_topic = f"General {entry.intent} discussion"
    
    def _get_most_active_time(self, user_id: str) -> str:
        """Get user's most active time of day."""
        profile = self.get_user_profile(user_id)
        if not profile.active_time:
            return "unknown"
        
        # Group by hour
        hour_counts = defaultdict(int)
        for timestamp in profile.active_time:
            hour = datetime.fromtimestamp(timestamp).hour
            hour_counts[hour] += 1
        
        most_active_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        if 6 <= most_active_hour < 12:
            return "morning"
        elif 12 <= most_active_hour < 18:
            return "afternoon"
        elif 18 <= most_active_hour < 22:
            return "evening"
        else:
            return "night"
    
    def _calculate_engagement_level(self, user_id: str) -> str:
        """Calculate user's engagement level."""
        profile = self.get_user_profile(user_id)
        
        if profile.total_queries < 5:
            return "new"
        elif profile.total_queries < 20:
            return "casual"
        elif profile.total_queries < 50:
            return "active"
        else:
            return "superfan"
    
    def export_memory(self) -> Dict[str, Any]:
        """Export memory data for persistence."""
        return {
            "conversation_history": [entry.__dict__ for entry in self.conversation_history],
            "user_profiles": {uid: profile.__dict__ for uid, profile in self.user_profiles.items()},
            "team_mentions": dict(self.team_mentions),
            "player_mentions": dict(self.player_mentions),
            "competition_mentions": dict(self.competition_mentions),
            "export_timestamp": time.time()
        }
    
    def import_memory(self, data: Dict[str, Any]) -> None:
        """Import memory data from persistence."""
        # Import conversation history
        for entry_data in data.get("conversation_history", []):
            entry = ConversationEntry(**entry_data)
            self.conversation_history.append(entry)
        
        # Import user profiles
        for uid, profile_data in data.get("user_profiles", {}).items():
            profile = UserProfile(**profile_data)
            self.user_profiles[uid] = profile
        
        # Import mention counts
        self.team_mentions.update(data.get("team_mentions", {}))
        self.player_mentions.update(data.get("player_mentions", {}))
        self.competition_mentions.update(data.get("competition_mentions", {}))
