# providers/api_football.py
import os, datetime as dt
from utils.http import get

BASE = "https://v3.football.api-sports.io"
KEY  = os.getenv("API_FOOTBALL_KEY","")

def _hdr():
    return {"x-apisports-key": KEY}

def fixtures_next(team_id, days_ahead=30, max_items=5):
    dfrom = dt.date.today()
    dto   = dfrom + dt.timedelta(days=days_ahead)
    r = get(f"{BASE}/fixtures", headers=_hdr(), params={
        "team": team_id, "from": dfrom.isoformat(), "to": dto.isoformat()
    })
    data = r.json().get("response", [])
    data.sort(key=lambda x: x.get("fixture",{}).get("date",""))
    return data[:max_items]

def fixtures_last(team_id, max_items=1):
    r = get(f"{BASE}/fixtures", headers=_hdr(), params={"team": team_id, "last": max_items})
    return r.json().get("response", [])

def live_by_team(team_id):
    r = get(f"{BASE}/fixtures", headers=_hdr(), params={"live": "all"})
    arr = r.json().get("response", [])
    return [x for x in arr if (x.get("teams",{}).get("home",{}).get("id")==team_id or
                               x.get("teams",{}).get("away",{}).get("id")==team_id)]

def standings(league_id, season):
    r = get(f"{BASE}/standings", headers=_hdr(), params={"league": league_id, "season": season})
    return r.json().get("response", [])

def lineups(fixture_id):
    r = get(f"{BASE}/fixtures/lineups", headers=_hdr(), params={"fixture": fixture_id})
    return r.json().get("response", [])

def injuries(team_id, season):
    r = get(f"{BASE}/injuries", headers=_hdr(), params={"team": team_id, "season": season})
    return r.json().get("response", [])
