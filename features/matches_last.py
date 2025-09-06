from utils.timeutil import fmt_abs
from utils.formatting import md_escape

def last_match_handler(fd) -> str:
    data = fd._get(f"/teams/{fd.team_id}/matches")
    finished = [m for m in data.get("matches", []) if m.get("status") == "FINISHED"]
    if not finished:
        return "No recent match results found."
    last = sorted(finished, key=lambda x: x["utcDate"], reverse=True)[0]
    ft = (last.get("score", {}) or {}).get("fullTime", {}) or {}
    hs, as_ = ft.get("home", 0), ft.get("away", 0)
    return (
        f"{fmt_abs(last['utcDate'])}\n"
        f"{md_escape(last['homeTeam']['name'])} {hs} - {as_} {md_escape(last['awayTeam']['name'])}"
    )
