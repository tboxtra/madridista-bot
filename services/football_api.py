import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FootballAPIService:
    """Service for fetching football data from various APIs"""
    
    def __init__(self):
        # API Keys - these should be set in environment variables
        self.football_data_key = os.getenv('FOOTBALL_DATA_API_KEY')
        self.api_football_key = os.getenv('API_FOOTBALL_KEY')
        
        # Base URLs
        self.football_data_base = "http://api.football-data.org/v4"
        self.api_football_base = "https://v3.football.api-sports.io"
        
        # Real Madrid specific IDs
        self.real_madrid_id = 86  # Football-Data.org ID for Real Madrid
        self.la_liga_id = 2014    # La Liga competition ID
        
        # Log API key status
        if self.football_data_key:
            logger.info("Football-Data.org API key configured")
        else:
            logger.warning("Football-Data.org API key not configured - using fallback data")
        
        if self.api_football_key:
            logger.info("API-Football key configured")
        else:
            logger.warning("API-Football key not configured - using fallback data")
    
    async def get_real_madrid_info(self) -> Dict[str, Any]:
        """Get comprehensive Real Madrid information"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback data")
            return self._get_fallback_madrid_info()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                # Get team info
                team_url = f"{self.football_data_base}/teams/{self.real_madrid_id}"
                async with session.get(team_url, headers=headers) as response:
                    if response.status == 200:
                        team_data = await response.json()
                        logger.info("Successfully fetched live Real Madrid data")
                        return {
                            'name': team_data.get('name', 'Real Madrid'),
                            'founded': team_data.get('founded', 1902),
                            'venue': team_data.get('venue', 'Santiago Bernabéu'),
                            'website': team_data.get('website', ''),
                            'crest': team_data.get('crest', ''),
                            'colors': team_data.get('clubColors', 'White'),
                            'last_updated': team_data.get('lastUpdated', ''),
                            'source': 'Live API'
                        }
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_madrid_info()
        except Exception as e:
            logger.error(f"Error fetching Real Madrid info: {e}")
            return self._get_fallback_madrid_info()
    
    def _get_fallback_madrid_info(self) -> Dict[str, Any]:
        """Get fallback Real Madrid information"""
        return {
            'name': 'Real Madrid Club de Fútbol',
            'founded': 1902,
            'venue': 'Santiago Bernabéu',
            'website': 'www.realmadrid.com',
            'crest': '',
            'colors': 'White and Gold',
            'last_updated': datetime.now().isoformat(),
            'source': 'Fallback Data'
        }
    
    async def get_real_madrid_squad(self) -> List[Dict[str, Any]]:
        """Get current Real Madrid squad"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback squad data")
            return self._get_fallback_squad()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                squad_url = f"{self.football_data_base}/teams/{self.real_madrid_id}"
                async with session.get(squad_url, headers=headers) as response:
                    if response.status == 200:
                        team_data = await response.json()
                        squad = team_data.get('squad', [])
                        logger.info(f"Successfully fetched live squad data: {len(squad)} players")
                        
                        # Process squad data
                        processed_squad = []
                        for player in squad:
                            processed_squad.append({
                                'name': player.get('name', ''),
                                'position': player.get('position', ''),
                                'nationality': player.get('nationality', ''),
                                'age': player.get('age', 0),
                                'shirt_number': player.get('shirtNumber', ''),
                                'date_of_birth': player.get('dateOfBirth', ''),
                                'source': 'Live API'
                            })
                        
                        return processed_squad
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_squad()
        except Exception as e:
            logger.error(f"Error fetching Real Madrid squad: {e}")
            return self._get_fallback_squad()
    
    def _get_fallback_squad(self) -> List[Dict[str, Any]]:
        """Get fallback squad data"""
        from data.football_knowledge import REAL_MADRID_FACTS
        
        squad = []
        for position, players in REAL_MADRID_FACTS["current_squad_2024"].items():
            for player in players:
                squad.append({
                    'name': player,
                    'position': position.rstrip('s').title(),
                    'nationality': 'Various',
                    'age': 0,
                    'shirt_number': '',
                    'date_of_birth': '',
                    'source': 'Fallback Data'
                })
        
        logger.info(f"Returning fallback squad data: {len(squad)} players")
        return squad
    
    async def get_real_madrid_matches(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent and upcoming Real Madrid matches"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback match data")
            return self._get_fallback_matches()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                # Get matches with better date filtering
                matches_url = f"{self.football_data_base}/teams/{self.real_madrid_id}/matches"
                
                # Get more matches initially to filter properly
                params = {
                    'limit': 20,  # Get more to filter properly
                    'dateFrom': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # Recent past
                    'dateTo': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')   # Near future
                }
                
                async with session.get(matches_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        matches_data = await response.json()
                        all_matches = matches_data.get('matches', [])
                        logger.info(f"Successfully fetched live match data: {len(all_matches)} matches")
                        
                        # Process and sort matches by date
                        processed_matches = []
                        for match in all_matches:
                            match_date = datetime.fromisoformat(match.get('utcDate', '').replace('Z', '+00:00'))
                            processed_matches.append({
                                'home_team': match.get('homeTeam', {}).get('name', ''),
                                'away_team': match.get('awayTeam', {}).get('name', ''),
                                'home_score': match.get('score', {}).get('fullTime', {}).get('home'),
                                'away_score': match.get('score', {}).get('fullTime', {}).get('away'),
                                'date': match.get('utcDate', ''),
                                'match_date': match_date,  # Add parsed date for sorting
                                'competition': match.get('competition', {}).get('name', ''),
                                'status': match.get('status', ''),
                                'venue': match.get('venue', ''),
                                'source': 'Live API'
                            })
                        
                        # Sort by date (most recent first, then upcoming)
                        processed_matches.sort(key=lambda x: x['match_date'], reverse=True)
                        
                        # Return only the requested limit
                        return processed_matches[:limit]
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_matches()
        except Exception as e:
            logger.error(f"Error fetching Real Madrid matches: {e}")
            return self._get_fallback_matches()
    
    def _get_fallback_matches(self) -> List[Dict[str, Any]]:
        """Get fallback match data"""
        # Return some recent/upcoming matches
        fallback_matches = [
            {
                'home_team': 'Real Madrid',
                'away_team': 'Barcelona',
                'home_score': 2,
                'away_score': 1,
                'date': '2024-04-21T20:00:00Z',
                'competition': 'La Liga',
                'status': 'FINISHED',
                'venue': 'Santiago Bernabéu',
                'source': 'Fallback Data'
            },
            {
                'home_team': 'Real Madrid',
                'away_team': 'Manchester City',
                'home_score': None,
                'away_score': None,
                'date': '2024-05-01T20:00:00Z',
                'competition': 'Champions League',
                'status': 'SCHEDULED',
                'venue': 'Santiago Bernabéu',
                'source': 'Fallback Data'
            }
        ]
        
        logger.info(f"Returning fallback match data: {len(fallback_matches)} matches")
        return fallback_matches
    
    async def get_la_liga_standings(self) -> List[Dict[str, Any]]:
        """Get current La Liga standings"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback standings data")
            return self._get_fallback_standings()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                standings_url = f"{self.football_data_base}/competitions/{self.la_liga_id}/standings"
                async with session.get(standings_url, headers=headers) as response:
                    if response.status == 200:
                        standings_data = await response.json()
                        standings = standings_data.get('standings', [])
                        logger.info("Successfully fetched live standings data")
                        
                        if standings:
                            table = standings[0].get('table', [])
                            processed_table = []
                            
                            for position in table:
                                processed_table.append({
                                    'position': position.get('position', 0),
                                    'team': position.get('team', {}).get('name', ''),
                                    'played': position.get('playedGames', 0),
                                    'won': position.get('won', 0),
                                    'drawn': position.get('draw', 0),
                                    'lost': position.get('lost', 0),
                                    'goals_for': position.get('goalsFor', 0),
                                    'goals_against': position.get('goalsAgainst', 0),
                                    'points': position.get('points', 0),
                                    'source': 'Live API'
                                })
                            
                            return processed_table
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_standings()
        except Exception as e:
            logger.error(f"Error fetching La Liga standings: {e}")
            return self._get_fallback_standings()
    
    def _get_fallback_standings(self) -> List[Dict[str, Any]]:
        """Get fallback standings data"""
        fallback_standings = [
            {'position': 1, 'team': 'Real Madrid', 'played': 30, 'won': 24, 'drawn': 6, 'lost': 0, 'goals_for': 65, 'goals_against': 18, 'points': 78, 'source': 'Fallback Data'},
            {'position': 2, 'team': 'Barcelona', 'played': 30, 'won': 21, 'drawn': 7, 'lost': 2, 'goals_for': 62, 'goals_against': 34, 'points': 70, 'source': 'Fallback Data'},
            {'position': 3, 'team': 'Girona', 'played': 30, 'won': 20, 'drawn': 5, 'lost': 5, 'goals_for': 62, 'goals_against': 35, 'points': 65, 'source': 'Fallback Data'},
            {'position': 4, 'team': 'Atlético Madrid', 'played': 30, 'won': 18, 'drawn': 4, 'lost': 8, 'goals_for': 55, 'goals_against': 35, 'points': 58, 'source': 'Fallback Data'},
            {'position': 5, 'team': 'Athletic Bilbao', 'played': 30, 'won': 16, 'drawn': 8, 'lost': 6, 'goals_for': 50, 'goals_against': 28, 'points': 56, 'source': 'Fallback Data'}
        ]
        
        logger.info(f"Returning fallback standings data: {len(fallback_standings)} teams")
        return fallback_standings
    
    def format_match_result(self, match: Dict[str, Any]) -> str:
        """Format match data into readable text"""
        source_indicator = "🟢" if match.get('source') == 'Live API' else "🟡"
        
        if match['status'] == 'FINISHED':
            return f"{source_indicator} 🏆 {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']} ({match['competition']})"
        elif match['status'] == 'SCHEDULED':
            try:
                match_date = datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
                return f"{source_indicator} 📅 {match['home_team']} vs {match['away_team']} - {match_date.strftime('%d %b %Y')} ({match['competition']})"
            except:
                return f"{source_indicator} 📅 {match['home_team']} vs {match['away_team']} - TBD ({match['competition']})"
        else:
            return f"{source_indicator} ⚽ {match['home_team']} vs {match['away_team']} - {match['status']} ({match['competition']})"
    
    def format_standings(self, standings: List[Dict[str, Any]], limit: int = 5) -> str:
        """Format standings into readable text"""
        if not standings:
            return "No standings data available"
        
        source_indicator = "🟢 Live Data" if standings[0].get('source') == 'Live API' else "🟡 Fallback Data"
        
        result = f"🏆 **La Liga Standings (Top {min(limit, len(standings))})** {source_indicator}\n\n"
        for i, team in enumerate(standings[:limit], 1):
            result += f"{i}. {team['team']} - {team['points']} pts ({team['played']}P {team['won']}W {team['drawn']}D {team['lost']}L)\n"
        
        return result
