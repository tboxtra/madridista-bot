"""
API Manager
Handles API configurations, rate limiting, and fallback strategies.
"""

import os
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class APIConfig:
    name: str
    base_url: str
    api_key: str
    rate_limit: int  # requests per minute
    timeout: int
    retry_attempts: int
    last_request: float = 0
    request_count: int = 0
    reset_time: float = 0

class APIManager:
    """Manages API configurations and rate limiting."""
    
    def __init__(self):
        self.apis = self._initialize_apis()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _initialize_apis(self) -> Dict[str, APIConfig]:
        """Initialize API configurations."""
        
        return {
            "openweather": APIConfig(
                name="OpenWeatherMap",
                base_url="https://api.openweathermap.org/data/2.5",
                api_key=os.getenv("OPENWEATHER_API_KEY", ""),
                rate_limit=60,
                timeout=10,
                retry_attempts=3
            ),
            "newsapi": APIConfig(
                name="NewsAPI",
                base_url="https://newsapi.org/v2",
                api_key=os.getenv("NEWS_API_KEY", ""),
                rate_limit=1000,
                timeout=10,
                retry_attempts=3
            ),
            "exchangerate": APIConfig(
                name="ExchangeRate-API",
                base_url="https://api.exchangerate-api.com/v4",
                api_key=os.getenv("EXCHANGE_RATE_API_KEY", ""),
                rate_limit=1000,
                timeout=10,
                retry_attempts=3
            ),
            "football_data": APIConfig(
                name="Football-Data",
                base_url="https://api.football-data.org/v4",
                api_key=os.getenv("FOOTBALL_DATA_API_KEY", ""),
                rate_limit=10,
                timeout=10,
                retry_attempts=3
            ),
            "api_football": APIConfig(
                name="API-Football",
                base_url="https://v3.football.api-sports.io",
                api_key=os.getenv("API_FOOTBALL_KEY", ""),
                rate_limit=100,
                timeout=10,
                retry_attempts=3
            ),
            "rapidapi": APIConfig(
                name="RapidAPI",
                base_url="https://api.rapidapi.com",
                api_key=os.getenv("RAPIDAPI_KEY", ""),
                rate_limit=1000,
                timeout=10,
                retry_attempts=3
            )
        }
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """Check if API is within rate limits."""
        
        if api_name not in self.apis:
            return False
        
        api = self.apis[api_name]
        current_time = time.time()
        
        # Reset counter if minute has passed
        if current_time - api.reset_time >= 60:
            api.request_count = 0
            api.reset_time = current_time
        
        # Check if within rate limit
        if api.request_count >= api.rate_limit:
            return False
        
        return True
    
    def _make_request(self, api_name: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API request with rate limiting and error handling."""
        
        if api_name not in self.apis:
            return {"ok": False, "message": f"API {api_name} not configured"}
        
        api = self.apis[api_name]
        
        # Check rate limit
        if not self._check_rate_limit(api_name):
            return {"ok": False, "message": f"Rate limit exceeded for {api_name}"}
        
        # Check cache first
        cache_key = f"{api_name}:{endpoint}:{str(params)}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return {"ok": True, "data": cached_data, "cached": True}
        
        # Prepare request
        url = f"{api.base_url}/{endpoint}"
        headers = {
            "User-Agent": "FootballBot/1.0"
        }
        
        # Add API key
        if api.api_key:
            if api_name == "openweather":
                params = params or {}
                params["appid"] = api.api_key
            elif api_name == "newsapi":
                headers["X-API-Key"] = api.api_key
            elif api_name == "api_football":
                headers["X-RapidAPI-Key"] = api.api_key
                headers["X-RapidAPI-Host"] = "v3.football.api-sports.io"
            elif api_name == "rapidapi":
                headers["X-RapidAPI-Key"] = api.api_key
            elif api_name == "football_data":
                headers["X-Auth-Token"] = api.api_key
        
        # Make request with retries
        for attempt in range(api.retry_attempts):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=api.timeout)
                
                # Update rate limit counter
                api.request_count += 1
                api.last_request = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    # Cache successful response
                    self.cache[cache_key] = (data, time.time())
                    return {"ok": True, "data": data, "cached": False}
                elif response.status_code == 429:
                    # Rate limited
                    return {"ok": False, "message": f"Rate limited by {api_name}"}
                elif response.status_code == 401:
                    # Authentication error
                    return {"ok": False, "message": f"Authentication failed for {api_name}"}
                else:
                    # Other error
                    return {"ok": False, "message": f"API error {response.status_code} from {api_name}"}
                    
            except requests.exceptions.Timeout:
                if attempt == api.retry_attempts - 1:
                    return {"ok": False, "message": f"Timeout error for {api_name}"}
                time.sleep(1)  # Wait before retry
            except requests.exceptions.RequestException as e:
                if attempt == api.retry_attempts - 1:
                    return {"ok": False, "message": f"Request error for {api_name}: {str(e)}"}
                time.sleep(1)  # Wait before retry
        
        return {"ok": False, "message": f"Failed to get data from {api_name}"}
    
    def get_weather_data(self, city: str, country: str = "") -> Dict[str, Any]:
        """Get weather data for a city."""
        
        if not self.apis["openweather"].api_key:
            return {"ok": False, "message": "OpenWeatherMap API key not configured"}
        
        location = f"{city},{country}" if country else city
        params = {
            "q": location,
            "units": "metric"
        }
        
        result = self._make_request("openweather", "weather", params)
        
        if result["ok"]:
            weather_data = result["data"]
            return {
                "ok": True,
                "city": weather_data["name"],
                "country": weather_data["sys"]["country"],
                "temperature": weather_data["main"]["temp"],
                "feels_like": weather_data["main"]["feels_like"],
                "humidity": weather_data["main"]["humidity"],
                "description": weather_data["weather"][0]["description"],
                "wind_speed": weather_data["wind"]["speed"],
                "visibility": weather_data.get("visibility", 0) / 1000,  # Convert to km
                "cached": result.get("cached", False)
            }
        
        return result
    
    def get_news_data(self, query: str, language: str = "en", page_size: int = 10) -> Dict[str, Any]:
        """Get news data for a query."""
        
        if not self.apis["newsapi"].api_key:
            return {"ok": False, "message": "NewsAPI key not configured"}
        
        params = {
            "q": query,
            "language": language,
            "pageSize": page_size,
            "sortBy": "publishedAt"
        }
        
        result = self._make_request("newsapi", "everything", params)
        
        if result["ok"]:
            news_data = result["data"]
            articles = []
            for article in news_data.get("articles", []):
                articles.append({
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "published_at": article["publishedAt"],
                    "source": article["source"]["name"]
                })
            
            return {
                "ok": True,
                "total_results": news_data["totalResults"],
                "articles": articles,
                "cached": result.get("cached", False)
            }
        
        return result
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get exchange rate between currencies."""
        
        if not self.apis["exchangerate"].api_key:
            return {"ok": False, "message": "ExchangeRate API key not configured"}
        
        endpoint = f"latest/{from_currency}"
        result = self._make_request("exchangerate", endpoint)
        
        if result["ok"]:
            rate_data = result["data"]
            rate = rate_data["rates"].get(to_currency, 0)
            
            return {
                "ok": True,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": rate,
                "date": rate_data["date"],
                "cached": result.get("cached", False)
            }
        
        return result
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get status of all APIs."""
        
        status = {}
        for api_name, api_config in self.apis.items():
            status[api_name] = {
                "configured": bool(api_config.api_key),
                "rate_limit": api_config.rate_limit,
                "current_requests": api_config.request_count,
                "last_request": api_config.last_request,
                "base_url": api_config.base_url
            }
        
        return status
    
    def clear_cache(self, api_name: str = None):
        """Clear API cache."""
        
        if api_name:
            # Clear specific API cache
            keys_to_remove = [key for key in self.cache.keys() if key.startswith(f"{api_name}:")]
            for key in keys_to_remove:
                del self.cache[key]
        else:
            # Clear all cache
            self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        
        return {
            "total_entries": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "apis": list(self.apis.keys())
        }
