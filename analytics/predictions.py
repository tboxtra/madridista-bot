"""
AI-Powered Match Prediction Engine
Provides intelligent match outcome predictions with confidence scores.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class PredictionResult:
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    confidence: float
    key_factors: List[str]
    predicted_score: str
    reasoning: str

class MatchPredictionEngine:
    """AI-powered match prediction system."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.historical_data = {}
        self.prediction_history = {}
    
    def predict_match_outcome(self, home_team: str, away_team: str, 
                            context: Dict = None) -> PredictionResult:
        """Predict match outcome with confidence scores."""
        
        if not context:
            context = {}
        
        # Get team form data
        home_form = self._get_team_form(home_team, days=30)
        away_form = self._get_team_form(away_team, days=30)
        
        # Get head-to-head data
        h2h_data = self._get_h2h_data(home_team, away_team)
        
        # Get additional context
        weather_data = context.get("weather", {})
        injury_data = context.get("injuries", {})
        
        # Calculate prediction using AI
        prediction = self._calculate_ai_prediction(
            home_team, away_team, home_form, away_form, h2h_data, 
            weather_data, injury_data
        )
        
        return prediction
    
    def predict_league_winner(self, league: str, remaining_matches: int) -> Dict:
        """Predict league winner with remaining matches."""
        
        prediction_prompt = f"""
        Predict the winner of {league} with {remaining_matches} matches remaining.
        
        Consider:
        - Current league table
        - Remaining fixtures difficulty
        - Team form and momentum
        - Historical performance in similar situations
        
        Provide:
        1. Most likely winner
        2. Probability percentage
        3. Key factors
        4. Alternative scenarios
        
        Respond in JSON format.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prediction_prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "ok": True,
                "prediction": result,
                "__source": "AI League Prediction"
            }
            
        except Exception as e:
            return {
                "ok": False,
                "message": f"League prediction failed: {str(e)}",
                "__source": "AI League Prediction"
            }
    
    def predict_transfer_probability(self, player: str, target_team: str) -> Dict:
        """Predict transfer probability using AI analysis."""
        
        prediction_prompt = f"""
        Analyze the probability of {player} transferring to {target_team}.
        
        Consider:
        - Player's current contract situation
        - Team's transfer needs and budget
        - Player's preferences and history
        - Market conditions
        - Recent rumors and reports
        
        Provide:
        1. Transfer probability (0-100%)
        2. Key factors influencing the move
        3. Potential obstacles
        4. Timeline estimate
        
        Respond in JSON format.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prediction_prompt}],
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "ok": True,
                "prediction": result,
                "__source": "AI Transfer Prediction"
            }
            
        except Exception as e:
            return {
                "ok": False,
                "message": f"Transfer prediction failed: {str(e)}",
                "__source": "AI Transfer Prediction"
            }
    
    def _get_team_form(self, team: str, days: int) -> Dict:
        """Get team form over specified days."""
        # This would integrate with actual data sources
        # For now, return mock data structure
        return {
            "team": team,
            "period_days": days,
            "matches_played": 5,
            "wins": 3,
            "draws": 1,
            "losses": 1,
            "goals_for": 8,
            "goals_against": 4,
            "form_score": 0.7,  # 0-1 scale
            "recent_results": ["W", "W", "D", "L", "W"]
        }
    
    def _get_h2h_data(self, team_a: str, team_b: str) -> Dict:
        """Get head-to-head historical data."""
        # This would integrate with actual data sources
        return {
            "team_a": team_a,
            "team_b": team_b,
            "total_meetings": 10,
            "team_a_wins": 4,
            "team_b_wins": 3,
            "draws": 3,
            "last_meeting": "2023-10-15",
            "last_result": f"{team_a} 2-1 {team_b}",
            "h2h_advantage": team_a  # Which team has historical advantage
        }
    
    def _calculate_ai_prediction(self, home_team: str, away_team: str,
                               home_form: Dict, away_form: Dict, h2h_data: Dict,
                               weather_data: Dict, injury_data: Dict) -> PredictionResult:
        """Calculate match prediction using AI analysis."""
        
        prediction_prompt = f"""
        Analyze this football match and predict the outcome:
        
        Match: {home_team} vs {away_team}
        
        Home Team Form ({home_team}):
        - Recent results: {home_form.get('recent_results', [])}
        - Form score: {home_form.get('form_score', 0)}
        - Goals: {home_form.get('goals_for', 0)} for, {home_form.get('goals_against', 0)} against
        
        Away Team Form ({away_team}):
        - Recent results: {away_form.get('recent_results', [])}
        - Form score: {away_form.get('form_score', 0)}
        - Goals: {away_form.get('goals_for', 0)} for, {away_form.get('goals_against', 0)} against
        
        Head-to-Head:
        - Total meetings: {h2h_data.get('total_meetings', 0)}
        - {home_team} wins: {h2h_data.get('team_a_wins', 0)}
        - {away_team} wins: {h2h_data.get('team_b_wins', 0)}
        - Draws: {h2h_data.get('draws', 0)}
        - Last result: {h2h_data.get('last_result', 'N/A')}
        
        Additional Factors:
        - Weather: {weather_data}
        - Injuries: {injury_data}
        
        Provide a detailed prediction with:
        1. Home win probability (0-100%)
        2. Draw probability (0-100%)
        3. Away win probability (0-100%)
        4. Overall confidence level (0-100%)
        5. Key factors influencing the prediction
        6. Most likely scoreline
        7. Detailed reasoning
        
        Respond in JSON format with these exact keys:
        {{
            "home_win_probability": 0.0,
            "draw_probability": 0.0,
            "away_win_probability": 0.0,
            "confidence": 0.0,
            "key_factors": ["factor1", "factor2", "factor3"],
            "predicted_score": "2-1",
            "reasoning": "detailed explanation"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prediction_prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return PredictionResult(
                home_win_probability=result.get("home_win_probability", 0.33),
                draw_probability=result.get("draw_probability", 0.33),
                away_win_probability=result.get("away_win_probability", 0.34),
                confidence=result.get("confidence", 0.7),
                key_factors=result.get("key_factors", []),
                predicted_score=result.get("predicted_score", "1-1"),
                reasoning=result.get("reasoning", "AI analysis based on form and history")
            )
            
        except Exception as e:
            # Fallback prediction
            return PredictionResult(
                home_win_probability=0.4,
                draw_probability=0.3,
                away_win_probability=0.3,
                confidence=0.5,
                key_factors=["Limited data available"],
                predicted_score="1-1",
                reasoning=f"Fallback prediction due to analysis error: {str(e)}"
            )
    
    def track_prediction_accuracy(self, prediction_id: str, actual_result: str) -> Dict:
        """Track prediction accuracy for learning."""
        
        if prediction_id in self.prediction_history:
            prediction = self.prediction_history[prediction_id]
            
            # Calculate accuracy
            predicted_winner = self._determine_predicted_winner(prediction)
            actual_winner = self._determine_actual_winner(actual_result)
            
            is_correct = predicted_winner == actual_winner
            
            # Store result
            self.prediction_history[prediction_id]["actual_result"] = actual_result
            self.prediction_history[prediction_id]["is_correct"] = is_correct
            self.prediction_history[prediction_id]["accuracy_tracked"] = True
            
            return {
                "ok": True,
                "prediction_id": prediction_id,
                "predicted": predicted_winner,
                "actual": actual_winner,
                "correct": is_correct,
                "confidence": prediction.get("confidence", 0)
            }
        
        return {"ok": False, "message": "Prediction not found"}
    
    def _determine_predicted_winner(self, prediction: Dict) -> str:
        """Determine predicted winner from prediction data."""
        home_prob = prediction.get("home_win_probability", 0)
        draw_prob = prediction.get("draw_probability", 0)
        away_prob = prediction.get("away_win_probability", 0)
        
        if home_prob > draw_prob and home_prob > away_prob:
            return "home"
        elif away_prob > home_prob and away_prob > draw_prob:
            return "away"
        else:
            return "draw"
    
    def _determine_actual_winner(self, result: str) -> str:
        """Determine actual winner from match result."""
        # Parse result like "2-1" or "Real Madrid 2-1 Barcelona"
        if "-" in result:
            parts = result.split("-")
            if len(parts) >= 2:
                try:
                    home_score = int(parts[0].split()[-1])
                    away_score = int(parts[1].split()[0])
                    
                    if home_score > away_score:
                        return "home"
                    elif away_score > home_score:
                        return "away"
                    else:
                        return "draw"
                except ValueError:
                    pass
        
        return "unknown"
    
    def get_prediction_stats(self) -> Dict:
        """Get overall prediction statistics."""
        total_predictions = len(self.prediction_history)
        tracked_predictions = [p for p in self.prediction_history.values() 
                             if p.get("accuracy_tracked", False)]
        
        if not tracked_predictions:
            return {
                "total_predictions": total_predictions,
                "tracked_predictions": 0,
                "accuracy_rate": 0,
                "average_confidence": 0
            }
        
        correct_predictions = sum(1 for p in tracked_predictions if p.get("is_correct", False))
        accuracy_rate = correct_predictions / len(tracked_predictions)
        average_confidence = sum(p.get("confidence", 0) for p in tracked_predictions) / len(tracked_predictions)
        
        return {
            "total_predictions": total_predictions,
            "tracked_predictions": len(tracked_predictions),
            "correct_predictions": correct_predictions,
            "accuracy_rate": accuracy_rate,
            "average_confidence": average_confidence
        }
