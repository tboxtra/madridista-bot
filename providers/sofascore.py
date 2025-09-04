import os, time, random, json, requests
from typing import Optional, Dict, Any, List

BASE = "https://api.sofascore.com/api/v1"
TEAM_ID = int(os.getenv("SOFA_TEAM_ID", "2817"))  # Real Madrid by default
UA = os.getenv("SOFA_USER_AGENT", "Mozilla/5.0 MadridistaBot/1.0")

S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "application/json"})
S_TIMEOUT = 12

def _get_json(path: str, tries=2, base_pause=0.6) -> dict:
    url = f"{BASE}{path}"
    for i in range(tries):
        try:
            r = S.get(url, timeout=S_TIMEOUT)
            if r.status_code in (429,) or 500 <= r.status_code < 600:
                if i < tries-1:
                    time.sleep(base_pause + random.random()*0.5)
                    continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, json.JSONDecodeError):
            if i < tries-1:
                time.sleep(base_pause + random.random()*0.5)
                continue
    return {}  # soft-fail

def _dig(d, *path):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur: return None
        cur = cur[k]
    return cur

def _minute_tuple(inc_time: dict):
    if not inc_time: return (0, 0)
    m = inc_time.get("minute")
    ex = inc_time.get("extra") or 0
    if m is None: return (0, 0)
    return (int(m), int(ex))

def minute_display(inc_time: dict) -> Optional[str]:
    if not inc_time: return None
    m = inc_time.get("minute")
    if m is None: return None
    ex = inc_time.get("extra")
    core = f"{m}+{ex}" if ex else f"{m}"
    return core + "′"

def scorer_text(inc: dict) -> str:
    for path in (("player","name"), ("goal","scorer","name"), ("playerIn","name")):
        v = _dig(inc, *path)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "Goal"

def _map_event(e: dict) -> Dict[str, Any]:
    home = _dig(e, "homeTeam", "name") or "Home"
    away = _dig(e, "awayTeam", "name") or "Away"
    comp = _dig(e, "tournament", "name") or _dig(e, "season", "name") or ""
    hs = _dig(e, "homeScore", "current") or 0
    as_ = _dig(e, "awayScore", "current") or 0
    minute = _dig(e, "time", "minute")
    return {
        "id": e.get("id"),
        "homeName": home,
        "awayName": away,
        "homeScore": hs,
        "awayScore": as_,
        "minute": minute,
        "competition": comp
    }

class SofaScoreProvider:
    def __init__(self, team_id: Optional[int] = None):
        self.team_id = int(team_id or TEAM_ID)

    def get_team_live_event(self) -> Optional[Dict[str, Any]]:
        data = _get_json("/sport/football/events/live")
        for e in data.get("events", []) or []:
            hid = _dig(e, "homeTeam", "id")
            aid = _dig(e, "awayTeam", "id")
            if hid == self.team_id or aid == self.team_id:
                return _map_event(e)
        return None

    def get_event_incidents(self, event_id) -> List[Dict[str, Any]]:
        data = _get_json(f"/event/{event_id}/incidents")
        info = _get_json(f"/event/{event_id}")
        e = info.get("event", {}) if isinstance(info, dict) else {}
        home_id = _dig(e, "homeTeam", "id")
        away_id = _dig(e, "awayTeam", "id")
        incs = data.get("incidents", []) or []
        out = []
        for inc in incs:
            itype = inc.get("type")
            tside = None
            tid = _dig(inc, "team", "id")
            if home_id and tid == home_id: tside = "home"
            elif away_id and tid == away_id: tside = "away"
            mdisp = minute_display(_dig(inc, "time") or {})
            text = ""
            if itype == "goal":
                text = f"{scorer_text(inc)} scores"
            elif itype == "yellow-card":
                text = f"Yellow card: {scorer_text(inc)}"
            elif itype == "red-card":
                text = f"RED card: {scorer_text(inc)}"
            elif itype == "substitution":
                pin = _dig(inc, "playerIn", "name") or "On"
                pout = _dig(inc, "playerOut", "name") or "Off"
                text = f"Substitution: {pin} for {pout}"
            elif itype == "period":
                text = inc.get("text") or "Period"
            elif itype == "var":
                text = "VAR check"
            else:
                text = inc.get("text") or (itype or "Event")

            base_m, base_ex = _minute_tuple(_dig(inc, "time") or {})
            inc_id = inc.get("id") or f"{itype}-{base_m}+{base_ex}-{tid}-{int(time.time()*1000)%100000}"
            out.append({
                "id": inc_id,
                "type": itype,
                "minute": mdisp,
                "minute_sort": (base_m, base_ex),
                "team": tside,
                "text": text
            })
        out.sort(key=lambda x: (x["minute_sort"][0], x["minute_sort"][1]))
        return out

    def short_event_line(self, ev: Dict[str, Any]) -> str:
        from utils.formatting import md_escape
        mn = f"{int(ev['minute'])}′ " if ev.get("minute") is not None else ""
        return f"*LIVE* {mn}\n{md_escape(ev['homeName'])} {ev['homeScore']} – {ev['awayScore']} {md_escape(ev['awayName'])}\n{md_escape(ev.get('competition',''))}"

    # New helper methods for extended functionality
    def team_squad(self, team_id: Optional[int] = None):
        tid = int(team_id or self.team_id)
        return _get_json(f"/team/{tid}/players")  # includes positions, injuries sometimes

    def event_lineups(self, event_id):
        return _get_json(f"/event/{event_id}/lineups")  # starting XI, bench

    def team_injuries(self, team_id: Optional[int] = None):
        tid = int(team_id or self.team_id)
        return _get_json(f"/team/{tid}/injuries")

    def h2h(self, team_a_id: int, team_b_id: int):
        return _get_json(f"/team/{team_a_id}/unique-tournament/season/0/opponent/{team_b_id}/matches")  # SofaScore H2H variant
