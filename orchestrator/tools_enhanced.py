"""
Enhanced tools that integrate new providers (weather, news, currency, cache).
These tools extend the existing toolset with advanced features.
"""

import os
from typing import Dict, List, Any, Optional
from providers.weather import weather_provider
from providers.news_enhanced import enhanced_news_provider
from providers.currency import currency_provider
from utils.cache import tool_cache, api_cache

def tool_weather_match(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get weather conditions for a match venue."""
    
    venue = args.get("venue", "")
    match_date = args.get("match_date")
    
    if not venue:
        return {"error": "Venue is required"}
    
    # Try to get from cache first
    cache_key = f"weather:{venue}:{match_date or 'current'}"
    cached_result = tool_cache.get_cached_result("tool_weather_match", {"venue": venue, "match_date": match_date})
    
    if cached_result:
        return cached_result
    
    # Get weather data
    weather_data = weather_provider.get_match_weather(venue, match_date)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_weather_match", {"venue": venue, "match_date": match_date}, weather_data, ttl=1800)
    
    return weather_data

def tool_weather_impact(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze weather impact on football match."""
    
    conditions = args.get("conditions", {})
    
    if not conditions:
        return {"error": "Weather conditions are required"}
    
    # Analyze impact
    impact = weather_provider.get_weather_impact(conditions)
    
    return {
        "impact_analysis": impact,
        "recommendations": weather_provider._get_weather_recommendations(impact),
        "match_affected": impact.get("affects_play", False)
    }

def tool_news_trending(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get trending football news with sentiment analysis."""
    
    topic = args.get("topic", "football")
    limit = args.get("limit", 10)
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_news_trending", {"topic": topic, "limit": limit})
    
    if cached_result:
        return cached_result
    
    # Get trending news
    news_data = enhanced_news_provider.get_trending_news(topic, limit)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_news_trending", {"topic": topic, "limit": limit}, news_data, ttl=900)  # 15 minutes
    
    return news_data

def tool_news_team(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team-specific news with sentiment analysis."""
    
    team_name = args.get("team_name", "")
    limit = args.get("limit", 5)
    
    if not team_name:
        return {"error": "Team name is required"}
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_news_team", {"team_name": team_name, "limit": limit})
    
    if cached_result:
        return cached_result
    
    # Get team news
    news_data = enhanced_news_provider.get_team_news(team_name, limit)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_news_team", {"team_name": team_name, "limit": limit}, news_data, ttl=1800)  # 30 minutes
    
    return news_data

def tool_news_player(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get player-specific news with sentiment analysis."""
    
    player_name = args.get("player_name", "")
    limit = args.get("limit", 5)
    
    if not player_name:
        return {"error": "Player name is required"}
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_news_player", {"player_name": player_name, "limit": limit})
    
    if cached_result:
        return cached_result
    
    # Get player news
    news_data = enhanced_news_provider.get_player_news(player_name, limit)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_news_player", {"player_name": player_name, "limit": limit}, news_data, ttl=1800)  # 30 minutes
    
    return news_data

def tool_news_competition(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get competition-specific news with sentiment analysis."""
    
    competition = args.get("competition", "")
    limit = args.get("limit", 5)
    
    if not competition:
        return {"error": "Competition name is required"}
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_news_competition", {"competition": competition, "limit": limit})
    
    if cached_result:
        return cached_result
    
    # Get competition news
    news_data = enhanced_news_provider.get_competition_news(competition, limit)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_news_competition", {"competition": competition, "limit": limit}, news_data, ttl=1800)  # 30 minutes
    
    return news_data

def tool_convert_transfer(args: Dict[str, Any]) -> Dict[str, Any]:
    """Convert transfer fee between currencies."""
    
    amount = args.get("amount", 0)
    from_currency = args.get("from_currency", "EUR")
    to_currency = args.get("to_currency", "USD")
    
    if not amount or amount <= 0:
        return {"error": "Valid amount is required"}
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_convert_transfer", {"amount": amount, "from_currency": from_currency, "to_currency": to_currency})
    
    if cached_result:
        return cached_result
    
    # Convert transfer fee
    conversion_data = currency_provider.convert_transfer_fee(amount, from_currency, to_currency)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_convert_transfer", {"amount": amount, "from_currency": from_currency, "to_currency": to_currency}, conversion_data, ttl=3600)  # 1 hour
    
    return conversion_data

def tool_market_trends(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get transfer market trends and analysis."""
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_market_trends", {})
    
    if cached_result:
        return cached_result
    
    # Get market trends
    trends_data = currency_provider.get_market_trends()
    
    # Cache the result
    tool_cache.cache_tool_result("tool_market_trends", {}, trends_data, ttl=7200)  # 2 hours
    
    return trends_data

def tool_compare_transfers(args: Dict[str, Any]) -> Dict[str, Any]:
    """Compare multiple transfer values in a common currency."""
    
    transfers = args.get("transfers", [])
    target_currency = args.get("target_currency", "EUR")
    
    if not transfers:
        return {"error": "Transfer list is required"}
    
    # Try to get from cache first
    cache_key = f"transfers:{len(transfers)}:{target_currency}"
    cached_result = tool_cache.get_cached_result("tool_compare_transfers", {"transfers": transfers, "target_currency": target_currency})
    
    if cached_result:
        return cached_result
    
    # Compare transfers
    comparison_data = currency_provider.compare_transfer_values(transfers, target_currency)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_compare_transfers", {"transfers": transfers, "target_currency": target_currency}, comparison_data, ttl=3600)  # 1 hour
    
    return comparison_data

def tool_currency_impact(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze currency impact on transfer values."""
    
    transfer_amount = args.get("transfer_amount", 0)
    currency = args.get("currency", "EUR")
    
    if not transfer_amount or transfer_amount <= 0:
        return {"error": "Valid transfer amount is required"}
    
    # Try to get from cache first
    cached_result = tool_cache.get_cached_result("tool_currency_impact", {"transfer_amount": transfer_amount, "currency": currency})
    
    if cached_result:
        return cached_result
    
    # Analyze currency impact
    impact_data = currency_provider.get_currency_impact(transfer_amount, currency)
    
    # Cache the result
    tool_cache.cache_tool_result("tool_currency_impact", {"transfer_amount": transfer_amount, "currency": currency}, impact_data, ttl=3600)  # 1 hour
    
    return impact_data

def tool_cache_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get cache statistics and performance metrics."""
    
    from utils.cache import get_cache_stats, cache_manager
    
    stats = get_cache_stats()
    entries_info = cache_manager.get_entries_info()
    
    return {
        "cache_stats": stats,
        "top_entries": entries_info[:10],  # Top 10 most accessed entries
        "cache_health": "good" if stats["hit_rate"] > 70 else "needs_optimization"
    }

def tool_clear_cache(args: Dict[str, Any]) -> Dict[str, Any]:
    """Clear cache entries (admin function)."""
    
    cache_type = args.get("cache_type", "all")
    
    from utils.cache import clear_all_cache, cleanup_cache
    
    if cache_type == "all":
        clear_all_cache()
        return {"message": "All cache cleared successfully"}
    elif cache_type == "expired":
        removed_count = cleanup_cache()
        return {"message": f"Removed {removed_count} expired entries"}
    else:
        return {"error": "Invalid cache type. Use 'all' or 'expired'"}

# Enhanced tool registry
ENHANCED_TOOLS = {
    "tool_weather_match": tool_weather_match,
    "tool_weather_impact": tool_weather_impact,
    "tool_news_trending": tool_news_trending,
    "tool_news_team": tool_news_team,
    "tool_news_player": tool_news_player,
    "tool_news_competition": tool_news_competition,
    "tool_convert_transfer": tool_convert_transfer,
    "tool_market_trends": tool_market_trends,
    "tool_compare_transfers": tool_compare_transfers,
    "tool_currency_impact": tool_currency_impact,
    "tool_cache_stats": tool_cache_stats,
    "tool_clear_cache": tool_clear_cache
}
