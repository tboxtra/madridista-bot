# providers/wiki.py
import os
import requests
from typing import Dict, Any, Optional

def wiki_lookup(query: str) -> Optional[Dict[str, Any]]:
    """Look up Wikipedia article for football history queries."""
    try:
        # Wikipedia API search
        search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        search_query = query.replace(" ", "_")
        
        r = requests.get(f"{search_url}{search_query}", timeout=10)
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
        
        r = requests.get(search_url, params=params, timeout=10)
        if r.status_code == 200:
            results = r.json().get("query", {}).get("search", [])
            if results:
                title = results[0]["title"]
                # Get summary for the found title
                return wiki_lookup(title)
                
    except Exception:
        pass
    
    return None
