from utils.timeutil import fmt_abs
from utils.formatting import md_escape

def matches_handler(fd) -> str:
    # Always return a single next-fixture line, no leading notices
    ups = fd.upcoming_matches(days_ahead=2)
    if ups:
        m = ups[0]
        return f"{fmt_abs(m['utcDate'])} • {md_escape(m['homeTeam']['name'])} vs {md_escape(m['awayTeam']['name'])}"
    nxt = fd.next_fixture()
    if nxt:
        return f"{fmt_abs(nxt['utcDate'])} • {md_escape(nxt['homeTeam']['name'])} vs {md_escape(nxt['awayTeam']['name'])}"
    return "No upcoming fixtures found."

