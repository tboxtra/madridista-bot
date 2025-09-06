import re
from nlp.resolve import resolve_team, resolve_comp
from providers.unified import fd_team_matches, fd_comp_table, fd_comp_scorers
from features.answers import fmt_table_top, fmt_recent_form, fmt_next_from_list, fmt_last_result

P_STANDINGS = re.compile(r"\b(table|standings|position|rank)\b", re.I)
P_FORM = re.compile(r"\b(form|last\s*\d+|recent)\b", re.I)
P_NEXT = re.compile(r"\b(next|upcoming|fixture|game)\b", re.I)
P_LAST = re.compile(r"\b(last|previous|recent)\b.*\b(match|game|score|result)\b", re.I)
P_SCORERS = re.compile(r"\b(top\s*scorers?|goalscorers?)\b", re.I)

def route_football(text: str):
    if P_STANDINGS.search(text):
        cid = resolve_comp(text)
        try:
            return fmt_table_top(fd_comp_table(cid), top=5, title="League Table (Top 5)")
        except Exception:
            return "Table data unavailable."
    
    if P_FORM.search(text):
        tid = resolve_team(text)
        try:
            return fmt_recent_form(fd_team_matches(tid, status="FINISHED", limit=10), k=5)
        except Exception:
            return "Recent results unavailable."
    
    if P_NEXT.search(text):
        tid = resolve_team(text)
        try:
            return fmt_next_from_list(fd_team_matches(tid, status=None, limit=20))
        except Exception:
            return "Next fixture unavailable."
    
    if P_LAST.search(text):
        tid = resolve_team(text)
        try:
            ms = fd_team_matches(tid, status="FINISHED", limit=1)
            return fmt_last_result(ms[0]) if ms else "No recent match found."
        except Exception:
            return "Last match data unavailable."
    
    if P_SCORERS.search(text):
        cid = resolve_comp(text)
        try:
            js = fd_comp_scorers(cid, limit=10)
            items = js.get("scorers", [])[:5]
            if not items:
                return "No scorers data."
            from utils.formatting import md_escape
            lines = ["*Top Scorers*"]
            for s in items:
                lines.append(f"{md_escape(s['player']['name'])} — {s['numberOfGoals']}g ({md_escape(s['team']['name'])})")
            return "\n".join(lines)
        except Exception:
            return "Scorers data unavailable."
    
    return None
