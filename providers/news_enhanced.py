"""
Enhanced news provider with multiple sources and sentiment analysis.
Integrates with NewsAPI and other free news sources.
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

class EnhancedNewsProvider:
    """Enhanced news provider with multiple sources and sentiment analysis."""
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        self.timeout = 10
        
        # Football-specific sources
        self.football_sources = [
            "bbc-sport",
            "espn",
            "the-sport-bible",
            "four-four-two",
            "goal",
            "skysports",
            "football-espana",
            "marca",
            "as",
            "sport"
        ]
        
        # Sentiment keywords
        self.positive_keywords = [
            "amazing", "brilliant", "excellent", "fantastic", "incredible",
            "outstanding", "superb", "wonderful", "great", "best", "win",
            "victory", "triumph", "success", "champion", "hero", "legend"
        ]
        
        self.negative_keywords = [
            "terrible", "awful", "disappointing", "poor", "bad", "lose",
            "defeat", "failure", "crisis", "disaster", "injury", "suspended",
            "banned", "controversy", "scandal", "problem", "issue"
        ]
    
    def get_trending_news(self, topic: str = "football", limit: int = 10) -> Dict[str, Any]:
        """Get trending football news from multiple sources."""
        
        if not self.news_api_key:
            return {"error": "NewsAPI key not configured"}
        
        try:
            # Get news from multiple sources
            all_articles = []
            
            for source in self.football_sources[:5]:  # Limit to 5 sources to stay within rate limits
                articles = self._get_news_from_source(source, topic)
                if articles:
                    all_articles.extend(articles)
            
            # Sort by relevance and recency
            sorted_articles = self._sort_articles(all_articles)
            
            # Analyze sentiment
            analyzed_articles = []
            for article in sorted_articles[:limit]:
                sentiment = self._analyze_sentiment(article)
                article["sentiment"] = sentiment
                analyzed_articles.append(article)
            
            # Get trending topics
            trending_topics = self._extract_trending_topics(analyzed_articles)
            
            return {
                "articles": analyzed_articles,
                "trending_topics": trending_topics,
                "total_articles": len(analyzed_articles),
                "sources_used": len(set(article.get("source", {}).get("name", "") for article in analyzed_articles)),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"News API error: {str(e)}"}
    
    def get_team_news(self, team_name: str, limit: int = 5) -> Dict[str, Any]:
        """Get news specific to a team."""
        
        if not self.news_api_key:
            return {"error": "NewsAPI key not configured"}
        
        try:
            # Search for team-specific news
            query = f"{team_name} football"
            articles = self._search_news(query, limit)
            
            # Analyze sentiment for team
            analyzed_articles = []
            for article in articles:
                sentiment = self._analyze_sentiment(article)
                article["sentiment"] = sentiment
                analyzed_articles.append(article)
            
            # Calculate overall team sentiment
            overall_sentiment = self._calculate_overall_sentiment(analyzed_articles)
            
            return {
                "team": team_name,
                "articles": analyzed_articles,
                "overall_sentiment": overall_sentiment,
                "total_articles": len(analyzed_articles),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Team news API error: {str(e)}"}
    
    def get_player_news(self, player_name: str, limit: int = 5) -> Dict[str, Any]:
        """Get news specific to a player."""
        
        if not self.news_api_key:
            return {"error": "NewsAPI key not configured"}
        
        try:
            # Search for player-specific news
            query = f"{player_name} football player"
            articles = self._search_news(query, limit)
            
            # Analyze sentiment for player
            analyzed_articles = []
            for article in articles:
                sentiment = self._analyze_sentiment(article)
                article["sentiment"] = sentiment
                analyzed_articles.append(article)
            
            # Calculate overall player sentiment
            overall_sentiment = self._calculate_overall_sentiment(analyzed_articles)
            
            return {
                "player": player_name,
                "articles": analyzed_articles,
                "overall_sentiment": overall_sentiment,
                "total_articles": len(analyzed_articles),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Player news API error: {str(e)}"}
    
    def get_competition_news(self, competition: str, limit: int = 5) -> Dict[str, Any]:
        """Get news specific to a competition."""
        
        if not self.news_api_key:
            return {"error": "NewsAPI key not configured"}
        
        try:
            # Search for competition-specific news
            query = f"{competition} football"
            articles = self._search_news(query, limit)
            
            # Analyze sentiment for competition
            analyzed_articles = []
            for article in articles:
                sentiment = self._analyze_sentiment(article)
                article["sentiment"] = sentiment
                analyzed_articles.append(article)
            
            # Calculate overall competition sentiment
            overall_sentiment = self._calculate_overall_sentiment(analyzed_articles)
            
            return {
                "competition": competition,
                "articles": analyzed_articles,
                "overall_sentiment": overall_sentiment,
                "total_articles": len(analyzed_articles),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Competition news API error: {str(e)}"}
    
    def _get_news_from_source(self, source: str, topic: str) -> List[Dict[str, Any]]:
        """Get news from a specific source."""
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                "sources": source,
                "q": topic,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return data.get("articles", [])
            
        except Exception as e:
            print(f"Error getting news from {source}: {e}")
            return []
    
    def _search_news(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search for news articles."""
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": limit,
                "language": "en",
                "apiKey": self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return data.get("articles", [])
            
        except Exception as e:
            print(f"Error searching news: {e}")
            return []
    
    def _sort_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort articles by relevance and recency."""
        
        def sort_key(article):
            # Prioritize recent articles
            published_at = article.get("publishedAt", "")
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    recency_score = (datetime.now() - pub_date).total_seconds()
                except:
                    recency_score = 86400  # 1 day default
            else:
                recency_score = 86400
            
            # Prioritize articles with more content
            content_length = len(article.get("description", "") or "")
            
            return (recency_score, -content_length)
        
        return sorted(articles, key=sort_key)
    
    def _analyze_sentiment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of an article."""
        
        # Combine title and description for analysis
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
        
        total_words = len(text.split())
        positive_ratio = positive_count / max(total_words, 1)
        negative_ratio = negative_count / max(total_words, 1)
        
        if positive_ratio > negative_ratio:
            sentiment = "positive"
            confidence = positive_ratio
        elif negative_ratio > positive_ratio:
            sentiment = "negative"
            confidence = negative_ratio
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": min(confidence, 1.0),
            "positive_score": positive_ratio,
            "negative_score": negative_ratio
        }
    
    def _calculate_overall_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall sentiment from multiple articles."""
        
        if not articles:
            return {"sentiment": "neutral", "confidence": 0.0}
        
        sentiments = [article.get("sentiment", {}).get("sentiment", "neutral") for article in articles]
        confidences = [article.get("sentiment", {}).get("confidence", 0.0) for article in articles]
        
        sentiment_counts = Counter(sentiments)
        most_common_sentiment = sentiment_counts.most_common(1)[0][0]
        
        # Calculate weighted confidence
        total_confidence = sum(confidences)
        avg_confidence = total_confidence / len(confidences) if confidences else 0.0
        
        return {
            "sentiment": most_common_sentiment,
            "confidence": avg_confidence,
            "distribution": dict(sentiment_counts),
            "total_articles": len(articles)
        }
    
    def _extract_trending_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics from articles."""
        
        # Simple keyword extraction (in production, use NLP libraries)
        all_text = " ".join([
            f"{article.get('title', '')} {article.get('description', '')}"
            for article in articles
        ]).lower()
        
        # Common football terms
        football_terms = [
            "transfer", "goal", "match", "league", "champions", "cup",
            "player", "team", "manager", "injury", "contract", "deal",
            "victory", "defeat", "draw", "penalty", "red card", "yellow card"
        ]
        
        trending_topics = []
        for term in football_terms:
            count = all_text.count(term)
            if count > 0:
                trending_topics.append({
                    "topic": term,
                    "mentions": count,
                    "relevance": count / len(articles) if articles else 0
                })
        
        # Sort by relevance
        trending_topics.sort(key=lambda x: x["relevance"], reverse=True)
        
        return trending_topics[:10]  # Top 10 trending topics

# Global enhanced news provider instance
enhanced_news_provider = EnhancedNewsProvider()
