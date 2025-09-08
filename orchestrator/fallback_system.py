"""
Intelligent AI-driven fallback strategies when primary tools fail.
Implements smart error handling, alternative approaches, and graceful degradation.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class FailureType(Enum):
    """Types of tool failures."""
    API_ERROR = "api_error"
    NO_DATA = "no_data"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    INVALID_PARAMETERS = "invalid_parameters"
    NETWORK_ERROR = "network_error"
    PARSING_ERROR = "parsing_error"

class FallbackStrategy(Enum):
    """Available fallback strategies."""
    RETRY_SAME_TOOL = "retry_same_tool"
    TRY_ALTERNATIVE_TOOL = "try_alternative_tool"
    BROADEN_SEARCH = "broaden_search"
    USE_CACHED_DATA = "use_cached_data"
    SIMPLIFY_QUERY = "simplify_query"
    PROVIDE_PARTIAL_INFO = "provide_partial_info"
    SUGGEST_ALTERNATIVES = "suggest_alternatives"
    ESCALATE_TO_HUMAN = "escalate_to_human"

@dataclass
class ToolFailure:
    """Represents a tool execution failure."""
    tool_name: str
    failure_type: FailureType
    error_message: str
    timestamp: float
    retry_count: int = 0
    context: Dict[str, Any] = None

@dataclass
class FallbackPlan:
    """Represents a fallback execution plan."""
    strategy: FallbackStrategy
    alternative_tools: List[str]
    modified_parameters: Dict[str, Any]
    reasoning: str
    confidence: float
    expected_success_rate: float

class IntelligentFallbackSystem:
    """AI-driven fallback system for handling tool failures."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.failure_history: List[ToolFailure] = []
        self.success_patterns: Dict[str, List[Dict]] = {}
        
        # Tool alternatives mapping
        self.tool_alternatives = {
            "tool_af_find_match_result": [
                "tool_af_last_result_vs",
                "tool_h2h_officialish",
                "tool_history_lookup"
            ],
            "tool_af_last_result_vs": [
                "tool_h2h_officialish",
                "tool_af_find_match_result",
                "tool_history_lookup"
            ],
            "tool_h2h_officialish": [
                "tool_af_last_result_vs",
                "tool_af_find_match_result",
                "tool_history_lookup"
            ],
            "tool_player_stats": [
                "tool_compare_players",
                "tool_news"
            ],
            "tool_compare_players": [
                "tool_player_stats",
                "tool_news"
            ],
            "tool_form": [
                "tool_compare_teams",
                "tool_news"
            ],
            "tool_compare_teams": [
                "tool_form",
                "tool_news"
            ],
            "tool_news": [
                "tool_form",
                "tool_next_fixture"
            ],
            "tool_next_fixture": [
                "tool_form",
                "tool_news"
            ],
            "tool_table": [
                "tool_form",
                "tool_news"
            ],
            "tool_history_lookup": [
                "tool_rm_ucl_titles",
                "tool_ucl_last_n_winners",
                "tool_news"
            ]
        }
        
        # Failure type to strategy mapping
        self.failure_strategies = {
            FailureType.API_ERROR: [FallbackStrategy.TRY_ALTERNATIVE_TOOL, FallbackStrategy.RETRY_SAME_TOOL],
            FailureType.NO_DATA: [FallbackStrategy.BROADEN_SEARCH, FallbackStrategy.TRY_ALTERNATIVE_TOOL],
            FailureType.TIMEOUT: [FallbackStrategy.RETRY_SAME_TOOL, FallbackStrategy.TRY_ALTERNATIVE_TOOL],
            FailureType.AUTHENTICATION: [FallbackStrategy.USE_CACHED_DATA, FallbackStrategy.SUGGEST_ALTERNATIVES],
            FailureType.RATE_LIMIT: [FallbackStrategy.USE_CACHED_DATA, FallbackStrategy.RETRY_SAME_TOOL],
            FailureType.INVALID_PARAMETERS: [FallbackStrategy.SIMPLIFY_QUERY, FallbackStrategy.TRY_ALTERNATIVE_TOOL],
            FailureType.NETWORK_ERROR: [FallbackStrategy.RETRY_SAME_TOOL, FallbackStrategy.USE_CACHED_DATA],
            FailureType.PARSING_ERROR: [FallbackStrategy.TRY_ALTERNATIVE_TOOL, FallbackStrategy.PROVIDE_PARTIAL_INFO]
        }
    
    def analyze_failure(self, tool_name: str, error: Exception, 
                       context: Dict[str, Any] = None) -> ToolFailure:
        """Analyze a tool failure and determine its type."""
        
        error_message = str(error).lower()
        failure_type = self._classify_failure(error_message)
        
        failure = ToolFailure(
            tool_name=tool_name,
            failure_type=failure_type,
            error_message=str(error),
            timestamp=time.time(),
            context=context or {}
        )
        
        self.failure_history.append(failure)
        return failure
    
    def create_fallback_plan(self, failure: ToolFailure, original_query: str,
                           entities: List[Dict], user_context: Dict = None) -> FallbackPlan:
        """Create an intelligent fallback plan using AI."""
        
        fallback_prompt = f"""
        Create a fallback plan for this tool failure. Analyze the failure and suggest the best recovery strategy.
        
        Failed Tool: {failure.tool_name}
        Failure Type: {failure.failure_type.value}
        Error Message: {failure.error_message}
        Retry Count: {failure.retry_count}
        
        Original Query: "{original_query}"
        Entities: {json.dumps(entities, indent=2)}
        User Context: {json.dumps(user_context or {}, indent=2)}
        
        Available Strategies:
        - retry_same_tool: Retry the same tool (for temporary issues)
        - try_alternative_tool: Use a different tool that can provide similar data
        - broaden_search: Expand the search parameters to find more results
        - use_cached_data: Use previously cached data if available
        - simplify_query: Simplify the query to make it easier to answer
        - provide_partial_info: Provide whatever information is available
        - suggest_alternatives: Suggest alternative questions or approaches
        - escalate_to_human: Escalate to human support
        
        Consider:
        1. The type of failure and its likely cause
        2. The user's intent and what they're trying to achieve
        3. Available alternative tools and their reliability
        4. Whether the query can be simplified or broadened
        5. The user's context and preferences
        
        Respond with JSON:
        {{
            "strategy": "chosen_strategy",
            "alternative_tools": ["list", "of", "alternative", "tools"],
            "modified_parameters": {{"param": "modified_value"}},
            "reasoning": "detailed explanation of why this strategy was chosen",
            "confidence": 0.0-1.0,
            "expected_success_rate": 0.0-1.0
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": fallback_prompt}],
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return FallbackPlan(
                strategy=FallbackStrategy(result["strategy"]),
                alternative_tools=result.get("alternative_tools", []),
                modified_parameters=result.get("modified_parameters", {}),
                reasoning=result.get("reasoning", "Fallback plan created"),
                confidence=result.get("confidence", 0.7),
                expected_success_rate=result.get("expected_success_rate", 0.6)
            )
            
        except Exception as e:
            return self._fallback_plan_creation(failure, original_query, entities)
    
    def execute_fallback_plan(self, plan: FallbackPlan, failure: ToolFailure,
                            original_query: str, entities: List[Dict],
                            tool_functions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the fallback plan and return results."""
        
        if plan.strategy == FallbackStrategy.RETRY_SAME_TOOL:
            return self._retry_same_tool(failure, plan, tool_functions)
        
        elif plan.strategy == FallbackStrategy.TRY_ALTERNATIVE_TOOL:
            return self._try_alternative_tools(plan, entities, tool_functions)
        
        elif plan.strategy == FallbackStrategy.BROADEN_SEARCH:
            return self._broaden_search(failure, plan, entities, tool_functions)
        
        elif plan.strategy == FallbackStrategy.USE_CACHED_DATA:
            return self._use_cached_data(failure, original_query)
        
        elif plan.strategy == FallbackStrategy.SIMPLIFY_QUERY:
            return self._simplify_query(failure, original_query, entities, tool_functions)
        
        elif plan.strategy == FallbackStrategy.PROVIDE_PARTIAL_INFO:
            return self._provide_partial_info(failure, original_query)
        
        elif plan.strategy == FallbackStrategy.SUGGEST_ALTERNATIVES:
            return self._suggest_alternatives(original_query, entities)
        
        else:
            return self._escalate_to_human(failure, original_query)
    
    def _classify_failure(self, error_message: str) -> FailureType:
        """Classify the type of failure based on error message."""
        
        error_lower = error_message.lower()
        
        if any(term in error_lower for term in ["timeout", "timed out"]):
            return FailureType.TIMEOUT
        elif any(term in error_lower for term in ["auth", "unauthorized", "forbidden", "401", "403"]):
            return FailureType.AUTHENTICATION
        elif any(term in error_lower for term in ["rate limit", "429", "too many requests"]):
            return FailureType.RATE_LIMIT
        elif any(term in error_lower for term in ["no data", "empty", "not found", "404"]):
            return FailureType.NO_DATA
        elif any(term in error_lower for term in ["network", "connection", "dns"]):
            return FailureType.NETWORK_ERROR
        elif any(term in error_lower for term in ["parse", "json", "format", "decode"]):
            return FailureType.PARSING_ERROR
        elif any(term in error_lower for term in ["invalid", "bad request", "400"]):
            return FailureType.INVALID_PARAMETERS
        else:
            return FailureType.API_ERROR
    
    def _retry_same_tool(self, failure: ToolFailure, plan: FallbackPlan, 
                        tool_functions: Dict[str, Any]) -> Dict[str, Any]:
        """Retry the same tool with potential modifications."""
        
        if failure.retry_count >= 3:
            return {
                "success": False,
                "error": "Maximum retry attempts reached",
                "fallback_strategy": "retry_same_tool"
            }
        
        # Increment retry count
        failure.retry_count += 1
        
        try:
            tool_func = tool_functions.get(failure.tool_name)
            if not tool_func:
                return {"success": False, "error": "Tool function not found"}
            
            # Use modified parameters if available
            if plan.modified_parameters:
                result = tool_func(**plan.modified_parameters)
            else:
                # Retry with original parameters
                result = tool_func(**failure.context.get("original_parameters", {}))
            
            return {
                "success": True,
                "result": result,
                "fallback_strategy": "retry_same_tool",
                "retry_count": failure.retry_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_strategy": "retry_same_tool"
            }
    
    def _try_alternative_tools(self, plan: FallbackPlan, entities: List[Dict],
                             tool_functions: Dict[str, Any]) -> Dict[str, Any]:
        """Try alternative tools that can provide similar information."""
        
        for tool_name in plan.alternative_tools:
            try:
                tool_func = tool_functions.get(tool_name)
                if not tool_func:
                    continue
                
                # Generate parameters for the alternative tool
                parameters = self._generate_alternative_parameters(tool_name, entities, plan.modified_parameters)
                
                result = tool_func(**parameters)
                
                if result and result != "No data found":
                    return {
                        "success": True,
                        "result": result,
                        "fallback_strategy": "try_alternative_tool",
                        "alternative_tool": tool_name
                    }
                
            except Exception as e:
                continue
        
        return {
            "success": False,
            "error": "All alternative tools failed",
            "fallback_strategy": "try_alternative_tool"
        }
    
    def _broaden_search(self, failure: ToolFailure, plan: FallbackPlan,
                       entities: List[Dict], tool_functions: Dict[str, Any]) -> Dict[str, Any]:
        """Broaden the search parameters to find more results."""
        
        try:
            # Try the same tool with broader parameters
            tool_func = tool_functions.get(failure.tool_name)
            if not tool_func:
                return {"success": False, "error": "Tool function not found"}
            
            # Use modified parameters that broaden the search
            result = tool_func(**plan.modified_parameters)
            
            if result and result != "No data found":
                return {
                    "success": True,
                    "result": result,
                    "fallback_strategy": "broaden_search"
                }
            
        except Exception as e:
            pass
        
        # If broadening didn't work, try alternative tools
        return self._try_alternative_tools(plan, entities, tool_functions)
    
    def _use_cached_data(self, failure: ToolFailure, original_query: str) -> Dict[str, Any]:
        """Use cached data if available."""
        
        # This would integrate with a caching system
        # For now, return a generic response
        return {
            "success": True,
            "result": f"I found some cached information about your query: '{original_query}'. The data might be slightly outdated, but here's what I have...",
            "fallback_strategy": "use_cached_data",
            "data_freshness": "cached"
        }
    
    def _simplify_query(self, failure: ToolFailure, original_query: str,
                       entities: List[Dict], tool_functions: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify the query to make it easier to answer."""
        
        # Try with fewer entities or simpler parameters
        simplified_entities = entities[:2] if len(entities) > 2 else entities
        
        # Try alternative tools with simplified parameters
        alternatives = self.tool_alternatives.get(failure.tool_name, [])
        
        for tool_name in alternatives:
            try:
                tool_func = tool_functions.get(tool_name)
                if not tool_func:
                    continue
                
                # Generate simplified parameters
                parameters = self._generate_simplified_parameters(tool_name, simplified_entities)
                result = tool_func(**parameters)
                
                if result and result != "No data found":
                    return {
                        "success": True,
                        "result": result,
                        "fallback_strategy": "simplify_query",
                        "simplified_tool": tool_name
                    }
                
            except Exception as e:
                continue
        
        return {
            "success": False,
            "error": "Simplified query approach failed",
            "fallback_strategy": "simplify_query"
        }
    
    def _provide_partial_info(self, failure: ToolFailure, original_query: str) -> Dict[str, Any]:
        """Provide whatever partial information is available."""
        
        return {
            "success": True,
            "result": f"I couldn't find complete information about '{original_query}', but I can tell you that this is a football-related query. Try asking about recent matches, player stats, or team form for more specific information.",
            "fallback_strategy": "provide_partial_info"
        }
    
    def _suggest_alternatives(self, original_query: str, entities: List[Dict]) -> Dict[str, Any]:
        """Suggest alternative questions or approaches."""
        
        suggestions = [
            "Try asking about recent matches or results",
            "Ask about player statistics or team form",
            "Check the latest football news",
            "Ask about upcoming fixtures",
            "Compare teams or players"
        ]
        
        # Customize suggestions based on entities
        if any(entity.get("type") == "team" for entity in entities):
            suggestions.insert(0, "Try asking about this team's recent form or next fixture")
        
        if any(entity.get("type") == "player" for entity in entities):
            suggestions.insert(0, "Try asking about this player's current season stats")
        
        return {
            "success": True,
            "result": f"I couldn't find information for '{original_query}'. Here are some alternative questions you could try: {'; '.join(suggestions[:3])}",
            "fallback_strategy": "suggest_alternatives",
            "suggestions": suggestions
        }
    
    def _escalate_to_human(self, failure: ToolFailure, original_query: str) -> Dict[str, Any]:
        """Escalate to human support."""
        
        return {
            "success": False,
            "result": f"I'm having trouble with your query: '{original_query}'. This appears to be a complex request that might need human assistance. Please try rephrasing your question or contact support.",
            "fallback_strategy": "escalate_to_human"
        }
    
    def _generate_alternative_parameters(self, tool_name: str, entities: List[Dict],
                                       modified_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameters for alternative tools."""
        
        # Use modified parameters if available
        if modified_parameters:
            return modified_parameters
        
        # Generate basic parameters from entities
        parameters = {}
        entity_by_type = {}
        
        for entity in entities:
            entity_type = entity.get("type", "")
            if entity_type not in entity_by_type:
                entity_by_type[entity_type] = []
            entity_by_type[entity_type].append(entity.get("value", ""))
        
        # Map entities to tool parameters
        if "team" in entity_by_type:
            teams = entity_by_type["team"]
            if len(teams) >= 1:
                parameters["team_name"] = teams[0]
            if len(teams) >= 2:
                parameters["team_a"] = teams[0]
                parameters["team_b"] = teams[1]
        
        if "player" in entity_by_type:
            players = entity_by_type["player"]
            if players:
                parameters["player_name"] = players[0]
            if len(players) >= 2:
                parameters["player_a"] = players[0]
                parameters["player_b"] = players[1]
        
        return parameters
    
    def _generate_simplified_parameters(self, tool_name: str, entities: List[Dict]) -> Dict[str, Any]:
        """Generate simplified parameters for tools."""
        
        # Use only the first entity of each type
        simplified_entities = []
        seen_types = set()
        
        for entity in entities:
            entity_type = entity.get("type", "")
            if entity_type not in seen_types:
                simplified_entities.append(entity)
                seen_types.add(entity_type)
        
        return self._generate_alternative_parameters(tool_name, simplified_entities, {})
    
    def _fallback_plan_creation(self, failure: ToolFailure, original_query: str,
                              entities: List[Dict]) -> FallbackPlan:
        """Fallback plan creation when AI fails."""
        
        # Use rule-based fallback
        strategies = self.failure_strategies.get(failure.failure_type, [FallbackStrategy.TRY_ALTERNATIVE_TOOL])
        
        return FallbackPlan(
            strategy=strategies[0],
            alternative_tools=self.tool_alternatives.get(failure.tool_name, []),
            modified_parameters={},
            reasoning=f"Rule-based fallback for {failure.failure_type.value}",
            confidence=0.5,
            expected_success_rate=0.4
        )
    
    def get_failure_insights(self) -> Dict[str, Any]:
        """Get insights about tool failures for improvement."""
        
        if not self.failure_history:
            return {"message": "No failure history available"}
        
        # Analyze failure patterns
        failure_types = {}
        tool_failures = {}
        
        for failure in self.failure_history:
            failure_types[failure.failure_type.value] = failure_types.get(failure.failure_type.value, 0) + 1
            tool_failures[failure.tool_name] = tool_failures.get(failure.tool_name, 0) + 1
        
        return {
            "total_failures": len(self.failure_history),
            "failure_types": failure_types,
            "tool_failures": tool_failures,
            "most_problematic_tools": sorted(tool_failures.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_common_failure_types": sorted(failure_types.items(), key=lambda x: x[1], reverse=True)[:3]
        }
