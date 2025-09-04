# features/router_football.py
import re
from nlp.resolve import resolve_team, resolve_comp, resolve_player, TEAM_ALIASES
from providers.unified import fd_team_matches, fd_comp_table, fd_comp_scorers
from features.answers import fmt_table_top, fmt_recent_form, fmt_next_from_list, fmt_last_result
from utils.formatting import md_escape

# Pattern matching for different types of football questions
P_STANDINGS = re.compile(r"\b(table|standings|position|rank)\b", re.I)
P_FORM      = re.compile(r"\b(form|last\s*\d+|recent)\b", re.I)
P_NEXT      = re.compile(r"\b(next|upcoming|schedule)\b", re.I)  # Removed 'fixture' and 'game' to avoid conflicts
P_LAST      = re.compile(r"\b(last|previous|recent|happened)\b.*\b(match|game|score|result|fixture)\b", re.I)
P_SCORERS   = re.compile(r"\b(top\s*scorers?|goalscorers?)\b", re.I)
P_H2H       = re.compile(r"\b(vs|versus|against|h2h|head\s*to\s*head)\b", re.I)  # Head-to-head matches

def route_football(text: str):
    """Route football-related questions to appropriate API calls"""
    
    # 0) Head-to-head matches (highest priority)
    if P_H2H.search(text) or " vs " in text.lower():
        # Try to extract team names from the text
        from nlp.resolve import TEAM_ALIASES
        
        # Look for team names in the text
        found_teams = []
        for alias, team_id in TEAM_ALIASES.items():
            if alias in text.lower():
                found_teams.append((alias, team_id))
        
        if len(found_teams) >= 2:
            # We found at least 2 teams, this is a head-to-head question
            team1_name, team1_id = found_teams[0]
            team2_name, team2_id = found_teams[1]
            
            try:
                # Get recent matches for both teams to find their last meeting
                from providers.unified import fd_team_matches
                
                # Get recent matches for both teams
                team1_matches = fd_team_matches(team1_id, status="FINISHED", limit=50)
                team2_matches = fd_team_matches(team2_id, status="FINISHED", limit=50)
                
                # Find matches where they played each other
                h2h_matches = []
                for match in team1_matches:
                    home_id = match.get("homeTeam", {}).get("id")
                    away_id = match.get("awayTeam", {}).get("id")
                    
                    if (home_id == team1_id and away_id == team2_id) or (home_id == team2_id and away_id == team1_id):
                        h2h_matches.append(match)
                
                if h2h_matches:
                    # Sort by date (most recent first)
                    h2h_matches.sort(key=lambda x: x["utcDate"], reverse=True)
                    latest_h2h = h2h_matches[0]
                    
                    # Format the head-to-head result
                    from utils.timeutil import fmt_abs
                    from utils.formatting import md_escape
                    
                    home_team = md_escape(latest_h2h["homeTeam"]["name"])
                    away_team = md_escape(latest_h2h["awayTeam"]["name"])
                    home_score = latest_h2h.get("score", {}).get("fullTime", {}).get("home", 0)
                    away_score = latest_h2h.get("score", {}).get("fullTime", {}).get("away", 0)
                    match_date = fmt_abs(latest_h2h["utcDate"])
                    
                    return f"⚽ *Last {team1_name.title()} vs {team2_name.title()}*\n\n{match_date}\n{home_team} {home_score}-{away_score} {away_team}"
                else:
                    return f"🤝 *{team1_name.title()} vs {team2_name.title()}*\n\nNo recent matches found between these teams. This could be because:\n• They haven't played recently\n• They're in different competitions\n• Data is temporarily unavailable"
            except Exception as e:
                return f"🤝 *{team1_name.title()} vs {team2_name.title()}*\n\nHead-to-head data temporarily unavailable. Please try:\n• `/last {team1_name}` - for {team1_name.title()}'s last result\n• `/last {team2_name}` - for {team2_name.title()}'s last result"
        
        elif len(found_teams) == 1:
            # Only found one team, ask for clarification
            team_name = found_teams[0][0]
            return f"🤝 *Head-to-Head Question*\n\nI found {team_name.title()} in your question. Please specify both teams clearly:\n• \"{team_name} vs [other team] last match\"\n• \"Last match between {team_name} and [other team]\"\n\nExamples:\n• \"Madrid vs Barcelona last match\"\n• \"Arsenal vs Chelsea last result\""
        
        else:
            # No teams found
            return "🤝 *Head-to-Head Question*\n\nI couldn't identify the teams in your question. Please specify both teams clearly:\n\nExamples:\n• \"Madrid vs Barcelona last match\"\n• \"Arsenal vs Chelsea last result\"\n• \"Last match between Bayern and Dortmund\""
    
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
            # Extract team name early for better error messages
            team_name = "this team"
            for alias, tid in TEAM_ALIASES.items():
                if tid == team_id and alias in text.lower():
                    team_name = alias.title()
                    break
            
            try:
                ms = fd_team_matches(team_id, status="FINISHED", limit=1)
                if ms:
                    return fmt_last_result(ms[0])
                else:
                    return f"⚽ *Last Match - {team_name}*\n\nNo recent match data found for {team_name}. This could be because:\n• The team hasn't played recently\n• Data is temporarily unavailable\n• Season hasn't started yet\n\nTry:\n• `/last` - for Madrid's last result\n• `/last barcelona` - for Barca's last result\n• `/last bayern` - for Bayern's last result"
            except Exception:
                return f"⚽ *Last Match - {team_name}*\n\nLast match data temporarily unavailable for {team_name}. Please try:\n• `/last` - for Madrid's last result\n• `/last barcelona` - for Barca's last result\n• `/last bayern` - for Bayern's last result"
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
