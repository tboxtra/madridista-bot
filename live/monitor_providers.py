import os
from typing import Optional, Dict, Any, Union
from utils.dedupe import DeDupe

PROVIDER_NAME = os.getenv("LIVE_PROVIDER", "sofascore").lower()
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "25"))

# Lazy import based on env
if PROVIDER_NAME == "sofascore":
    from providers.sofascore import SofaScoreProvider as Provider
elif PROVIDER_NAME == "livescore":
    from providers.livescore_rapid import LiveScoreProvider as Provider  # you add this when ready
else:
    from providers.sofascore import SofaScoreProvider as Provider

class LiveState:
    def __init__(self):
        self.event_id = None
        self.homeScore = None
        self.awayScore = None
        self.dedupe = DeDupe(maxlen=400)  # remember recent incidents

STATE = LiveState()
PROV = Provider()

def _team_tag(team):
    return "🤍" if team == "home" else ("💙" if team == "away" else "")

def _format_incident_line(inc):
    minute = f"{inc['minute']}' " if inc.get("minute") is not None else ""
    tag = _team_tag(inc.get("team"))
    return f"{minute}{tag} {inc['text']}".strip()

async def monitor_tick(context):
    bot = context.application.bot
    subs: set = context.application.bot_data.get("subs", set())
    if not subs:
        return

    # 1) Is there a live event for our team?
    ev = PROV.get_team_live_event()
    if not ev:
        # reset state if no live
        STATE.event_id = None
        STATE.homeScore = STATE.awayScore = None
        return

    # 2) If new match or score changed, announce scoreline
    score_changed = (
        STATE.event_id != str(ev["id"]) or
        STATE.homeScore != ev["homeScore"] or
        STATE.awayScore != ev["awayScore"]
    )
    if score_changed:
        STATE.event_id = str(ev["id"])
        STATE.homeScore = ev["homeScore"]
        STATE.awayScore = ev["awayScore"]
        headline = PROV.short_event_line(ev)
        for chat_id in subs:
            try:
                await bot.send_message(chat_id=chat_id, text=headline, parse_mode="Markdown")
            except Exception:
                pass

    # 3) Pull incidents and send only new ones
    incs = PROV.get_event_incidents(STATE.event_id)
    for inc in incs[-5:]:  # last few only
        key = f"{STATE.event_id}:{inc['id']}"
        if not STATE.dedupe.is_new(key):
            continue
        # only push high-signal ones (you can expand)
        if inc["type"] in ("goal", "yellow-card", "red-card", "substitution", "var", "period"):
            text = _format_incident_line(inc)
            for chat_id in subs:
                try:
                    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
                except Exception:
                    pass
