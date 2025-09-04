"""
Football Knowledge Base - Accurate data for Real Madrid and football
This provides fallback data when APIs are not available
"""

REAL_MADRID_FACTS = {
    "club_info": {
        "name": "Real Madrid Club de Fútbol",
        "founded": 1902,
        "stadium": "Santiago Bernabéu",
        "capacity": 81044,
        "city": "Madrid",
        "country": "Spain",
        "colors": "White and Gold",
        "nicknames": ["Los Blancos", "Los Merengues", "La Casa Blanca"],
        "motto": "¡Hala Madrid y nada más!"
    },
    
    "achievements": {
        "la_liga_titles": 36,
        "copa_del_rey": 20,
        "champions_league": 14,
        "uefa_super_cup": 5,
        "fifa_club_world_cup": 5,
        "supercopa_de_espana": 13
    },
    
    "current_squad_2024": {
        "goalkeepers": [
            "Thibaut Courtois", "Andriy Lunin", "Kepa Arrizabalaga"
        ],
        "defenders": [
            "Dani Carvajal", "Éder Militão", "David Alaba", "Antonio Rüdiger",
            "Ferland Mendy", "Fran García", "Nacho Fernández", "Lucas Vázquez"
        ],
        "midfielders": [
            "Luka Modrić", "Toni Kroos", "Federico Valverde", "Eduardo Camavinga",
            "Aurélien Tchouaméni", "Jude Bellingham", "Arda Güler", "Dani Ceballos"
        ],
        "forwards": [
            "Vinícius Júnior", "Rodrygo", "Joselu", "Brahim Díaz",
            "Endrick", "Arda Güler"
        ]
    },
    
    "legendary_players": {
        "cristiano_ronaldo": {
            "years": "2009-2018",
            "goals": 450,
            "titles": "4 Champions League, 2 La Liga, 2 Copa del Rey",
            "achievements": "4x Ballon d'Or at Madrid, 4x European Golden Shoe"
        },
        "raul_gonzalez": {
            "years": "1994-2010",
            "goals": 323,
            "titles": "6 La Liga, 3 Champions League, 2 Copa del Rey",
            "nickname": "El Capitán"
        },
        "zinedine_zidane": {
            "years": "2001-2006",
            "goals": 49,
            "titles": "1 Champions League, 1 La Liga, 1 Copa del Rey",
            "achievements": "2002 Champions League final winner"
        },
        "iker_casillas": {
            "years": "1999-2015",
            "clean_sheets": 264,
            "titles": "5 La Liga, 3 Champions League, 2 Copa del Rey",
            "nickname": "San Iker"
        }
    },
    
    "current_season_2024": {
        "manager": "Carlo Ancelotti",
        "captain": "Nacho Fernández",
        "vice_captain": "Luka Modrić",
        "formation": "4-3-3",
        "key_players": ["Jude Bellingham", "Vinícius Júnior", "Federico Valverde"]
    },
    
    "rivalries": {
        "el_clasico": {
            "opponent": "FC Barcelona",
            "first_meeting": 1902,
            "total_matches": "Over 280",
            "madrid_wins": "Over 100",
            "barcelona_wins": "Over 100"
        },
        "madrid_derby": {
            "opponent": "Atlético Madrid",
            "first_meeting": 1929,
            "total_matches": "Over 200",
            "madrid_wins": "Over 100",
            "atletico_wins": "Over 50"
        }
    },
    
    "stadium_history": {
        "santiago_bernabeu": {
            "opened": 1947,
            "capacity": 81044,
            "surface": "Grass",
            "cost": "€1.17 billion (renovation)",
            "features": "Retractable roof, modern facilities, museum"
        }
    }
}

FOOTBALL_TERMS = {
    "positions": {
        "goalkeeper": "Player who defends the goal and can use hands",
        "defender": "Player who prevents opponents from scoring",
        "midfielder": "Player who controls the game and connects defense to attack",
        "forward": "Player who scores goals and creates attacking plays"
    },
    
    "competitions": {
        "la_liga": "Top Spanish football league, 20 teams, 38 matches per season",
        "champions_league": "Europe's premier club competition, featuring top teams",
        "copa_del_rey": "Spanish cup competition, knockout format",
        "europa_league": "Second-tier European competition",
        "conference_league": "Third-tier European competition"
    },
    
    "tactics": {
        "4-3-3": "Formation with 4 defenders, 3 midfielders, 3 forwards",
        "4-4-2": "Formation with 4 defenders, 4 midfielders, 2 forwards",
        "3-5-2": "Formation with 3 defenders, 5 midfielders, 2 forwards",
        "possession": "Style focused on keeping the ball",
        "counter_attack": "Style focused on quick transitions from defense to attack"
    }
}

LA_LIGA_TEAMS_2024 = [
    "Real Madrid", "Barcelona", "Atlético Madrid", "Athletic Bilbao",
    "Real Sociedad", "Girona", "Real Betis", "Las Palmas",
    "Rayo Vallecano", "Getafe", "Osasuna", "Villarreal",
    "Valencia", "Mallorca", "Alavés", "Celta Vigo",
    "Sevilla", "Cádiz", "Granada", "Almería"
]

CHAMPIONS_LEAGUE_HISTORY = {
    "total_titles": 14,
    "years_won": [
        1956, 1957, 1958, 1959, 1960, 1966, 1998, 2000,
        2002, 2014, 2016, 2017, 2018, 2022
    ],
    "final_appearances": 17,
    "consecutive_titles": "5 (1956-1960)",
    "recent_performance": "Winners in 2022, Semi-finalists in 2023"
}

def get_player_info(player_name: str) -> dict:
    """Get information about a specific player"""
    player_name_lower = player_name.lower()
    
    # Check current squad
    for position, players in REAL_MADRID_FACTS["current_squad_2024"].items():
        for player in players:
            if player_name_lower in player.lower():
                return {
                    "name": player,
                    "position": position.rstrip('s').title(),
                    "status": "Current player",
                    "team": "Real Madrid"
                }
    
    # Check legendary players
    for player_key, player_info in REAL_MADRID_FACTS["legendary_players"].items():
        if player_name_lower in player_key.lower() or player_name_lower in player_info.get("years", "").lower():
            return {
                "name": player_key.replace("_", " ").title(),
                "status": "Legend",
                "years": player_info["years"],
                "achievements": player_info["achievements"]
            }
    
    return {"name": player_name, "status": "Player not found in database"}

def get_competition_info(competition: str) -> dict:
    """Get information about a specific competition"""
    competition_lower = competition.lower()
    
    if "liga" in competition_lower or "la liga" in competition_lower:
        return {
            "name": "La Liga",
            "type": "Domestic League",
            "teams": 20,
            "matches": 38,
            "madrid_titles": REAL_MADRID_FACTS["achievements"]["la_liga_titles"]
        }
    elif "champions" in competition_lower or "ucl" in competition_lower:
        return {
            "name": "UEFA Champions League",
            "type": "European Competition",
            "madrid_titles": REAL_MADRID_FACTS["achievements"]["champions_league"],
            "history": CHAMPIONS_LEAGUE_HISTORY
        }
    elif "copa" in competition_lower or "king" in competition_lower:
        return {
            "name": "Copa del Rey",
            "type": "Domestic Cup",
            "madrid_titles": REAL_MADRID_FACTS["achievements"]["copa_del_rey"]
        }
    
    return {"name": competition, "status": "Competition not found in database"}

def get_recent_achievements() -> str:
    """Get recent Real Madrid achievements"""
    return f"""
🏆 **Recent Real Madrid Achievements**

**2023-24 Season:**
• La Liga: Champions
• Champions League: Semi-finals
• Supercopa de España: Winners

**2022-23 Season:**
• La Liga: 2nd place
• Champions League: Semi-finals
• Copa del Rey: Winners
• FIFA Club World Cup: Winners

**2021-22 Season:**
• La Liga: Champions
• Champions League: Champions
• Supercopa de España: Winners
"""

def get_banter_responses() -> dict:
    """Get banter responses for different situations"""
    return {
        "barcelona": [
            "😂 Barça fans still talking about that 5-0 from 2010? We've won 4 Champions Leagues since then!",
            "🤍 14 Champions League titles vs 5... need I say more?",
            "⚽ Messi left, we're still here winning trophies!",
            "🏆 We're the kings of Europe, they're the kings of excuses!"
        ],
        "atletico": [
            "🤍 Madrid is white, not red and white!",
            "🏆 36 La Liga titles vs 11... the numbers don't lie!",
            "⚽ We play at the Bernabéu, they play at the Metropolitano... enough said!",
            "🤣 Atleti fans still celebrating that one Champions League final appearance?"
        ],
        "champions_league": [
            "👑 14 Champions League titles - we're the undisputed kings of Europe!",
            "🏆 We've won more Champions Leagues than any other club combined!",
            "⚽ The Bernabéu is where European dreams come to die!",
            "🤍 Real Madrid and Champions League - name a better duo!"
        ],
        "general": [
            "🤍 ¡Hala Madrid y nada más!",
            "🏆 We're not just a club, we're a dynasty!",
            "⚽ Real Madrid - where legends are made!",
            "👑 Kings of Europe, Kings of Spain!"
        ]
    }
