from typing import Dict, Any, List, Optional
from providers.unified import fd_team_matches, fd_comp_table, fd_comp_scorers
from providers.sofascore import SofaScoreProvider
from nlp.resolve import resolve_team, resolve_comp
from utils.timeutil import fmt_abs, now_utc, parse_iso_utc
from utils.formatting import md_escape

SOFA = SofaScoreProvider()

def tool_next_fixture(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return the nearest upcoming fixture for a team (default Real Madrid)."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    matches = fd_team_matches(team_id, status=None, limit=30)
    future = [m for m in matches if m.get("status") in {"SCHEDULED","TIMED"}]
    future.sort(key=lambda x: x["utcDate"])
    if not future:
        return {"ok": False, "message": "No upcoming fixtures."}
    m = future[0]
    return {"ok": True, "when": fmt_abs(m["utcDate"]),
            "home": m["homeTeam"]["name"], "away": m["awayTeam"]["name"]}

def tool_last_result(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return the latest finished result for a team."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    ms = fd_team_matches(team_id, status="FINISHED", limit=1)
    if not ms:
        return {"ok": False, "message": "No recent match found."}
    m = ms[0]; ft = (m.get("score",{}) or {}).get("fullTime",{}) or {}
    return {"ok": True, "when": fmt_abs(m["utcDate"]),
            "home": m["homeTeam"]["name"], "away": m["awayTeam"]["name"],
            "home_score": ft.get("home",0), "away_score": ft.get("away",0)}

def tool_live_now(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return live score for the configured team if playing now (SofaScore)."""
    ev = SOFA.get_team_live_event()
    if not ev:
        return {"ok": False, "message": "No live match right now."}
    return {"ok": True, "minute": ev.get("minute"), "home": ev["homeName"],
            "away": ev["awayName"], "home_score": ev["homeScore"],
            "away_score": ev["awayScore"], "competition": ev.get("competition","")}

def tool_table(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return top rows of a league table (default LaLiga)."""
    comp_id = args.get("competition_id") or resolve_comp(args.get("competition","") or "")
    js = fd_comp_table(comp_id)
    table = (js.get("standings",[]) or [{}])[0].get("table",[])[:10]
    rows = [{"pos": r["position"], "team": r["team"]["name"], "pts": r["points"]} for r in table]
    return {"ok": True, "rows": rows}

def tool_form(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return last N finished results for a team (default 5)."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    k = int(args.get("k",5))
    ms = fd_team_matches(team_id, status="FINISHED", limit=max(10,k))
    out = []
    for m in ms[:k]:
        ft = (m.get("score",{}) or {}).get("fullTime",{}) or {}
        out.append({"when": fmt_abs(m["utcDate"]), "home": m["homeTeam"]["name"],
                    "away": m["awayTeam"]["name"], "home_score": ft.get("home",0),
                    "away_score": ft.get("away",0)})
    return {"ok": True, "results": out}

def tool_scorers(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return top goal scorers for a competition (default LaLiga)."""
    comp_id = args.get("competition_id") or resolve_comp(args.get("competition","") or "")
    limit = int(args.get("limit",10))
    js = fd_comp_scorers(comp_id, limit=limit)
    items = js.get("scorers", [])[:limit]
    rows = [{"player": s["player"]["name"], "team": s["team"]["name"], "goals": s["numberOfGoals"]} for s in items]
    return {"ok": True, "rows": rows}

def tool_injuries(args: Dict[str, Any]) -> Dict[str, Any]:
    """List injuries/unavailable for a team (SofaScore)."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    try:
        js = SOFA.team_injuries()
        players = (js.get("players") or [])
        out = [{"name": p.get("name"), "status": (p.get("injury") or {}).get("type") or p.get("status","Unavailable")}
               for p in players]
        return {"ok": True, "players": out}
    except Exception:
        return {"ok": False, "message": "Injury data unavailable."}

def tool_squad(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return squad list, optionally filtered by position prefix."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    pos = (args.get("position") or "").lower()
    try:
        js = SOFA.team_squad()
        players = js.get("players") or []
        if pos:
            players = [p for p in players if (p.get("position") or "").lower().startswith(pos)]
        out = [{"name": p.get("name") or p.get("shortName"), "position": p.get("position","")} for p in players]
        return {"ok": True, "players": out[:30]}
    except Exception:
        return {"ok": False, "message": "Squad data unavailable."}

def tool_last_man_of_match(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return the Man of the Match (or top-rated player) of last finished match for the configured team."""
    # We already built this logic earlier; call event_best_player on last event id from SofaScore if you maintain it.
    # For simplicity here: try current live event, else fallback message.
    ev = SOFA.get_team_live_event()
    if not ev:
        return {"ok": False, "message": "No recent MoM available (needs last event lookup endpoint wired)."}
    try:
        best = SOFA.event_best_player(ev["id"])
        if not best:
            return {"ok": False, "message": "No MoM data found."}
        return {"ok": True, "name": best.get("name"), "rating": best.get("rating")}
    except Exception:
        return {"ok": False, "message": "MoM data unavailable."}
