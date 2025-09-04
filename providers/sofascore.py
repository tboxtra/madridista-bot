import os, time, requests
from typing import Optional, Dict, Any, List

BASE = "https://api.sofascore.com/api/v1"
TEAM_ID = int(os.getenv("SOFA_TEAM_ID", "2817"))  # Real Madrid default
UA = os.getenv("SOFA_USER_AGENT", "Mozilla/5.0 (compatible; Bot/1.0)")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "application/json"})

def _get(path: str) -> dict:
    r = S.get(f"{BASE}{path}", timeout=20)
    r.raise_for_status()
    return r.json()

def _map_event(e: dict) -> Dict[str, Any]:
    # SofaScore event object → normalized
    home = e.get("homeTeam", {}).get("name", "Home")
    away = e.get("awayTeam", {}).get("name", "Away")
    comp = e.get("tournament", {}).get("name", "") or e.get("season", {}).get("name", "")
    score = e.get("homeScore", {}).get("current", 0), e.get("awayScore", {}).get("current", 0)
    minute = e.get("time", {}).get("minute")  # can be None
    return {
        "id": e.get("id"),
        "homeName": home,
        "awayName": away,
        "homeScore": score[0],
        "awayScore": score[1],
        "minute": minute,
        "competition": comp or "",
    }

def _map_incident(inc: dict, home_id: int | None, away_id: int | None) -> Dict[str, Any]:
    # Common types:
    # type: 'goal', 'yellow-card', 'red-card', 'substitution', 'var', 'period' etc.
    itype = inc.get("type")
    minute = inc.get("time", {}).get("minute")
    team_side = None
    tid = inc.get("team", {}).get("id")
    if home_id and tid == home_id:
        team_side = "home"
    elif away_id and tid == away_id:
        team_side = "away"

    desc = []
    # player text
    for key in ("player", "playerIn", "playerOut"):
        p = inc.get(key, {})
        if p and p.get("name"):
            tag = "in" if key == "playerIn" else ("out" if key == "playerOut" else "")
            desc.append(f"{p['name']}{' (in)' if tag=='in' else ''}{' (out)' if tag=='out' else ''}")

    # build human text
    human = ""
    if itype == "goal":
        who = desc[0] if desc else "Goal"
        human = f"{who} scores"
    elif itype == "yellow-card":
        who = desc[0] if desc else "Yellow card"
        human = f"Yellow card: {who}"
    elif itype == "red-card":
        who = desc[0] if desc else "Red card"
        human = f"RED card: {who}"
    elif itype == "substitution":
        human = "Substitution: " + (", ".join(desc) if desc else "")
    elif itype == "var":
        human = "VAR check"
    elif itype == "period":
        #  'HT', 'FT', etc.
        period = inc.get("text", "Period")
        human = period
    else:
        human = inc.get("text") or itype or "Event"

    # a stable ID if sofa doesn't provide one
    inc_id = inc.get("id") or f"{itype}-{minute}-{tid}-{int(time.time()*1000)%100000}"

    return {
        "id": inc_id,
        "type": itype,
        "minute": minute,
        "team": team_side,
        "text": human
    }

class SofaScoreProvider:
    def __init__(self, team_id: int | None = None):
        self.team_id = int(team_id or TEAM_ID)

    def get_team_live_event(self) -> Optional[Dict[str, Any]]:
        # Option A: global live list, filter by team id
        # /sport/football/events/live
        try:
            data = _get("/sport/football/events/live")
            for e in data.get("events", []):
                home_id = e.get("homeTeam", {}).get("id")
                away_id = e.get("awayTeam", {}).get("id")
                if home_id == self.team_id or away_id == self.team_id:
                    return _map_event(e)
            return None
        except Exception as e:
            print(f"SofaScore live event error: {e}")
            return None

    def get_event_incidents(self, event_id) -> List[Dict[str, Any]]:
        # /event/{id}/incidents
        try:
            data = _get(f"/event/{event_id}/incidents")
            # also need team ids for side mapping
            info = _get(f"/event/{event_id}")
            e = info.get("event", {})
            home_id = e.get("homeTeam", {}).get("id")
            away_id = e.get("awayTeam", {}).get("id")
            incidents = data.get("incidents", []) or []
            out = []
            for inc in incidents:
                out.append(_map_incident(inc, home_id, away_id))
            # sort by minute (None last)
            out.sort(key=lambda x: (x["minute"] is None, x["minute"] if x["minute"] is not None else 9999))
            return out
        except Exception as e:
            print(f"SofaScore incidents error: {e}")
            return []

    def short_event_line(self, event: Dict[str, Any]) -> str:
        minute = f"{event['minute']}'" if event.get("minute") else ""
        return f"**LIVE** {minute}\n{event['homeName']} {event['homeScore']} – {event['awayScore']} {event['awayName']}\n{event['competition']}"
