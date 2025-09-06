from typing import Dict, Any, List, Optional
from providers.unified import fd_team_matches, fd_comp_table, fd_comp_scorers
from providers.sofascore import SofaScoreProvider, player_search, player_season_stats, team_h2h, team_recent_form, team_next_event, event_lineups
from providers.news import news_soccer
from nlp.resolve import resolve_team, resolve_comp, resolve_player_name
from utils.timeutil import fmt_abs, now_utc, parse_iso_utc
from utils.formatting import md_escape

# Citation constants
CIT_SOFA = "SofaScore"
CIT_FD = "Football-Data"
CIT_LS = "LiveScore"

SOFA = SofaScoreProvider()

def tool_next_fixture(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return the nearest upcoming fixture for a team (default Real Madrid)."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    matches = fd_team_matches(team_id, status=None, limit=30, window_days=90)
    future = [m for m in matches if m.get("status") in {"SCHEDULED","TIMED"}]
    future.sort(key=lambda x: x["utcDate"])
    if not future:
        return {"ok": False, "message": "No upcoming fixtures.", "__source": CIT_FD}
    m = future[0]
    return {"ok": True, "when": fmt_abs(m["utcDate"]),
            "home": m["homeTeam"]["name"], "away": m["awayTeam"]["name"], "__source": CIT_FD}

def tool_last_result(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return the latest finished result for a team."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    ms = fd_team_matches(team_id, status="FINISHED", limit=1, window_days=180)
    if not ms:
        return {"ok": False, "message": "No recent match found.", "__source": CIT_FD}
    m = ms[0]; ft = (m.get("score",{}) or {}).get("fullTime",{}) or {}
    return {"ok": True, "when": fmt_abs(m["utcDate"]),
            "home": m["homeTeam"]["name"], "away": m["awayTeam"]["name"],
            "home_score": ft.get("home",0), "away_score": ft.get("away",0), "__source": CIT_FD}

def tool_live_now(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return live score for the configured team if playing now (SofaScore)."""
    ev = SOFA.get_team_live_event()
    if not ev:
        return {"ok": False, "message": "No live match right now.", "__source": CIT_SOFA}
    return {"ok": True, "minute": ev.get("minute"), "home": ev["homeName"],
            "away": ev["awayName"], "home_score": ev["homeScore"],
            "away_score": ev["awayScore"], "competition": ev.get("competition",""), "__source": CIT_SOFA}

def tool_table(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return top rows of a league table (default LaLiga)."""
    comp_id = args.get("competition_id") or resolve_comp(args.get("competition","") or "")
    js = fd_comp_table(comp_id)
    table = (js.get("standings",[]) or [{}])[0].get("table",[])[:10]
    rows = [{"pos": r["position"], "team": r["team"]["name"], "pts": r["points"]} for r in table]
    return {"ok": True, "rows": rows, "__source": CIT_FD}

def tool_form(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return last N finished results for a team (default 5)."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    k = int(args.get("k",5))
    ms = fd_team_matches(team_id, status="FINISHED", limit=max(10,k), window_days=180)
    out = []
    for m in ms[:k]:
        ft = (m.get("score",{}) or {}).get("fullTime",{}) or {}
        out.append({"when": fmt_abs(m["utcDate"]), "home": m["homeTeam"]["name"],
                    "away": m["awayTeam"]["name"], "home_score": ft.get("home",0),
                    "away_score": ft.get("away",0)})
    return {"ok": True, "results": out, "__source": CIT_FD}

def tool_scorers(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return top goal scorers for a competition (default LaLiga)."""
    comp_id = args.get("competition_id") or resolve_comp(args.get("competition","") or "")
    limit = int(args.get("limit",10))
    js = fd_comp_scorers(comp_id, limit=limit)
    items = js.get("scorers", [])[:limit]
    rows = [{"player": s["player"]["name"], "team": s["team"]["name"], "goals": s["numberOfGoals"]} for s in items]
    return {"ok": True, "rows": rows, "__source": CIT_FD}

def tool_injuries(args: Dict[str, Any]) -> Dict[str, Any]:
    """List injuries/unavailable for a team (SofaScore)."""
    team_id = args.get("team_id") or resolve_team(args.get("team_name","") or "")
    try:
        js = SOFA.team_injuries()
        players = (js.get("players") or [])
        out = [{"name": p.get("name"), "status": (p.get("injury") or {}).get("type") or p.get("status","Unavailable")}
               for p in players]
        return {"ok": True, "players": out, "__source": CIT_SOFA}
    except Exception:
        return {"ok": False, "message": "Injury data unavailable.", "__source": CIT_SOFA}

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
        return {"ok": True, "players": out[:30], "__source": CIT_SOFA}
    except Exception:
        return {"ok": False, "message": "Squad data unavailable.", "__source": CIT_SOFA}

def tool_last_man_of_match(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return the Man of the Match (or top-rated player) of last finished match for the configured team."""
    # We already built this logic earlier; call event_best_player on last event id from SofaScore if you maintain it.
    # For simplicity here: try current live event, else fallback message.
    ev = SOFA.get_team_live_event()
    if not ev:
        return {"ok": False, "message": "No recent MoM available (needs last event lookup endpoint wired).", "__source": CIT_SOFA}
    try:
        best = SOFA.event_best_player(ev["id"])
        if not best:
            return {"ok": False, "message": "No MoM data found.", "__source": CIT_SOFA}
        return {"ok": True, "name": best.get("name"), "rating": best.get("rating"), "__source": CIT_SOFA}
    except Exception:
        return {"ok": False, "message": "MoM data unavailable.", "__source": CIT_SOFA}

def _is_recent_ts(ts, max_age_days: int = 120):
    # SofaScore gives startTimestamp (seconds)
    try:
        from datetime import datetime, timezone, timedelta
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return (datetime.now(timezone.utc) - dt) <= timedelta(days=max_age_days)
    except Exception:
        return False

def tool_compare_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two teams' recent form (last k). Uses SofaScore last events and ignores stale (>120d)."""
    a = args.get("team_a") or "Real Madrid"
    b = args.get("team_b") or "Barcelona"
    k = int(args.get("k", 5))
    ta, tb = resolve_team(a), resolve_team(b)

    fa = [m for m in team_recent_form(ta, limit=max(10, k)) if _is_recent_ts(m.get("ts"))][:k]
    fb = [m for m in team_recent_form(tb, limit=max(10, k)) if _is_recent_ts(m.get("ts"))][:k]

    if len(fa) < max(1, k//2) or len(fb) < max(1, k//2):
        return {"ok": False, "message": "Not enough recent matches to compare (season gap?).", "__source": "SofaScore"}

    def pts(h, a):
        if h > a: return 3
        if h == a: return 1
        return 0

    # naive side detection by comparing team name prefix; you can store team ids if you keep them
    def sum_pts(arr, team_name: str):
        s = 0
        for m in arr:
            home = (m["home"] or "").lower()
            if home.startswith(team_name.lower().split()[0]):
                s += pts(m["home_score"], m["away_score"])
            else:
                s += pts(m["away_score"], m["home_score"])
        return s

    pa = sum_pts(fa, a)
    pb = sum_pts(fb, b)
    verdict = a if pa > pb + 1 else b if pb > pa + 1 else "too close to call"

    return {
        "ok": True,
        "__source": "SofaScore",
        "k": k,
        "team_a": a, "team_b": b,
        "points_a": pa, "points_b": pb,
        "verdict": verdict,
        "form_a": fa, "form_b": fb
    }

def tool_h2h_summary(args: Dict[str, Any]) -> Dict[str, Any]:
    """Head-to-head summary between two teams."""
    a = args.get("team_a") or "Real Madrid"
    b = args.get("team_b") or "Barcelona"
    ta, tb = resolve_team(a), resolve_team(b)
    js = team_h2h(ta, tb)
    matches = (js.get("events") or [])[:10]
    wins_a = wins_b = draws = 0
    
    for e in matches:
        hs = (e.get("homeScore") or {}).get("current", 0)
        as_ = (e.get("awayScore") or {}).get("current", 0)
        if hs == as_:
            draws += 1
        elif hs > as_ and e.get("homeTeam", {}).get("id") == ta:
            wins_a += 1
        elif hs < as_ and e.get("awayTeam", {}).get("id") == ta:
            wins_a += 1
        else:
            wins_b += 1
    
    return {"ok": True, "team_a": a, "team_b": b,
            "wins_a": wins_a, "wins_b": wins_b, "draws": draws, "sample": len(matches), "__source": CIT_SOFA}

def tool_player_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    """Basic player season stats via SofaScore (goals/assists/apps if available)."""
    name = args.get("player_name") or resolve_player_name(args.get("query", "") or "")
    if not name:
        return {"ok": False, "message": "Player not recognized."}
    
    p = player_search(name)
    if not p:
        return {"ok": False, "message": f"No player found for {name}."}
    
    pid = p.get("id")
    season = player_season_stats(pid)
    
    # The structure varies by endpoint; extract common fields where present
    out = {"name": p.get("name") or name}
    s = season if isinstance(season, dict) else {}
    agg = s.get("statistics") or s.get("summary") or {}
    out["team"] = (p.get("team") or {}).get("name")
    out["apps"] = agg.get("appearances") or agg.get("matchesPlayed")
    out["goals"] = agg.get("goals")
    out["assists"] = agg.get("assists")
    out["rating"] = agg.get("rating")
    
    return {"ok": True, **out, "__source": CIT_SOFA}

def tool_news(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get top football news; optional filter by keyword/team."""
    q = (args.get("query") or "").lower().strip()
    arts = news_soccer(limit=15)
    if q:
        arts = [a for a in arts if q in ((a.get("title", "") + " " + a.get("body", "")).lower())]
    rows = [{"title": a.get("title"), "source": a.get("source"), "url": a.get("url")} for a in arts[:5]]
    return {"ok": True, "items": rows, "__source": CIT_LS}

def _per90(total, minutes):
    """Calculate per-90 statistics"""
    try:
        t = float(total or 0.0)
        m = float(minutes or 0.0)
        if m <= 0:
            return None
        return round(t * 90.0 / m, 2)
    except Exception:
        return None

def _extract_player_agg(season_json: dict) -> dict:
    """
    Best-effort extraction across SofaScore variants:
    returns { minutes, goals, assists, shots, xg, keyPasses, rating }
    Only fields present are returned.
    """
    s = season_json or {}
    agg = s.get("statistics") or s.get("summary") or s.get("aggregatedStatistics") or {}
    out = {}
    for k_sofa, k_out in [
        ("minutesPlayed", "minutes"), ("goals", "goals"), ("assists", "assists"),
        ("shotsTotal", "shots"), ("xg", "xg"), ("keyPasses", "keyPasses"),
        ("rating", "rating")
    ]:
        if agg.get(k_sofa) is not None:
            out[k_out] = agg.get(k_sofa)
    # sometimes minutes nested
    if "minutes" not in out:
        mins = agg.get("minutes") or agg.get("timePlayed")
        if mins is not None:
            out["minutes"] = mins
    return out

def tool_compare_players(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two players' season stats; derive per-90 for goals/assists/shots/xg when minutes exist.
    Args: player_a, player_b (names)
    """
    a_name = args.get("player_a") or resolve_player_name(args.get("query_a", "") or "")
    b_name = args.get("player_b") or resolve_player_name(args.get("query_b", "") or "")
    if not a_name or not b_name:
        return {"ok": False, "message": "Please provide two player names.", "__source": CIT_SOFA}

    pa = player_search(a_name)
    pb = player_search(b_name)
    if not pa or not pb:
        return {"ok": False, "message": "Could not find one or both players.", "__source": CIT_SOFA}

    sa = player_season_stats(pa["id"])
    sb = player_season_stats(pb["id"])
    agg_a = _extract_player_agg(sa)
    agg_b = _extract_player_agg(sb)

    # compute per90s where possible
    def enrich(agg):
        mins = agg.get("minutes")
        for k in ["goals", "assists", "shots", "xg"]:
            if agg.get(k) is not None:
                agg[k + "_p90"] = _per90(agg.get(k), mins)
        return agg

    A = enrich(agg_a)
    B = enrich(agg_b)
    return {
        "ok": True,
        "__source": CIT_SOFA,
        "a": {"name": pa.get("name") or a_name, **A},
        "b": {"name": pb.get("name") or b_name, **B},
    }

def tool_next_lineups(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get probable/confirmed lineups for the team's next event if available.
    """
    team_id = args.get("team_id") or resolve_team(args.get("team_name", "") or "")
    ev = team_next_event(team_id)
    if not ev:
        return {"ok": False, "message": "No upcoming event found.", "__source": CIT_SOFA}
    eid = ev.get("id")
    lu = event_lineups(eid)
    
    # Normalize output minimally
    def pick(side):
        s = (lu.get(side) or {})
        status = s.get("formation") or s.get("manager", {}).get("name") or "lineup"
        players = []
        for p in s.get("players", [])[:11]:
            nm = p.get("player", {}).get("name") or p.get("name")
            pos = p.get("position") or p.get("shirtNumber")
            players.append({"name": nm, "pos": pos})
        bench = []
        for p in s.get("players", [])[11:18]:
            nm = p.get("player", {}).get("name") or p.get("name")
            bench.append({"name": nm})
        return {"status": status, "xi": players, "bench": bench}
    
    home = pick("home")
    away = pick("away")
    return {"ok": True, "__source": CIT_SOFA,
            "event": {"home": ev.get("homeTeam", {}).get("name"), "away": ev.get("awayTeam", {}).get("name")},
            "home": home, "away": away}
