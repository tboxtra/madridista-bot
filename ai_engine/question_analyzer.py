#!/usr/bin/env python3
"""
AI-powered question analyzer for football questions
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

# Initialize OpenAI client
_client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

# System prompt for question analysis
SYSTEM_PROMPT = """You are a football data expert. Analyze user questions and extract:
1. INTENT: What the user wants to know (table, form, next match, last match, h2h, scorers, squad, injuries, etc.)
2. TEAMS: Which teams are mentioned (with IDs if known)
3. COMPETITIONS: Which competitions/leagues are mentioned
4. TIME_PERIOD: When they want data for (recent, upcoming, last 5, etc.)
5. API_CALLS: What API calls should be made to answer the question

Available team IDs: Real Madrid (86), Barcelona (81), Arsenal (57), Chelsea (61), Liverpool (64), Manchester United (66), Manchester City (65), Bayern Munich (5), Juventus (109), PSG (524)

Available competition IDs: LaLiga (2014), Premier League (2021), Champions League (2001), Bundesliga (2002), Serie A (2019), Ligue 1 (2015)

Return a JSON object with this structure:
{
  "intent": "string describing what user wants",
  "teams": [{"name": "team name", "id": team_id}],
  "competitions": [{"name": "comp name", "id": comp_id}],
  "time_period": "string describing time period",
  "api_calls": ["list", "of", "api", "calls", "needed"],
  "response_type": "table|form|next|last|h2h|scorers|squad|injuries|general",
  "confidence": 0.95
}"""

def analyze_question(question: str) -> Optional[Dict]:
    """
    Use AI to analyze a football question and determine what the user wants
    """
    if not _client:
        return None
    
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this football question: {question}"}
            ],
            temperature=0.1,  # Low temperature for consistent analysis
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        if not content:
            return None
        
        # Try to parse JSON response
        try:
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract key information
            return extract_fallback_analysis(question)
            
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return extract_fallback_analysis(question)

def extract_fallback_analysis(question: str) -> Dict:
    """
    Fallback analysis when AI fails
    """
    question_lower = question.lower()
    
    # Basic intent detection
    intent = "general"
    if any(word in question_lower for word in ["vs", "versus", "against", "h2h", "head to head"]):
        intent = "h2h"
    elif any(word in question_lower for word in ["table", "standings", "position"]):
        intent = "table"
    elif any(word in question_lower for word in ["form", "last", "recent", "results"]):
        intent = "form"
    elif any(word in question_lower for word in ["next", "upcoming", "when"]):
        intent = "next"
    elif any(word in question_lower for word in ["scorers", "goals"]):
        intent = "scorers"
    elif any(word in question_lower for word in ["squad", "players", "roster"]):
        intent = "squad"
    elif any(word in question_lower for word in ["injuries", "injured", "unavailable"]):
        intent = "injuries"
    
    # Basic team detection
    teams = []
    team_aliases = {
        "madrid": 86, "real madrid": 86, "barcelona": 81, "arsenal": 57,
        "chelsea": 61, "liverpool": 64, "manchester united": 66, "man city": 65,
        "bayern": 5, "juventus": 109, "psg": 524
    }
    
    for alias, team_id in team_aliases.items():
        if alias in question_lower:
            teams.append({"name": alias.title(), "id": team_id})
    
    # Basic competition detection
    competitions = []
    comp_aliases = {
        "laliga": 2014, "premier league": 2021, "champions league": 2001,
        "bundesliga": 2002, "serie a": 2019, "ligue 1": 2015
    }
    
    for alias, comp_id in comp_aliases.items():
        if alias in question_lower:
            competitions.append({"name": alias.title(), "id": comp_id})
    
    return {
        "intent": intent,
        "teams": teams,
        "competitions": competitions,
        "time_period": "recent" if "last" in question_lower else "upcoming" if "next" in question_lower else "current",
        "api_calls": [f"get_{intent}_data"],
        "response_type": intent,
        "confidence": 0.7
    }

def get_ai_enhanced_response(question: str) -> str:
    """
    Get an AI-enhanced response by analyzing the question and calling appropriate APIs
    """
    analysis = analyze_question(question)
    if not analysis:
        # If AI analysis fails, use fallback analysis
        analysis = extract_fallback_analysis(question)
    
    if not analysis:
        return "I'm having trouble understanding your question. Could you rephrase it?"
    
    intent = analysis.get("intent", "general")
    teams = analysis.get("teams", [])
    competitions = analysis.get("competitions", [])
    response_type = analysis.get("response_type", "general")
    
    # Generate contextual response based on AI analysis
    if response_type == "h2h" and len(teams) >= 2:
        team1, team2 = teams[0], teams[1]
        return f"🤖 **AI Analysis**: You're asking about the last match between {team1['name']} and {team2['name']}. Let me fetch that data for you..."
    
    elif response_type == "table" and competitions:
        comp = competitions[0]
        return f"🤖 **AI Analysis**: You want to see the {comp['name']} table. Let me get the current standings..."
    
    elif response_type == "form" and teams:
        team = teams[0]
        return f"🤖 **AI Analysis**: You want to see {team['name']}'s recent form. Let me fetch their last few results..."
    
    elif response_type == "scorers" and competitions:
        comp = competitions[0]
        return f"🤖 **AI Analysis**: You want to see the top scorers in {comp['name']}. Let me get that data..."
    
    else:
        return f"🤖 **AI Analysis**: I understand you're asking about {intent}. Let me find the relevant information for you..."
