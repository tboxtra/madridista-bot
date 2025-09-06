import os
import requests

RAPID_KEY = os.getenv("RAPIDAPI_KEY")
LS_URL = "https://livescore6.p.rapidapi.com/news/list"

def news_soccer(category: str = "soccer", limit: int = 10):
    """Get soccer news from LiveScore via RapidAPI"""
    if not RAPID_KEY:
        return []
    try:
        r = requests.get(
            LS_URL,
            params={"category": category},
            headers={
                "x-rapidapi-host": "livescore6.p.rapidapi.com",
                "x-rapidapi-key": RAPID_KEY
            },
            timeout=15
        )
        r.raise_for_status()
        js = r.json()
        arts = js.get("articles") or []
        return arts[:limit]
    except Exception:
        return []
