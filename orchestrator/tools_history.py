# orchestrator/tools_history.py
import os
from typing import Dict, Any
from providers import wiki

USE_LOCAL_KB = os.getenv("USE_LOCAL_KB", "false").lower() == "true"

def tool_rm_ucl_titles(args: Dict[str, Any]) -> Dict[str, Any]:
    # External first: Wikipedia page for "Real Madrid CF in international football" or "Real Madrid CF in European football"
    data = wiki.wiki_lookup("Real Madrid CF in international football") or wiki.wiki_lookup("Real Madrid CF in European football")
    if data:
        return {"ok": True, "__source": "Wikipedia", "title": data.get("title"), "url": data.get("url"),
                "summary": data.get("summary"), "extract": (data.get("extract") or "")[:900]}
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
