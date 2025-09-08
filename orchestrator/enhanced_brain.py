"""
Enhanced AI brain with multi-step reasoning, memory, dynamic tool selection,
intelligent fallbacks, and proactive suggestions.
"""

import json
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Import our new modules
from .reasoning import AIReasoningPipeline
from .memory import ConversationMemory
from .tool_selector import DynamicToolSelector
from .fallback_system import IntelligentFallbackSystem
from .proactive_system import ProactiveSuggestionSystem

# Import existing modules
from . import tools
from . import tools_ext
from . import tools_history
from . import tools_enhanced
from . import arbiter

class EnhancedFootballBrain:
    """Enhanced AI brain with advanced reasoning capabilities."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        
        # Initialize all subsystems
        self.reasoning_pipeline = AIReasoningPipeline(openai_client)
        self.memory = ConversationMemory()
        self.tool_selector = DynamicToolSelector(openai_client)
        self.fallback_system = IntelligentFallbackSystem(openai_client)
        self.proactive_system = ProactiveSuggestionSystem(openai_client)
        
        # Tool registry (only tools that actually exist)
        self.tool_functions = {
            # Core tools
            "tool_next_fixture": tools.tool_next_fixture,
            "tool_last_result": tools.tool_last_result,
            "tool_live_now": tools.tool_live_now,
            "tool_table": tools.tool_table,
            "tool_form": tools.tool_form,
            "tool_scorers": tools.tool_scorers,
            "tool_injuries": tools.tool_injuries,
            "tool_squad": tools.tool_squad,
            "tool_last_man_of_match": tools.tool_last_man_of_match,
            "tool_compare_teams": tools.tool_compare_teams,
            "tool_h2h_summary": tools.tool_h2h_summary,
            "tool_player_stats": tools.tool_player_stats,
            "tool_news": tools.tool_news,
            "tool_compare_players": tools.tool_compare_players,
            "tool_next_lineups": tools.tool_next_lineups,
            "tool_glossary": tools.tool_glossary,
            "tool_next_fixtures_multi": tools.tool_next_fixtures_multi,
            
            # Extended tools (only existing ones)
            "tool_af_find_match_result": tools_ext.tool_af_find_match_result,
            "tool_af_last_result_vs": tools_ext.tool_af_last_result_vs,
            "tool_af_next_fixture": tools_ext.tool_af_next_fixture,
            "tool_af_last_result": tools_ext.tool_af_last_result,
            "tool_sofa_form": tools_ext.tool_sofa_form,
            "tool_news_top": tools_ext.tool_news_top,
            "tool_highlights": tools_ext.tool_highlights,
            "tool_youtube_latest": tools_ext.tool_youtube_latest,
            "tool_club_elo": tools_ext.tool_club_elo,
            "tool_odds_snapshot": tools_ext.tool_odds_snapshot,
            
            # History tools
            "tool_h2h_officialish": tools_history.tool_h2h_officialish,
            "tool_history_lookup": tools_history.tool_history_lookup,
            "tool_rm_ucl_titles": tools_history.tool_rm_ucl_titles,
            "tool_ucl_last_n_winners": tools_history.tool_ucl_last_n_winners,
            
            # Enhanced tools
            "tool_weather_match": tools_enhanced.tool_weather_match,
            "tool_weather_impact": tools_enhanced.tool_weather_impact,
            "tool_news_trending": tools_enhanced.tool_news_trending,
            "tool_news_team": tools_enhanced.tool_news_team,
            "tool_news_player": tools_enhanced.tool_news_player,
            "tool_news_competition": tools_enhanced.tool_news_competition,
            "tool_convert_transfer": tools_enhanced.tool_convert_transfer,
            "tool_market_trends": tools_enhanced.tool_market_trends,
            "tool_compare_transfers": tools_enhanced.tool_compare_transfers,
            "tool_currency_impact": tools_enhanced.tool_currency_impact,
            "tool_cache_stats": tools_enhanced.tool_cache_stats,
            "tool_clear_cache": tools_enhanced.tool_clear_cache,
        }
        
        # System prompt for enhanced AI
        self.system_prompt = """
        You are an advanced Real Madrid superfan and football assistant with enhanced AI capabilities.
        
        CORE CAPABILITIES:
        - Multi-step reasoning: Analyze queries step by step
        - Context awareness: Remember conversation history and user preferences
        - Dynamic tool selection: Choose the best tools based on intent and context
        - Intelligent fallbacks: Handle failures gracefully with alternative approaches
        - Proactive suggestions: Anticipate user needs and provide related information
        
        WORKFLOW:
        1. Analyze the user's intent and extract entities
        2. Consider conversation context and user preferences
        3. Select the most appropriate tools dynamically
        4. Execute tools with proper parameters
        5. Handle any failures with intelligent fallbacks
        6. Synthesize response with contextual insights
        7. Provide proactive suggestions for related topics
        
        RESPONSE GUIDELINES:
        - Be a passionate Real Madrid fan with personality
        - Use actual data from tools, never hallucinate
        - Include contextual insights and historical context
        - Provide proactive suggestions for related topics
        - Be concise but informative (1-3 paragraphs)
        - Include citations for facts
        - Handle errors gracefully with helpful alternatives
        
        TOOL SELECTION:
        - Always use tools for factual information
        - Choose tools based on intent, not keywords
        - Consider data freshness and reliability
        - Use multiple tools when beneficial
        - Handle tool failures with fallbacks
        
        CONTEXT AWARENESS:
        - Remember user's favorite teams and players
        - Track conversation flow and topics
        - Provide personalized recommendations
        - Anticipate follow-up questions
        
        Keep banter clean and football-focused. Prefer Real Madrid & LaLiga content.
        """
    
    def process_query(self, query: str, user_id: str = "default", 
                     context: Dict = None) -> Dict[str, Any]:
        """Process a query using the enhanced AI brain."""
        
        start_time = time.time()
        
        try:
            # Step 1: Get user context and conversation history
            user_context = self.memory.get_user_context(user_id)
            recent_context = self.memory.get_recent_context(user_id)
            user_preferences = self.memory.get_user_preferences(user_id)
            
            # Step 2: Multi-step reasoning pipeline
            reasoning_result = self.reasoning_pipeline.run_pipeline(query, {
                "user_context": user_context.__dict__,
                "recent_context": recent_context,
                "user_preferences": user_preferences
            })
            
            intent = reasoning_result["intent"]
            entities = reasoning_result["entities"]
            tool_plan = reasoning_result["tool_plan"]
            parameters = reasoning_result["parameters"]
            
            # Step 3: Dynamic tool selection and execution
            tool_scores = self.tool_selector.score_tools(
                intent.output_data.get("intent", "general"),
                entities.output_data.get("entities", []),
                recent_context,
                user_preferences
            )
            
            selected_tools = self.tool_selector.select_best_tools(tool_scores, max_tools=3)
            
            # Step 4: Execute tools with fallback handling
            tool_results = []
            successful_tools = []
            
            for tool_score in selected_tools:
                tool_name = tool_score.tool_name
                tool_func = self.tool_functions.get(tool_name)
                
                if not tool_func:
                    continue
                
                # Generate parameters for the tool
                tool_parameters = self.tool_selector.generate_tool_parameters(
                    tool_name, entities.output_data.get("entities", []), recent_context
                )
                
                try:
                    # Execute the tool (tools expect args dictionary)
                    result = tool_func(tool_parameters)
                    
                    if result and result != "No data found":
                        tool_results.append({
                            "tool": tool_name,
                            "result": result,
                            "parameters": tool_parameters
                        })
                        successful_tools.append(tool_name)
                    
                except Exception as e:
                    # Handle tool failure with intelligent fallback
                    failure = self.fallback_system.analyze_failure(tool_name, e, {
                        "original_parameters": tool_parameters,
                        "query": query,
                        "entities": entities.output_data
                    })
                    
                    fallback_plan = self.fallback_system.create_fallback_plan(
                        failure, query, entities.output_data.get("entities", []), user_preferences
                    )
                    
                    fallback_result = self.fallback_system.execute_fallback_plan(
                        fallback_plan, failure, query, entities.output_data.get("entities", []), self.tool_functions
                    )
                    
                    if fallback_result.get("success"):
                        tool_results.append({
                            "tool": tool_name,
                            "result": fallback_result["result"],
                            "parameters": tool_parameters,
                            "fallback_used": True
                        })
                        successful_tools.append(tool_name)
            
            # Step 5: Generate contextual insights
            contextual_insights = self.proactive_system.generate_contextual_insights(
                query, entities.output_data.get("entities", []), user_preferences, tool_results
            )
            
            # Step 6: Synthesize response
            if tool_results:
                response = self.reasoning_pipeline.synthesize_response(
                    query, tool_results, reasoning_result["reasoning_steps"]
                )
            else:
                response = "I couldn't find specific information for your query. Try asking about recent matches, player stats, or team form!"
            
            # Step 7: Generate proactive suggestions
            suggestions = self.proactive_system.generate_suggestions(
                query, response, entities.output_data.get("entities", []), user_preferences
            )
            
            # Step 8: Update memory
            self.memory.add_conversation(
                user_id=user_id,
                query=query,
                response=response,
                intent=intent.output_data.get("intent", "general"),
                entities=entities.output_data.get("entities", []),
                tools_used=successful_tools
            )
            
            # Step 9: Prepare final response
            final_response = {
                "response": response,
                "suggestions": [
                    {
                        "title": s.title,
                        "description": s.description,
                        "action": s.action,
                        "type": s.type.value
                    }
                    for s in suggestions
                ],
                "contextual_insights": [
                    {
                        "type": i.insight_type,
                        "content": i.content,
                        "relevance": i.relevance.value
                    }
                    for i in contextual_insights
                ],
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "tools_used": successful_tools,
                    "intent": intent.output_data.get("intent", "general"),
                    "entities": entities.output_data.get("entities", []),
                    "reasoning_steps": len(reasoning_result["reasoning_steps"]),
                    "fallbacks_used": any(r.get("fallback_used", False) for r in tool_results)
                }
            }
            
            return final_response
            
        except Exception as e:
            # Ultimate fallback
            return {
                "response": f"I encountered an error processing your query: '{query}'. Please try rephrasing your question or ask about recent matches, player stats, or team form.",
                "suggestions": [
                    {
                        "title": "Try a different question",
                        "description": "Ask about recent matches or player stats",
                        "action": "Show me recent match results",
                        "type": "follow_up_question"
                    }
                ],
                "contextual_insights": [],
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "tools_used": [],
                    "intent": "unknown",
                    "entities": [],
                    "reasoning_steps": 0,
                    "error": str(e),
                    "fallback_used": True
                }
            }
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about a user's interaction patterns."""
        
        user_context = self.memory.get_user_context(user_id)
        conversation_insights = self.memory.get_conversation_insights()
        suggestion_insights = self.proactive_system.get_suggestion_insights()
        failure_insights = self.fallback_system.get_failure_insights()
        
        return {
            "user_context": user_context,
            "conversation_insights": conversation_insights,
            "suggestion_insights": suggestion_insights,
            "failure_insights": failure_insights
        }
    
    def export_memory(self) -> Dict[str, Any]:
        """Export conversation memory for persistence."""
        return self.memory.export_memory()
    
    def import_memory(self, data: Dict[str, Any]) -> None:
        """Import conversation memory from persistence."""
        self.memory.import_memory(data)
