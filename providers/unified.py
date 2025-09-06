import os
import requests

FD_BASE = "https://api.football-data.org/v4"
FD_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
S = requests.Session()
if FD_KEY:
    S.headers.update({"X-Auth-Token": FD_KEY})

def fd_team_matches(team_id: int, status: str = None, limit=20):
    r = S.get(f"{FD_BASE}/teams/{team_id}/matches", timeout=20)
    r.raise_for_status()
    ms = r.json().get("matches", [])
    if status:
        ms = [m for m in ms if m.get("status") == status]
    return sorted(ms, key=lambda x: x["utcDate"], reverse=True)[:limit]

def fd_comp_table(comp_id: int):
    r = S.get(f"{FD_BASE}/competitions/{comp_id}/standings", timeout=20)
    r.raise_for_status()
    return r.json()

def fd_comp_scorers(comp_id: int, limit=10):
    r = S.get(f"{FD_BASE}/competitions/{comp_id}/scorers", params={"limit": limit}, timeout=20)
    r.raise_for_status()
    return r.json()
