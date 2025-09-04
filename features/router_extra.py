# features/router_extra.py
import re
from providers.fd_wrap import league_table, team_matches, scorers
from providers.sofascore import SofaScoreProvider
from features.answers import fmt_table, fmt_form, fmt_scorers, fmt_squad, fmt_injuries

# Initialize SofaScore provider
sofa_provider = SofaScoreProvider()

# Pattern matching for different types of questions
P_TABLE   = re.compile(r"\b(table|standings|position)\b", re.I)
P_FORM    = re.compile(r"\b(form|last\s*5|recent)\b", re.I)
P_SCORERS = re.compile(r"\b(top\s*scorers?|goalscorers?)\b", re.I)
P_SQUAD   = re.compile(r"\b(squad|roster|players)\b", re.I)
P_GK      = re.compile(r"\b(goalkeepers?|gks?)\b", re.I)
P_DEF     = re.compile(r"\b(defenders?)\b", re.I)
P_MID     = re.compile(r"\b(midfielders?)\b", re.I)
P_FWD     = re.compile(r"\b(forwards?|strikers?)\b", re.I)
P_INJ     = re.compile(r"\b(injur|unavailable|sidelined|suspension)\b", re.I)

def route_related(text: str):
    t = text.lower()

    if P_TABLE.search(t):
        try:
            return fmt_table(league_table("laliga"))
        except Exception:
            return "Table data is unavailable at the moment."

    if P_FORM.search(t):
        try:
            ms = team_matches("Real Madrid", status="FINISHED", limit=10)
            return fmt_form(ms, k=5)
        except Exception:
            return "Recent form data is unavailable."

    if P_SCORERS.search(t):
        try:
            return fmt_scorers(scorers("laliga", limit=10))
        except Exception:
            return "Scorers data is unavailable."

    if P_INJ.search(t):
        try:
            return fmt_injuries(sofa_provider.team_injuries())
        except Exception:
            return "No injury information available."

    if P_SQUAD.search(t):
        try:
            return fmt_squad(sofa_provider.team_squad())
        except Exception:
            return "Squad data is unavailable."

    # positional squads
    if P_GK.search(t):
        try:
            return fmt_squad(sofa_provider.team_squad(), pos="goalkeeper")
        except Exception:
            return "No goalkeeper info available."
    if P_DEF.search(t):
        try:
            return fmt_squad(sofa_provider.team_squad(), pos="defender")
        except Exception:
            return "No defender info available."
    if P_MID.search(t):
        try:
            return fmt_squad(sofa_provider.team_squad(), pos="midfielder")
        except Exception:
            return "No midfielder info available."
    if P_FWD.search(t):
        try:
            return fmt_squad(sofa_provider.team_squad(), pos="forward")
        except Exception:
            return "No forward info available."

    return None  # let main router handle or refuse
