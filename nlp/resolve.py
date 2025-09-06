import re

TEAM_ALIASES = {
    "real madrid": 86, "rm": 86, "realmadrid": 86, "los blancos": 86,
    "barcelona": 81, "fc barcelona": 81, "barca": 81,
    "atletico": 78, "atleti": 78, "atletico madrid": 78
}

COMP_ALIASES = {
    "laliga": 2014, "la liga": 2014, "champions league": 2001, "ucl": 2001,
    "copa del rey": 2010, "premier league": 2021, "epl": 2021,
    "serie a": 2019, "bundesliga": 2002, "ligue 1": 2015
}

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())

def resolve_team(text: str) -> int | None:
    t = _norm(text)
    for alias, tid in TEAM_ALIASES.items():
        if alias in t:
            return tid
    # default to Madrid if the user didn't name a team
    return 86

def resolve_comp(text: str) -> int | None:
    t = _norm(text)
    for alias, cid in COMP_ALIASES.items():
        if alias in t:
            return cid
    # default to LaLiga
    return 2014
