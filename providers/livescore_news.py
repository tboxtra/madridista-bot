# providers/livescore_news.py
import os
from utils.http import get
RKEY = os.getenv("RAPIDAPI_KEY","")
HOST = "livescore6.p.rapidapi.com"

def _hdr():
    return {"x-rapidapi-key": RKEY, "x-rapidapi-host": HOST}

def soccer_news(limit=8):
    r = get(f"https://{HOST}/news/list", headers=_hdr(), params={"category":"soccer"})
    items = (r.json().get("data") or {}).get("articles") or r.json().get("articles") or []
    return items[:limit]