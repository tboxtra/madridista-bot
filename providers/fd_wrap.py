from providers.unified import fd_comp_table, fd_comp_scorers, fd_team_matches
from nlp.resolve import resolve_comp, resolve_team

def league_table(comp_name: str):
    """Get league table for a competition"""
    comp_id = resolve_comp(comp_name)
    return fd_comp_table(comp_id)

def team_matches(team_name: str, status: str = None, limit: int = 10):
    """Get matches for a team"""
    team_id = resolve_team(team_name)
    return fd_team_matches(team_id, status, limit)

def scorers(comp_name: str, limit: int = 10):
    """Get top scorers for a competition"""
    comp_id = resolve_comp(comp_name)
    return fd_comp_scorers(comp_id, limit)
