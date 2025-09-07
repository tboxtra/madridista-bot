import os
import requests
from datetime import datetime, timedelta, timezone

FD_BASE = "https://api.football-data.org/v4"
FD_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
S = requests.Session()
if FD_KEY:
    S.headers.update({"X-Auth-Token": FD_KEY})

def _today_iso():
    # Use UTC; Railway TZ is set to Africa/Lagos for formatting elsewhere
    return datetime.now(timezone.utc).date()

def fd_team_matches(team_id: int, status: str = None, limit=20, window_days: int = 120):
    """
    Get team matches with configurable date window.
    Football-Data supports dateFrom/dateTo filtering.
    For historical searches, use larger window_days values.
    """
    today = _today_iso()
    date_from = (today - timedelta(days=window_days)).isoformat()
    date_to = (today + timedelta(days=30)).isoformat()  # a week into the future for 'next'
    params = {"dateFrom": date_from, "dateTo": date_to, "limit": 200}
    r = S.get(f"{FD_BASE}/teams/{team_id}/matches", params=params, timeout=20)
    r.raise_for_status()
    ms = r.json().get("matches", [])
    if status:
        ms = [m for m in ms if m.get("status") == status]
    # sort DESC by utcDate (latest first)
    ms.sort(key=lambda x: x["utcDate"], reverse=True)
    return ms[:limit]

def fd_team_matches_historical(team_id: int, status: str = None, limit=50, window_days: int = 3650):
    """
    Get historical team matches with extended date window (default 10 years).
    Use this for comprehensive historical searches.
    """
    return fd_team_matches(team_id, status, limit, window_days)

def fd_comp_table(comp_id: int):
    r = S.get(f"{FD_BASE}/competitions/{comp_id}/standings", timeout=20)
    r.raise_for_status()
    return r.json()

def fd_comp_scorers(comp_id: int, limit=10):
    r = S.get(f"{FD_BASE}/competitions/{comp_id}/scorers", params={"limit": limit}, timeout=20)
    r.raise_for_status()
    return r.json()
