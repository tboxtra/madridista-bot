"""
Advanced Personalization Engine
Learns user preferences and adapts responses accordingly.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from openai import OpenAI

class ResponseStyle(Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    ANALYTICAL = "analytical"
    ENTHUSIASTIC = "enthusiastic"
    HUMOROUS = "humorous"

class DetailLevel(Enum):
    BRIEF = "brief"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

class EngagementLevel(Enum):
    CASUAL = "casual"
    REGULAR = "regular"
    SUPERFAN = "superfan"

@dataclass
class UserPersonality:
    user_id: str
    preferred_teams: List[str]
    response_style: ResponseStyle
    detail_level: DetailLevel
    interests: List[str]  # ["stats", "news", "predictions", "history", "transfers"]
    timezone: str
    language: str
    engagement_level: EngagementLevel
    favorite_players: List[str]
    preferred_competitions: List[str]
    query_patterns: Dict[str, int]  # intent -> count
    last_updated: str

class PersonalizationEngine:
    """Advanced personalization system for user experience."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.user_profiles = {}
        self.personality_cache = {}
    
    def analyze_user_personality(self, user_id: str, 
                               conversation_history: List[Dict]) -> UserPersonality:
        """Analyze user personality from conversation patterns."""
        
        # Check cache first
        if user_id in self.personality_cache:
            cached_profile = self.personality_cache[user_id]
            if self._is_profile_fresh(cached_profile):
                return cached_profile
        
        # Analyze recent conversations
        recent_conversations = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
        
        personality_prompt = f"""
        Analyze this user's personality and preferences from their conversation history:
        
        User ID: {user_id}
        Conversation History: {json.dumps(recent_conversations, indent=2)}
        
        Determine and respond with JSON:
        {{
            "preferred_teams": ["list of team names mentioned frequently"],
            "response_style": "casual|formal|analytical|enthusiastic|humorous",
            "detail_level": "brief|detailed|comprehensive",
            "interests": ["stats", "news", "predictions", "history", "transfers", "injuries"],
            "timezone": "UTC",
            "language": "en",
            "engagement_level": "casual|regular|superfan",
            "favorite_players": ["list of players mentioned"],
            "preferred_competitions": ["list of competitions mentioned"],
            "query_patterns": {{"intent": count}},
            "reasoning": "explanation of analysis"
        }}
        
        Guidelines:
        - Extract teams mentioned 3+ times as preferred
        - Determine response style from language patterns
        - Assess detail level from question complexity
        - Identify interests from query topics
        - Estimate engagement from interaction frequency
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": personality_prompt}],
                temperature=0.3
            )
            
            personality_data = json.loads(response.choices[0].message.content)
            
            # Create UserPersonality object
            user_personality = UserPersonality(
                user_id=user_id,
                preferred_teams=personality_data.get("preferred_teams", []),
                response_style=ResponseStyle(personality_data.get("response_style", "casual")),
                detail_level=DetailLevel(personality_data.get("detail_level", "detailed")),
                interests=personality_data.get("interests", ["stats", "news"]),
                timezone=personality_data.get("timezone", "UTC"),
                language=personality_data.get("language", "en"),
                engagement_level=EngagementLevel(personality_data.get("engagement_level", "regular")),
                favorite_players=personality_data.get("favorite_players", []),
                preferred_competitions=personality_data.get("preferred_competitions", []),
                query_patterns=personality_data.get("query_patterns", {}),
                last_updated=datetime.now().isoformat()
            )
            
            # Cache the result
            self.personality_cache[user_id] = user_personality
            self.user_profiles[user_id] = user_personality
            
            return user_personality
            
        except Exception as e:
            # Return default personality on error
            return self._get_default_personality(user_id)
    
    def personalize_response(self, response: str, user_personality: UserPersonality, 
                           query_context: Dict = None) -> str:
        """Personalize response based on user personality."""
        
        if not query_context:
            query_context = {}
        
        personalization_prompt = f"""
        Personalize this football response for a user with these characteristics:
        
        User Profile:
        - Response Style: {user_personality.response_style.value}
        - Detail Level: {user_personality.detail_level.value}
        - Interests: {user_personality.interests}
        - Preferred Teams: {user_personality.preferred_teams}
        - Engagement Level: {user_personality.engagement_level.value}
        - Favorite Players: {user_personality.favorite_players}
        
        Query Context: {json.dumps(query_context, indent=2)}
        
        Original Response: {response}
        
        Adapt the response to match their personality:
        1. Adjust tone to match response style
        2. Modify detail level (brief/detailed/comprehensive)
        3. Emphasize their interests and preferred teams
        4. Use appropriate language for their engagement level
        5. Include relevant context about their favorite players/teams
        
        Keep the core information but make it feel personal and engaging for this specific user.
        """
        
        try:
            personalized_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": personalization_prompt}],
                temperature=0.7
            )
            
            return personalized_response.choices[0].message.content
            
        except Exception as e:
            # Return original response if personalization fails
            return response
    
    def update_user_preferences(self, user_id: str, interaction_data: Dict):
        """Update user preferences based on new interactions."""
        
        if user_id not in self.user_profiles:
            return
        
        user_profile = self.user_profiles[user_id]
        
        # Update query patterns
        intent = interaction_data.get("intent", "general")
        if intent in user_profile.query_patterns:
            user_profile.query_patterns[intent] += 1
        else:
            user_profile.query_patterns[intent] = 1
        
        # Update preferred teams
        mentioned_teams = interaction_data.get("mentioned_teams", [])
        for team in mentioned_teams:
            if team not in user_profile.preferred_teams:
                user_profile.preferred_teams.append(team)
        
        # Update favorite players
        mentioned_players = interaction_data.get("mentioned_players", [])
        for player in mentioned_players:
            if player not in user_profile.favorite_players:
                user_profile.favorite_players.append(player)
        
        # Update last updated timestamp
        user_profile.last_updated = datetime.now().isoformat()
        
        # Invalidate cache
        if user_id in self.personality_cache:
            del self.personality_cache[user_id]
    
    def get_personalized_suggestions(self, user_personality: UserPersonality, 
                                   current_query: str):
        """Generate personalized suggestions based on user profile."""
        
        suggestions = []
        
        # Team-specific suggestions
        for team in user_personality.preferred_teams[:3]:  # Top 3 teams
            if "news" in user_personality.interests:
                suggestions.append(f"Latest news about {team}")
            if "stats" in user_personality.interests:
                suggestions.append(f"{team} recent form and statistics")
            if "predictions" in user_personality.interests:
                suggestions.append(f"{team} next match prediction")
        
        # Interest-based suggestions
        if "transfers" in user_personality.interests:
            suggestions.append("Latest transfer news and rumors")
        if "injuries" in user_personality.interests:
            suggestions.append("Current injury updates")
        if "history" in user_personality.interests:
            suggestions.append("Historical matchups and records")
        
        # Engagement level suggestions
        if user_personality.engagement_level == EngagementLevel.SUPERFAN:
            suggestions.extend([
                "Advanced tactical analysis",
                "Detailed player performance metrics",
                "Comprehensive league standings"
            ])
        elif user_personality.engagement_level == EngagementLevel.REGULAR:
            suggestions.extend([
                "Match predictions",
                "Team comparisons",
                "Recent results summary"
            ])
        else:  # Casual
            suggestions.extend([
                "Quick match updates",
                "Simple team stats",
                "Easy-to-understand predictions"
            ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_response_style_guidelines(self, response_style: ResponseStyle) -> Dict:
        """Get guidelines for different response styles."""
        
        guidelines = {
            ResponseStyle.CASUAL: {
                "tone": "friendly and relaxed",
                "language": "informal, use contractions",
                "examples": ["Hey!", "Pretty cool", "That's awesome"]
            },
            ResponseStyle.FORMAL: {
                "tone": "professional and respectful",
                "language": "formal, complete sentences",
                "examples": ["Good day", "I believe", "It appears that"]
            },
            ResponseStyle.ANALYTICAL: {
                "tone": "data-driven and objective",
                "language": "precise, statistics-focused",
                "examples": ["Based on the data", "Statistically", "The metrics show"]
            },
            ResponseStyle.ENTHUSIASTIC: {
                "tone": "excited and passionate",
                "language": "energetic, exclamation marks",
                "examples": ["Amazing!", "Incredible!", "Fantastic!"]
            },
            ResponseStyle.HUMOROUS: {
                "tone": "light-hearted and witty",
                "language": "playful, use humor appropriately",
                "examples": ["That's a spicy take!", "Plot twist!", "Mind = blown"]
            }
        }
        
        return guidelines.get(response_style, guidelines[ResponseStyle.CASUAL])
    
    def _is_profile_fresh(self, profile: UserPersonality) -> bool:
        """Check if user profile is fresh (less than 24 hours old)."""
        try:
            from datetime import datetime, timedelta
            last_updated = datetime.fromisoformat(profile.last_updated)
            return datetime.now() - last_updated < timedelta(hours=24)
        except:
            return False
    
    def _get_default_personality(self, user_id: str) -> UserPersonality:
        """Get default personality for new users."""
        return UserPersonality(
            user_id=user_id,
            preferred_teams=["Real Madrid"],  # Default to Real Madrid
            response_style=ResponseStyle.CASUAL,
            detail_level=DetailLevel.DETAILED,
            interests=["stats", "news", "predictions"],
            timezone="UTC",
            language="en",
            engagement_level=EngagementLevel.REGULAR,
            favorite_players=[],
            preferred_competitions=["La Liga", "Champions League"],
            query_patterns={},
            last_updated=datetime.now().isoformat()
        )
    
    def export_user_profiles(self) -> Dict:
        """Export all user profiles for persistence."""
        return {
            user_id: asdict(profile) for user_id, profile in self.user_profiles.items()
        }
    
    def import_user_profiles(self, profiles_data: Dict):
        """Import user profiles from persistence."""
        for user_id, profile_data in profiles_data.items():
            try:
                # Convert enum strings back to enum objects
                profile_data["response_style"] = ResponseStyle(profile_data["response_style"])
                profile_data["detail_level"] = DetailLevel(profile_data["detail_level"])
                profile_data["engagement_level"] = EngagementLevel(profile_data["engagement_level"])
                
                self.user_profiles[user_id] = UserPersonality(**profile_data)
            except Exception as e:
                print(f"Error importing profile for user {user_id}: {e}")
    
    def get_user_insights(self, user_id: str) -> Dict:
        """Get insights about a specific user."""
        if user_id not in self.user_profiles:
            return {"error": "User profile not found"}
        
        profile = self.user_profiles[user_id]
        
        return {
            "user_id": user_id,
            "preferred_teams": profile.preferred_teams,
            "response_style": profile.response_style.value,
            "detail_level": profile.detail_level.value,
            "interests": profile.interests,
            "engagement_level": profile.engagement_level.value,
            "total_queries": sum(profile.query_patterns.values()),
            "most_common_intent": max(profile.query_patterns.items(), key=lambda x: x[1])[0] if profile.query_patterns else "general",
            "last_updated": profile.last_updated
        }
