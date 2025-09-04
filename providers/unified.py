# providers/unified.py
import requests, os
from utils.timeutil import window_filter, parse_iso_utc, now_utc

FD_BASE = "https://api.football-data.org/v4"
FD_KEY  = os.getenv("FOOTBALL_DATA_API_KEY")
FD_S = requests.Session()
if FD_KEY: 
    FD_S.headers.update({"X-Auth-Token": FD_KEY})

def fd_team_matches(team_id: int, status=None, limit=20):
    """Get matches for any team with optional status filter"""
    try:
        r = FD_S.get(f"{FD_BASE}/teams/{team_id}/matches", timeout=20)
        r.raise_for_status()
        ms = r.json().get("matches", [])
        if status: 
            ms = [m for m in ms if m.get("status")==status]
        return sorted(ms, key=lambda x: x["utcDate"], reverse=True)[:limit]
    except Exception:
        return []

def fd_comp_table(comp_id: int):
    """Get standings table for any competition"""
    try:
        r = FD_S.get(f"{FD_BASE}/competitions/{comp_id}/standings", timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def fd_comp_scorers(comp_id: int, limit=10):
    """Get top scorers for any competition"""
    try:
        r = FD_S.get(f"{FD_BASE}/competitions/{comp_id}/scorers", 
                     params={"limit": limit}, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def fd_team_info(team_id: int):
    """Get basic team information"""
    try:
        r = FD_S.get(f"{FD_BASE}/teams/{team_id}", timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def fd_comp_info(comp_id: int):
    """Get basic competition information"""
    try:
        r = FD_S.get(f"{FD_BASE}/competitions/{comp_id}", timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}
