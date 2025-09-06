# orchestrator/tools_history.py
import os, re, html as htmlmod
from typing import Dict, Any, List
from providers import wiki
from utils.http import get

USE_LOCAL_KB = os.getenv("USE_LOCAL_KB", "false").lower() == "true"

def tool_rm_ucl_titles(args: Dict[str, Any]) -> Dict[str, Any]:
    # External first: Wikipedia page for "Real Madrid CF in international football" or "Real Madrid CF in European football"
    data = wiki.wiki_lookup("Real Madrid CF in international football") or wiki.wiki_lookup("Real Madrid CF in European football")
    if data:
        return {"ok": True, "__source": "Wikipedia", "title": data.get("title"), "url": data.get("url"),
                "summary": data.get("description"), "extract": (data.get("extract") or "")[:900]}
    # Optional local KB if allowed
    if USE_LOCAL_KB:
        try:
            import json, os
            KB_PATH = os.path.join(os.path.dirname(__file__), "..", "kb", "history", "real_madrid.json")
            with open(KB_PATH, "r", encoding="utf-8") as f:
                rm = json.load(f)
            return {"ok": True, "__source": "KB", "titles": rm.get("ucl_titles", [])}
        except Exception:
            pass
    return {"ok": False, "__source": "Wikipedia", "message": "Unable to fetch titles externally."}

def tool_history_lookup(args: Dict[str, Any]) -> Dict[str, Any]:
    q = (args.get("query") or "").strip()
    if not q:
        return {"ok": False, "__source": "Wikipedia", "message": "Provide a query"}
    data = wiki.wiki_lookup(q)
    if not data:
        return {"ok": False, "__source": "Wikipedia", "message": "No article found"}
    return {
        "ok": True, "__source": "Wikipedia",
        "title": data.get("title"), "url": data.get("url"),
        "summary": data.get("description"),
        "extract": (data.get("extract") or "")[:900]
    }

def tool_ucl_last_n_winners(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamically parse the Wikipedia finals page to get the last N winners.
    No hard-coded teams; pulls table rows, newest first.
    """
    n = int(args.get("n", 5))
    # Fetch HTML of the finals list:
    try:
        r = get(wiki.WIKI_API, headers={"User-Agent": "MadridistaBot/1.0"}, timeout=12, params={
            "action": "parse", "page": "List of European Cup and UEFA Champions League finals", "prop": "text", "format": "json"
        })
        html = (r.json().get("parse") or {}).get("text", {}).get("*", "")
    except Exception:
        html = ""

    winners: List[Dict[str, str]] = []
    if html:
        rows = re.findall(r"<tr>(.*?)</tr>", html, flags=re.S | re.I)
        for row in rows:
            # year
            m_year = re.search(r">(19\d{2}|20\d{2})<", row)
            # winner (first team link in the row is usually the winner)
            # capture the anchor text (strip tags/entities)
            teams = re.findall(r'<a[^>]*>([^<]+)</a>', row, flags=re.I)
            year = m_year.group(1) if m_year else None
            if year and teams:
                winner = htmlmod.unescape(teams[0]).strip()
                winners.append({"season": year, "winner": winner})
        # keep unique by (season -> first occurrence) and sort newest first
        seen = set()
        cleaned = []
        for w in winners:
            if w["season"] in seen:
                continue
            seen.add(w["season"])
            cleaned.append(w)
        winners = sorted(cleaned, key=lambda x: x["season"], reverse=True)[:n]

    if not winners:
        return {"ok": False, "__source": "Wikipedia", "message": "Could not parse winners list."}

    return {
        "ok": True, "__source": "Wikipedia", "items": winners,
        "page": "https://en.wikipedia.org/wiki/List_of_European_Cup_and_UEFA_Champions_League_finals"
    }
