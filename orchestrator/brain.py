import os, json, re
from openai import OpenAI
from orchestrator import tools as T
from orchestrator import tools_history as TH
from orchestrator import tools_ext as TX
from orchestrator.arbiter import plan_tools, _is_empty as _empty, validate_recency
from utils.banter_ai import ai_banter

STRICT_FACTS = os.getenv("STRICT_FACTS","true").lower() == "true"
HISTORY_ON = os.getenv("HISTORY_ENABLE","true").lower() == "true"
LOG_TOOL_CALLS = os.getenv("LOG_TOOL_CALLS","true").lower() == "true"

FACTY_HINTS = (
  "when","what time","score","result","fixture","lineup","xi","injury","table","standings",
  "scorer","goals","assists","rating","compare","vs","versus","h2h","news","transfer",
  "prediction","predict","odds","form","last match","next match","today","yesterday","tomorrow",
  "year","season","final","finals","history","historical","record","formation","tactics",
  "winner","winners","champion","champions"
)

def _looks_factual(q: str) -> bool:
    ql = (q or "").lower()
    if re.search(r"\b(19[0-9]{2}|20[0-2][0-9])\b", ql):  # years
        return True
    return any(k in ql for k in FACTY_HINTS)

def _looks_historical(q: str) -> bool:
    """Detect historical queries that need Wikipedia/history tools."""
    ql = (q or "").lower()
    return (
        re.search(r"\b(19[0-9]{2}|20[0-2][0-9])\b", ql) or
        any(w in ql for w in [
            "history", "winner", "winners", "champions", "finals", "decade", 
            "legend", "record", "records", "past", "previous", "last", "first",
            "ever", "all time", "historic", "classic", "famous", "notable"
        ])
    )

CITATIONS_ON = os.getenv("CITATIONS", "true").lower() == "true"
SAFE_MAX = 900

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _safe(s: str) -> str: 
    return (s or "")[:SAFE_MAX].strip()

def _banter_intent(q: str) -> str:
    ql = (q or "").lower()
    if any(k in ql for k in ["predict","prediction","scoreline","call it","who wins","bet","odds"]):
        return "prediction"
    if any(k in ql for k in ["debate","argue","convince","who's better","who is better","clear of"]):
        return "argument"
    if any(k in ql for k in ["banter","trash talk","talk your talk","clap back","ratio"]):
        return "banter"
    if any(k in ql for k in ["barca","barcelona","xavi","camp nou"]) and len(ql) < 140:
        return "banter"
    return ""

def _facts_from_toolpayload(payloads):
    facts = []
    for p in payloads:
        if not isinstance(p, dict): continue
        if p.get("when") and p.get("home") and p.get("away"):
            if "home_score" in p:
                facts.append(f"Last match: {p['home']} {p['home_score']}-{p['away_score']} {p['away']} on {p['when']}")
            else:
                facts.append(f"Next match: {p['home']} vs {p['away']} on {p['when']}")
        if p.get("points_a") is not None and p.get("points_b") is not None:
            facts.append(f"Form (last {p.get('k',5)}): {p.get('team_a','A')}={p['points_a']}, {p.get('team_b','B')}={p['points_b']}")
        if p.get("rows") and "pts" in p["rows"][0]:
            lead = p["rows"][0]; facts.append(f"Top of table: {lead['team']} {lead['pts']} pts")
        if p.get("items") and p["items"] and "title" in p["items"][0]:
            facts.append("News feed active today")
        if p.get("name") and ("rating" in p or "minutes" in p or "goals" in p):
            # player stats tool
            mins = p.get("minutes"); g = p.get("goals"); a = p.get("assists")
            if g is not None or a is not None:
                facts.append(f"{p['name']} stats: {g or 0}g, {a or 0}a" + (f" in {mins}m" if mins else ""))
        if p.get("event") and p["event"].get("home") and p["event"].get("away"):
            facts.append(f"Lineups for {p['event']['home']} vs {p['event']['away']} possibly available")
    return facts[:10]

def _in_scope(q: str) -> bool:
    ql = (q or "").lower()
    football_terms = (
        "football","soccer","match","fixture","goal","assist","lineup","line up","xi",
        "premier","laliga","ucl","champions","league","table","standings","scorers",
        "injury","injuries","squad","h2h","compare","form","live","result","score",
        "news","headline","rumor","transfer","transfers",
        "tactic","tactics","formation","offside","var","history","legend","coach","manager",
        "pressing","counter","xg",
        "real madrid","madrid","barca","barcelona","bernabeu","vinicius","bellingham","ancelotti","mbapp",
        # Historical terms
        "european cup","champions league","world cup","euro","copa","final","cup","trophy",
        "won","winner","champion","champions","victory","defeat","beat","defeated",
        "1960","1961","1962","1963","1964","1965","1966","1967","1968","1969","1970",
        "1971","1972","1973","1974","1975","1976","1977","1978","1979","1980",
        "1981","1982","1983","1984","1985","1986","1987","1988","1989","1990",
        "1991","1992","1993","1994","1995","1996","1997","1998","1999","2000",
        "2001","2002","2003","2004","2005","2006","2007","2008","2009","2010",
        "2011","2012","2013","2014","2015","2016","2017","2018","2019","2020",
        "2021","2022","2023","2024","2025"
    )
    return any(t in ql for t in football_terms)

SYSTEM = (
  "You are a Real Madrid superfan and football assistant. "
  "ALWAYS think about the question FIRST before answering. "
  "For any factual information, you must SELECT the best tool to fetch data before responding. "
  "You are never allowed to make up data or dates. "
  "Examples:\n"
  "- If about past champions, winners, or historical records, use tool_history_lookup.\n"
  "- If about next fixtures or upcoming matches, use tool_af_next_fixture.\n"
  "- If about live games, recent form, or current stats, use SofaScore tools.\n"
  "- If about news or headlines, use tool_news_top.\n"
  "- If about Real Madrid UCL history specifically, use tool_rm_ucl_titles.\n"
  "If multiple tools might be useful, call them all, then combine the results naturally. "
  "Think step by step: understand the question, select appropriate tools, fetch data, then compose your fanboy response. "
  "Prefer Real Madrid & LaLiga. Be concise (1–3 short paragraphs). Keep banter clean."
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
  },
  {"name":"tool_glossary","description":"Explain football terms, rules, tactics from internal KB",
   "parameters":{"type":"object","properties":{"term":{"type":"string"}}}},
  {"name":"tool_next_fixtures_multi","description":"Next fixtures for multiple teams",
   "parameters":{"type":"object","properties":{"team_names":{"type":"array","items":{"type":"string"}}}}},
  {"name":"tool_predict_fixture","description":"Fan-style score prediction for next match",
   "parameters":{"type":"object","properties":{"team_name":{"type":"string"}}}},
  {"name":"tool_rm_ucl_titles","description":"Real Madrid UEFA Champions League titles and history",
   "parameters":{"type":"object","properties":{}}},
  {"name":"tool_history_lookup","description":"Look up football history from Wikipedia",
   "parameters":{"type":"object","properties":{"query":{"type":"string"}}}},
  {"name":"tool_ucl_last_n_winners","description":"Last N UCL winners from Wikipedia finals list",
   "parameters":{"type":"object","properties":{"n":{"type":"integer"}}}},
  {"name":"tool_af_next_fixture","description":"Next fixture via API-Football","parameters":{"type":"object","properties":{"team_id":{"type":"integer"}}}},
  {"name":"tool_af_last_result","description":"Last finished via API-Football","parameters":{"type":"object","properties":{"team_id":{"type":"integer"}}}},
  {"name":"tool_sofa_form","description":"Recent form via SofaScore","parameters":{"type":"object","properties":{"team_id":{"type":"integer"},"k":{"type":"integer"}}}},
  {"name":"tool_news_top","description":"Top soccer news via LiveScore","parameters":{"type":"object","properties":{"query":{"type":"string"}}}},
  {"name":"tool_highlights","description":"Highlights via Scorebat","parameters":{"type":"object","properties":{"team_name":{"type":"string"}}}},
  {"name":"tool_youtube_latest","description":"Latest videos from club channel","parameters":{"type":"object","properties":{"channel_id":{"type":"string"}}}},
  {"name":"tool_club_elo","description":"Club Elo rating","parameters":{"type":"object","properties":{"team_name":{"type":"string"}}}},
  {"name":"tool_odds_snapshot","description":"Prematch odds snapshot","parameters":{"type":"object","properties":{"sport_key":{"type":"string"}}}}
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
  "tool_glossary": T.tool_glossary,
  "tool_next_fixtures_multi": T.tool_next_fixtures_multi,
  "tool_predict_fixture": T.tool_predict_fixture,
  "tool_rm_ucl_titles": TH.tool_rm_ucl_titles,
  "tool_history_lookup": TH.tool_history_lookup,
  "tool_ucl_last_n_winners": TH.tool_ucl_last_n_winners,
  "tool_af_next_fixture": TX.tool_af_next_fixture,
  "tool_af_last_result": TX.tool_af_last_result,
  "tool_sofa_form": TX.tool_sofa_form,
  "tool_news_top": TX.tool_news_top,
  "tool_highlights": TX.tool_highlights,
  "tool_youtube_latest": TX.tool_youtube_latest,
  "tool_club_elo": TX.tool_club_elo,
  "tool_odds_snapshot": TX.tool_odds_snapshot,
}

# Optional: very light pre-router to hint the model
def _pre_hint(text: str):
    t = (text or "").lower()
    if any(x in t for x in ["last 5 ucl", "last five ucl", "ucl winners", "recent champions league winners", "last 5 champions league winners"]):
        return "Use tool_ucl_last_n_winners first, then summarize."
    if any(w in t for w in ["who won", "winners", "champions", "finals", "season", "history"]):
        return "Use tool_history_lookup first."
    if "news" in t or "rumor" in t:
        return "Use tool_news_top."
    if any(w in t for w in ["compare", "vs", "versus", "h2h","head to head"]):
        return "Use tool_compare_teams or tool_compare_players for comparisons; call tools before answering."
    if any(w in t for w in ["lineup", "line-ups", "line up", "xi", "starting eleven"]):
        return "Use tool_next_lineups; call tools before answering."
    if any(w in t for w in ["stats", "per 90", "goals", "assists", "rating"]):
        return "Use tool_player_stats or tool_compare_players; call tools before answering."
    if any(w in t for w in ["news", "headline", "rumor", "transfer"]):
        return "Use tool_news; call tools before answering."
    if _looks_historical(t):
        return "Use tool_history_lookup or tool_rm_ucl_titles for historical details."
    if "fixture" in t or "next match" in t or "who do" in t and "play" in t:
        return "Use tool_next_fixture or tool_next_fixtures_multi; call tools before answering."
    if "last match" in t or "result" in t or "score" in t:
        return "Use tool_last_result or tool_live_now; call tools before answering."
    if any(w in t for w in ["what is", "explain", "meaning of", "define", "how does", "how do"]):
        return "You may need tool_glossary if this is a rules/tactics/term question."
    if "fixture" in t and ((" and " in t) or "both" in t or "two teams" in t):
        return "You may need tool_next_fixtures_multi."
    if "highlight" in t or "video" in t:
        return "You may need tool_highlights or tool_youtube_latest."
    if "elo" in t or "strength" in t:
        return "You may need tool_club_elo."
    if "odds" in t or "bookies" in t or "lines" in t:
        return "You may need tool_odds_snapshot."
    if "news" in t:
        return "You may need tool_news_top."
    return None

def answer_nl_question(text: str, context_summary: str = "") -> str:
    """Natural language in; football answer out (tools + LLM composition)."""
    text = (text or "").strip()
    if not text: 
        return "Ask me any football question (fixtures, live, players, lineups, news)."
    if not _in_scope(text):
        return "I'm a football-only assistant. Ask me about matches, players, lineups, standings, or news."
    
    try:
        hint = _pre_hint(text)
        FEWSHOT = [
            {"role":"system","content":"Style: friendly, concise, 1–3 short paragraphs max, use bullets only when helpful."},
            {"role":"user","content":"Explain xG quickly."},
            {"role":"assistant","content":"xG (expected goals) estimates how likely a shot is to become a goal. A tap-in might be 0.6–0.7 xG; a 30-yarder maybe 0.03. Over time, xG shows chance quality better than raw shots."},
        ]
        msgs = [{"role":"system","content": SYSTEM}, *FEWSHOT]
        if hint:
            msgs.append({"role":"system","content": hint})
        if HISTORY_ON and _looks_historical(text):
            msgs.append({"role":"system","content":"This looks historical. You MUST call a history tool (tool_history_lookup or tool_ucl_last_n_winners) before answering."})
        if context_summary:
            msgs.append({"role":"system","content": f"Context: {context_summary}"})
        if text.startswith("(Conversation summary context"):
            # Let the LLM know the first lines are context, not a user ask to analyze literally
            msgs.append({"role":"system","content":"The user message begins with a summary context for this chat. Use it to keep continuity and avoid repeating known info."})
        msgs.append({"role":"user","content": text})

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            tools=[{"type":"function","function": f} for f in FUNCTIONS],
            tool_choice="auto",
            temperature=0.3,
            max_tokens=220
        )

        needs_facts = _looks_factual(text)
        needs_history = _looks_historical(text)
        msg = r.choices[0].message

        # Force tool selection for factual queries
        if needs_facts and not getattr(msg, "tool_calls", None):
            # Determine specific tool needed
            if needs_history:
                tool_hint = "This is a historical query. You MUST use tool_history_lookup or tool_ucl_last_n_winners to get Wikipedia data before answering."
            else:
                tool_hint = "This is a factual query. You MUST call at least one appropriate tool before answering."
            
            msgs.insert(1, {"role":"system","content": tool_hint})
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=msgs,
                tools=[{"type":"function","function": f} for f in FUNCTIONS],
                tool_choice="auto",
                temperature=0.2,
                max_tokens=220,
                timeout=30
            )
            msg = r.choices[0].message

        # If model didn't call tools and it's a factual ask, we enforce a plan
        results_payloads = []
        sources = set()

        def _run_call(name, args):
            if LOG_TOOL_CALLS: 
                print(f"[arbiter] trying {name} with {args}")
            fn = NAME_TO_FUNC.get(name)
            res = fn(args or {}) if fn else {"ok": False, "message": "Unknown tool"}
            src = res.get("__source")
            if src: 
                sources.add(src)
            results_payloads.append(res)
            return res

        needs_facts = _looks_factual(text)
        if not getattr(msg, "tool_calls", None) and needs_facts:
            # 1) Planned cascade: try likely tools in order until one yields non-empty, valid data
            for tool_name in plan_tools(text):
                res = _run_call(tool_name, {})
                ok = (res.get("ok") is True) and (not _empty(res))
                valid, why = validate_recency(text, res)
                if ok and valid:
                    # Give this result back to the model to compose the final answer
                    tool_msgs = [{"role":"tool","tool_call_id":"arbiter", "name":tool_name, "content": json.dumps(res)}]
                    r2 = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role":"system","content": SYSTEM},{"role":"user","content": text}] + tool_msgs,
                        temperature=0.5, max_tokens=380
                    )
                    out = (r2.choices[0].message.content or "").strip()
                    if CITATIONS_ON and sources:
                        out += "\n\n(" + " • ".join(sorted(sources)) + ")"
                    return _safe(out)
            # 2) If still nothing & STRICT => don't guess
            if STRICT_FACTS:
                return "I can't verify that without external data. Try specifying team or timeframe."
            # 3) Non-strict fallback: return first tool's message
            first = results_payloads[0] if results_payloads else {}
            return (first.get("message") or "Couldn't fetch that yet.").strip()

        # Normal path: model DID call tools → execute them all as before
        tool_msgs = []
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                res = _run_call(name, args)
                tool_msgs.append({"role":"tool","tool_call_id": tc.id, "name": name, "content": json.dumps(res)})

            # Second pass for composition
            r2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content": SYSTEM},{"role":"user","content": text}, msg] + tool_msgs,
                temperature=0.5, max_tokens=380
            )
            out = (r2.choices[0].message.content or "").strip()
            
            # Apply AI banter override when appropriate
            banter_mode = _banter_intent(text)
            if banter_mode:
                try:
                    facts_list = _facts_from_toolpayload(results_payloads)
                    out = ai_banter(banter_mode, text, facts_list) or out
                except Exception:
                    pass
            
            if CITATIONS_ON and sources:
                out += "\n\n(" + " • ".join(sorted(sources)) + ")"
            return _safe(out)

        return _safe(msg.content or "Can you rephrase that?")
    
    except Exception as e:
        return f"I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
