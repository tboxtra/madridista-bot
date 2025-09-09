"""
Enhanced Tools V2
Improved tools using the new API manager and user management system.
"""

import json
from typing import Dict, Any
from utils.api_manager import APIManager
from utils.user_manager import UserManager

# Global instances
api_manager = APIManager()
user_manager = UserManager()

def tool_weather_match_enhanced(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced weather tool with better error handling."""
    
    team = args.get("team_name", "Real Madrid")
    city = args.get("city", "Madrid")
    country = args.get("country", "ES")
    
    try:
        # Get weather data
        weather_result = api_manager.get_weather_data(city, country)
        
        if weather_result["ok"]:
            weather_data = weather_result
            
            # Analyze weather impact on football
            impact_analysis = _analyze_weather_impact(weather_data)
            
            return {
                "ok": True,
                "team": team,
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "description": weather_data["description"],
                "humidity": weather_data["humidity"],
                "wind_speed": weather_data["wind_speed"],
                "visibility": weather_data["visibility"],
                "impact_analysis": impact_analysis,
                "cached": weather_result.get("cached", False),
                "__source": "Enhanced Weather API"
            }
        else:
            return {
                "ok": False,
                "message": f"Weather data unavailable: {weather_result['message']}",
                "__source": "Enhanced Weather API"
            }
            
    except Exception as e:
        return {
            "ok": False,
            "message": f"Weather service error: {str(e)}",
            "__source": "Enhanced Weather API"
        }

def tool_news_enhanced(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced news tool with better filtering and sentiment."""
    
    query = args.get("query", "football")
    language = args.get("language", "en")
    page_size = args.get("page_size", 10)
    
    try:
        # Get news data
        news_result = api_manager.get_news_data(query, language, page_size)
        
        if news_result["ok"]:
            articles = news_result["articles"]
            
            # Filter and rank articles
            filtered_articles = _filter_football_news(articles)
            
            return {
                "ok": True,
                "query": query,
                "total_results": news_result["total_results"],
                "articles": filtered_articles[:5],  # Top 5
                "cached": news_result.get("cached", False),
                "__source": "Enhanced News API"
            }
        else:
            return {
                "ok": False,
                "message": f"News unavailable: {news_result['message']}",
                "__source": "Enhanced News API"
            }
            
    except Exception as e:
        return {
            "ok": False,
            "message": f"News service error: {str(e)}",
            "__source": "Enhanced News API"
        }

def tool_currency_enhanced(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced currency conversion tool."""
    
    from_currency = args.get("from_currency", "EUR")
    to_currency = args.get("to_currency", "USD")
    amount = args.get("amount", 1)
    
    try:
        # Get exchange rate
        rate_result = api_manager.get_exchange_rate(from_currency, to_currency)
        
        if rate_result["ok"]:
            rate = rate_result["rate"]
            converted_amount = amount * rate
            
            return {
                "ok": True,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": amount,
                "rate": rate,
                "converted_amount": converted_amount,
                "date": rate_result["date"],
                "cached": rate_result.get("cached", False),
                "__source": "Enhanced Currency API"
            }
        else:
            return {
                "ok": False,
                "message": f"Currency data unavailable: {rate_result['message']}",
                "__source": "Enhanced Currency API"
            }
            
    except Exception as e:
        return {
            "ok": False,
            "message": f"Currency service error: {str(e)}",
            "__source": "Enhanced Currency API"
        }

def tool_user_achievements_enhanced(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced user achievements tool."""
    
    user_id = args.get("user_id", "")
    
    if not user_id:
        return {"ok": False, "message": "User ID required"}
    
    try:
        achievements = user_manager.get_user_achievements(user_id)
        
        if achievements["ok"]:
            return achievements
        else:
            return {
                "ok": False,
                "message": "User not found or no achievements",
                "__source": "Enhanced User Manager"
            }
            
    except Exception as e:
        return {
            "ok": False,
            "message": f"Achievement system error: {str(e)}",
            "__source": "Enhanced User Manager"
        }

def tool_user_insights_enhanced(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced user insights tool."""
    
    user_id = args.get("user_id", "")
    
    if not user_id:
        return {"ok": False, "message": "User ID required"}
    
    try:
        insights = user_manager.get_user_insights(user_id)
        
        if insights["ok"]:
            return insights
        else:
            return {
                "ok": False,
                "message": "User not found",
                "__source": "Enhanced User Manager"
            }
            
    except Exception as e:
        return {
            "ok": False,
            "message": f"User insights error: {str(e)}",
            "__source": "Enhanced User Manager"
        }

def tool_api_status(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get API status and health."""
    
    try:
        api_status = api_manager.get_api_status()
        cache_stats = api_manager.get_cache_stats()
        
        return {
            "ok": True,
            "api_status": api_status,
            "cache_stats": cache_stats,
            "__source": "API Manager"
        }
        
    except Exception as e:
        return {
            "ok": False,
            "message": f"API status error: {str(e)}",
            "__source": "API Manager"
        }

def _analyze_weather_impact(weather_data: Dict[str, Any]) -> str:
    """Analyze how weather conditions might affect football."""
    
    temperature = weather_data["temperature"]
    humidity = weather_data["humidity"]
    wind_speed = weather_data["wind_speed"]
    visibility = weather_data["visibility"]
    
    impacts = []
    
    # Temperature impact
    if temperature < 5:
        impacts.append("Very cold conditions may affect player performance and ball control")
    elif temperature > 30:
        impacts.append("Hot weather may cause fatigue and require more hydration breaks")
    elif 15 <= temperature <= 25:
        impacts.append("Ideal temperature conditions for optimal performance")
    
    # Humidity impact
    if humidity > 80:
        impacts.append("High humidity may make the ball heavier and affect passing accuracy")
    elif humidity < 30:
        impacts.append("Low humidity may cause the ball to move faster")
    
    # Wind impact
    if wind_speed > 15:
        impacts.append("Strong winds may significantly affect long passes and set pieces")
    elif wind_speed > 8:
        impacts.append("Moderate winds may influence ball trajectory")
    
    # Visibility impact
    if visibility < 1:
        impacts.append("Poor visibility may affect player awareness and referee decisions")
    
    return "; ".join(impacts) if impacts else "Weather conditions should not significantly impact the match"

def _filter_football_news(articles: list) -> list:
    """Filter and rank football news articles."""
    
    football_keywords = [
        "football", "soccer", "champions league", "premier league", "laliga", "serie a",
        "bundesliga", "real madrid", "barcelona", "manchester", "liverpool", "chelsea",
        "arsenal", "tottenham", "bayern", "psg", "juventus", "milan", "inter",
        "transfer", "goal", "match", "fixture", "player", "manager", "coach"
    ]
    
    filtered_articles = []
    
    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        
        # Check if article is football-related
        if any(keyword in title or keyword in description for keyword in football_keywords):
            # Add relevance score
            relevance_score = sum(1 for keyword in football_keywords if keyword in title or keyword in description)
            article["relevance_score"] = relevance_score
            filtered_articles.append(article)
    
    # Sort by relevance score
    filtered_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return filtered_articles

# Enhanced tool registry
ENHANCED_TOOLS_V2 = {
    "tool_weather_match_enhanced": tool_weather_match_enhanced,
    "tool_news_enhanced": tool_news_enhanced,
    "tool_currency_enhanced": tool_currency_enhanced,
    "tool_user_achievements_enhanced": tool_user_achievements_enhanced,
    "tool_user_insights_enhanced": tool_user_insights_enhanced,
    "tool_api_status": tool_api_status
}
