import re

TEAM_ALIASES = {
    "real madrid": 86, "rm": 86, "realmadrid": 86, "los blancos": 86,
    "barcelona": 81, "fc barcelona": 81, "barca": 81,
    "atletico": 78, "atleti": 78, "atletico madrid": 78,
    "real sociedad": 92, "sociedad": 92,
    "girona": 298, "sevilla": 559, "athletic club": 77, "athletic bilbao": 77,
    "manchester city": 65, "man city": 65, "city": 65,
    "arsenal": 57, "bayern": 5, "psg": 524, "liverpool": 64, "chelsea": 61,
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

# Simple player normalizer (pass-through if unknown)
def resolve_player_name(text: str) -> str | None:
    t = _norm(text)
    # common aliases
    if "cr7" in t or "ronaldo" in t:
        return "Cristiano Ronaldo"
    if "vini" in t or "vinicius" in t:
        return "Vinícius Júnior"
    if "bellingham" in t:
        return "Jude Bellingham"
    if "mbappe" in t or "mbappé" in t:
        return "Kylian Mbappé"
    # try "first last" present in user query
    parts = [p for p in t.split() if p.isalpha()]
    if len(parts) >= 2:
        return " ".join(w.capitalize() for w in parts[-2:])
    return None
