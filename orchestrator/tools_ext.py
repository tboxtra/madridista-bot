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
    Get the most recent competitive result between two teams using API-Football fixtures.
    Args: team_a_id (int), team_b_id (int), team_a (str), team_b (str), days_back (int=1825)
    """
    # Support both ID and name inputs
    a = int(args.get("team_a_id") or 0) or af_id(args.get("team_a") or "")
    b = int(args.get("team_b_id") or 0) or af_id(args.get("team_b") or "")
    days_back = int(args.get("days_back", 1825))  # 5 years default
    
    if not a or not b:
        return {"ok": False, "__source": CIT_AF, "message": "team_a_id/team_a and team_b_id/team_b required."}

    # Pull last N fixtures for both teams and filter intersections
    fa = AF.fixtures_last(a, max_items=50)
    fb = AF.fixtures_last(b, max_items=50)
    
    # Index by fixture id for speed
    ids_b = {x.get("fixture",{}).get("id") for x in fb}
    inter = [x for x in fa if x.get("fixture",{}).get("id") in ids_b]

    # Fallback: filter by opponent id if no intersection found
    if not inter:
        inter = [x for x in fa if (x.get("teams",{}).get("home",{}).get("id")==b or
                                   x.get("teams",{}).get("away",{}).get("id")==b)]

    # Keep finished games only, newest first
    inter = [x for x in inter if (x.get("fixture",{}).get("status",{}).get("short") in {"FT","AET","PEN"})]
    inter.sort(key=lambda x: x.get("fixture",{}).get("date",""), reverse=True)

    if not inter:
        return {"ok": False, "__source": CIT_AF, "message": "No recent competitive meetings found."}

    last = inter[0]
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
        "fixture_id": fx.get("id")
    }
