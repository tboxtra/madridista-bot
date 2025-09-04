# providers/fd_wrap.py
import os, requests
BASE = "https://api.football-data.org/v4"
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
HEADERS = {"X-Auth-Token": API_KEY} if API_KEY else {}

TEAM_IDS = {"Real Madrid": 86}
COMP_IDS = { "laliga": 2014, "ucl": 2001, "copa-del-rey": 2010 }

S = requests.Session(); S.headers.update(HEADERS)

def _get(path, params=None):
    r = S.get(f"{BASE}{path}", params=params or {}, timeout=20)
    r.raise_for_status()
    return r.json()

def league_table(comp_key="laliga"):
    comp_id = COMP_IDS[comp_key]
    return _get(f"/competitions/{comp_id}/standings")

def team_matches(team_name="Real Madrid", status=None, limit=20):
    tid = TEAM_IDS.get(team_name, 86)
    data = _get(f"/teams/{tid}/matches")
    ms = data.get("matches", [])
    if status:
        ms = [m for m in ms if m.get("status")==status]
    return sorted(ms, key=lambda x: x["utcDate"], reverse=True)[:limit]

def scorers(comp_key="laliga", limit=10):
    comp_id = COMP_IDS[comp_key]
    return _get(f"/competitions/{comp_id}/scorers", params={"limit": limit})
