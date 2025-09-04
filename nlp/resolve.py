# nlp/resolve.py
import re

# Minimal seeds. You can expand incrementally.
TEAM_ALIASES = {
  # Real Madrid priority
  "real madrid": 86, "rm": 86, "realmadrid": 86, "los blancos": 86, "madrid": 86,
  # Example rivals
  "barcelona": 81, "fc barcelona": 81, "barca": 81, "barça": 81,
  "atletico": 78, "atletico madrid": 78, "atleti": 78, "atlético": 78,
  "sevilla": 559, "valencia": 95, "athletic": 77, "athletic bilbao": 77,
  # Premier League
  "manchester united": 66, "man utd": 66, "united": 66,
  "manchester city": 65, "man city": 65, "city": 65,
  "arsenal": 57, "chelsea": 61, "liverpool": 64, "tottenham": 73,
  # Serie A
  "juventus": 109, "inter": 108, "milan": 98, "ac milan": 98,
  "napoli": 492, "roma": 100, "atalanta": 102,
  # Bundesliga
  "bayern munich": 5, "bayern": 5, "dortmund": 4, "bvb": 4,
  "leipzig": 173, "leverkusen": 161, "bayer": 161,
  # Ligue 1
  "psg": 524, "paris": 524, "marseille": 516, "lyon": 80,
  "monaco": 548, "nice": 522, "lille": 521,
}

COMP_ALIASES = {
  # LaLiga priority
  "laliga": 2014, "la liga": 2014, "spain la liga": 2014, "primera": 2014,
  # UEFA competitions
  "ucl": 2001, "champions league": 2001, "uefa champions": 2001,
  "europa": 2002, "uefa europa": 2002, "europa league": 2002,
  "copa del rey": 2010, "copa": 2010, "king's cup": 2010,
  # Other top leagues
  "premier league": 2021, "epl": 2021, "english premier": 2021,
  "serie a": 2019, "italian serie": 2019, "bundesliga": 2002, "german bundesliga": 2002,
  "ligue 1": 2015, "french ligue": 2015, "france ligue": 2015,
  # National cups
  "fa cup": 2000, "english fa cup": 2000, "dfb pokal": 2001, "german cup": 2001,
  "coppa italia": 2002, "italian cup": 2002, "coupe de france": 2003, "french cup": 2003,
}

PLAYER_HINTS = {
  # lightweight: we only need a name string; detailed IDs can come later
  "ronaldo": "cristiano ronaldo", "cr7": "cristiano ronaldo",
  "vini": "vinícius júnior", "vinicius": "vinícius júnior", "vinícius": "vinícius júnior",
  "bellingham": "jude bellingham", "jude": "jude bellingham",
  "benzema": "karim benzema", "mbappe": "kylian mbappé", "mbappé": "kylian mbappé",
  "haaland": "erling haaland", "erling": "erling haaland",
  "messi": "lionel messi", "leo": "lionel messi",
}

def norm(s: str) -> str:
  return re.sub(r"\s+", " ", s.lower().strip())

def resolve_team(text: str):
  t = norm(text)
  for alias, tid in TEAM_ALIASES.items():
    if alias in t: return tid
  # default priority: Real Madrid
  if any(k in t for k in ["match", "game", "fixture", "table", "standing", "form", "next", "last"]) and "barca" not in t:
    return 86
  return None

def resolve_comp(text: str):
  t = norm(text)
  for alias, cid in COMP_ALIASES.items():
    if alias in t: return cid
  # default priority: LaLiga
  return 2014

def resolve_player(text: str):
  t = norm(text)
  for alias, pname in PLAYER_HINTS.items():
    if alias in t: return pname
  # if user typed a full name, pass it through (basic heuristic)
  if len(t.split()) >= 2: return t
  return None
