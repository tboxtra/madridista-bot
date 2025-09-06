import os, json
from openai import OpenAI
from orchestrator import tools as T

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
}

def answer_nl_question(text: str) -> str:
    """Natural language in; football answer out (tools + LLM composition)."""
    try:
        # First LLM call (decide if a tool is needed)
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
              {"role":"system","content": SYSTEM},
              {"role":"user","content": text}
            ],
            tools=[{"type":"function","function": f} for f in FUNCTIONS],
            tool_choice="auto",
            temperature=0.3,
            max_tokens=220
        )

        msg = r.choices[0].message
        # If the model chose a tool, execute it and call the model again with tool result
        if msg.tool_calls:
            tool_msg = msg.tool_calls[0]
            name = tool_msg.function.name
            args = json.loads(tool_msg.function.arguments or "{}")
            fn = NAME_TO_FUNC.get(name)
            if not fn:
                return "I couldn't find the right data source for that."
            result = fn(args)

            r2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                  {"role":"system","content": SYSTEM},
                  {"role":"user","content": text},
                  msg,
                  {"role":"tool","tool_call_id": tool_msg.id, "name": name, "content": json.dumps(result)}
                ],
                temperature=0.5,
                max_tokens=260
            )
            return r2.choices[0].message.content.strip()

        # No tool needed (concept/rules/chat in-scope)
        return (msg.content or "Can you rephrase that?").strip()
    
    except Exception as e:
        return f"I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
