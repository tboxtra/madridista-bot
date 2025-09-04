from utils.freshness import is_fresh, source_stamp
from utils.timeutil import now_utc
from utils.formatting import md_escape
from providers.sofascore import SofaScoreProvider

PROV = SofaScoreProvider()

def live_handler() -> str:
    ev = PROV.get_team_live_event()
    pulled_at = now_utc()
    if not ev:
        return "No live match right now."
    if not is_fresh(pulled_at, 120):
        return f"Updating live data… ({source_stamp('SofaScore')})"
    mn = f"{int(ev['minute'])}′ " if ev.get("minute") is not None else ""
    return (
        f"*LIVE* {mn}\n"
        f"{md_escape(ev['homeName'])} {ev['homeScore']} – {ev['awayScore']} {md_escape(ev['awayName'])}\n"
        f"{md_escape(ev.get('competition',''))}  ({source_stamp('SofaScore')})"
    )
