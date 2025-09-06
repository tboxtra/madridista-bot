# providers/wiki.py
import os
import requests
from typing import Dict, Any, Optional

# Wikipedia requires a User-Agent header
HEADERS = {
    "User-Agent": "MadridistaBot/1.0 (https://github.com/tboxtra/madridista-bot; football bot for Real Madrid fans)"
}

def wiki_lookup(query: str) -> Optional[Dict[str, Any]]:
    """Look up Wikipedia article for football history queries."""
    try:
        # Wikipedia API search
        search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        search_query = query.replace(" ", "_")
        
        r = requests.get(f"{search_url}{search_query}", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                "title": data.get("title", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "summary": data.get("extract", ""),
                "description": data.get("description", "")
            }
        
        # Try search API if direct lookup fails
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 1
        }
        
        r = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            results = r.json().get("query", {}).get("search", [])
            if results:
                title = results[0]["title"]
                # Get summary for the found title
                return wiki_lookup(title)
                
    except Exception as e:
        print(f"Wikipedia lookup error: {e}")
    
    return None
