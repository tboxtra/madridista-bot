import os, json
from openai import OpenAI
from orchestrator import tools as T

CITATIONS_ON = os.getenv("CITATIONS", "true").lower() == "true"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = (
  "You are a friendly, concise football assistant. "
  "Scope is strictly football (clubs, leagues, players, fixtures, rules). "
  "Use the provided tools for any facts (scores, fixtures, standings, injuries, squads, scorers, live). "
  "If a question is about football concepts (rules/history) and no tool is required, answer briefly. "
  "If the user asks outside football, decline politely and offer football topics. "
  "Keep answers under ~120 words unless the user asks for detail. "
  "Always prefer Real Madrid and LaLiga when ambiguous."
)

# Tool schemas for function calling (names must match T.* function names)
FUNCTIONS = [
  {"name":"tool_next_fixture","description":"Nearest upcoming fixture for a team",
   "parameters":{"type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"}}}},
  {"name":"tool_last_result","description":"Latest finished result for a team",
   "parameters":{"type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"}}}},
  {"name":"tool_live_now","description":"Live score for configured team","parameters":{"type":"object","properties":{}} },
  {"name":"tool_table","description":"League table top rows","parameters":{"type":"object","properties":{"competition":{"type":"string"},"competition_id":{"type":"integer"}}}},
  {"name":"tool_form","description":"Recent results for a team","parameters":{"type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"},"k":{"type":"integer"}}}},
  {"name":"tool_scorers","description":"Top scorers of a competition","parameters":{"type":"object","properties":{"competition":{"type":"string"},"competition_id":{"type":"integer"},"limit":{"type":"integer"}}}},
  {"name":"tool_injuries","description":"Team injuries/unavailable","parameters":{"type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"}}}},
  {"name":"tool_squad","description":"Team squad (optional position filter)","parameters":{"type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"},"position":{"type":"string"}}}},
  {"name":"tool_last_man_of_match","description":"Last Man of the Match or top-rated player","parameters":{"type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"}}}},
  {"name":"tool_compare_teams","description":"Compare two teams' recent form (last k) with quick verdict",
   "parameters":{"type":"object","properties":{"team_a":{"type":"string"},"team_b":{"type":"string"},"k":{"type":"integer"}}}},
  {"name":"tool_h2h_summary","description":"Head-to-head summary between two teams",
   "parameters":{"type":"object","properties":{"team_a":{"type":"string"},"team_b":{"type":"string"}}}},
  {"name":"tool_player_stats","description":"Basic player season stats (apps/goals/assists/rating)",
   "parameters":{"type":"object","properties":{"player_name":{"type":"string"},"query":{"type":"string"}}}},
  {"name":"tool_news","description":"Top football news (optional filter)",
   "parameters":{"type":"object","properties":{"query":{"type":"string"}}}},
  {"name":"tool_compare_players","description":"Compare two players' season stats with per-90","parameters":{
    "type":"object","properties":{"player_a":{"type":"string"},"player_b":{"type":"string"},"query_a":{"type":"string"},"query_b":{"type":"string"}}
  }},
  {"name":"tool_next_lineups","description":"Probable or confirmed lineups for the next match","parameters":{
    "type":"object","properties":{"team_name":{"type":"string"},"team_id":{"type":"integer"}}}
  }
]

NAME_TO_FUNC = {
  "tool_next_fixture": T.tool_next_fixture,
  "tool_last_result": T.tool_last_result,
  "tool_live_now": T.tool_live_now,
  "tool_table": T.tool_table,
  "tool_form": T.tool_form,
  "tool_scorers": T.tool_scorers,
  "tool_injuries": T.tool_injuries,
  "tool_squad": T.tool_squad,
  "tool_last_man_of_match": T.tool_last_man_of_match,
  "tool_compare_teams": T.tool_compare_teams,
  "tool_h2h_summary": T.tool_h2h_summary,
  "tool_player_stats": T.tool_player_stats,
  "tool_news": T.tool_news,
  "tool_compare_players": T.tool_compare_players,
  "tool_next_lineups": T.tool_next_lineups,
}

# Optional: very light pre-router to hint the model
def _pre_hint(text: str):
    t = text.lower()
    if any(w in t for w in ["compare", "vs", "versus"]):
        return "You may need tool_compare_teams or tool_h2h_summary or tool_compare_players."
    if any(w in t for w in ["lineup", "line-ups", "line up", "xi", "starting eleven"]):
        return "You may need tool_next_lineups."
    if any(w in t for w in ["stats", "per 90", "goals", "assists", "rating"]):
        return "You may need tool_player_stats or tool_compare_players."
    if any(w in t for w in ["news", "headline", "rumor"]):
        return "You may need tool_news."
    return None

def answer_nl_question(text: str) -> str:
    """Natural language in; football answer out (tools + LLM composition)."""
    try:
        hint = _pre_hint(text)
        msgs = [{"role":"system","content": SYSTEM}]
        if hint:
            msgs.append({"role":"system","content": hint})
        msgs.append({"role":"user","content": text})

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            tools=[{"type":"function","function": f} for f in FUNCTIONS],
            tool_choice="auto",
            temperature=0.3,
            max_tokens=220
        )

        msg = r.choices[0].message
        if msg.tool_calls:
            # Support multiple tool calls (e.g., compare both + h2h)
            tool_msgs = []
            sources = set()
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                fn = NAME_TO_FUNC.get(name)
                result = fn(args) if fn else {"ok": False, "message": "Unknown tool"}
                src = result.get("__source")
                if src:
                    sources.add(src)
                tool_msgs.append({"role":"tool","tool_call_id": tc.id, "name": name, "content": json.dumps(result)})

            r2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content": SYSTEM},{"role":"user","content": text}, msg, *tool_msgs],
                temperature=0.5,
                max_tokens=380
            )
            out = r2.choices[0].message.content.strip()
            if CITATIONS_ON and sources:
                out += "\n\n(" + " • ".join(sorted(sources)) + ")"
            return out

        return (msg.content or "Can you rephrase that?").strip()
    
    except Exception as e:
        return f"I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
