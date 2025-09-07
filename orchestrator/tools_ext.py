# orchestrator/tools_ext.py
from typing import Dict, Any
from providers import api_football as AF, sofa as SOFA, livescore_news as LSN, scorebat as SB, youtube as YT, elo as ELO, odds as ODDS
from providers.ids import af_id

CIT_AF = "API-Football"
CIT_SOFA = "SofaScore"
CIT_LS = "LiveScore"
CIT_SB = "Scorebat"
CIT_YT = "YouTube"
CIT_ELO = "ClubElo"
CIT_ODDS = "OddsAPI"

def tool_af_next_fixture(args: Dict[str, Any]) -> Dict[str, Any]:
    team_id = args.get("team_id")
    arr = AF.fixtures_next(team_id, days_ahead=30, max_items=1)
    if not arr: return {"ok": False, "__source": CIT_AF, "message": "No upcoming"}
    f = arr[0]
    fx = f.get("fixture",{})
    return {"ok": True, "__source": CIT_AF, "fixture_id": fx.get("id"),
            "when": fx.get("date"), "home": f.get("teams",{}).get("home",{}).get("name"),
            "away": f.get("teams",{}).get("away",{}).get("name")}

def tool_af_last_result(args: Dict[str, Any]) -> Dict[str, Any]:
    team_id = args.get("team_id")
    arr = AF.fixtures_last(team_id, max_items=1)
    if not arr: return {"ok": False, "__source": CIT_AF, "message":"No finished"}
    f = arr[0]
    fx = f.get("fixture",{}); sc = f.get("goals",{})
    return {"ok": True, "__source": CIT_AF, "when": fx.get("date"), "home": f["teams"]["home"]["name"],
            "away": f["teams"]["away"]["name"], "home_score": sc.get("home"), "away_score": sc.get("away")}

def tool_sofa_form(args: Dict[str, Any]) -> Dict[str, Any]:
    team_id = args.get("team_id"); k = int(args.get("k",5))
    arr = SOFA.team_form(team_id, limit=max(k,10))
    return {"ok": True, "__source": CIT_SOFA, "events": arr[:k]}

def tool_news_top(args: Dict[str, Any]) -> Dict[str, Any]:
    q = args.get("query","")
    items = LSN.soccer_news(limit=8)
    if q: items = [x for x in items if q.lower() in (x.get("title","")+x.get("content","")).lower()]
    return {"ok": True, "__source": CIT_LS, "items": items[:5]}

def tool_highlights(args: Dict[str, Any]) -> Dict[str, Any]:
    team = args.get("team_name","Real Madrid")
    vids = SB.latest_by_team(team, limit=5)
    return {"ok": True, "__source": CIT_SB, "items": vids}

def tool_youtube_latest(args: Dict[str, Any]) -> Dict[str, Any]:
    channel_id = args.get("channel_id") or "UCWV3obpZVGgJ3j9FVhEjF2Q"  # Real Madrid C.F.
    vids = YT.latest_videos(channel_id, limit=4)
    return {"ok": True, "__source": CIT_YT, "items": vids}

def tool_club_elo(args: Dict[str, Any]) -> Dict[str, Any]:
    team = args.get("team_name","Real Madrid")
    e = ELO.team_elo(team)
    if not e: return {"ok": False, "__source": CIT_ELO, "message":"No Elo"}
    return {"ok": True, "__source": CIT_ELO, **e}

def tool_odds_snapshot(args: Dict[str, Any]) -> Dict[str, Any]:
    sport = args.get("sport_key","soccer_epl")  # change per league
    js = ODDS.prematch_odds(sport_key=sport)
    return {"ok": True, "__source": CIT_ODDS, "markets": js[:5]}

def tool_af_last_result_vs(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the most recent competitive result between two teams using API-Football H2H endpoint.
    Args: team_a_id (int), team_b_id (int), team_a (str), team_b (str), max_items (int=50)
    """
    # Support both ID and name inputs
    a = int(args.get("team_a_id") or 0) or af_id(args.get("team_a") or "")
    b = int(args.get("team_b_id") or 0) or af_id(args.get("team_b") or "")
    max_items = int(args.get("max_items", 50))  # Get more H2H results for comprehensive search
    
    if not a or not b:
        return {"ok": False, "__source": CIT_AF, "message": "team_a_id/team_a and team_b_id/team_b required."}

    # Use dedicated H2H endpoint for direct head-to-head results
    h2h_fixtures = AF.fixtures_h2h(a, b, max_items=max_items)
    
    # Keep finished games only, newest first (already sorted by the API function)
    finished = [x for x in h2h_fixtures if (x.get("fixture",{}).get("status",{}).get("short") in {"FT","AET","PEN"})]

    if not finished:
        return {"ok": False, "__source": CIT_AF, "message": f"No competitive meetings found between these teams."}

    last = finished[0]
    fx   = last.get("fixture",{})
    teams= last.get("teams",{})
    goals= last.get("goals",{})
    return {
        "ok": True, "__source": CIT_AF,
        "when": fx.get("date"),
        "home": teams.get("home",{}).get("name"),
        "away": teams.get("away",{}).get("name"),
        "home_score": goals.get("home"),
        "away_score": goals.get("away"),
        "fixture_id": fx.get("id"),
        "competition": last.get("league",{}).get("name", ""),
        "total_h2h_found": len(finished)
    }

def tool_af_find_match_result(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find a specific match result between two teams (e.g., when team_a beat team_b).
    Args: team_a_id (int), team_b_id (int), team_a (str), team_b (str), winner (str), max_items (int=50)
    """
    # Support both ID and name inputs
    a = int(args.get("team_a_id") or 0) or af_id(args.get("team_a") or "")
    b = int(args.get("team_b_id") or 0) or af_id(args.get("team_b") or "")
    winner = (args.get("winner") or "").lower()
    max_items = int(args.get("max_items", 50))
    
    if not a or not b:
        return {"ok": False, "__source": CIT_AF, "message": "team_a_id/team_a and team_b_id/team_b required."}

    # Get H2H fixtures
    h2h_fixtures = AF.fixtures_h2h(a, b, max_items=max_items)
    
    # Keep finished games only
    finished = [x for x in h2h_fixtures if (x.get("fixture",{}).get("status",{}).get("short") in {"FT","AET","PEN"})]

    if not finished:
        return {"ok": False, "__source": CIT_AF, "message": f"No competitive meetings found between these teams."}

    # If winner is specified, filter for matches where that team won
    if winner:
        winner_matches = []
        for match in finished:
            teams = match.get("teams", {})
            goals = match.get("goals", {})
            home_team = teams.get("home", {}).get("name", "").lower()
            away_team = teams.get("away", {}).get("name", "").lower()
            home_score = goals.get("home", 0)
            away_score = goals.get("away", 0)
            
            # Check if the specified winner actually won this match
            if winner in home_team and home_score > away_score:
                winner_matches.append(match)
            elif winner in away_team and away_score > home_score:
                winner_matches.append(match)
        
        if winner_matches:
            finished = winner_matches
        else:
            return {"ok": False, "__source": CIT_AF, "message": f"No matches found where {winner} beat the opponent."}

    # Return the most recent match (or the most recent match where winner won)
    last = finished[0]
    fx = last.get("fixture", {})
    teams = last.get("teams", {})
    goals = last.get("goals", {})
    
    return {
        "ok": True, "__source": CIT_AF,
        "when": fx.get("date"),
        "home": teams.get("home", {}).get("name"),
        "away": teams.get("away", {}).get("name"),
        "home_score": goals.get("home"),
        "away_score": goals.get("away"),
        "fixture_id": fx.get("id"),
        "competition": last.get("league", {}).get("name", ""),
        "total_h2h_found": len(finished),
        "winner_filter": winner if winner else None
    }
