"""
Interactive Features
Polls, quizzes, and gamified interactions for enhanced user engagement.
"""

import json
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

@dataclass
class PollData:
    poll_id: str
    question: str
    options: List[str]
    correct_answer: Optional[int]
    poll_type: str  # "prediction", "quiz", "comparison"
    created_at: datetime
    expires_at: datetime
    participants: Dict[str, str]  # user_id -> answer
    results: Dict[str, int]  # option -> count

@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    difficulty: str  # "easy", "medium", "hard"
    category: str  # "history", "stats", "players", "teams"

class InteractiveFeatures:
    """Interactive features for enhanced user engagement."""
    
    def __init__(self):
        self.active_polls = {}
        self.user_predictions = {}
        self.quiz_questions = self._initialize_quiz_questions()
        self.user_scores = {}  # user_id -> score
    
    def create_match_prediction_poll(self, match_data: Dict) -> InlineKeyboardMarkup:
        """Create interactive prediction poll for upcoming match."""
        
        home_team = match_data.get("home_team", "Home Team")
        away_team = match_data.get("away_team", "Away Team")
        match_time = match_data.get("match_time", "TBD")
        match_id = match_data.get("match_id", f"match_{datetime.now().timestamp()}")
        
        # Create poll data
        poll_id = f"prediction_{match_id}"
        poll_data = PollData(
            poll_id=poll_id,
            question=f"Who will win: {home_team} vs {away_team}?",
            options=[f"{home_team} Win", "Draw", f"{away_team} Win"],
            correct_answer=None,  # Will be set after match
            poll_type="prediction",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            participants={},
            results={f"{home_team} Win": 0, "Draw": 0, f"{away_team} Win": 0}
        )
        
        self.active_polls[poll_id] = poll_data
        
        keyboard = [
            [
                InlineKeyboardButton(f"🏠 {home_team}", callback_data=f"predict_home_{poll_id}"),
                InlineKeyboardButton("🤝 Draw", callback_data=f"predict_draw_{poll_id}"),
                InlineKeyboardButton(f"{away_team} 🏠", callback_data=f"predict_away_{poll_id}")
            ],
            [
                InlineKeyboardButton("📊 View Predictions", callback_data=f"view_predictions_{poll_id}"),
                InlineKeyboardButton("🎯 My Predictions", callback_data="my_predictions")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_quick_quiz(self, category: str = None, difficulty: str = None):
        """Create quick football trivia quiz."""
        
        # Filter questions by category and difficulty
        available_questions = self.quiz_questions
        if category:
            available_questions = [q for q in available_questions if q.category == category]
        if difficulty:
            available_questions = [q for q in available_questions if q.difficulty == difficulty]
        
        if not available_questions:
            available_questions = self.quiz_questions
        
        # Select random question
        question = random.choice(available_questions)
        
        keyboard = []
        for i, option in enumerate(question.options):
            keyboard.append([InlineKeyboardButton(
                f"{chr(65+i)}. {option}", 
                callback_data=f"quiz_answer_{i}_{question.correct_answer}"
            )])
        
        keyboard.append([InlineKeyboardButton("💡 Show Explanation", callback_data=f"quiz_explanation_{question.correct_answer}")])
        
        return InlineKeyboardMarkup(keyboard), question
    
    def create_team_comparison_poll(self, team_a: str, team_b: str) -> InlineKeyboardMarkup:
        """Create team comparison poll."""
        
        poll_id = f"comparison_{team_a}_{team_b}_{datetime.now().timestamp()}"
        
        poll_data = PollData(
            poll_id=poll_id,
            question=f"Which team is better: {team_a} or {team_b}?",
            options=[team_a, team_b, "Equal"],
            correct_answer=None,
            poll_type="comparison",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=12),
            participants={},
            results={team_a: 0, team_b: 0, "Equal": 0}
        )
        
        self.active_polls[poll_id] = poll_data
        
        keyboard = [
            [
                InlineKeyboardButton(f"🏆 {team_a}", callback_data=f"compare_{team_a}_{poll_id}"),
                InlineKeyboardButton(f"🏆 {team_b}", callback_data=f"compare_{team_b}_{poll_id}")
            ],
            [
                InlineKeyboardButton("⚖️ Equal", callback_data=f"compare_equal_{poll_id}"),
                InlineKeyboardButton("📊 Detailed Comparison", callback_data=f"detailed_compare_{team_a}_{team_b}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_player_comparison_poll(self, player_a: str, player_b: str) -> InlineKeyboardMarkup:
        """Create player comparison poll."""
        
        poll_id = f"player_comparison_{player_a}_{player_b}_{datetime.now().timestamp()}"
        
        poll_data = PollData(
            poll_id=poll_id,
            question=f"Who is the better player: {player_a} or {player_b}?",
            options=[player_a, player_b, "Equal"],
            correct_answer=None,
            poll_type="player_comparison",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=12),
            participants={},
            results={player_a: 0, player_b: 0, "Equal": 0}
        )
        
        self.active_polls[poll_id] = poll_data
        
        keyboard = [
            [
                InlineKeyboardButton(f"⭐ {player_a}", callback_data=f"player_compare_{player_a}_{poll_id}"),
                InlineKeyboardButton(f"⭐ {player_b}", callback_data=f"player_compare_{player_b}_{poll_id}")
            ],
            [
                InlineKeyboardButton("⚖️ Equal", callback_data=f"player_compare_equal_{poll_id}"),
                InlineKeyboardButton("📊 Player Stats", callback_data=f"player_stats_{player_a}_{player_b}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_league_winner_poll(self, league: str, teams: List[str]) -> InlineKeyboardMarkup:
        """Create league winner prediction poll."""
        
        poll_id = f"league_winner_{league}_{datetime.now().timestamp()}"
        
        # Limit to top 6 teams for poll
        top_teams = teams[:6]
        
        poll_data = PollData(
            poll_id=poll_id,
            question=f"Who will win {league} this season?",
            options=top_teams,
            correct_answer=None,
            poll_type="league_winner",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30),
            participants={},
            results={team: 0 for team in top_teams}
        )
        
        self.active_polls[poll_id] = poll_data
        
        keyboard = []
        for i, team in enumerate(top_teams):
            keyboard.append([InlineKeyboardButton(
                f"🏆 {team}", 
                callback_data=f"league_winner_{team}_{poll_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("📊 View Results", callback_data=f"view_league_results_{poll_id}")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def handle_poll_response(self, user_id: str, callback_data: str) -> Dict:
        """Handle user response to poll."""
        
        try:
            if callback_data.startswith("predict_"):
                return self._handle_prediction_response(user_id, callback_data)
            elif callback_data.startswith("quiz_answer_"):
                return self._handle_quiz_response(user_id, callback_data)
            elif callback_data.startswith("compare_"):
                return self._handle_comparison_response(user_id, callback_data)
            elif callback_data.startswith("league_winner_"):
                return self._handle_league_winner_response(user_id, callback_data)
            else:
                return {"ok": False, "message": "Unknown poll type"}
                
        except Exception as e:
            return {"ok": False, "message": f"Error handling poll response: {str(e)}"}
    
    def _handle_prediction_response(self, user_id: str, callback_data: str) -> Dict:
        """Handle match prediction response."""
        
        parts = callback_data.split("_")
        if len(parts) < 3:
            return {"ok": False, "message": "Invalid prediction data"}
        
        prediction_type = parts[1]  # home, draw, away
        poll_id = "_".join(parts[2:])
        
        if poll_id not in self.active_polls:
            return {"ok": False, "message": "Poll not found"}
        
        poll = self.active_polls[poll_id]
        
        # Update user's prediction
        poll.participants[user_id] = prediction_type
        
        # Update results
        if prediction_type == "home":
            poll.results[poll.options[0]] += 1
        elif prediction_type == "draw":
            poll.results[poll.options[1]] += 1
        elif prediction_type == "away":
            poll.results[poll.options[2]] += 1
        
        return {
            "ok": True,
            "message": f"Prediction recorded: {prediction_type}",
            "poll_id": poll_id,
            "user_prediction": prediction_type
        }
    
    def _handle_quiz_response(self, user_id: str, callback_data: str) -> Dict:
        """Handle quiz response."""
        
        parts = callback_data.split("_")
        if len(parts) < 4:
            return {"ok": False, "message": "Invalid quiz data"}
        
        user_answer = int(parts[2])
        correct_answer = int(parts[3])
        
        is_correct = user_answer == correct_answer
        
        # Update user score
        if user_id not in self.user_scores:
            self.user_scores[user_id] = {"correct": 0, "total": 0}
        
        self.user_scores[user_id]["total"] += 1
        if is_correct:
            self.user_scores[user_id]["correct"] += 1
        
        return {
            "ok": True,
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "score": self.user_scores[user_id]
        }
    
    def _handle_comparison_response(self, user_id: str, callback_data: str) -> Dict:
        """Handle comparison poll response."""
        
        parts = callback_data.split("_")
        if len(parts) < 3:
            return {"ok": False, "message": "Invalid comparison data"}
        
        choice = parts[1]
        poll_id = "_".join(parts[2:])
        
        if poll_id not in self.active_polls:
            return {"ok": False, "message": "Poll not found"}
        
        poll = self.active_polls[poll_id]
        poll.participants[user_id] = choice
        
        # Update results
        if choice in poll.results:
            poll.results[choice] += 1
        
        return {
            "ok": True,
            "message": f"Vote recorded: {choice}",
            "poll_id": poll_id,
            "user_choice": choice
        }
    
    def _handle_league_winner_response(self, user_id: str, callback_data: str) -> Dict:
        """Handle league winner prediction response."""
        
        parts = callback_data.split("_")
        if len(parts) < 4:
            return {"ok": False, "message": "Invalid league winner data"}
        
        team = parts[2]
        poll_id = "_".join(parts[3:])
        
        if poll_id not in self.active_polls:
            return {"ok": False, "message": "Poll not found"}
        
        poll = self.active_polls[poll_id]
        poll.participants[user_id] = team
        
        if team in poll.results:
            poll.results[team] += 1
        
        return {
            "ok": True,
            "message": f"League winner prediction recorded: {team}",
            "poll_id": poll_id,
            "user_prediction": team
        }
    
    def get_poll_results(self, poll_id: str) -> Dict:
        """Get results for a specific poll."""
        
        if poll_id not in self.active_polls:
            return {"ok": False, "message": "Poll not found"}
        
        poll = self.active_polls[poll_id]
        total_votes = sum(poll.results.values())
        
        if total_votes == 0:
            return {
                "ok": True,
                "poll_id": poll_id,
                "question": poll.question,
                "results": poll.results,
                "total_votes": 0,
                "percentages": {option: 0 for option in poll.results.keys()}
            }
        
        percentages = {
            option: (count / total_votes) * 100 
            for option, count in poll.results.items()
        }
        
        return {
            "ok": True,
            "poll_id": poll_id,
            "question": poll.question,
            "results": poll.results,
            "total_votes": total_votes,
            "percentages": percentages,
            "created_at": poll.created_at.isoformat(),
            "expires_at": poll.expires_at.isoformat()
        }
    
    def get_user_predictions(self, user_id: str) -> Dict:
        """Get user's prediction history."""
        
        user_predictions = []
        
        for poll_id, poll in self.active_polls.items():
            if user_id in poll.participants:
                user_predictions.append({
                    "poll_id": poll_id,
                    "question": poll.question,
                    "user_prediction": poll.participants[user_id],
                    "poll_type": poll.poll_type,
                    "created_at": poll.created_at.isoformat()
                })
        
        return {
            "ok": True,
            "user_id": user_id,
            "total_predictions": len(user_predictions),
            "predictions": user_predictions
        }
    
    def get_user_quiz_score(self, user_id: str) -> Dict:
        """Get user's quiz score."""
        
        if user_id not in self.user_scores:
            return {
                "ok": True,
                "user_id": user_id,
                "correct": 0,
                "total": 0,
                "accuracy": 0
            }
        
        score = self.user_scores[user_id]
        accuracy = (score["correct"] / score["total"]) * 100 if score["total"] > 0 else 0
        
        return {
            "ok": True,
            "user_id": user_id,
            "correct": score["correct"],
            "total": score["total"],
            "accuracy": accuracy
        }
    
    def _initialize_quiz_questions(self) -> List[QuizQuestion]:
        """Initialize quiz questions database."""
        
        return [
            QuizQuestion(
                question="Which team has won the most Champions League titles?",
                options=["Real Madrid", "Barcelona", "Bayern Munich", "AC Milan"],
                correct_answer=0,
                explanation="Real Madrid has won 14 Champions League titles, more than any other team.",
                difficulty="easy",
                category="history"
            ),
            QuizQuestion(
                question="Who is Real Madrid's all-time top scorer?",
                options=["Cristiano Ronaldo", "Raul", "Karim Benzema", "Alfredo Di Stefano"],
                correct_answer=0,
                explanation="Cristiano Ronaldo scored 450 goals for Real Madrid in 438 appearances.",
                difficulty="medium",
                category="players"
            ),
            QuizQuestion(
                question="In which year did Real Madrid win their first Champions League?",
                options=["1956", "1960", "1966", "1998"],
                correct_answer=0,
                explanation="Real Madrid won their first European Cup (now Champions League) in 1956.",
                difficulty="hard",
                category="history"
            ),
            QuizQuestion(
                question="Which player has the most assists in La Liga history?",
                options=["Lionel Messi", "Xavi", "Andres Iniesta", "Cristiano Ronaldo"],
                correct_answer=0,
                explanation="Lionel Messi has the most assists in La Liga history with over 200 assists.",
                difficulty="medium",
                category="stats"
            ),
            QuizQuestion(
                question="What is the capacity of Santiago Bernabeu?",
                options=["81,044", "75,000", "85,000", "90,000"],
                correct_answer=0,
                explanation="Santiago Bernabeu has a capacity of 81,044 spectators.",
                difficulty="hard",
                category="teams"
            ),
            QuizQuestion(
                question="Which Real Madrid player has won the most Ballon d'Or awards?",
                options=["Cristiano Ronaldo", "Alfredo Di Stefano", "Luka Modric", "Karim Benzema"],
                correct_answer=0,
                explanation="Cristiano Ronaldo won 4 Ballon d'Or awards while at Real Madrid.",
                difficulty="easy",
                category="players"
            )
        ]
    
    def get_random_quiz_question(self, category: str = None, difficulty: str = None) -> QuizQuestion:
        """Get a random quiz question."""
        
        available_questions = self.quiz_questions
        
        if category:
            available_questions = [q for q in available_questions if q.category == category]
        
        if difficulty:
            available_questions = [q for q in available_questions if q.difficulty == difficulty]
        
        if not available_questions:
            available_questions = self.quiz_questions
        
        return random.choice(available_questions)
    
    def cleanup_expired_polls(self):
        """Clean up expired polls."""
        
        current_time = datetime.now()
        expired_polls = []
        
        for poll_id, poll in self.active_polls.items():
            if current_time > poll.expires_at:
                expired_polls.append(poll_id)
        
        for poll_id in expired_polls:
            del self.active_polls[poll_id]
        
        return len(expired_polls)
