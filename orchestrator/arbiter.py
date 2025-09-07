# orchestrator/arbiter.py
import re, time
from typing import Dict, Any, List, Tuple, Optional

# Lightweight signals the arbiter uses to score results
def _is_empty(payload: Dict[str, Any]) -> bool:
    if not payload or not payload.get("ok"): return True
    # Consider "empty" when common containers are missing/empty:
    keys = ("items","rows","events","extract","fixture_id","when","home","away")
    return not any(k in payload and payload[k] for k in keys)

def _ts_now() -> float:
    return time.time()

def _looks_live(q: str) -> bool:
    ql = (q or "").lower()
    return any(w in ql for w in ["live","now","currently","minute","ht","ft"])

def _looks_next(q: str) -> bool:
    ql = (q or "").lower()
    return any(w in ql for w in ["next","upcoming","who do","fixture","play next","schedule"])

def _looks_last(q: str) -> bool:
    ql = (q or "").lower()
    return any(w in ql for w in ["last","previous","most recent","result","score","final score","ft","ended","beat","defeated","won","happened when"])

def _looks_news(q: str) -> bool:
    ql = (q or "").lower()
    return any(w in ql for w in ["news","headline","rumor","transfer","breaking"])

def _looks_history(q: str) -> bool:
    ql = (q or "").lower()
    return bool(re.search(r"\b(19[0-9]{2}|20[0-2][0-9])\b", ql) or
                any(w in ql for w in ["history","historical","winner","winners","champion","finals","season","decade","record","happened when","beat","defeated","won","past","ago"]))

def _looks_players(q: str) -> bool:
    ql = (q or "").lower()
    return any(w in ql for w in ["player","stats","per 90","goals","assists","rating"])

def _looks_compare(q: str) -> bool:
    ql = (q or "").lower()
    return any(w in ql for w in ["compare","vs","versus","h2h","head to head","last score between","last result between","beat","defeated","won against","when","between"])

def plan_tools(user_q: str) -> List[str]:
    """
    Return an ordered plan of tool names to try for this query.
    Keep names aligned with NAME_TO_FUNC in brain.
    """
    plan = []
    
    # Priority 1: Specific match result queries (most specific first)
    if _looks_compare(user_q) and any(w in user_q.lower() for w in ["happened when", "beat", "defeated", "won against", "when did", "defeat"]):
        plan += ["tool_af_find_match_result", "tool_af_last_result_vs", "tool_h2h_officialish", "tool_h2h_summary", "tool_compare_teams"]
    
    # Priority 2: Other intents
    elif _looks_live(user_q):           plan += ["tool_live_now", "tool_af_last_result"]
    elif _looks_next(user_q):           plan += ["tool_af_next_fixture", "tool_next_fixture"]
    elif _looks_last(user_q):           plan += ["tool_af_last_result", "tool_last_result"]
    elif _looks_news(user_q):           plan += ["tool_news_top"]
    elif _looks_players(user_q):        plan += ["tool_player_stats", "tool_compare_players"]
    elif _looks_compare(user_q):        plan += ["tool_af_last_result_vs", "tool_h2h_officialish", "tool_h2h_summary", "tool_compare_teams"]
    elif _looks_history(user_q):        plan += ["tool_history_lookup"]
    
    # Always add general fallbacks at the end:
    plan += ["tool_sofa_form", "tool_table", "tool_history_lookup"]
    
    # De-dup while preserving order
    seen=set(); ordered=[]
    for t in plan:
        if t not in seen:
            ordered.append(t); seen.add(t)
    return ordered

def validate_recency(q: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    For 'last/next/today' questions, reject stale (e.g., > 180d old) or far-future.
    Returns (is_valid, reason_if_invalid)
    """
    ql = (q or "").lower()
    if any(w in ql for w in ["today","now","live"]):
        # must have live-ish signals
        liveish = ("events" in payload) or (payload.get("when") and payload.get("fixture_id"))
        return (bool(liveish), "not_live")
    if any(w in ql for w in ["last","previous","most recent"]):
        # last result should have a score and a recent date; basic fields exist?
        has_score = all(k in payload for k in ["home","away","when"])
        return (bool(has_score), "no_last_result")
    if any(w in ql for w in ["next","upcoming","fixture","play next"]):
        return (bool(payload.get("when") and payload.get("home") and payload.get("away")), "no_next_fixture")
    return (True, "")
