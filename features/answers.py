from utils.formatting import md_escape
from utils.timeutil import fmt_abs, now_utc
from datetime import datetime

def fmt_table_top(json_obj, top=5, title="League Table (Top 5)"):
    tables = json_obj.get("standings", [])
    if not tables:
        return "Table unavailable."
    table = tables[0].get("table", [])[:top]
    lines = [f"*{title}*"]
    for row in table:
        lines.append(f"{row['position']}. {md_escape(row['team']['name'])}  {row['points']} pts")
    return "\n".join(lines)

def fmt_last_result(match) -> str:
    ft = (match.get("score", {}) or {}).get("fullTime", {}) or {}
    hs, as_ = ft.get("home", 0), ft.get("away", 0)
    return f"{fmt_abs(match['utcDate'])}\n{md_escape(match['homeTeam']['name'])} {hs}-{as_} {md_escape(match['awayTeam']['name'])}"

def fmt_recent_form(matches, k=5):
    if not matches:
        return "No recent matches."
    return "*Recent Results*\n" + "\n".join(fmt_last_result(m) for m in matches[:k])

def fmt_next_from_list(matches):
    future = [m for m in matches if m.get("status") in {"SCHEDULED", "TIMED"}]
    future.sort(key=lambda x: x["utcDate"])
    if not future:
        return "No upcoming fixtures found."
    m = future[0]
    return f"{fmt_abs(m['utcDate'])} • {md_escape(m['homeTeam']['name'])} vs {md_escape(m['awayTeam']['name'])}"

def fmt_table(table_data):
    """Format league table data"""
    return fmt_table_top(table_data, top=5, title="LaLiga Table (Top 5)")

def fmt_form(matches, k=5):
    """Format recent form data"""
    return fmt_recent_form(matches, k)

def fmt_scorers(scorers_data):
    """Format top scorers data"""
    items = scorers_data.get("scorers", [])[:5]
    if not items:
        return "No scorers data available."
    lines = ["*Top Scorers*"]
    for s in items:
        lines.append(f"{md_escape(s['player']['name'])} — {s['numberOfGoals']}g ({md_escape(s['team']['name'])})")
    return "\n".join(lines)

def fmt_squad(squad_data):
    """Format squad data"""
    if not squad_data:
        return "Squad data unavailable."
    return "Squad information temporarily unavailable."

def fmt_injuries(injuries_data):
    """Format injuries data"""
    if not injuries_data:
        return "No injury information available."
    return "Injury information temporarily unavailable."
