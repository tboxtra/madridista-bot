"""
Dynamic AI-driven tool selection system.
Scores and selects tools based on intent, entities, context, and user preferences.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ToolCategory(Enum):
    """Categories of tools for better organization."""
    MATCH_DATA = "match_data"
    PLAYER_DATA = "player_data"
    TEAM_DATA = "team_data"
    NEWS = "news"
    HISTORY = "history"
    COMPARISON = "comparison"
    LIVE_DATA = "live_data"
    FIXTURES = "fixtures"

@dataclass
class ToolMetadata:
    """Metadata for each tool to enable intelligent selection."""
    name: str
    category: ToolCategory
    description: str
    required_entities: List[str]  # team, player, competition, etc.
    optional_entities: List[str]
    data_freshness: str  # real_time, recent, historical
    reliability_score: float  # 0.0-1.0
    response_time: str  # fast, medium, slow
    coverage: List[str]  # leagues/competitions covered

@dataclass
class ToolScore:
    """Score for a tool based on current context."""
    tool_name: str
    score: float
    reasoning: str
    confidence: float
    execution_priority: int

class DynamicToolSelector:
    """AI-driven tool selection system."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        
        # Tool metadata registry (only for tools that actually exist)
        self.tool_metadata = {
            "tool_af_find_match_result": ToolMetadata(
                name="tool_af_find_match_result",
                category=ToolCategory.MATCH_DATA,
                description="Find specific match results between teams with winner filtering",
                required_entities=["team", "team"],
                optional_entities=["competition", "date"],
                data_freshness="historical",
                reliability_score=0.9,
                response_time="medium",
                coverage=["all_major_leagues"]
            ),
            "tool_af_last_result_vs": ToolMetadata(
                name="tool_af_last_result_vs",
                category=ToolCategory.MATCH_DATA,
                description="Get last head-to-head result between two teams",
                required_entities=["team", "team"],
                optional_entities=["competition"],
                data_freshness="recent",
                reliability_score=0.9,
                response_time="fast",
                coverage=["all_major_leagues"]
            ),
            "tool_h2h_officialish": ToolMetadata(
                name="tool_h2h_officialish",
                category=ToolCategory.MATCH_DATA,
                description="Wikipedia-based head-to-head summary",
                required_entities=["team", "team"],
                optional_entities=[],
                data_freshness="historical",
                reliability_score=0.7,
                response_time="slow",
                coverage=["major_teams"]
            ),
            "tool_player_stats": ToolMetadata(
                name="tool_player_stats",
                category=ToolCategory.PLAYER_DATA,
                description="Get player season statistics",
                required_entities=["player"],
                optional_entities=["competition"],
                data_freshness="recent",
                reliability_score=0.85,
                response_time="fast",
                coverage=["major_leagues"]
            ),
            "tool_compare_players": ToolMetadata(
                name="tool_compare_players",
                category=ToolCategory.COMPARISON,
                description="Compare two players' statistics",
                required_entities=["player", "player"],
                optional_entities=["competition"],
                data_freshness="recent",
                reliability_score=0.85,
                response_time="medium",
                coverage=["major_leagues"]
            ),
            "tool_form": ToolMetadata(
                name="tool_form",
                category=ToolCategory.TEAM_DATA,
                description="Get team's recent form and results",
                required_entities=["team"],
                optional_entities=["competition"],
                data_freshness="recent",
                reliability_score=0.9,
                response_time="fast",
                coverage=["all_major_leagues"]
            ),
            "tool_compare_teams": ToolMetadata(
                name="tool_compare_teams",
                category=ToolCategory.COMPARISON,
                description="Compare two teams' recent form",
                required_entities=["team", "team"],
                optional_entities=["competition"],
                data_freshness="recent",
                reliability_score=0.9,
                response_time="fast",
                coverage=["all_major_leagues"]
            ),
            "tool_news": ToolMetadata(
                name="tool_news",
                category=ToolCategory.NEWS,
                description="Get latest football news",
                required_entities=[],
                optional_entities=["team", "player", "competition"],
                data_freshness="real_time",
                reliability_score=0.8,
                response_time="fast",
                coverage=["global"]
            ),
            "tool_next_fixture": ToolMetadata(
                name="tool_next_fixture",
                category=ToolCategory.FIXTURES,
                description="Get next upcoming fixture for a team",
                required_entities=["team"],
                optional_entities=["competition"],
                data_freshness="real_time",
                reliability_score=0.95,
                response_time="fast",
                coverage=["all_major_leagues"]
            ),
            "tool_table": ToolMetadata(
                name="tool_table",
                category=ToolCategory.TEAM_DATA,
                description="Get league table standings",
                required_entities=["competition"],
                optional_entities=[],
                data_freshness="recent",
                reliability_score=0.95,
                response_time="fast",
                coverage=["all_major_leagues"]
            ),
            "tool_history_lookup": ToolMetadata(
                name="tool_history_lookup",
                category=ToolCategory.HISTORY,
                description="Look up historical football information",
                required_entities=[],
                optional_entities=["team", "player", "competition"],
                data_freshness="historical",
                reliability_score=0.7,
                response_time="slow",
                coverage=["major_teams"]
            ),
            "tool_rm_ucl_titles": ToolMetadata(
                name="tool_rm_ucl_titles",
                category=ToolCategory.HISTORY,
                description="Real Madrid's Champions League titles",
                required_entities=[],
                optional_entities=[],
                data_freshness="historical",
                reliability_score=0.95,
                response_time="fast",
                coverage=["real_madrid"]
            ),
            "tool_ucl_last_n_winners": ToolMetadata(
                name="tool_ucl_last_n_winners",
                category=ToolCategory.HISTORY,
                description="Last N Champions League winners",
                required_entities=[],
                optional_entities=[],
                data_freshness="historical",
                reliability_score=0.9,
                response_time="medium",
                coverage=["champions_league"]
            ),
            "tool_live_now": ToolMetadata(
                name="tool_live_now",
                category=ToolCategory.LIVE_DATA,
                description="Get live scores for configured team",
                required_entities=[],
                optional_entities=[],
                data_freshness="real_time",
                reliability_score=0.9,
                response_time="fast",
                coverage=["configured_team"]
            )
        }
        
        # Intent to tool category mapping
        self.intent_category_mapping = {
            "match_result": [ToolCategory.MATCH_DATA, ToolCategory.HISTORY],
            "h2h_comparison": [ToolCategory.MATCH_DATA, ToolCategory.COMPARISON],
            "player_stats": [ToolCategory.PLAYER_DATA],
            "team_form": [ToolCategory.TEAM_DATA],
            "news": [ToolCategory.NEWS],
            "fixtures": [ToolCategory.FIXTURES],
            "table": [ToolCategory.TEAM_DATA],
            "history": [ToolCategory.HISTORY],
            "comparison": [ToolCategory.COMPARISON],
            "general": [ToolCategory.NEWS, ToolCategory.TEAM_DATA]
        }
    
    def score_tools(self, intent: str, entities: List[Dict], context: Dict = None, 
                   user_preferences: Dict = None) -> List[ToolScore]:
        """Score all available tools based on current context."""
        
        scores = []
        relevant_categories = self.intent_category_mapping.get(intent, [ToolCategory.NEWS])
        
        for tool_name, metadata in self.tool_metadata.items():
            score = self._calculate_tool_score(
                tool_name, metadata, intent, entities, context, user_preferences, relevant_categories
            )
            scores.append(score)
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x.score, reverse=True)
        
        return scores
    
    def select_best_tools(self, scores: List[ToolScore], max_tools: int = 3) -> List[ToolScore]:
        """Select the best tools based on scores."""
        
        # Filter out tools with very low scores
        viable_tools = [score for score in scores if score.score > 0.3]
        
        # Select top tools, ensuring diversity
        selected_tools = []
        used_categories = set()
        
        for score in viable_tools:
            if len(selected_tools) >= max_tools:
                break
            
            tool_metadata = self.tool_metadata[score.tool_name]
            
            # Prefer tools from different categories for diversity
            if tool_metadata.category not in used_categories or len(selected_tools) < 2:
                selected_tools.append(score)
                used_categories.add(tool_metadata.category)
        
        # If we don't have enough diverse tools, add more from the same categories
        if len(selected_tools) < max_tools:
            for score in viable_tools:
                if len(selected_tools) >= max_tools:
                    break
                if score not in selected_tools:
                    selected_tools.append(score)
        
        return selected_tools
    
    def generate_tool_parameters(self, tool_name: str, entities: List[Dict], 
                               context: Dict = None) -> Dict[str, Any]:
        """Generate parameters for a specific tool using AI."""
        
        metadata = self.tool_metadata.get(tool_name)
        if not metadata:
            return {}
        
        param_prompt = f"""
        Generate parameters for the tool '{tool_name}' based on the extracted entities and context.
        
        Tool Description: {metadata.description}
        Required Entities: {metadata.required_entities}
        Optional Entities: {metadata.optional_entities}
        
        Extracted Entities: {json.dumps(entities, indent=2)}
        Context: {json.dumps(context or {}, indent=2)}
        
        Generate the exact parameters needed for this tool. Be precise with team names, player names, etc.
        Use the entity values directly, but ensure they match the tool's expected format.
        
        Respond with JSON containing the parameters:
        {{
            "parameters": {{"param_name": "param_value"}},
            "confidence": 0.0-1.0,
            "reasoning": "how parameters were derived from entities"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": param_prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("parameters", {})
            
        except Exception as e:
            return self._fallback_parameter_generation(tool_name, entities, metadata)
    
    def _calculate_tool_score(self, tool_name: str, metadata: ToolMetadata, intent: str,
                            entities: List[Dict], context: Dict, user_preferences: Dict,
                            relevant_categories: List[ToolCategory]) -> ToolScore:
        """Calculate score for a specific tool."""
        
        score = 0.0
        reasoning_parts = []
        
        # 1. Category relevance (40% weight)
        if metadata.category in relevant_categories:
            score += 0.4
            reasoning_parts.append(f"Category {metadata.category.value} matches intent {intent}")
        else:
            reasoning_parts.append(f"Category {metadata.category.value} doesn't match intent {intent}")
        
        # 2. Entity compatibility (30% weight)
        entity_score = self._calculate_entity_compatibility(metadata, entities)
        score += entity_score * 0.3
        reasoning_parts.append(f"Entity compatibility: {entity_score:.2f}")
        
        # 3. Reliability score (15% weight)
        score += metadata.reliability_score * 0.15
        reasoning_parts.append(f"Reliability: {metadata.reliability_score:.2f}")
        
        # 4. Data freshness relevance (10% weight)
        freshness_score = self._calculate_freshness_relevance(metadata.data_freshness, intent, context)
        score += freshness_score * 0.1
        reasoning_parts.append(f"Data freshness relevance: {freshness_score:.2f}")
        
        # 5. User preferences (5% weight)
        if user_preferences:
            preference_score = self._calculate_preference_score(tool_name, user_preferences)
            score += preference_score * 0.05
            reasoning_parts.append(f"User preference: {preference_score:.2f}")
        
        # Calculate confidence based on how well we can satisfy the tool's requirements
        confidence = min(1.0, entity_score + (0.5 if metadata.category in relevant_categories else 0.0))
        
        return ToolScore(
            tool_name=tool_name,
            score=score,
            reasoning="; ".join(reasoning_parts),
            confidence=confidence,
            execution_priority=int((1.0 - score) * 10)  # Lower score = higher priority
        )
    
    def _calculate_entity_compatibility(self, metadata: ToolMetadata, entities: List[Dict]) -> float:
        """Calculate how well entities match tool requirements."""
        
        entity_types = [entity.get("type", "") for entity in entities]
        
        # Check required entities
        required_satisfied = 0
        for required in metadata.required_entities:
            if required in entity_types:
                required_satisfied += 1
        
        if not metadata.required_entities:
            required_score = 1.0
        else:
            required_score = required_satisfied / len(metadata.required_entities)
        
        # Check optional entities (bonus)
        optional_satisfied = 0
        for optional in metadata.optional_entities:
            if optional in entity_types:
                optional_satisfied += 1
        
        optional_score = optional_satisfied / max(1, len(metadata.optional_entities)) * 0.3
        
        return min(1.0, required_score + optional_score)
    
    def _calculate_freshness_relevance(self, data_freshness: str, intent: str, context: Dict) -> float:
        """Calculate how relevant the data freshness is for the intent."""
        
        freshness_preferences = {
            "match_result": {"real_time": 0.3, "recent": 0.8, "historical": 0.9},
            "h2h_comparison": {"real_time": 0.2, "recent": 0.9, "historical": 0.8},
            "player_stats": {"real_time": 0.2, "recent": 0.9, "historical": 0.6},
            "team_form": {"real_time": 0.3, "recent": 0.9, "historical": 0.4},
            "news": {"real_time": 0.9, "recent": 0.7, "historical": 0.2},
            "fixtures": {"real_time": 0.9, "recent": 0.8, "historical": 0.1},
            "table": {"real_time": 0.4, "recent": 0.9, "historical": 0.3},
            "history": {"real_time": 0.1, "recent": 0.3, "historical": 0.9},
            "comparison": {"real_time": 0.2, "recent": 0.8, "historical": 0.6},
            "general": {"real_time": 0.5, "recent": 0.7, "historical": 0.5}
        }
        
        intent_preferences = freshness_preferences.get(intent, {"real_time": 0.5, "recent": 0.7, "historical": 0.5})
        return intent_preferences.get(data_freshness, 0.5)
    
    def _calculate_preference_score(self, tool_name: str, user_preferences: Dict) -> float:
        """Calculate score based on user preferences."""
        
        # Check if user has used this tool before
        tools_used = user_preferences.get("tools_used", [])
        if tool_name in tools_used:
            return 0.8
        
        # Check if user prefers this category
        preferred_intents = user_preferences.get("preferred_query_types", [])
        tool_metadata = self.tool_metadata.get(tool_name)
        if tool_metadata:
            for intent, categories in self.intent_category_mapping.items():
                if intent in preferred_intents and tool_metadata.category in categories:
                    return 0.6
        
        return 0.5  # Neutral preference
    
    def _fallback_parameter_generation(self, tool_name: str, entities: List[Dict], 
                                     metadata: ToolMetadata) -> Dict[str, Any]:
        """Fallback parameter generation using simple rules."""
        
        parameters = {}
        
        # Extract entities by type
        entity_by_type = {}
        for entity in entities:
            entity_type = entity.get("type", "")
            if entity_type not in entity_by_type:
                entity_by_type[entity_type] = []
            entity_by_type[entity_type].append(entity.get("value", ""))
        
        # Generate parameters based on tool requirements
        if "team" in metadata.required_entities:
            teams = entity_by_type.get("team", [])
            if len(teams) >= 1:
                parameters["team_name"] = teams[0]
            if len(teams) >= 2:
                parameters["team_a"] = teams[0]
                parameters["team_b"] = teams[1]
        
        if "player" in metadata.required_entities:
            players = entity_by_type.get("player", [])
            if players:
                parameters["player_name"] = players[0]
            if len(players) >= 2:
                parameters["player_a"] = players[0]
                parameters["player_b"] = players[1]
        
        if "competition" in metadata.required_entities:
            competitions = entity_by_type.get("competition", [])
            if competitions:
                parameters["competition"] = competitions[0]
        
        return parameters
    
    def get_tool_recommendations(self, intent: str, entities: List[Dict], 
                               context: Dict = None) -> List[Dict[str, Any]]:
        """Get tool recommendations with explanations."""
        
        scores = self.score_tools(intent, entities, context)
        selected_tools = self.select_best_tools(scores, max_tools=3)
        
        recommendations = []
        for tool_score in selected_tools:
            metadata = self.tool_metadata[tool_score.tool_name]
            parameters = self.generate_tool_parameters(tool_score.tool_name, entities, context)
            
            recommendations.append({
                "tool_name": tool_score.tool_name,
                "score": tool_score.score,
                "confidence": tool_score.confidence,
                "reasoning": tool_score.reasoning,
                "parameters": parameters,
                "metadata": {
                    "category": metadata.category.value,
                    "description": metadata.description,
                    "reliability": metadata.reliability_score,
                    "response_time": metadata.response_time
                }
            })
        
        return recommendations
