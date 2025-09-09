"""
Proactive information suggestions and related topic recommendations.
Anticipates user needs and provides additional context and suggestions.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SuggestionType(Enum):
    """Types of proactive suggestions."""
    FOLLOW_UP_QUESTION = "follow_up_question"
    RELATED_TOPIC = "related_topic"
    CONTEXTUAL_INFO = "contextual_info"
    TRENDING_TOPIC = "trending_topic"
    PERSONALIZED_RECOMMENDATION = "personalized_recommendation"
    NEWS_UPDATE = "news_update"
    MATCH_REMINDER = "match_reminder"
    STATISTICS_INSIGHT = "statistics_insight"

class RelevanceLevel(Enum):
    """Relevance levels for suggestions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ProactiveSuggestion:
    """Represents a proactive suggestion."""
    type: SuggestionType
    title: str
    description: str
    relevance: RelevanceLevel
    confidence: float
    reasoning: str
    action: str  # The suggested query or action
    metadata: Dict[str, Any] = None

@dataclass
class ContextualInsight:
    """Represents a contextual insight to add to responses."""
    insight_type: str
    content: str
    relevance: RelevanceLevel
    source: str
    timestamp: float

class ProactiveSuggestionSystem:
    """System for generating proactive suggestions and contextual insights."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.suggestion_history: List[ProactiveSuggestion] = []
        self.user_interaction_patterns: Dict[str, List[Dict]] = {}
        
        # Suggestion templates and patterns
        self.suggestion_templates = {
            "team_focus": [
                "{team} next match",
                "{team} recent form"
            ],
            "player_focus": [
                "{player} stats",
                "Compare {player}"
            ],
            "match_focus": [
                "Head-to-head record",
                "Match prediction"
            ],
            "comparison_focus": [
                "Season comparison",
                "Recent form"
            ],
            "news_focus": [
                "Latest news",
                "Transfer updates"
            ]
        }
        
        # Contextual insight patterns
        self.insight_patterns = {
            "historical_context": [
                "This is their first meeting since {date}",
                "They last played in {competition} in {year}",
                "This rivalry dates back to {year}",
                "They've met {count} times in {competition}"
            ],
            "statistical_context": [
                "This season, {team} has {stat}",
                "In their last {count} matches, {team} has {stat}",
                "{player} has scored {goals} goals in {competition}",
                "{team} is currently {position} in {competition}"
            ],
            "trending_context": [
                "This is a trending topic right now",
                "Many fans are discussing this",
                "This match is highly anticipated",
                "This player is in great form"
            ]
        }
    
    def generate_suggestions(self, query: str, response: str, entities: List[Dict],
                           user_context: Dict, conversation_history: List[Dict] = None) -> List[ProactiveSuggestion]:
        """Generate proactive suggestions based on current context."""
        
        suggestions = []
        
        # 1. Follow-up questions based on entities
        follow_up_suggestions = self._generate_follow_up_suggestions(entities, user_context)
        suggestions.extend(follow_up_suggestions)
        
        # 2. Related topics based on query intent
        related_suggestions = self._generate_related_topic_suggestions(query, entities, user_context)
        suggestions.extend(related_suggestions)
        
        # 3. Personalized recommendations
        personalized_suggestions = self._generate_personalized_suggestions(user_context, conversation_history)
        suggestions.extend(personalized_suggestions)
        
        # 4. Trending topics
        trending_suggestions = self._generate_trending_suggestions(entities, user_context)
        suggestions.extend(trending_suggestions)
        
        # 5. Contextual information
        contextual_suggestions = self._generate_contextual_suggestions(query, entities, user_context)
        suggestions.extend(contextual_suggestions)
        
        # Filter and rank suggestions
        filtered_suggestions = self._filter_and_rank_suggestions(suggestions, user_context)
        
        return filtered_suggestions[:2]  # Return top 2 suggestions only
    
    def generate_contextual_insights(self, query: str, entities: List[Dict],
                                   user_context: Dict, tool_results: List[Dict] = None) -> List[ContextualInsight]:
        """Generate contextual insights to enhance responses."""
        
        insights = []
        
        # 1. Historical context
        historical_insights = self._generate_historical_insights(entities, tool_results)
        insights.extend(historical_insights)
        
        # 2. Statistical context
        statistical_insights = self._generate_statistical_insights(entities, tool_results)
        insights.extend(statistical_insights)
        
        # 3. Trending context
        trending_insights = self._generate_trending_insights(entities, user_context)
        insights.extend(trending_insights)
        
        # 4. Comparative context
        comparative_insights = self._generate_comparative_insights(entities, tool_results)
        insights.extend(comparative_insights)
        
        return insights
    
    def _generate_follow_up_suggestions(self, entities: List[Dict], user_context: Dict) -> List[ProactiveSuggestion]:
        """Generate follow-up question suggestions."""
        
        suggestions = []
        entity_types = [entity.get("type", "") for entity in entities]
        
        # Team-focused suggestions
        if "team" in entity_types:
            teams = [entity.get("value", "") for entity in entities if entity.get("type") == "team"]
            for team in teams[:2]:  # Limit to 2 teams
                for template in self.suggestion_templates["team_focus"]:
                    suggestion = ProactiveSuggestion(
                        type=SuggestionType.FOLLOW_UP_QUESTION,
                        title=f"Ask about {team}",
                        description=template.format(team=team),
                        relevance=RelevanceLevel.HIGH,
                        confidence=0.8,
                        reasoning=f"User is interested in {team}",
                        action=template.format(team=team)
                    )
                    suggestions.append(suggestion)
        
        # Player-focused suggestions
        if "player" in entity_types:
            players = [entity.get("value", "") for entity in entities if entity.get("type") == "player"]
            for player in players[:2]:  # Limit to 2 players
                for template in self.suggestion_templates["player_focus"]:
                    suggestion = ProactiveSuggestion(
                        type=SuggestionType.FOLLOW_UP_QUESTION,
                        title=f"Ask about {player}",
                        description=template.format(player=player),
                        relevance=RelevanceLevel.HIGH,
                        confidence=0.8,
                        reasoning=f"User is interested in {player}",
                        action=template.format(player=player)
                    )
                    suggestions.append(suggestion)
        
        # Match-focused suggestions
        if len([e for e in entities if e.get("type") == "team"]) >= 2:
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.FOLLOW_UP_QUESTION,
                title="Compare the teams",
                description="Ask about head-to-head comparison",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.7,
                reasoning="User is comparing two teams",
                action="Compare these teams' recent form"
            ))
        
        return suggestions
    
    def _generate_related_topic_suggestions(self, query: str, entities: List[Dict],
                                          user_context: Dict) -> List[ProactiveSuggestion]:
        """Generate related topic suggestions."""
        
        suggestions = []
        
        # Use AI to generate related topics
        related_topics_prompt = f"""
        Generate related football topics based on this query and entities.
        
        Query: "{query}"
        Entities: {json.dumps(entities, indent=2)}
        User Context: {json.dumps(user_context, indent=2)}
        
        Suggest 3-5 related topics that would be interesting to explore.
        Consider:
        - Related teams, players, or competitions
        - Historical context
        - Current events
        - Statistical comparisons
        - News and updates
        
        Respond with JSON:
        {{
            "related_topics": [
                {{
                    "title": "Topic title",
                    "description": "Brief description",
                    "relevance": "high|medium|low",
                    "suggested_query": "What to ask about this topic"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": related_topics_prompt}],
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            
            for topic in result.get("related_topics", []):
                suggestion = ProactiveSuggestion(
                    type=SuggestionType.RELATED_TOPIC,
                    title=topic["title"],
                    description=topic["description"],
                    relevance=RelevanceLevel(topic["relevance"]),
                    confidence=0.7,
                    reasoning="AI-generated related topic",
                    action=topic["suggested_query"]
                )
                suggestions.append(suggestion)
                
        except Exception as e:
            # Fallback to rule-based suggestions
            suggestions.extend(self._fallback_related_topics(entities))
        
        return suggestions
    
    def _generate_personalized_suggestions(self, user_context: Dict,
                                         conversation_history: List[Dict] = None) -> List[ProactiveSuggestion]:
        """Generate personalized suggestions based on user preferences."""
        
        suggestions = []
        
        # Get user preferences
        favorite_teams = user_context.get("favorite_teams", [])
        preferred_query_types = user_context.get("preferred_query_types", [])
        
        # Suggest based on favorite teams
        for team in favorite_teams[:2]:
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.PERSONALIZED_RECOMMENDATION,
                title=f"Your favorite team: {team}",
                description=f"Check the latest news about {team}",
                relevance=RelevanceLevel.HIGH,
                confidence=0.9,
                reasoning=f"User's favorite team is {team}",
                action=f"What's the latest news about {team}?"
            ))
        
        # Suggest based on query patterns
        if "match_result" in preferred_query_types:
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.PERSONALIZED_RECOMMENDATION,
                title="Recent match results",
                description="You often ask about match results",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.7,
                reasoning="User frequently asks about match results",
                action="Show me recent match results"
            ))
        
        return suggestions
    
    def _generate_trending_suggestions(self, entities: List[Dict], user_context: Dict) -> List[ProactiveSuggestion]:
        """Generate suggestions based on trending topics."""
        
        suggestions = []
        
        # This would integrate with a trending topics system
        # For now, provide some general trending suggestions
        
        trending_topics = [
            "Champions League latest updates",
            "Transfer window news",
            "Top scorer race",
            "League standings",
            "Injury updates"
        ]
        
        for topic in trending_topics[:2]:
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.TRENDING_TOPIC,
                title=f"Trending: {topic}",
                description=f"Check out the latest on {topic}",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.6,
                reasoning="This is a trending football topic",
                action=f"Tell me about {topic}"
            ))
        
        return suggestions
    
    def _generate_contextual_suggestions(self, query: str, entities: List[Dict],
                                       user_context: Dict) -> List[ProactiveSuggestion]:
        """Generate contextual information suggestions."""
        
        suggestions = []
        
        # Time-based suggestions
        current_hour = time.localtime().tm_hour
        if 18 <= current_hour <= 22:  # Evening
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.CONTEXTUAL_INFO,
                title="Evening matches",
                description="Check for evening matches",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.6,
                reasoning="It's evening, good time for match updates",
                action="Show me live matches"
            ))
        
        # Season-based suggestions
        current_month = time.localtime().tm_mon
        if current_month in [1, 7, 8]:  # Transfer windows
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.CONTEXTUAL_INFO,
                title="Transfer news",
                description="Transfer window is active",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.7,
                reasoning="Transfer window season",
                action="Show me transfer news"
            ))
        
        return suggestions
    
    def _generate_historical_insights(self, entities: List[Dict], tool_results: List[Dict] = None) -> List[ContextualInsight]:
        """Generate historical context insights."""
        
        insights = []
        
        # This would analyze tool results for historical context
        # For now, provide some general insights
        
        teams = [entity.get("value", "") for entity in entities if entity.get("type") == "team"]
        if len(teams) >= 2:
            insights.append(ContextualInsight(
                insight_type="historical_context",
                content=f"{teams[0]} and {teams[1]} have a long-standing rivalry",
                relevance=RelevanceLevel.MEDIUM,
                source="historical_data",
                timestamp=time.time()
            ))
        
        return insights
    
    def _generate_statistical_insights(self, entities: List[Dict], tool_results: List[Dict] = None) -> List[ContextualInsight]:
        """Generate statistical context insights."""
        
        insights = []
        
        # This would analyze tool results for statistical context
        # For now, provide some general insights
        
        return insights
    
    def _generate_trending_insights(self, entities: List[Dict], user_context: Dict) -> List[ContextualInsight]:
        """Generate trending context insights."""
        
        insights = []
        
        # This would integrate with trending data
        # For now, provide some general insights
        
        return insights
    
    def _generate_comparative_insights(self, entities: List[Dict], tool_results: List[Dict] = None) -> List[ContextualInsight]:
        """Generate comparative context insights."""
        
        insights = []
        
        # This would analyze tool results for comparative context
        # For now, provide some general insights
        
        return insights
    
    def _filter_and_rank_suggestions(self, suggestions: List[ProactiveSuggestion],
                                   user_context: Dict) -> List[ProactiveSuggestion]:
        """Filter and rank suggestions based on relevance and user context."""
        
        # Remove duplicates
        unique_suggestions = []
        seen_actions = set()
        
        for suggestion in suggestions:
            if suggestion.action not in seen_actions:
                unique_suggestions.append(suggestion)
                seen_actions.add(suggestion.action)
        
        # Sort by relevance and confidence
        def sort_key(suggestion):
            relevance_score = {"high": 3, "medium": 2, "low": 1}[suggestion.relevance.value]
            return (relevance_score, suggestion.confidence)
        
        unique_suggestions.sort(key=sort_key, reverse=True)
        
        return unique_suggestions
    
    def _fallback_related_topics(self, entities: List[Dict]) -> List[ProactiveSuggestion]:
        """Fallback related topics when AI generation fails."""
        
        suggestions = []
        
        teams = [entity.get("value", "") for entity in entities if entity.get("type") == "team"]
        players = [entity.get("value", "") for entity in entities if entity.get("type") == "player"]
        
        if teams:
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.RELATED_TOPIC,
                title="Team comparison",
                description="Compare teams' performance",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.6,
                reasoning="Rule-based team comparison suggestion",
                action="Compare these teams"
            ))
        
        if players:
            suggestions.append(ProactiveSuggestion(
                type=SuggestionType.RELATED_TOPIC,
                title="Player comparison",
                description="Compare players' stats",
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.6,
                reasoning="Rule-based player comparison suggestion",
                action="Compare these players"
            ))
        
        return suggestions
    
    def track_suggestion_interaction(self, suggestion: ProactiveSuggestion, user_id: str, clicked: bool) -> None:
        """Track user interaction with suggestions for learning."""
        
        interaction = {
            "suggestion_type": suggestion.type.value,
            "action": suggestion.action,
            "clicked": clicked,
            "timestamp": time.time(),
            "user_id": user_id
        }
        
        if user_id not in self.user_interaction_patterns:
            self.user_interaction_patterns[user_id] = []
        
        self.user_interaction_patterns[user_id].append(interaction)
        
        # Keep only recent interactions (last 100)
        if len(self.user_interaction_patterns[user_id]) > 100:
            self.user_interaction_patterns[user_id] = self.user_interaction_patterns[user_id][-100:]
    
    def get_suggestion_insights(self) -> Dict[str, Any]:
        """Get insights about suggestion performance."""
        
        if not self.suggestion_history:
            return {"message": "No suggestion history available"}
        
        # Analyze suggestion performance
        type_counts = {}
        relevance_counts = {}
        
        for suggestion in self.suggestion_history:
            type_counts[suggestion.type.value] = type_counts.get(suggestion.type.value, 0) + 1
            relevance_counts[suggestion.relevance.value] = relevance_counts.get(suggestion.relevance.value, 0) + 1
        
        return {
            "total_suggestions": len(self.suggestion_history),
            "suggestion_types": type_counts,
            "relevance_distribution": relevance_counts,
            "most_common_suggestions": sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "average_confidence": sum(s.confidence for s in self.suggestion_history) / len(self.suggestion_history)
        }
