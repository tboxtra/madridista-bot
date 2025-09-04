from asyncio import Lock
import os
from typing import Optional
from utils.formatting import md_escape
from utils.freshness import is_fresh, source_stamp
from utils.timeutil import now_utc
from utils.dedupe import DeDupe

PROVIDER_NAME = os.getenv("LIVE_PROVIDER", "sofascore").lower()
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "25"))

if PROVIDER_NAME == "sofascore":
    from providers.sofascore import SofaScoreProvider as Provider, minute_display
else:
    from providers.sofascore import SofaScoreProvider as Provider, minute_display

JOB_LOCK = Lock()
PROV = Provider()

class LiveState:
    def __init__(self):
        self.event_id: Optional[str] = None
        self.homeScore: Optional[int] = None
        self.awayScore: Optional[int] = None
        self.last_scoreline: Optional[str] = None
        self.dedupe = DeDupe(maxlen=400)

STATE = LiveState()

async def monitor_tick(context):
    if JOB_LOCK.locked(): return
    async with JOB_LOCK:
        await _impl(context)

async def _impl(context):
    bot = context.application.bot
    subs: set[int] = context.application.bot_data.get("subs", set())
    if not subs: return

    ev = PROV.get_team_live_event()
    pulled_at = now_utc()
    context.application.bot_data["LIVE_LAST_PULL_UTC"] = pulled_at

    if not ev:
        STATE.event_id = STATE.last_scoreline = None
        STATE.homeScore = STATE.awayScore = None
        STATE.dedupe = DeDupe(maxlen=400)
        return

    if not is_fresh(pulled_at, 120):
        msg = f"Updating live data… ({source_stamp('SofaScore')})"
        for chat_id in subs:
            try: await bot.send_message(chat_id=chat_id, text=msg)
            except: pass
        return

    scoreline = f"{ev['homeScore']}-{ev['awayScore']}"
    if STATE.event_id != str(ev["id"]) or STATE.last_scoreline != scoreline:
        STATE.event_id = str(ev["id"])
        STATE.homeScore, STATE.awayScore = ev["homeScore"], ev["awayScore"]
        STATE.last_scoreline = scoreline
        headline = PROV.short_event_line(ev)
        for chat_id in subs:
            try: await bot.send_message(chat_id=chat_id, text=headline, parse_mode="Markdown")
            except: pass

    incs = PROV.get_event_incidents(STATE.event_id)
    for inc in incs[-6:]:
        key = f"{STATE.event_id}:{inc['id']}"
        if not STATE.dedupe.is_new(key): continue
        if inc["type"] in ("goal","yellow-card","red-card","substitution","var","period"):
            minute_txt = f"{inc['minute']} " if inc.get("minute") else ""
            text = f"{minute_txt}{md_escape(inc['text'])}"
            for chat_id in subs:
                try: await bot.send_message(chat_id=chat_id, text=text)
                except: pass
