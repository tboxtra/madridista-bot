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
        
    async def get_real_madrid_info(self) -> Dict[str, Any]:
        """Get comprehensive Real Madrid information"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key} if self.football_data_key else {}
                
                # Get team info
                team_url = f"{self.football_data_base}/teams/{self.real_madrid_id}"
                async with session.get(team_url, headers=headers) as response:
                    if response.status == 200:
                        team_data = await response.json()
                        return {
                            'name': team_data.get('name', 'Real Madrid'),
                            'founded': team_data.get('founded', 1902),
                            'venue': team_data.get('venue', 'Santiago Bernabéu'),
                            'website': team_data.get('website', ''),
                            'crest': team_data.get('crest', ''),
                            'colors': team_data.get('clubColors', 'White'),
                            'last_updated': team_data.get('lastUpdated', '')
                        }
        except Exception as e:
            logger.error(f"Error fetching Real Madrid info: {e}")
            return {}
    
    async def get_real_madrid_squad(self) -> List[Dict[str, Any]]:
        """Get current Real Madrid squad"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key} if self.football_data_key else {}
                
                squad_url = f"{self.football_data_base}/teams/{self.real_madrid_id}"
                async with session.get(squad_url, headers=headers) as response:
                    if response.status == 200:
                        team_data = await response.json()
                        squad = team_data.get('squad', [])
                        
                        # Process squad data
                        processed_squad = []
                        for player in squad:
                            processed_squad.append({
                                'name': player.get('name', ''),
                                'position': player.get('position', ''),
                                'nationality': player.get('nationality', ''),
                                'age': player.get('age', 0),
                                'shirt_number': player.get('shirtNumber', ''),
                                'date_of_birth': player.get('dateOfBirth', '')
                            })
                        
                        return processed_squad
        except Exception as e:
            logger.error(f"Error fetching Real Madrid squad: {e}")
            return []
    
    async def get_real_madrid_matches(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent and upcoming Real Madrid matches"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key} if self.football_data_key else {}
                
                # Get recent matches
                matches_url = f"{self.football_data_base}/teams/{self.real_madrid_id}/matches"
                params = {
                    'limit': limit,
                    'dateFrom': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'dateTo': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                }
                
                async with session.get(matches_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        matches_data = await response.json()
                        matches = matches_data.get('matches', [])
                        
                        processed_matches = []
                        for match in matches:
                            processed_matches.append({
                                'home_team': match.get('homeTeam', {}).get('name', ''),
                                'away_team': match.get('awayTeam', {}).get('name', ''),
                                'home_score': match.get('score', {}).get('fullTime', {}).get('home'),
                                'away_score': match.get('score', {}).get('fullTime', {}).get('away'),
                                'date': match.get('utcDate', ''),
                                'competition': match.get('competition', {}).get('name', ''),
                                'status': match.get('status', ''),
                                'venue': match.get('venue', '')
                            })
                        
                        return processed_matches
        except Exception as e:
            logger.error(f"Error fetching Real Madrid matches: {e}")
            return []
    
    async def get_la_liga_standings(self) -> List[Dict[str, Any]]:
        """Get current La Liga standings"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key} if self.football_data_key else {}
                
                standings_url = f"{self.football_data_base}/competitions/{self.la_liga_id}/standings"
                async with session.get(standings_url, headers=headers) as response:
                    if response.status == 200:
                        standings_data = await response.json()
                        standings = standings_data.get('standings', [])
                        
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
                                    'points': position.get('points', 0)
                                })
                            
                            return processed_table
        except Exception as e:
            logger.error(f"Error fetching La Liga standings: {e}")
            return []
    
    async def get_player_stats(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player statistics (if available)"""
        try:
            # This would require a more comprehensive API
            # For now, return basic info
            return {
                'name': player_name,
                'note': 'Detailed stats require premium API access'
            }
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return None
    
    async def get_champions_league_info(self) -> Dict[str, Any]:
        """Get Champions League information for Real Madrid"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key} if self.football_data_key else {}
                
                # Champions League ID is 2000
                cl_url = f"{self.football_data_base}/competitions/2000/teams"
                async with session.get(cl_url, headers=headers) as response:
                    if response.status == 200:
                        cl_data = await response.json()
                        teams = cl_data.get('teams', [])
                        
                        # Find Real Madrid
                        real_madrid = next((team for team in teams if team.get('id') == self.real_madrid_id), None)
                        
                        if real_madrid:
                            return {
                                'competition': 'UEFA Champions League',
                                'season': cl_data.get('season', {}).get('startDate', ''),
                                'group': real_madrid.get('group', ''),
                                'status': 'Active'
                            }
        except Exception as e:
            logger.error(f"Error fetching Champions League info: {e}")
            return {}
    
    def format_match_result(self, match: Dict[str, Any]) -> str:
        """Format match data into readable text"""
        if match['status'] == 'FINISHED':
            return f"🏆 {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']} ({match['competition']})"
        elif match['status'] == 'SCHEDULED':
            match_date = datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
            return f"📅 {match['home_team']} vs {match['away_team']} - {match_date.strftime('%d %b %Y')} ({match['competition']})"
        else:
            return f"⚽ {match['home_team']} vs {match['away_team']} - {match['status']} ({match['competition']})"
    
    def format_standings(self, standings: List[Dict[str, Any]], limit: int = 5) -> str:
        """Format standings into readable text"""
        if not standings:
            return "No standings data available"
        
        result = "🏆 **La Liga Standings (Top 5)**\n\n"
        for i, team in enumerate(standings[:limit], 1):
            result += f"{i}. {team['team']} - {team['points']} pts ({team['played']}P {team['won']}W {team['drawn']}D {team['lost']}L)\n"
        
        return result
