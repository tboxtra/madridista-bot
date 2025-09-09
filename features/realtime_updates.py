"""
Real-time Updates System
Handles live match updates, notifications, and real-time data streaming.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from utils.api_manager import APIManager

@dataclass
class LiveMatch:
    match_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    minute: int
    status: str
    events: List[Dict[str, Any]]
    last_updated: datetime

@dataclass
class Notification:
    user_id: str
    type: str  # "goal", "match_start", "match_end", "news"
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime

class RealTimeUpdateSystem:
    """Handles real-time updates and notifications."""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self.live_matches = {}
        self.subscribers = {}  # user_id -> List[subscriptions]
        self.notifications = []
        self.update_interval = 30  # seconds
        self.is_running = False
        self.update_task = None
    
    async def start(self):
        """Start the real-time update system."""
        if not self.is_running:
            self.is_running = True
            self.update_task = asyncio.create_task(self._update_loop())
            print("✅ Real-time update system started")
    
    async def stop(self):
        """Stop the real-time update system."""
        if self.is_running:
            self.is_running = False
            if self.update_task:
                self.update_task.cancel()
            print("✅ Real-time update system stopped")
    
    async def _update_loop(self):
        """Main update loop for real-time data."""
        while self.is_running:
            try:
                await self._check_live_matches()
                await self._check_news_updates()
                await self._process_notifications()
                
                # Wait before next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _check_live_matches(self):
        """Check for live match updates."""
        try:
            # Get live matches from API
            live_result = self.api_manager._make_request("football_data", "matches", {"status": "LIVE"})
            
            if live_result["ok"]:
                matches_data = live_result["data"]["matches"]
                
                for match_data in matches_data:
                    match_id = str(match_data["id"])
                    
                    # Create or update live match
                    live_match = LiveMatch(
                        match_id=match_id,
                        home_team=match_data["homeTeam"]["name"],
                        away_team=match_data["awayTeam"]["name"],
                        home_score=match_data["score"]["fullTime"]["home"] or 0,
                        away_score=match_data["score"]["fullTime"]["away"] or 0,
                        minute=match_data.get("minute", 0),
                        status=match_data["status"],
                        events=[],
                        last_updated=datetime.now()
                    )
                    
                    # Check for score changes
                    if match_id in self.live_matches:
                        old_match = self.live_matches[match_id]
                        if (old_match.home_score != live_match.home_score or 
                            old_match.away_score != live_match.away_score):
                            # Score changed - send notifications
                            await self._notify_score_change(old_match, live_match)
                    
                    self.live_matches[match_id] = live_match
                    
        except Exception as e:
            print(f"Error checking live matches: {e}")
    
    async def _check_news_updates(self):
        """Check for news updates."""
        try:
            # Get latest news
            news_result = self.api_manager.get_news_data("football", page_size=5)
            
            if news_result["ok"]:
                articles = news_result["articles"]
                
                # Check for new articles (simplified - in real implementation, store last article IDs)
                for article in articles:
                    # Check if this is a breaking news article
                    if self._is_breaking_news(article):
                        await self._notify_breaking_news(article)
                        
        except Exception as e:
            print(f"Error checking news updates: {e}")
    
    async def _notify_score_change(self, old_match: LiveMatch, new_match: LiveMatch):
        """Notify subscribers about score changes."""
        
        # Find subscribers for this match
        subscribers = self._get_match_subscribers(new_match.match_id)
        
        for user_id in subscribers:
            notification = Notification(
                user_id=user_id,
                type="goal",
                title="⚽ Goal Update!",
                message=f"{new_match.home_team} {new_match.home_score}-{new_match.away_score} {new_match.away_team} ({new_match.minute}')",
                data={
                    "match_id": new_match.match_id,
                    "home_team": new_match.home_team,
                    "away_team": new_match.away_team,
                    "home_score": new_match.home_score,
                    "away_score": new_match.away_score,
                    "minute": new_match.minute
                },
                timestamp=datetime.now()
            )
            
            self.notifications.append(notification)
    
    async def _notify_breaking_news(self, article: Dict[str, Any]):
        """Notify subscribers about breaking news."""
        
        # Find subscribers for news
        news_subscribers = self._get_news_subscribers()
        
        for user_id in news_subscribers:
            notification = Notification(
                user_id=user_id,
                type="news",
                title="📰 Breaking News",
                message=article["title"],
                data={
                    "url": article["url"],
                    "source": article["source"],
                    "published_at": article["published_at"]
                },
                timestamp=datetime.now()
            )
            
            self.notifications.append(notification)
    
    def _is_breaking_news(self, article: Dict[str, Any]) -> bool:
        """Check if article is breaking news."""
        
        breaking_keywords = [
            "breaking", "urgent", "just in", "exclusive", "confirmed",
            "transfer", "injury", "suspension", "manager", "coach"
        ]
        
        title = article.get("title", "").lower()
        return any(keyword in title for keyword in breaking_keywords)
    
    def _get_match_subscribers(self, match_id: str) -> List[str]:
        """Get subscribers for a specific match."""
        
        subscribers = []
        for user_id, subscriptions in self.subscribers.items():
            if "matches" in subscriptions and match_id in subscriptions["matches"]:
                subscribers.append(user_id)
        
        return subscribers
    
    def _get_news_subscribers(self) -> List[str]:
        """Get subscribers for news updates."""
        
        subscribers = []
        for user_id, subscriptions in self.subscribers.items():
            if "news" in subscriptions and subscriptions["news"]:
                subscribers.append(user_id)
        
        return subscribers
    
    async def _process_notifications(self):
        """Process pending notifications."""
        
        # In a real implementation, this would send notifications via Telegram
        # For now, we'll just log them
        for notification in self.notifications:
            print(f"📢 Notification for {notification.user_id}: {notification.title} - {notification.message}")
        
        # Clear processed notifications
        self.notifications.clear()
    
    def subscribe_user(self, user_id: str, subscription_type: str, data: Any = None):
        """Subscribe user to updates."""
        
        if user_id not in self.subscribers:
            self.subscribers[user_id] = {}
        
        if subscription_type == "matches":
            if "matches" not in self.subscribers[user_id]:
                self.subscribers[user_id]["matches"] = []
            if data and data not in self.subscribers[user_id]["matches"]:
                self.subscribers[user_id]["matches"].append(data)
        
        elif subscription_type == "news":
            self.subscribers[user_id]["news"] = True
        
        elif subscription_type == "team":
            if "teams" not in self.subscribers[user_id]:
                self.subscribers[user_id]["teams"] = []
            if data and data not in self.subscribers[user_id]["teams"]:
                self.subscribers[user_id]["teams"].append(data)
    
    def unsubscribe_user(self, user_id: str, subscription_type: str, data: Any = None):
        """Unsubscribe user from updates."""
        
        if user_id not in self.subscribers:
            return
        
        if subscription_type == "matches" and "matches" in self.subscribers[user_id]:
            if data:
                self.subscribers[user_id]["matches"].remove(data)
            else:
                self.subscribers[user_id]["matches"] = []
        
        elif subscription_type == "news":
            self.subscribers[user_id]["news"] = False
        
        elif subscription_type == "team" and "teams" in self.subscribers[user_id]:
            if data:
                self.subscribers[user_id]["teams"].remove(data)
            else:
                self.subscribers[user_id]["teams"] = []
    
    def get_live_matches(self) -> List[LiveMatch]:
        """Get current live matches."""
        return list(self.live_matches.values())
    
    def get_user_subscriptions(self, user_id: str) -> Dict[str, Any]:
        """Get user's subscriptions."""
        return self.subscribers.get(user_id, {})
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        return {
            "total_subscribers": len(self.subscribers),
            "live_matches": len(self.live_matches),
            "pending_notifications": len(self.notifications),
            "update_interval": self.update_interval
        }
