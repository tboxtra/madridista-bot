import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
from utils.time_utils import (
    get_current_time, get_utc_now, format_time_until, 
    format_match_time, get_time_status, is_match_live,
    format_last_updated
)
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
            'last_updated': format_last_updated(),
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
        """Get recent and upcoming Real Madrid matches with priority on immediate upcoming"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback match data")
            return self._get_fallback_matches()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                # Get matches with focus on immediate upcoming
                matches_url = f"{self.football_data_base}/teams/{self.real_madrid_id}/matches"
                
                # Get more matches initially to filter properly - focus on immediate future
                params = {
                    'limit': 30,  # Get more to filter properly
                    'dateFrom': (get_current_time() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Yesterday
                    'dateTo': (get_current_time() + timedelta(days=14)).strftime('%Y-%m-%d')    # Next 2 weeks
                }
                
                async with session.get(matches_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        matches_data = await response.json()
                        all_matches = matches_data.get('matches', [])
                        logger.info(f"Successfully fetched live match data: {len(all_matches)} matches")
                        
                        # Process and prioritize matches by immediacy
                        processed_matches = []
                        
                        for match in all_matches:
                            try:
                                match_date_str = match.get('utcDate', '')
                                if not match_date_str:
                                    continue
                                
                                # Use new time utilities for better formatting
                                time_status = get_time_status(match_date_str)
                                time_until = format_time_until(match_date_str)
                                
                                processed_matches.append({
                                    'id': match.get('id', ''),  # Add match ID for live updates
                                    'home_team': match.get('homeTeam', {}).get('name', ''),
                                    'away_team': match.get('awayTeam', {}).get('name', ''),
                                    'home_score': match.get('score', {}).get('fullTime', {}).get('home'),
                                    'away_score': match.get('score', {}).get('fullTime', {}).get('away'),
                                    'date': match_date_str,
                                    'time_status': time_status,
                                    'time_until': time_until,
                                    'competition': match.get('competition', {}).get('name', ''),
                                    'status': match.get('status', ''),
                                    'venue': match.get('venue', ''),
                                    'source': 'Live API'
                                })
                            except Exception as e:
                                logger.warning(f"Error processing match date: {e}")
                                continue
                        
                        # Sort by priority: LIVE > Starting soon > Today > Recent > Upcoming
                        def match_priority(match):
                            time_status = match.get('time_status', '📅 Upcoming')
                            
                            # Live matches get highest priority
                            if '⚡ Live' in time_status:
                                return -1000
                            # Starting soon (15 minutes) gets high priority
                            elif '🚨 Starting soon' in time_status:
                                return -500
                            # Starting soon (1 hour) gets medium priority
                            elif '⏰ Starting soon' in time_status:
                                return -200
                            # Today/Tomorrow gets normal priority
                            elif '📅 Today/Tomorrow' in time_status:
                                return 0
                            # Upcoming gets lower priority
                            elif '📅 Upcoming' in time_status:
                                return 1000
                            # Finished matches get lowest priority
                            elif '🏁 Finished' in time_status:
                                return 2000
                            else:
                                return 1500
                        
                        processed_matches.sort(key=match_priority)
                        
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
        elif match['status'] == 'LIVE':
            return f"{source_indicator} 🔴 LIVE NOW! {match['home_team']} vs {match['away_team']} ({match['competition']})"
        elif match['status'] == 'SCHEDULED':
            try:
                match_date = datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
                now = datetime.now()
                time_diff = (match_date - now).total_seconds() / 60
                
                if time_diff <= 0:
                    # Match should be starting now
                    return f"{source_indicator} ⚡ STARTING NOW! {match['home_team']} vs {match['away_team']} ({match['competition']})"
                elif time_diff <= 30:
                    # Starting in next 30 minutes
                    return f"{source_indicator} ⚡ {match['home_team']} vs {match['away_team']} - Starting in {int(time_diff)} minutes! ({match['competition']})"
                elif time_diff <= 60:
                    # Starting in next hour
                    return f"{source_indicator} ⏰ {match['home_team']} vs {match['away_team']} - Starting in {int(time_diff)} minutes ({match['competition']})"
                elif time_diff <= 1440:  # 24 hours
                    # Starting today
                    hours = int(time_diff // 60)
                    minutes = int(time_diff % 60)
                    if hours > 0:
                        time_str = f"{hours}h {minutes}m"
                    else:
                        time_str = f"{minutes}m"
                    return f"{source_indicator} ⏰ {match['home_team']} vs {match['away_team']} - Starting in {time_str} ({match['competition']})"
                else:
                    # Starting in future days
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

    async def get_live_match_updates(self, match_id: str = None) -> Dict[str, Any]:
        """Get live match updates and commentary data"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback live data")
            return self._get_fallback_live_data()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                # If no specific match, get Real Madrid's live matches
                if not match_id:
                    matches = await self.get_real_madrid_matches(limit=10)
                    live_matches = [m for m in matches if m.get('status') == 'LIVE']
                    if not live_matches:
                        return {'status': 'no_live_matches', 'message': 'No live matches currently'}
                    
                    match_id = live_matches[0].get('id')
                
                # Get detailed match data
                match_url = f"{self.football_data_base}/matches/{match_id}"
                async with session.get(match_url, headers=headers) as response:
                    if response.status == 200:
                        match_data = await response.json()
                        
                        # Extract live information
                        live_info = {
                            'match_id': match_id,
                            'home_team': match_data.get('homeTeam', {}).get('name', ''),
                            'away_team': match_data.get('awayTeam', {}).get('name', ''),
                            'home_score': match_data.get('score', {}).get('fullTime', {}).get('home', 0),
                            'away_score': match_data.get('score', {}).get('fullTime', {}).get('home', 0),
                            'minute': match_data.get('minute', 0),
                            'status': match_data.get('status', ''),
                            'competition': match_data.get('competition', {}).get('name', ''),
                            'venue': match_data.get('venue', ''),
                            'last_updated': format_last_updated(),
                            'source': 'Live API'
                        }
                        
                        # Add match events if available
                        if 'goals' in match_data:
                            live_info['goals'] = match_data['goals']
                        if 'bookings' in match_data:
                            live_info['bookings'] = match_data['bookings']
                        if 'substitutions' in match_data:
                            live_info['substitutions'] = match_data['substitutions']
                        
                        logger.info(f"Successfully fetched live match updates for {live_info['home_team']} vs {live_info['away_team']}")
                        return live_info
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_live_data()
        except Exception as e:
            logger.error(f"Error fetching live match updates: {e}")
            return self._get_fallback_live_data()
    
    async def get_transfer_news(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest transfer news and rumors"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback transfer news")
            return self._get_fallback_transfer_news()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                # Get transfer news from competitions
                news_url = f"{self.football_data_base}/competitions/{self.la_liga_id}/news"
                params = {'limit': limit * 2}  # Get more to filter for Madrid-related news
                
                async with session.get(news_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        news_data = await response.json()
                        articles = news_data.get('articles', [])
                        
                        # Filter for Real Madrid related news
                        madrid_news = []
                        for article in articles:
                            title = article.get('title', '').lower()
                            content = article.get('content', '').lower()
                            
                            # Check if article mentions Real Madrid or related terms
                            madrid_keywords = ['real madrid', 'madrid', 'bernabeu', 'ancelotti', 'vinicius', 'bellingham', 'mbappe']
                            if any(keyword in title or keyword in content for keyword in madrid_keywords):
                                madrid_news.append({
                                    'title': article.get('title', ''),
                                    'summary': article.get('summary', ''),
                                    'url': article.get('url', ''),
                                    'published_at': article.get('publishedAt', ''),
                                    'source': 'Live API'
                                })
                        
                        logger.info(f"Found {len(madrid_news)} Madrid-related news articles")
                        return madrid_news[:limit]
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_transfer_news()
        except Exception as e:
            logger.error(f"Error fetching transfer news: {e}")
            return self._get_fallback_transfer_news()
    
    async def get_match_highlights(self, match_id: str) -> Dict[str, Any]:
        """Get match highlights and key moments"""
        if not self.football_data_key:
            logger.info("No API key - returning fallback highlights")
            return self._get_fallback_highlights()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'X-Auth-Token': self.football_data_key}
                
                # Get match highlights
                highlights_url = f"{self.football_data_base}/matches/{match_id}/highlights"
                async with session.get(highlights_url, headers=headers) as response:
                    if response.status == 200:
                        highlights_data = await response.json()
                        
                        highlights = {
                            'match_id': match_id,
                            'goals': highlights_data.get('goals', []),
                            'key_moments': highlights_data.get('keyMoments', []),
                            'cards': highlights_data.get('cards', []),
                            'substitutions': highlights_data.get('substitutions', []),
                            'source': 'Live API'
                        }
                        
                        logger.info(f"Successfully fetched highlights for match {match_id}")
                        return highlights
                    else:
                        logger.warning(f"API returned status {response.status}")
                        return self._get_fallback_highlights()
        except Exception as e:
            logger.error(f"Error fetching match highlights: {e}")
            return self._get_fallback_highlights()
    
    def _get_fallback_live_data(self) -> Dict[str, Any]:
        """Get fallback live match data"""
        return {
            'status': 'fallback',
            'message': 'Live data temporarily unavailable',
            'home_team': 'Real Madrid',
            'away_team': 'Opponent',
            'home_score': 0,
            'away_score': 0,
            'minute': 0,
            'status': 'LIVE',
            'competition': 'La Liga',
            'venue': 'Santiago Bernabéu',
            'last_updated': format_last_updated(),
            'source': 'Fallback Data'
        }
    
    def _get_fallback_transfer_news(self) -> List[Dict[str, Any]]:
        """Get fallback transfer news"""
        return [
            {
                'title': 'Real Madrid Transfer Update',
                'summary': 'Transfer news temporarily unavailable. Check back soon for latest updates.',
                'url': '',
                'published_at': format_last_updated(),
                'source': 'Fallback Data'
            }
        ]
    
    def _get_fallback_highlights(self) -> Dict[str, Any]:
        """Get fallback match highlights"""
        return {
            'match_id': 'unknown',
            'goals': [],
            'key_moments': [],
            'cards': [],
            'substitutions': [],
            'source': 'Fallback Data'
        }
