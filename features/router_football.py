# features/router_football.py
import re
from nlp.resolve import resolve_team, resolve_comp, resolve_player
from providers.unified import fd_team_matches, fd_comp_table, fd_comp_scorers
from features.answers import fmt_table_top, fmt_recent_form, fmt_next_from_list, fmt_last_result
from utils.formatting import md_escape

# Pattern matching for different types of football questions
P_STANDINGS = re.compile(r"\b(table|standings|position|rank)\b", re.I)
P_FORM      = re.compile(r"\b(form|last\s*\d+|recent)\b", re.I)
P_NEXT      = re.compile(r"\b(next|upcoming|fixture|game)\b", re.I)
P_LAST      = re.compile(r"\b(last|previous|recent)\b.*\b(match|game|score|result)\b", re.I)
P_SCORERS   = re.compile(r"\b(top\s*scorers?|goalscorers?)\b", re.I)

def route_football(text: str):
    """Route football-related questions to appropriate API calls"""
    
    # 1) league table
    if P_STANDINGS.search(text):
        comp_id = resolve_comp(text)  # default LaLiga
        try:
            table_data = fd_comp_table(comp_id)
            if table_data:
                # Get competition name for title
                comp_name = "League Table"
                if "competition" in table_data:
                    comp_name = table_data["competition"].get("name", "League Table")
                return fmt_table_top(table_data, top=5, title=f"{comp_name} (Top 5)")
            else:
                return "Table data unavailable."
        except Exception:
            return "Table data unavailable."

    # 2) recent form / results
    if P_FORM.search(text):
        team_id = resolve_team(text)  # default Real Madrid
        if team_id:
            try:
                ms = fd_team_matches(team_id, status="FINISHED", limit=10)
                if ms:
                    return fmt_recent_form(ms, k=5)
                else:
                    return "No recent results found."
            except Exception:
                return "Recent results unavailable."
        else:
            return "Please specify a team for form information."

    # 3) next fixture
    if P_NEXT.search(text):
        team_id = resolve_team(text)  # default Real Madrid
        if team_id:
            try:
                ms = fd_team_matches(team_id, status=None, limit=20)
                if ms:
                    return fmt_next_from_list(ms)
                else:
                    return "No upcoming fixtures found."
            except Exception:
                return "Next fixture unavailable."
        else:
            return "Please specify a team for fixture information."

    # 4) last match (single line score)
    if P_LAST.search(text):
        team_id = resolve_team(text)
        if team_id:
            try:
                ms = fd_team_matches(team_id, status="FINISHED", limit=1)
                if ms:
                    return fmt_last_result(ms[0])
                else:
                    return "No recent match found."
            except Exception:
                return "Last match data unavailable."
        else:
            return "Please specify a team for match information."

    # 5) top scorers by competition (default LaLiga)
    if P_SCORERS.search(text):
        comp_id = resolve_comp(text)
        try:
            js = fd_comp_scorers(comp_id, limit=10)
            if js and "scorers" in js:
                items = js.get("scorers", [])[:5]
                if items:
                    lines = ["*Top Scorers*"]
                    for s in items:
                        lines.append(f"{md_escape(s['player']['name'])} — {s['numberOfGoals']}g ({md_escape(s['team']['name'])})")
                    return "\n".join(lines)
                else:
                    return "No scorers data available."
            else:
                return "Scorers data unavailable."
        except Exception:
            return "Scorers data unavailable."

    return None  # let other routers handle
