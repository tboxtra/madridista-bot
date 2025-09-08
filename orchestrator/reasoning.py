"""
Multi-step AI reasoning pipeline for football bot.
Implements intent analysis, entity extraction, tool planning, and response synthesis.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    """Types of football-related intents."""
    MATCH_RESULT = "match_result"
    H2H_COMPARISON = "h2h_comparison"
    PLAYER_STATS = "player_stats"
    TEAM_FORM = "team_form"
    NEWS = "news"
    FIXTURES = "fixtures"
    TABLE = "table"
    HISTORY = "history"
    COMPARISON = "comparison"
    GENERAL = "general"

@dataclass
class ExtractedEntity:
    """Represents an extracted entity from user query."""
    type: str  # team, player, competition, date, etc.
    value: str
    confidence: float
    variations: List[str] = None

@dataclass
class ReasoningStep:
    """Represents a step in the reasoning pipeline."""
    step_name: str
    input_data: Any
    output_data: Any
    confidence: float
    reasoning: str

@dataclass
class ToolPlan:
    """Represents a planned tool execution."""
    tool_name: str
    parameters: Dict[str, Any]
    priority: int
    reasoning: str
    expected_output: str

class AIReasoningPipeline:
    """Multi-step AI reasoning pipeline for football queries."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.reasoning_steps = []
        
    def analyze_intent(self, query: str, context: Dict = None) -> ReasoningStep:
        """Step 1: Analyze the intent of the user query."""
        
        intent_prompt = f"""
        Analyze this football query and determine the primary intent. Consider the context if provided.
        
        Query: "{query}"
        Context: {context or "No context available"}
        
        Intent types:
        - match_result: Asking about specific match results, scores, or outcomes
        - h2h_comparison: Head-to-head records between teams
        - player_stats: Player statistics, performance, or comparisons
        - team_form: Team recent form, results, or performance
        - news: Latest news, headlines, or updates
        - fixtures: Upcoming matches or schedule
        - table: League standings or rankings
        - history: Historical records, champions, or past events
        - comparison: Comparing teams, players, or statistics
        - general: General football questions or explanations
        
        Respond with JSON:
        {{
            "intent": "intent_type",
            "confidence": 0.0-1.0,
            "reasoning": "explanation of why this intent was chosen",
            "sub_intents": ["list", "of", "secondary", "intents"],
            "complexity": "simple|moderate|complex"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": intent_prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            step = ReasoningStep(
                step_name="intent_analysis",
                input_data={"query": query, "context": context},
                output_data=result,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "Intent analyzed")
            )
            
            self.reasoning_steps.append(step)
            return step
            
        except Exception as e:
            # Fallback to simple keyword-based intent detection
            return self._fallback_intent_analysis(query)
    
    def extract_entities(self, query: str, intent: ReasoningStep) -> ReasoningStep:
        """Step 2: Extract entities from the query."""
        
        entity_prompt = f"""
        Extract all relevant entities from this football query. Be comprehensive and include variations.
        
        Query: "{query}"
        Intent: {intent.output_data.get('intent', 'unknown')}
        
        Extract these entity types:
        - teams: Team names (include all variations like "Man City" = "Manchester City")
        - players: Player names
        - competitions: League names, tournament names
        - dates: Time references (last, recent, 2023, etc.)
        - numbers: Quantities, years, match counts
        - actions: Verbs like "beat", "lost", "scored", "won"
        
        Respond with JSON:
        {{
            "entities": [
                {{
                    "type": "entity_type",
                    "value": "canonical_value",
                    "confidence": 0.0-1.0,
                    "variations": ["list", "of", "variations"],
                    "context": "how this entity relates to the query"
                }}
            ],
            "reasoning": "explanation of entity extraction"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": entity_prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            step = ReasoningStep(
                step_name="entity_extraction",
                input_data={"query": query, "intent": intent.output_data},
                output_data=result,
                confidence=0.9,
                reasoning=result.get("reasoning", "Entities extracted")
            )
            
            self.reasoning_steps.append(step)
            return step
            
        except Exception as e:
            return self._fallback_entity_extraction(query)
    
    def plan_tools(self, intent: ReasoningStep, entities: ReasoningStep, context: Dict = None) -> ReasoningStep:
        """Step 3: Plan which tools to use based on intent and entities."""
        
        available_tools = [
            "tool_af_find_match_result", "tool_af_last_result_vs", "tool_h2h_officialish",
            "tool_player_stats", "tool_compare_players", "tool_form", "tool_compare_teams",
            "tool_news", "tool_next_fixture", "tool_table", "tool_history_lookup",
            "tool_rm_ucl_titles", "tool_ucl_last_n_winners", "tool_next_lineups",
            "tool_scorers", "tool_injuries", "tool_squad", "tool_live_now"
        ]
        
        tool_planning_prompt = f"""
        Plan which tools to use for this football query. Consider the intent, entities, and context.
        
        Intent: {intent.output_data}
        Entities: {entities.output_data}
        Context: {context or "No context"}
        Available Tools: {available_tools}
        
        For each tool, consider:
        - How well it matches the intent
        - Whether it can use the extracted entities
        - Expected output quality
        - Priority order
        
        Respond with JSON:
        {{
            "tool_plan": [
                {{
                    "tool_name": "tool_name",
                    "parameters": {{"param": "value"}},
                    "priority": 1-5,
                    "reasoning": "why this tool is needed",
                    "expected_output": "what this tool should return"
                }}
            ],
            "execution_strategy": "parallel|sequential|conditional",
            "reasoning": "overall tool planning strategy"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": tool_planning_prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            step = ReasoningStep(
                step_name="tool_planning",
                input_data={"intent": intent.output_data, "entities": entities.output_data, "context": context},
                output_data=result,
                confidence=0.85,
                reasoning=result.get("reasoning", "Tools planned")
            )
            
            self.reasoning_steps.append(step)
            return step
            
        except Exception as e:
            return self._fallback_tool_planning(intent, entities)
    
    def generate_parameters(self, entities: ReasoningStep, tool_plan: ReasoningStep) -> ReasoningStep:
        """Step 4: Generate specific parameters for each planned tool."""
        
        param_prompt = f"""
        Generate specific parameters for each tool in the plan. Use the extracted entities.
        
        Entities: {entities.output_data}
        Tool Plan: {tool_plan.output_data}
        
        For each tool, generate the exact parameters needed. Be precise with team names, player names, etc.
        
        Respond with JSON:
        {{
            "tool_parameters": [
                {{
                    "tool_name": "tool_name",
                    "parameters": {{"exact": "parameter", "values": "here"}},
                    "confidence": 0.0-1.0,
                    "reasoning": "how parameters were derived from entities"
                }}
            ],
            "reasoning": "overall parameter generation strategy"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": param_prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            step = ReasoningStep(
                step_name="parameter_generation",
                input_data={"entities": entities.output_data, "tool_plan": tool_plan.output_data},
                output_data=result,
                confidence=0.9,
                reasoning=result.get("reasoning", "Parameters generated")
            )
            
            self.reasoning_steps.append(step)
            return step
            
        except Exception as e:
            return self._fallback_parameter_generation(entities, tool_plan)
    
    def synthesize_response(self, query: str, tool_results: List[Dict], reasoning_steps: List[ReasoningStep]) -> str:
        """Step 5: Synthesize the final response using tool results and reasoning."""
        
        # Prepare reasoning summary
        reasoning_summary = "\n".join([
            f"- {step.step_name}: {step.reasoning} (confidence: {step.confidence:.2f})"
            for step in reasoning_steps
        ])
        
        synthesis_prompt = f"""
        Synthesize a fanboy response for this football query using the tool results and reasoning.
        
        Original Query: "{query}"
        
        Reasoning Steps:
        {reasoning_summary}
        
        Tool Results:
        {json.dumps(tool_results, indent=2)}
        
        Guidelines:
        - Be a passionate Real Madrid fan
        - Use actual data from tool results
        - Add personality and banter
        - Include citations for facts
        - Be concise (1-3 paragraphs)
        - If no data found, suggest alternatives
        
        Respond with the final fanboy response:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": synthesis_prompt}],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return self._fallback_response_synthesis(query, tool_results)
    
    def run_pipeline(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Run the complete reasoning pipeline."""
        
        # Step 1: Intent Analysis
        intent_step = self.analyze_intent(query, context)
        
        # Step 2: Entity Extraction
        entity_step = self.extract_entities(query, intent_step)
        
        # Step 3: Tool Planning
        tool_plan_step = self.plan_tools(intent_step, entity_step, context)
        
        # Step 4: Parameter Generation
        param_step = self.generate_parameters(entity_step, tool_plan_step)
        
        return {
            "intent": intent_step,
            "entities": entity_step,
            "tool_plan": tool_plan_step,
            "parameters": param_step,
            "reasoning_steps": self.reasoning_steps
        }
    
    # Fallback methods for when AI calls fail
    def _fallback_intent_analysis(self, query: str) -> ReasoningStep:
        """Fallback intent analysis using keyword matching."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["beat", "won", "lost", "score", "result"]):
            intent = "match_result"
        elif any(word in query_lower for word in ["vs", "against", "h2h", "head to head"]):
            intent = "h2h_comparison"
        elif any(word in query_lower for word in ["player", "stats", "goals", "assists"]):
            intent = "player_stats"
        elif any(word in query_lower for word in ["form", "recent", "last"]):
            intent = "team_form"
        elif any(word in query_lower for word in ["news", "headlines", "update"]):
            intent = "news"
        elif any(word in query_lower for word in ["next", "upcoming", "fixture"]):
            intent = "fixtures"
        else:
            intent = "general"
        
        return ReasoningStep(
            step_name="intent_analysis_fallback",
            input_data={"query": query},
            output_data={"intent": intent, "confidence": 0.6, "reasoning": "Fallback keyword matching"},
            confidence=0.6,
            reasoning="Fallback keyword matching"
        )
    
    def _fallback_entity_extraction(self, query: str) -> ReasoningStep:
        """Fallback entity extraction using regex patterns."""
        entities = []
        
        # Team name patterns
        team_patterns = [
            r'\b(man city|manchester city)\b', r'\b(madrid|real madrid)\b',
            r'\b(barca|barcelona)\b', r'\b(spurs|tottenham)\b',
            r'\b(juve|juventus)\b', r'\b(arsenal)\b', r'\b(chelsea)\b',
            r'\b(liverpool)\b', r'\b(united|manchester united)\b'
        ]
        
        for pattern in team_patterns:
            matches = re.findall(pattern, query.lower())
            if matches:
                entities.append({
                    "type": "team",
                    "value": matches[0],
                    "confidence": 0.7,
                    "variations": [matches[0]]
                })
        
        return ReasoningStep(
            step_name="entity_extraction_fallback",
            input_data={"query": query},
            output_data={"entities": entities, "reasoning": "Fallback regex extraction"},
            confidence=0.6,
            reasoning="Fallback regex extraction"
        )
    
    def _fallback_tool_planning(self, intent: ReasoningStep, entities: ReasoningStep) -> ReasoningStep:
        """Fallback tool planning using simple rules."""
        intent_type = intent.output_data.get("intent", "general")
        
        tool_mapping = {
            "match_result": [{"tool_name": "tool_af_find_match_result", "priority": 1}],
            "h2h_comparison": [{"tool_name": "tool_af_last_result_vs", "priority": 1}],
            "player_stats": [{"tool_name": "tool_player_stats", "priority": 1}],
            "team_form": [{"tool_name": "tool_form", "priority": 1}],
            "news": [{"tool_name": "tool_news", "priority": 1}],
            "fixtures": [{"tool_name": "tool_next_fixture", "priority": 1}]
        }
        
        tool_plan = tool_mapping.get(intent_type, [{"tool_name": "tool_news", "priority": 1}])
        
        return ReasoningStep(
            step_name="tool_planning_fallback",
            input_data={"intent": intent.output_data, "entities": entities.output_data},
            output_data={"tool_plan": tool_plan, "reasoning": "Fallback rule-based planning"},
            confidence=0.6,
            reasoning="Fallback rule-based planning"
        )
    
    def _fallback_parameter_generation(self, entities: ReasoningStep, tool_plan: ReasoningStep) -> ReasoningStep:
        """Fallback parameter generation."""
        return ReasoningStep(
            step_name="parameter_generation_fallback",
            input_data={"entities": entities.output_data, "tool_plan": tool_plan.output_data},
            output_data={"tool_parameters": [], "reasoning": "Fallback parameter generation"},
            confidence=0.5,
            reasoning="Fallback parameter generation"
        )
    
    def _fallback_response_synthesis(self, query: str, tool_results: List[Dict]) -> str:
        """Fallback response synthesis."""
        if tool_results:
            return f"I found some information about your query: '{query}'. Here are the results: {json.dumps(tool_results, indent=2)}"
        else:
            return f"I couldn't find specific information about '{query}'. Try asking about recent matches, player stats, or team form!"
