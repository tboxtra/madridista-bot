import os, requests
from typing import List, Dict, Union

HOST = os.getenv("LIVESCORE_RAPIDAPI_HOST", "livescore6.p.rapidapi.com")
KEY  = os.getenv("LIVESCORE_RAPIDAPI_KEY")
CAT  = os.getenv("NEWS_CATEGORY", "soccer")
LIMIT = int(os.getenv("NEWS_LIMIT", "8"))

# Make this optional for bot startup
# if not KEY:
#     raise RuntimeError("Missing LIVESCORE_RAPIDAPI_KEY")

S = requests.Session()
S.headers.update({
    "x-rapidapi-host": HOST,
    "x-rapidapi-key": KEY,
    "accept": "application/json",
    "user-agent": "MadridistaBot/1.0"
})

def fetch_news_raw(category=None):
    if not KEY:
        return {"error": "Missing LIVESCORE_RAPIDAPI_KEY"}
    
    cat = (category or CAT).strip().lower()
    url = f"https://{HOST}/news/list"
    r = S.get(url, params={"category": cat}, timeout=20)
    r.raise_for_status()
    return r.json()

def normalize_items(raw):
    """
    Convert LiveScore payload to a simple list:
      {title, url, source, published, summary}
    """
    items = []
    # LiveScore response shape may vary; common keys: "data" -> "articles" or "news"
    candidates = []
    if isinstance(raw, dict):
        for k in ("data", "news", "articles"):
            v = raw.get(k)
            if isinstance(v, list):
                candidates = v
                break
        if not candidates and "data" in raw and isinstance(raw["data"], dict):
            for k in ("news", "articles"):
                v = raw["data"].get(k)
                if isinstance(v, list):
                    candidates = v
                    break

    for x in candidates[:LIMIT]:
        title = x.get("title") or x.get("headline") or ""
        url   = x.get("url") or x.get("link") or ""
        src   = x.get("source") or x.get("provider") or ""
        pub   = x.get("published") or x.get("pubDate") or x.get("time") or ""
        desc  = x.get("description") or x.get("summary") or ""
        items.append({
            "title": title.strip(),
            "url": url.strip(),
            "source": (src or "").strip(),
            "published": (pub or "").strip(),
            "summary": (desc or "").strip()
        })
    return items

MADRID_KEYWORDS = [
    "real madrid", "madrid", "bernabéu", "bernabeu",
    "vinícius", "vinicius", "bellingham", "ancelotti",
    "mbappé", "mbappe", "rudiger", "tchouameni", "rodrygo",
    "cristiano", "ronaldo", "cr7"
]

def madrid_filter(items):
    out = []
    for it in items:
        blob = f"{it.get('title','')} {it.get('summary','')}".lower()
        if any(k in blob for k in MADRID_KEYWORDS):
            out.append(it)
    return out
