# features/router_football.py
import re
from nlp.resolve import resolve_team, resolve_comp, resolve_player
from providers.unified import fd_team_matches, fd_comp_table, fd_comp_scorers
from features.answers import fmt_table_top, fmt_recent_form, fmt_next_from_list, fmt_last_result
from utils.formatting import md_escape

# Pattern matching for different types of football questions
P_STANDINGS = re.compile(r"\b(table|standings|position|rank)\b", re.I)
P_FORM      = re.compile(r"\b(form|last\s*\d+|recent)\b", re.I)
P_NEXT      = re.compile(r"\b(next|upcoming|fixture|game)\b", re.I)
P_LAST      = re.compile(r"\b(last|previous|recent)\b.*\b(match|game|score|result)\b", re.I)
P_SCORERS   = re.compile(r"\b(top\s*scorers?|goalscorers?)\b", re.I)

def route_football(text: str):
    """Route football-related questions to appropriate API calls"""
    
    # 1) league table
    if P_STANDINGS.search(text):
        comp_id = resolve_comp(text)  # default LaLiga
        try:
            table_data = fd_comp_table(comp_id)
            if table_data and "standings" in table_data:
                # Get competition name for title
                comp_name = "League Table"
                if "competition" in table_data:
                    comp_name = table_data["competition"].get("name", "League Table")
                return fmt_table_top(table_data, top=5, title=f"{comp_name} (Top 5)")
            else:
                return "📊 *League Table*\n\nTable data is temporarily unavailable. Please try:\n• `/table` - for LaLiga table\n• `/table premier league` - for EPL table\n• `/table ucl` - for Champions League table"
        except Exception:
            return "📊 *League Table*\n\nTable data is temporarily unavailable. Please try:\n• `/table` - for LaLiga table\n• `/table premier league` - for EPL table\n• `/table ucl` - for Champions League table"

    # 2) recent form / results
    if P_FORM.search(text):
        team_id = resolve_team(text)  # default Real Madrid
        if team_id:
            try:
                ms = fd_team_matches(team_id, status="FINISHED", limit=10)
                if ms:
                    return fmt_recent_form(ms, k=5)
                else:
                    return "📈 *Recent Form*\n\nNo recent results found. Please try:\n• `/form` - for Madrid's recent form\n• `/form barcelona` - for Barca's recent form\n• `/form bayern` - for Bayern's recent form"
            except Exception:
                return "📈 *Recent Form*\n\nRecent results temporarily unavailable. Please try:\n• `/form` - for Madrid's recent form\n• `/form barcelona` - for Barca's recent form\n• `/form bayern` - for Bayern's recent form"
        else:
            return "📈 *Recent Form*\n\nPlease specify a team for form information. Try:\n• `/form` - for Madrid's recent form\n• `/form barcelona` - for Barca's recent form\n• `/form bayern` - for Bayern's recent form"

    # 3) next fixture
    if P_NEXT.search(text):
        team_id = resolve_team(text)  # default Real Madrid
        if team_id:
            try:
                ms = fd_team_matches(team_id, status=None, limit=20)
                if ms:
                    return fmt_next_from_list(ms)
                else:
                    return "📅 *Next Fixture*\n\nNo upcoming fixtures found. Please try:\n• `/next` - for Madrid's next fixture\n• `/next barcelona` - for Barca's next fixture\n• `/next bayern` - for Bayern's next fixture"
            except Exception:
                return "📅 *Next Fixture*\n\nNext fixture temporarily unavailable. Please try:\n• `/next` - for Madrid's next fixture\n• `/next barcelona` - for Barca's next fixture\n• `/next bayern` - for Bayern's next fixture"
        else:
            return "📅 *Next Fixture*\n\nPlease specify a team for fixture information. Try:\n• `/next` - for Madrid's next fixture\n• `/next barcelona` - for Barca's next fixture\n• `/next bayern` - for Bayern's next fixture"

    # 4) last match (single line score)
    if P_LAST.search(text):
        team_id = resolve_team(text)
        if team_id:
            try:
                ms = fd_team_matches(team_id, status="FINISHED", limit=1)
                if ms:
                    return fmt_last_result(ms[0])
                else:
                    return "⚽ *Last Match*\n\nNo recent match found. Please try:\n• `/last` - for Madrid's last result\n• `/last barcelona` - for Barca's last result\n• `/last bayern` - for Bayern's last result"
            except Exception:
                return "⚽ *Last Match*\n\nLast match data temporarily unavailable. Please try:\n• `/last` - for Madrid's last result\n• `/last barcelona` - for Barca's last result\n• `/last bayern` - for Bayern's last result"
        else:
            return "⚽ *Last Match*\n\nPlease specify a team for match information. Try:\n• `/last` - for Madrid's last result\n• `/last barcelona` - for Barca's last result\n• `/last bayern` - for Bayern's last result"

    # 5) top scorers by competition (default LaLiga)
    if P_SCORERS.search(text):
        comp_id = resolve_comp(text)
        try:
            js = fd_comp_scorers(comp_id, limit=10)
            if js and "scorers" in js:
                items = js.get("scorers", [])[:5]
                if items:
                    lines = ["*Top Scorers*"]
                    for s in items:
                        lines.append(f"{md_escape(s['player']['name'])} — {s['numberOfGoals']}g ({md_escape(s['team']['name'])})")
                    return "\n".join(lines)
                else:
                    return "🥅 *Top Scorers*\n\nNo scorers data available. Please try:\n• `/scorers` - for LaLiga top scorers\n• `/scorers ucl` - for Champions League scorers\n• `/scorers premier league` - for EPL scorers"
            else:
                return "🥅 *Top Scorers*\n\nScorers data temporarily unavailable. Please try:\n• `/scorers` - for LaLiga top scorers\n• `/scorers ucl` - for Champions League scorers\n• `/scorers premier league` - for EPL scorers"
        except Exception:
            return "🥅 *Top Scorers*\n\nScorers data temporarily unavailable. Please try:\n• `/scorers` - for LaLiga top scorers\n• `/scorers ucl` - for Champions League scorers\n• `/scorers premier league` - for EPL scorers"

    return None  # let other routers handle
