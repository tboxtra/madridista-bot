from utils.timeutil import fmt_abs
from utils.formatting import md_escape

def matches_handler(fd) -> str:
    ups = fd.upcoming_matches(days_ahead=2)
    if ups:
        lines = ["*Upcoming (next 48h):*"]
        for m in ups[:5]:
            lines.append(f"{fmt_abs(m['utcDate'])} • {md_escape(m['homeTeam']['name'])} vs {md_escape(m['awayTeam']['name'])}")
        return "\n".join(lines)
    nxt = fd.next_fixture()
    if nxt:
        return f"No fixtures in 48h.\n*Next:* {fmt_abs(nxt['utcDate'])} • {md_escape(nxt['homeTeam']['name'])} vs {md_escape(nxt['awayTeam']['name'])}"
    return "No fixtures in the next week."
