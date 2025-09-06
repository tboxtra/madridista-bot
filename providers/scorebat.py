# providers/scorebat.py
import os
from utils.http import get
BASE = os.getenv("SCOREBAT_API","https://www.scorebat.com/video-api/v3/")

def latest_by_team(team_name, limit=5):
    r = get(BASE, timeout=15)
    arr = r.json().get("response", []) or []
    hits = [x for x in arr if team_name.lower() in (x.get("title","")+" "+x.get("competition","")).lower()]
    return hits[:limit]
