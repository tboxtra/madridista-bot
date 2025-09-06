# providers/sofa.py
import os
from utils.http import get
RKEY = os.getenv("RAPIDAPI_KEY","")
HOST = "sofascore.p.rapidapi.com"

def _hdr():
    return {"x-rapidapi-key": RKEY, "x-rapidapi-host": HOST}

def team_form(team_id, limit=10):
    # endpoint varies; use recent events as form proxy
    r = get(f"https://{HOST}/teams/get-last-matches", headers=_hdr(), params={"teamId": team_id, "count": limit})
    return r.json().get("events", [])

def ratings_for_event(event_id):
    r = get(f"https://{HOST}/event/players", headers=_hdr(), params={"eventId": event_id})
    return r.json()
