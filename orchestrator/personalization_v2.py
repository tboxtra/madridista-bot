"""
Enhanced Personalization V2
Advanced user profiling with machine learning-inspired features.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from openai import OpenAI

@dataclass
class UserBehaviorPattern:
    preferred_query_times: List[int]  # Hours of day
    query_frequency: Dict[str, int]  # Day of week -> count
    session_length: float  # Average session length
    response_engagement: float  # How often user responds to suggestions
    topic_transitions: Dict[str, List[str]]  # From topic -> to topics

@dataclass
class UserPreferences:
    teams: Dict[str, float]  # Team -> preference score
    players: Dict[str, float]  # Player -> preference score
    competitions: Dict[str, float]  # Competition -> preference score
    topics: Dict[str, float]  # Topic -> preference score
    response_style: str
    detail_level: str
    engagement_level: str

@dataclass
class UserInsights:
    user_id: str
    behavior_pattern: UserBehaviorPattern
    preferences: UserPreferences
    personality_traits: Dict[str, float]
    engagement_score: float
    loyalty_score: float
    last_updated: datetime

class EnhancedPersonalizationEngine:
    """Advanced personalization with behavioral analysis."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.user_insights = {}
        self.conversation_history = defaultdict(list)
        self.behavior_patterns = {}
    
    def analyze_user_behavior(self, user_id: str, conversation_history: List[Dict]) -> UserBehaviorPattern:
        """Analyze user behavior patterns."""
        
        if not conversation_history:
            return self._get_default_behavior_pattern()
        
        # Analyze query times
        query_times = []
        query_frequency = defaultdict(int)
        session_lengths = []
        topic_transitions = defaultdict(list)
        
        current_session_start = None
        last_topic = None
        
        for interaction in conversation_history:
            timestamp = datetime.fromisoformat(interaction.get("timestamp", datetime.now().isoformat()))
            query_times.append(timestamp.hour)
            query_frequency[timestamp.strftime("%A")] += 1
            
            # Track session length
            if current_session_start is None:
                current_session_start = timestamp
            elif (timestamp - current_session_start).total_seconds() > 3600:  # 1 hour gap
                session_lengths.append((timestamp - current_session_start).total_seconds())
                current_session_start = timestamp
            
            # Track topic transitions
            current_topic = self._extract_topic(interaction.get("query", ""))
            if last_topic and current_topic:
                topic_transitions[last_topic].append(current_topic)
            last_topic = current_topic
        
        # Calculate final session length
        if current_session_start:
            session_lengths.append((datetime.now() - current_session_start).total_seconds())
        
        return UserBehaviorPattern(
            preferred_query_times=self._get_peak_hours(query_times),
            query_frequency=dict(query_frequency),
            session_length=np.mean(session_lengths) if session_lengths else 0,
            response_engagement=self._calculate_engagement_score(conversation_history),
            topic_transitions=dict(topic_transitions)
        )
    
    def analyze_user_preferences(self, user_id: str, conversation_history: List[Dict]) -> UserPreferences:
        """Analyze user preferences using advanced techniques."""
        
        # Extract entities from conversations
        teams = Counter()
        players = Counter()
        competitions = Counter()
        topics = Counter()
        
        for interaction in conversation_history:
            query = interaction.get("query", "").lower()
            
            # Extract teams
            team_mentions = self._extract_teams(query)
            for team in team_mentions:
                teams[team] += 1
            
            # Extract players
            player_mentions = self._extract_players(query)
            for player in player_mentions:
                players[player] += 1
            
            # Extract competitions
            competition_mentions = self._extract_competitions(query)
            for competition in competition_mentions:
                competitions[competition] += 1
            
            # Extract topics
            topic = self._extract_topic(query)
            if topic:
                topics[topic] += 1
        
        # Calculate preference scores (normalized)
        team_scores = self._normalize_scores(teams)
        player_scores = self._normalize_scores(players)
        competition_scores = self._normalize_scores(competitions)
        topic_scores = self._normalize_scores(topics)
        
        # Analyze response style and detail level
        response_style = self._analyze_response_style(conversation_history)
        detail_level = self._analyze_detail_level(conversation_history)
        engagement_level = self._analyze_engagement_level(conversation_history)
        
        return UserPreferences(
            teams=team_scores,
            players=player_scores,
            competitions=competition_scores,
            topics=topic_scores,
            response_style=response_style,
            detail_level=detail_level,
            engagement_level=engagement_level
        )
    
    def generate_personality_traits(self, user_id: str, conversation_history: List[Dict]) -> Dict[str, float]:
        """Generate personality traits using AI analysis."""
        
        if not conversation_history:
            return self._get_default_personality_traits()
        
        # Create conversation summary for AI analysis
        conversation_summary = self._create_conversation_summary(conversation_history)
        
        personality_prompt = f"""
        Analyze this user's personality based on their football conversation history:
        
        {conversation_summary}
        
        Rate the user on these personality dimensions (0.0 to 1.0):
        1. Enthusiasm - How passionate and excited they are about football
        2. Knowledge - How knowledgeable they appear about football
        3. Curiosity - How much they ask questions and seek information
        4. Loyalty - How loyal they are to specific teams/players
        5. Social - How much they engage in discussions and comparisons
        6. Analytical - How much they focus on stats and data
        7. Casual - How casual vs formal their communication style is
        8. Competitive - How much they focus on winning/losing/competitions
        
        Respond with JSON:
        {{
            "enthusiasm": 0.0-1.0,
            "knowledge": 0.0-1.0,
            "curiosity": 0.0-1.0,
            "loyalty": 0.0-1.0,
            "social": 0.0-1.0,
            "analytical": 0.0-1.0,
            "casual": 0.0-1.0,
            "competitive": 0.0-1.0
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": personality_prompt}],
                temperature=0.3
            )
            
            traits = json.loads(response.choices[0].message.content)
            return traits
            
        except Exception as e:
            print(f"Error generating personality traits: {e}")
            return self._get_default_personality_traits()
    
    def create_user_insights(self, user_id: str, conversation_history: List[Dict]) -> UserInsights:
        """Create comprehensive user insights."""
        
        behavior_pattern = self.analyze_user_behavior(user_id, conversation_history)
        preferences = self.analyze_user_preferences(user_id, conversation_history)
        personality_traits = self.generate_personality_traits(user_id, conversation_history)
        
        # Calculate engagement and loyalty scores
        engagement_score = self._calculate_overall_engagement(behavior_pattern, preferences, personality_traits)
        loyalty_score = self._calculate_loyalty_score(preferences, personality_traits)
        
        insights = UserInsights(
            user_id=user_id,
            behavior_pattern=behavior_pattern,
            preferences=preferences,
            personality_traits=personality_traits,
            engagement_score=engagement_score,
            loyalty_score=loyalty_score,
            last_updated=datetime.now()
        )
        
        self.user_insights[user_id] = insights
        return insights
    
    def personalize_response(self, response: str, user_insights: UserInsights, query_context: Dict = None) -> str:
        """Personalize response based on comprehensive user insights."""
        
        if not user_insights:
            return response
        
        # Create personalization prompt
        personalization_prompt = f"""
        Personalize this football response for a user with these characteristics:
        
        User Insights:
        - Response Style: {user_insights.preferences.response_style}
        - Detail Level: {user_insights.preferences.detail_level}
        - Engagement Level: {user_insights.preferences.engagement_level}
        - Favorite Teams: {list(user_insights.preferences.teams.keys())[:3]}
        - Personality Traits: {user_insights.personality_traits}
        - Engagement Score: {user_insights.engagement_score:.2f}
        - Loyalty Score: {user_insights.loyalty_score:.2f}
        
        Query Context: {json.dumps(query_context or {}, indent=2)}
        
        Original Response: {response}
        
        Adapt the response to match their personality and preferences:
        1. Adjust tone based on personality traits (enthusiasm, casualness, etc.)
        2. Modify detail level based on their preference
        3. Emphasize their favorite teams and interests
        4. Use appropriate language for their engagement level
        5. Include relevant context based on their knowledge level
        6. Add competitive elements if they're competitive
        7. Include social elements if they're social
        
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
            print(f"Error personalizing response: {e}")
            return response
    
    def generate_personalized_suggestions(self, user_insights: UserInsights, current_query: str) -> List[str]:
        """Generate highly personalized suggestions."""
        
        suggestions = []
        
        # Team-based suggestions
        top_teams = sorted(user_insights.preferences.teams.items(), key=lambda x: x[1], reverse=True)[:3]
        for team, score in top_teams:
            if user_insights.personality_traits.get("analytical", 0) > 0.7:
                suggestions.append(f"📊 Advanced analytics for {team}")
            elif user_insights.personality_traits.get("enthusiasm", 0) > 0.7:
                suggestions.append(f"🔥 Latest {team} news and updates")
            else:
                suggestions.append(f"ℹ️ {team} recent form and statistics")
        
        # Topic-based suggestions
        top_topics = sorted(user_insights.preferences.topics.items(), key=lambda x: x[1], reverse=True)[:3]
        for topic, score in top_topics:
            if topic == "transfers" and user_insights.personality_traits.get("curiosity", 0) > 0.6:
                suggestions.append("🔄 Latest transfer rumors and confirmed deals")
            elif topic == "predictions" and user_insights.personality_traits.get("competitive", 0) > 0.6:
                suggestions.append("🎯 Match predictions and betting insights")
            elif topic == "history" and user_insights.personality_traits.get("knowledge", 0) > 0.6:
                suggestions.append("📚 Historical matchups and legendary moments")
        
        # Personality-based suggestions
        if user_insights.personality_traits.get("social", 0) > 0.7:
            suggestions.append("👥 Team comparison polls and discussions")
        if user_insights.personality_traits.get("analytical", 0) > 0.7:
            suggestions.append("📈 Detailed performance metrics and trends")
        if user_insights.personality_traits.get("competitive", 0) > 0.7:
            suggestions.append("🏆 League standings and title race analysis")
        
        return suggestions[:2]  # Return top 2 suggestions only
    
    def _get_peak_hours(self, query_times: List[int]) -> List[int]:
        """Get peak query hours."""
        if not query_times:
            return []
        
        hour_counts = Counter(query_times)
        # Return hours with above-average activity
        avg_count = len(query_times) / 24
        return [hour for hour, count in hour_counts.items() if count > avg_count]
    
    def _calculate_engagement_score(self, conversation_history: List[Dict]) -> float:
        """Calculate user engagement score."""
        if not conversation_history:
            return 0.5
        
        # Factors: query length, follow-up questions, response to suggestions
        total_queries = len(conversation_history)
        avg_query_length = np.mean([len(interaction.get("query", "")) for interaction in conversation_history])
        follow_up_ratio = sum(1 for i in range(1, len(conversation_history)) 
                            if conversation_history[i].get("is_follow_up", False)) / max(1, total_queries - 1)
        
        # Normalize to 0-1 scale
        engagement = (avg_query_length / 100) * 0.4 + follow_up_ratio * 0.6
        return min(1.0, max(0.0, engagement))
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["stats", "statistics", "numbers", "data"]):
            return "stats"
        elif any(word in query_lower for word in ["news", "rumor", "transfer", "breaking"]):
            return "news"
        elif any(word in query_lower for word in ["predict", "prediction", "forecast"]):
            return "predictions"
        elif any(word in query_lower for word in ["compare", "vs", "versus", "better"]):
            return "comparison"
        elif any(word in query_lower for word in ["history", "historical", "past", "legend"]):
            return "history"
        elif any(word in query_lower for word in ["form", "recent", "last", "performance"]):
            return "form"
        else:
            return "general"
    
    def _extract_teams(self, query: str) -> List[str]:
        """Extract team names from query."""
        # Simplified team extraction - in real implementation, use NER
        teams = []
        team_keywords = {
            "real madrid": "Real Madrid",
            "barcelona": "Barcelona",
            "manchester united": "Manchester United",
            "liverpool": "Liverpool",
            "chelsea": "Chelsea",
            "arsenal": "Arsenal"
        }
        
        for keyword, team_name in team_keywords.items():
            if keyword in query:
                teams.append(team_name)
        
        return teams
    
    def _extract_players(self, query: str) -> List[str]:
        """Extract player names from query."""
        # Simplified player extraction
        players = []
        player_keywords = {
            "messi": "Lionel Messi",
            "ronaldo": "Cristiano Ronaldo",
            "benzema": "Karim Benzema",
            "modric": "Luka Modric"
        }
        
        for keyword, player_name in player_keywords.items():
            if keyword in query:
                players.append(player_name)
        
        return players
    
    def _extract_competitions(self, query: str) -> List[str]:
        """Extract competition names from query."""
        competitions = []
        comp_keywords = {
            "champions league": "Champions League",
            "premier league": "Premier League",
            "laliga": "La Liga",
            "serie a": "Serie A"
        }
        
        for keyword, comp_name in comp_keywords.items():
            if keyword in query:
                competitions.append(comp_name)
        
        return competitions
    
    def _normalize_scores(self, counter: Counter) -> Dict[str, float]:
        """Normalize counter scores to 0-1 range."""
        if not counter:
            return {}
        
        max_count = max(counter.values())
        return {item: count / max_count for item, count in counter.items()}
    
    def _analyze_response_style(self, conversation_history: List[Dict]) -> str:
        """Analyze user's preferred response style."""
        if not conversation_history:
            return "casual"
        
        # Analyze query characteristics
        avg_length = np.mean([len(interaction.get("query", "")) for interaction in conversation_history])
        formal_indicators = sum(1 for interaction in conversation_history 
                              if any(word in interaction.get("query", "").lower() 
                                    for word in ["please", "could you", "would you", "analysis"]))
        
        if avg_length > 50 and formal_indicators > len(conversation_history) * 0.3:
            return "formal"
        elif avg_length < 20:
            return "brief"
        else:
            return "casual"
    
    def _analyze_detail_level(self, conversation_history: List[Dict]) -> str:
        """Analyze user's preferred detail level."""
        if not conversation_history:
            return "detailed"
        
        detail_indicators = sum(1 for interaction in conversation_history 
                              if any(word in interaction.get("query", "").lower() 
                                    for word in ["detailed", "comprehensive", "analysis", "breakdown"]))
        
        if detail_indicators > len(conversation_history) * 0.4:
            return "comprehensive"
        elif detail_indicators < len(conversation_history) * 0.1:
            return "brief"
        else:
            return "detailed"
    
    def _analyze_engagement_level(self, conversation_history: List[Dict]) -> str:
        """Analyze user's engagement level."""
        if not conversation_history:
            return "regular"
        
        total_queries = len(conversation_history)
        if total_queries > 50:
            return "superfan"
        elif total_queries > 20:
            return "regular"
        else:
            return "casual"
    
    def _create_conversation_summary(self, conversation_history: List[Dict]) -> str:
        """Create a summary of conversation history for AI analysis."""
        if not conversation_history:
            return "No conversation history available."
        
        # Take last 10 interactions
        recent_interactions = conversation_history[-10:]
        
        summary_parts = []
        for interaction in recent_interactions:
            query = interaction.get("query", "")
            timestamp = interaction.get("timestamp", "")
            summary_parts.append(f"[{timestamp}] {query}")
        
        return "\n".join(summary_parts)
    
    def _calculate_overall_engagement(self, behavior_pattern: UserBehaviorPattern, 
                                    preferences: UserPreferences, 
                                    personality_traits: Dict[str, float]) -> float:
        """Calculate overall engagement score."""
        
        # Combine multiple factors
        session_factor = min(1.0, behavior_pattern.session_length / 1800)  # 30 minutes max
        response_factor = behavior_pattern.response_engagement
        enthusiasm_factor = personality_traits.get("enthusiasm", 0.5)
        curiosity_factor = personality_traits.get("curiosity", 0.5)
        
        engagement = (session_factor * 0.3 + response_factor * 0.3 + 
                     enthusiasm_factor * 0.2 + curiosity_factor * 0.2)
        
        return min(1.0, max(0.0, engagement))
    
    def _calculate_loyalty_score(self, preferences: UserPreferences, 
                               personality_traits: Dict[str, float]) -> float:
        """Calculate loyalty score."""
        
        # Check team preference concentration
        if not preferences.teams:
            return 0.5
        
        team_scores = list(preferences.teams.values())
        if len(team_scores) == 1:
            concentration = 1.0
        else:
            # Calculate Gini coefficient for concentration
            sorted_scores = sorted(team_scores)
            n = len(sorted_scores)
            cumsum = np.cumsum(sorted_scores)
            concentration = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
        
        loyalty_trait = personality_traits.get("loyalty", 0.5)
        
        return (concentration * 0.7 + loyalty_trait * 0.3)
    
    def _get_default_behavior_pattern(self) -> UserBehaviorPattern:
        """Get default behavior pattern."""
        return UserBehaviorPattern(
            preferred_query_times=[],
            query_frequency={},
            session_length=0,
            response_engagement=0.5,
            topic_transitions={}
        )
    
    def _get_default_personality_traits(self) -> Dict[str, float]:
        """Get default personality traits."""
        return {
            "enthusiasm": 0.5,
            "knowledge": 0.5,
            "curiosity": 0.5,
            "loyalty": 0.5,
            "social": 0.5,
            "analytical": 0.5,
            "casual": 0.5,
            "competitive": 0.5
        }
