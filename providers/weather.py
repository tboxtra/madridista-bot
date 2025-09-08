"""
Weather provider for football matches.
Integrates with OpenWeatherMap API for match conditions and weather insights.
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class WeatherProvider:
    """Weather provider for football match conditions."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.timeout = 10
        
    def get_match_weather(self, venue: str, match_date: str = None) -> Dict[str, Any]:
        """Get weather conditions for a match venue."""
        
        if not self.api_key:
            return {"error": "OpenWeatherMap API key not configured"}
        
        try:
            # Get coordinates for venue (simplified - would need venue database)
            coords = self._get_venue_coordinates(venue)
            if not coords:
                return {"error": f"Could not find coordinates for venue: {venue}"}
            
            # Get current weather or forecast
            if match_date:
                weather_data = self._get_forecast(coords, match_date)
            else:
                weather_data = self._get_current_weather(coords)
            
            if not weather_data:
                return {"error": "Could not retrieve weather data"}
            
            # Analyze weather impact
            impact = self._analyze_weather_impact(weather_data)
            
            return {
                "venue": venue,
                "date": match_date or "current",
                "temperature": weather_data.get("main", {}).get("temp", 0),
                "feels_like": weather_data.get("main", {}).get("feels_like", 0),
                "humidity": weather_data.get("main", {}).get("humidity", 0),
                "wind_speed": weather_data.get("wind", {}).get("speed", 0),
                "wind_direction": weather_data.get("wind", {}).get("deg", 0),
                "conditions": weather_data.get("weather", [{}])[0].get("description", ""),
                "visibility": weather_data.get("visibility", 0),
                "impact": impact,
                "recommendations": self._get_weather_recommendations(impact)
            }
            
        except Exception as e:
            return {"error": f"Weather API error: {str(e)}"}
    
    def get_weather_impact(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather impact on football match."""
        
        impact_factors = {
            "temperature_impact": self._analyze_temperature_impact(conditions.get("temperature", 0)),
            "wind_impact": self._analyze_wind_impact(conditions.get("wind_speed", 0)),
            "precipitation_impact": self._analyze_precipitation_impact(conditions.get("conditions", "")),
            "visibility_impact": self._analyze_visibility_impact(conditions.get("visibility", 0))
        }
        
        overall_impact = self._calculate_overall_impact(impact_factors)
        
        return {
            "overall_impact": overall_impact,
            "factors": impact_factors,
            "description": self._get_impact_description(overall_impact),
            "affects_play": overall_impact > 0.3
        }
    
    def _get_venue_coordinates(self, venue: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a football venue."""
        
        # Simplified venue database - in production, this would be a proper database
        venue_coords = {
            "santiago bernabeu": {"lat": 40.4531, "lon": -3.6883},
            "camp nou": {"lat": 41.3809, "lon": 2.1228},
            "wembley": {"lat": 51.5560, "lon": -0.2795},
            "old trafford": {"lat": 53.4631, "lon": -2.2913},
            "anfield": {"lat": 53.4308, "lon": -2.9608},
            "stamford bridge": {"lat": 51.4817, "lon": -0.1910},
            "emirates": {"lat": 51.5549, "lon": -0.1084},
            "etihad": {"lat": 53.4831, "lon": -2.2004},
            "allianz arena": {"lat": 48.2188, "lon": 11.6242},
            "san siro": {"lat": 45.4781, "lon": 9.1240},
            "signal iduna park": {"lat": 51.4926, "lon": 7.4518},
            "parc des princes": {"lat": 48.8414, "lon": 2.2531}
        }
        
        venue_lower = venue.lower()
        for venue_name, coords in venue_coords.items():
            if venue_name in venue_lower or venue_lower in venue_name:
                return coords
        
        return None
    
    def _get_current_weather(self, coords: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Get current weather for coordinates."""
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def _get_forecast(self, coords: Dict[str, float], match_date: str) -> Optional[Dict[str, Any]]:
        """Get weather forecast for specific date."""
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            forecast_data = response.json()
            
            # Find closest forecast to match date
            match_datetime = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
            
            closest_forecast = None
            min_time_diff = float('inf')
            
            for forecast in forecast_data.get("list", []):
                forecast_time = datetime.fromtimestamp(forecast["dt"])
                time_diff = abs((forecast_time - match_datetime).total_seconds())
                
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_forecast = forecast
            
            return closest_forecast
            
        except Exception as e:
            print(f"Forecast API error: {e}")
            return None
    
    def _analyze_weather_impact(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather impact on football match."""
        
        temp = weather_data.get("main", {}).get("temp", 20)
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        conditions = weather_data.get("weather", [{}])[0].get("description", "").lower()
        visibility = weather_data.get("visibility", 10000)
        
        impact_factors = {
            "temperature_impact": self._analyze_temperature_impact(temp),
            "wind_impact": self._analyze_wind_impact(wind_speed),
            "precipitation_impact": self._analyze_precipitation_impact(conditions),
            "visibility_impact": self._analyze_visibility_impact(visibility)
        }
        
        overall_impact = self._calculate_overall_impact(impact_factors)
        
        return {
            "overall_impact": overall_impact,
            "factors": impact_factors,
            "description": self._get_impact_description(overall_impact),
            "affects_play": overall_impact > 0.3
        }
    
    def _analyze_temperature_impact(self, temperature: float) -> float:
        """Analyze temperature impact on match."""
        
        # Optimal temperature range: 15-25°C
        if 15 <= temperature <= 25:
            return 0.0  # No impact
        elif 10 <= temperature < 15 or 25 < temperature <= 30:
            return 0.2  # Mild impact
        elif 5 <= temperature < 10 or 30 < temperature <= 35:
            return 0.4  # Moderate impact
        else:
            return 0.6  # High impact
    
    def _analyze_wind_impact(self, wind_speed: float) -> float:
        """Analyze wind impact on match."""
        
        # Wind speed in m/s
        if wind_speed < 5:
            return 0.0  # No impact
        elif 5 <= wind_speed < 10:
            return 0.2  # Mild impact
        elif 10 <= wind_speed < 15:
            return 0.4  # Moderate impact
        else:
            return 0.6  # High impact
    
    def _analyze_precipitation_impact(self, conditions: str) -> float:
        """Analyze precipitation impact on match."""
        
        if "clear" in conditions or "sunny" in conditions:
            return 0.0  # No impact
        elif "cloud" in conditions:
            return 0.1  # Minimal impact
        elif "rain" in conditions or "drizzle" in conditions:
            return 0.4  # Moderate impact
        elif "storm" in conditions or "heavy" in conditions:
            return 0.7  # High impact
        else:
            return 0.2  # Mild impact
    
    def _analyze_visibility_impact(self, visibility: int) -> float:
        """Analyze visibility impact on match."""
        
        # Visibility in meters
        if visibility > 5000:
            return 0.0  # No impact
        elif 2000 <= visibility <= 5000:
            return 0.2  # Mild impact
        elif 1000 <= visibility < 2000:
            return 0.4  # Moderate impact
        else:
            return 0.6  # High impact
    
    def _calculate_overall_impact(self, factors: Dict[str, float]) -> float:
        """Calculate overall weather impact score."""
        
        weights = {
            "temperature_impact": 0.3,
            "wind_impact": 0.3,
            "precipitation_impact": 0.3,
            "visibility_impact": 0.1
        }
        
        overall = sum(factors.get(factor, 0) * weight for factor, weight in weights.items())
        return min(overall, 1.0)  # Cap at 1.0
    
    def _get_impact_description(self, impact: float) -> str:
        """Get description of weather impact."""
        
        if impact < 0.2:
            return "Ideal playing conditions"
        elif impact < 0.4:
            return "Good playing conditions with minor factors"
        elif impact < 0.6:
            return "Challenging conditions that may affect play"
        else:
            return "Difficult conditions that will significantly impact the match"
    
    def _get_weather_recommendations(self, impact: Dict[str, Any]) -> List[str]:
        """Get weather-based recommendations."""
        
        recommendations = []
        
        if impact["overall_impact"] > 0.5:
            recommendations.append("Weather conditions may significantly affect the match")
        
        if impact["factors"]["wind_impact"] > 0.3:
            recommendations.append("Strong winds may affect passing and set pieces")
        
        if impact["factors"]["precipitation_impact"] > 0.3:
            recommendations.append("Wet conditions may make the pitch slippery")
        
        if impact["factors"]["temperature_impact"] > 0.3:
            recommendations.append("Extreme temperatures may affect player performance")
        
        if not recommendations:
            recommendations.append("Weather conditions are ideal for football")
        
        return recommendations

# Global weather provider instance
weather_provider = WeatherProvider()
