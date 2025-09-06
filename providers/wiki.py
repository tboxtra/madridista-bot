# providers/wiki.py
import re
from typing import Optional, Dict, Any
from utils.http import get

WIKI_REST = "https://en.wikipedia.org/api/rest_v1"
WIKI_API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "MadridistaBot/1.0 (+football assistant)"}
TIMEOUT = 12

def _slug(s: str) -> str: 
    return re.sub(r"\s+", "_", (s or "").strip())

def wiki_search(query: str) -> Optional[str]:
    try:
        r = get(WIKI_API, headers=UA, timeout=TIMEOUT, params={
            "action": "opensearch", "search": query, "limit": 1, "namespace": 0, "format": "json"
        })
        js = r.json()
        return js[1][0] if isinstance(js, list) and js[1] else None
    except Exception:
        return None

def wiki_summary(title: str) -> Optional[Dict[str, Any]]:
    try:
        r = get(f"{WIKI_REST}/page/summary/{_slug(title)}", headers=UA, timeout=TIMEOUT)
        js = r.json()
        if js.get("title"): 
            return js
    except Exception:
        pass
    # fallback
    try:
        r = get(WIKI_API, headers=UA, timeout=TIMEOUT, params={
            "action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1, "format": "json", "titles": title
        })
        js = r.json()
        page = next(iter((js.get("query") or {}).get("pages", {}).values()), {})
        if page.get("title"):
            return {
                "title": page["title"], 
                "extract": page.get("extract", ""),
                "content_urls": {"desktop": {"page": f"https://en.wikipedia.org/wiki/{_slug(page['title'])}"}}
            }
    except Exception:
        pass
    return None

def wiki_extract(title: str, max_chars=4000) -> Optional[str]:
    try:
        r = get(WIKI_API, headers=UA, timeout=TIMEOUT, params={
            "action": "query", "prop": "extracts", "format": "json", "explaintext": 1, "titles": title
        })
        js = r.json()
        page = next(iter((js.get("query") or {}).get("pages", {}).values()), {})
        return (page.get("extract") or "")[:max_chars]
    except Exception:
        return None

def wiki_lookup(query: str) -> Optional[Dict[str, Any]]:
    # Try multiple search strategies for better results
    search_terms = [query]
    
    # Add specific search terms for common historical queries
    if "ucl" in query.lower() or "champions league" in query.lower():
        if "2020" in query:
            search_terms.extend(["2020 UEFA Champions League Final", "Bayern Munich 2020", "UEFA Champions League 2019-20"])
        elif "2021" in query:
            search_terms.extend(["2021 UEFA Champions League Final", "Chelsea 2021", "UEFA Champions League 2020-21"])
        elif "2022" in query:
            search_terms.extend(["2022 UEFA Champions League Final", "Real Madrid 2022", "UEFA Champions League 2021-22"])
        elif "2023" in query:
            search_terms.extend(["2023 UEFA Champions League Final", "Manchester City 2023", "UEFA Champions League 2022-23"])
        elif "2024" in query:
            search_terms.extend(["2024 UEFA Champions League Final", "Real Madrid 2024", "UEFA Champions League 2023-24"])
    
    # Try each search term until we get a good result
    for term in search_terms:
        title = wiki_search(term) or term
        sumy = wiki_summary(title)
        if sumy and sumy.get("extract") and len(sumy.get("extract", "")) > 100:
            url = (sumy.get("content_urls", {}) or {}).get("desktop", {}).get("page", "") or f"https://en.wikipedia.org/wiki/{_slug(sumy.get('title', ''))}"
            extract = sumy.get("extract") or wiki_extract(sumy.get("title", "")) or ""
            return {
                "title": sumy.get("title"),
                "url": url,
                "description": sumy.get("description"),
                "extract": extract
            }
    
    # Fallback to original logic
    title = wiki_search(query) or query
    sumy = wiki_summary(title)
    if not sumy:
        return None
    url = (sumy.get("content_urls", {}) or {}).get("desktop", {}).get("page", "") or f"https://en.wikipedia.org/wiki/{_slug(sumy.get('title', ''))}"
    extract = sumy.get("extract") or wiki_extract(sumy.get("title", "")) or ""
    return {
        "title": sumy.get("title"),
        "url": url,
        "description": sumy.get("description"),
        "extract": extract
    }
