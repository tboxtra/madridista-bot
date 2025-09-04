# features/answers.py
from utils.formatting import md_escape
from utils.timeutil import fmt_abs

def fmt_table(fd_table_json):
    """Return top 5 lines of LaLiga table."""
    tables = fd_table_json.get("standings", [])
    if not tables: return "Table unavailable."
    table = tables[0].get("table", [])[:5]
    lines = ["*LaLiga Table (Top 5)*"]
    for row in table:
        lines.append(f"{row['position']}. {md_escape(row['team']['name'])}  {row['points']} pts")
    return "\n".join(lines)

def fmt_form(matches, k=5):
    if not matches: return "No recent matches."
    lines = ["*Recent Form (last 5)*"]
    for m in matches[:k]:
        home = md_escape(m['homeTeam']['name']); away = md_escape(m['awayTeam']['name'])
        ft = m.get("score",{}).get("fullTime",{}) or {}
        hs, as_ = ft.get("home",0), ft.get("away",0)
        lines.append(f"{fmt_abs(m['utcDate'])} • {home} {hs}-{as_} {away}")
    return "\n".join(lines)

def fmt_scorers(fd_scorers_json):
    items = fd_scorers_json.get("scorers", [])[:5]
    if not items: return "No scorers data."
    lines = ["*Top Scorers*"]
    for s in items:
        lines.append(f"{md_escape(s['player']['name'])} — {s['numberOfGoals']}g ({md_escape(s['team']['name'])})")
    return "\n".join(lines)

def fmt_squad(sofa_squad_json, pos=None):
    players = (sofa_squad_json.get("players") or []) if isinstance(sofa_squad_json, dict) else []
    if not players: return "No squad data."
    if pos: players = [p for p in players if (p.get("position") or "").lower().startswith(pos.lower())]
    lines = [f"*Squad*{' — ' + pos.title() if pos else ''}"]
    for p in players[:20]:
        nm = p.get("name") or p.get("shortName") or "Player"
        position = p.get("position") or ""
        lines.append(f"• {md_escape(nm)} ({position})")
    return "\n".join(lines)

def fmt_injuries(sofa_inj_json):
    items = sofa_inj_json.get("players") or []
    if not items: return "No listed injuries."
    lines = ["*Injuries / Unavailable*"]
    for p in items[:12]:
        nm = p.get("name") or "Player"
        reason = (p.get("injury") or {}).get("type") or p.get("status") or "Unavailable"
        lines.append(f"• {md_escape(nm)} — {md_escape(reason)}")
    return "\n".join(lines)
