import os, requests
from typing import List, Dict, Any, Optional
from utils.timeutil import parse_iso_utc, now_utc, window_filter

BASE = "https://api.football-data.org/v4"
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
HEADERS = {"X-Auth-Token": API_KEY} if API_KEY else {}
TEAM_IDS = {"Real Madrid": 86}

class FootballData:
    def __init__(self):
        if not API_KEY:
            raise RuntimeError("Missing FOOTBALL_DATA_API_KEY")
        self.s = requests.Session()
        self.s.headers.update(HEADERS)
        self.team_name = os.getenv("TEAM_NAME", "Real Madrid")
        self.team_id = TEAM_IDS.get(self.team_name, 86)

    def _get(self, path: str, params=None):
        r = self.s.get(f"{BASE}{path}", params=params or {}, timeout=25)
        r.raise_for_status()
        return r.json()

    def upcoming_matches(self, days_ahead: int = 2) -> List[Dict[str, Any]]:
        data = self._get(f"/teams/{self.team_id}/matches")
        return window_filter(data.get("matches", []), days=days_ahead, max_days_cap=7)

    def next_fixture(self) -> Optional[Dict[str, Any]]:
        data = self._get(f"/teams/{self.team_id}/matches")
        future = []
        for m in data.get("matches", []):
            if m.get("status") not in {"SCHEDULED","TIMED"}: continue
            try: dt = parse_iso_utc(m["utcDate"])
            except Exception: continue
            if dt > now_utc():
                future.append(m)
        future.sort(key=lambda x: x["utcDate"])
        if future:
            first_dt = parse_iso_utc(future[0]["utcDate"])
            if (first_dt - now_utc()).days <= 30:
                return future[0]
        return None

