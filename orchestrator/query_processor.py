"""
Advanced Query Processor
Handles complex multi-part queries with improved decomposition and orchestration.
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class QueryPart:
    intent: str
    entities: Dict[str, Any]
    priority: int
    tools_needed: List[str]
    parameters: Dict[str, Any]

class AdvancedQueryProcessor:
    """Processes complex queries with multi-part decomposition."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.tool_functions = {}
    
    def decompose_complex_query(self, query: str) -> List[QueryPart]:
        """Decompose complex query into multiple parts."""
        
        decomposition_prompt = f"""
        Analyze this complex football query and break it down into individual, actionable parts:
        
        Query: "{query}"
        
        Break it down into separate queries that can be handled by specific tools. Each part should be:
        1. Self-contained and actionable
        2. Have a clear intent (stats, prediction, comparison, news, etc.)
        3. Include relevant entities (teams, players, competitions, etc.)
        4. Specify priority (1=highest, 5=lowest)
        
        Respond with JSON array:
        [
            {{
                "intent": "intent_type",
                "entities": {{"teams": [], "players": [], "competitions": []}},
                "priority": 1,
                "tools_needed": ["tool1", "tool2"],
                "parameters": {{"param1": "value1"}}
            }}
        ]
        
        Common intents: stats, prediction, comparison, news, history, form, table, fixtures, transfers
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": decomposition_prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            query_parts = []
            for part_data in result:
                query_parts.append(QueryPart(
                    intent=part_data["intent"],
                    entities=part_data["entities"],
                    priority=part_data["priority"],
                    tools_needed=part_data["tools_needed"],
                    parameters=part_data["parameters"]
                ))
            
            # Sort by priority
            query_parts.sort(key=lambda x: x.priority)
            
            return query_parts
            
        except Exception as e:
            # Fallback: treat as single query
            return [QueryPart(
                intent="general",
                entities={"query": query},
                priority=1,
                tools_needed=["tool_news"],
                parameters={"query": query}
            )]
    
    def execute_query_parts(self, query_parts: List[QueryPart], user_id: str) -> List[Dict[str, Any]]:
        """Execute multiple query parts and collect results."""
        
        results = []
        
        for part in query_parts:
            try:
                # Select best tool for this part
                best_tool = self._select_best_tool(part)
                
                if best_tool and best_tool in self.tool_functions:
                    # Execute tool
                    tool_func = self.tool_functions[best_tool]
                    result = tool_func(part.parameters)
                    
                    results.append({
                        "intent": part.intent,
                        "tool_used": best_tool,
                        "result": result,
                        "success": result.get("ok", False)
                    })
                else:
                    results.append({
                        "intent": part.intent,
                        "tool_used": None,
                        "result": {"ok": False, "message": "No suitable tool found"},
                        "success": False
                    })
                    
            except Exception as e:
                results.append({
                    "intent": part.intent,
                    "tool_used": None,
                    "result": {"ok": False, "message": f"Error: {str(e)}"},
                    "success": False
                })
        
        return results
    
    def _select_best_tool(self, query_part: QueryPart) -> str:
        """Select the best tool for a query part."""
        
        intent = query_part.intent.lower()
        entities = query_part.entities
        
        # Tool selection based on intent
        if intent == "stats":
            if "teams" in entities and len(entities["teams"]) > 0:
                return "tool_compare_teams"
            elif "players" in entities and len(entities["players"]) > 0:
                return "tool_compare_players"
            else:
                return "tool_form"
        
        elif intent == "prediction":
            if "teams" in entities and len(entities["teams"]) >= 2:
                return "tool_predict_match_outcome"
            else:
                return "tool_predict_fixture"
        
        elif intent == "comparison":
            if "teams" in entities and len(entities["teams"]) >= 2:
                return "tool_compare_teams"
            elif "players" in entities and len(entities["players"]) >= 2:
                return "tool_compare_players"
            else:
                return "tool_h2h_summary"
        
        elif intent == "news":
            return "tool_news"
        
        elif intent == "history":
            return "tool_history_lookup"
        
        elif intent == "form":
            return "tool_form"
        
        elif intent == "table":
            return "tool_table"
        
        elif intent == "fixtures":
            return "tool_next_fixture"
        
        elif intent == "transfers":
            return "tool_predict_transfer_probability"
        
        else:
            return "tool_news"  # Default fallback
    
    def synthesize_results(self, query: str, results: List[Dict[str, Any]], user_context: Dict = None) -> str:
        """Synthesize multiple results into a coherent response."""
        
        # Filter successful results
        successful_results = [r for r in results if r["success"]]
        
        if not successful_results:
            return "I couldn't find the information you're looking for. Please try rephrasing your question."
        
        # Create synthesis prompt
        synthesis_prompt = f"""
        Synthesize these multiple football query results into a comprehensive, engaging response:
        
        Original Query: "{query}"
        
        Results:
        {json.dumps(successful_results, indent=2)}
        
        User Context: {json.dumps(user_context or {}, indent=2)}
        
        Create a fanboy-style response that:
        1. Addresses all parts of the original query
        2. Integrates information from multiple sources
        3. Maintains enthusiasm and personality
        4. Provides actionable insights
        5. Suggests follow-up questions
        6. Uses emojis and engaging language
        
        Be comprehensive but concise (2-4 paragraphs).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": synthesis_prompt}],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback synthesis
            return self._fallback_synthesis(query, successful_results)
    
    def _fallback_synthesis(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Fallback synthesis when AI synthesis fails."""
        
        response_parts = []
        
        for result in results:
            intent = result["intent"]
            tool_result = result["result"]
            
            if intent == "stats":
                response_parts.append(f"📊 **Statistics**: {tool_result.get('message', 'Data retrieved')}")
            elif intent == "prediction":
                response_parts.append(f"🔮 **Prediction**: {tool_result.get('message', 'Prediction made')}")
            elif intent == "comparison":
                response_parts.append(f"⚖️ **Comparison**: {tool_result.get('message', 'Teams compared')}")
            elif intent == "news":
                response_parts.append(f"📰 **News**: {tool_result.get('message', 'Latest news')}")
            else:
                response_parts.append(f"ℹ️ **{intent.title()}**: {tool_result.get('message', 'Information retrieved')}")
        
        return "\n\n".join(response_parts)
    
    def set_tool_functions(self, tool_functions: Dict[str, Any]):
        """Set available tool functions."""
        self.tool_functions = tool_functions
