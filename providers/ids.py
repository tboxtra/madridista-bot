# providers/ids.py
# Comprehensive team name variations for AI-driven recognition
API_FOOTBALL_IDS = {
    # Real Madrid variations
    "real madrid": 541, "madrid": 541, "rm": 541, "realmadrid": 541, "los blancos": 541,
    
    # Arsenal variations
    "arsenal": 42, "gunners": 42, "afc arsenal": 42,
    
    # Barcelona variations
    "barcelona": 529, "barca": 529, "fc barcelona": 529, "blaugrana": 529, "barça": 529,
    
    # Atletico Madrid variations
    "atletico madrid": 530, "atletico": 530, "atleti": 530, "atm": 530, "atlético": 530,
    
    # Manchester City variations
    "manchester city": 50, "man city": 50, "city": 50, "mcfc": 50, "sky blues": 50,
    
    # Manchester United variations
    "manchester united": 33, "man united": 33, "man utd": 33, "united": 33, "mufc": 33, "man u": 33,
    
    # Liverpool variations
    "liverpool": 40, "lfc": 40, "reds": 40, "liverpool fc": 40,
    
    # Chelsea variations
    "chelsea": 49, "cfc": 49, "blues": 49, "chelsea fc": 49,
    
    # Tottenham variations
    "tottenham": 47, "spurs": 47, "tottenham hotspur": 47, "thfc": 47,
    
    # Bayern Munich variations
    "bayern munich": 157, "bayern": 157, "fc bayern": 157, "fc bayern munich": 157,
    
    # PSG variations
    "psg": 85, "paris saint germain": 85, "paris sg": 85, "paris": 85,
    
    # Juventus variations
    "juventus": 496, "juve": 496, "juventus fc": 496, "bianconeri": 496,
    
    # AC Milan variations
    "ac milan": 489, "milan": 489, "acm": 489, "rossoneri": 489,
    
    # Inter Milan variations
    "inter milan": 505, "inter": 505, "inter fc": 505, "nerazzurri": 505,
    
    # Napoli variations
    "napoli": 492, "ssc napoli": 492, "partenopei": 492,
    
    # Roma variations
    "roma": 497, "as roma": 497, "giallorossi": 497,
    
    # Lazio variations
    "lazio": 487, "ss lazio": 487, "biancocelesti": 487,
    
    # Borussia Dortmund variations
    "borussia dortmund": 165, "dortmund": 165, "bvb": 165, "bvb 09": 165,
    
    # Leipzig variations
    "leipzig": 721, "rb leipzig": 721, "red bull leipzig": 721,
    
    # Ajax variations
    "ajax": 194, "afc ajax": 194, "ajax amsterdam": 194,
    
    # Porto variations
    "porto": 503, "fc porto": 503, "dragões": 503,
    
    # Benfica variations
    "benfica": 498, "sl benfica": 498, "águias": 498,
    
    # Celtic variations
    "celtic": 247, "celtic fc": 247, "bhoys": 247,
    
    # Rangers variations
    "rangers": 257, "rangers fc": 257, "gers": 257,
    
    # Sevilla variations
    "sevilla": 559, "sevilla fc": 559, "sevillistas": 559,
    
    # Valencia variations
    "valencia": 532, "valencia cf": 532, "che": 532,
    
    # Real Sociedad variations
    "real sociedad": 548, "sociedad": 548, "real soc": 548,
    
    # Athletic Bilbao variations
    "athletic bilbao": 531, "bilbao": 531, "athletic": 531, "leones": 531,
    
    # Villarreal variations
    "villarreal": 533, "villarreal cf": 533, "submarino amarillo": 533,
    
    # Betis variations
    "betis": 543, "real betis": 543, "verdiblancos": 543,
}

def af_id(name: str) -> int:
    """Get API-Football team ID from team name."""
    return API_FOOTBALL_IDS.get((name or "").lower().strip(), 0)
