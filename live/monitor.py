import os
from typing import Optional
from services.football_api import FootballAPIService
from telegram import Update
from telegram.ext import ContextTypes

POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))

class LiveState:
    def __init__(self):
        self.active_match_id: Optional[int] = None
        self.last_home: Optional[int] = None
        self.last_away: Optional[int] = None

STATE = LiveState()

def format_live_line(m) -> str:
    home = m["home_team"]
    away = m["away_team"]
    comp = m.get("competition", "")
    h = m.get("home_score", 0)
    a = m.get("away_score", 0)
    return f"**LIVE**: {home} {h} – {a} {away}\n{comp}"

async def monitor_tick(context) -> None:
    """Runs on a schedule; posts to all subscribed chats when score changes."""
    bot = context.application.bot
    subs: set[int] = context.application.bot_data.get("subs", set())

    if not subs:
        return  # nobody subscribed

    # Use our existing FootballAPIService
    football_api = FootballAPIService()
    
    # Get live matches
    matches = await football_api.get_real_madrid_matches(limit=10)
    live_matches = [m for m in matches if m.get('status') == 'LIVE']
    
    if not live_matches:
        # reset state when no live match
        STATE.active_match_id = None
        STATE.last_home = STATE.last_away = None
        return

    # Get the first live match
    live = live_matches[0]
    
    # Identify match & score
    match_id = live.get('id') or hash(str(live.get('date', '')) + live.get('home_team', ''))
    h = live.get('home_score', 0)
    a = live.get('away_score', 0)

    # First time we see this match or score change?
    changed = (
        STATE.active_match_id != match_id or
        STATE.last_home != h or
        STATE.last_away != a
    )

    if not changed:
        return

    # Update state
    STATE.active_match_id = match_id
    STATE.last_home = h
    STATE.last_away = a

    # Compose message
    msg = format_live_line(live)

    # Broadcast to all subscribers
    for chat_id in subs:
        try:
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
        except Exception:
            # ignore individual failures so others still get updates
            pass
