# orchestrator/tools_ext.py
from typing import Dict, Any
from providers import api_football as AF, sofa as SOFA, livescore_news as LSN, scorebat as SB, youtube as YT, elo as ELO, odds as ODDS

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
