"""
Telegram Interactive Features Integration
Handles interactive polls, quizzes, and buttons in Telegram.
"""

import json
from typing import Dict, Any, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from features.interactive import InteractiveFeatures

class TelegramInteractiveHandler:
    """Handles interactive features in Telegram."""
    
    def __init__(self):
        self.interactive = InteractiveFeatures()
        self.active_polls = {}
        self.user_responses = {}
    
    async def create_match_prediction_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE, match_data: Dict):
        """Create and send a match prediction poll in Telegram."""
        
        try:
            # Create the poll
            keyboard = self.interactive.create_match_prediction_poll(match_data)
            
            # Create poll message
            poll_text = f"🔮 **Match Prediction Poll**\n\n"
            poll_text += f"**{match_data.get('home_team', 'Home Team')} vs {match_data.get('away_team', 'Away Team')}**\n"
            poll_text += f"📅 {match_data.get('match_time', 'TBD')}\n\n"
            poll_text += "Who do you think will win? Cast your vote below! ⚽"
            
            # Send the poll with inline keyboard
            await update.message.reply_text(
                poll_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {"ok": True, "message": "Poll created successfully"}
            
        except Exception as e:
            return {"ok": False, "message": f"Failed to create poll: {str(e)}"}
    
    async def create_quiz_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str = None, difficulty: str = None):
        """Create and send a quiz question in Telegram."""
        
        try:
            # Create the quiz
            keyboard, question = self.interactive.create_quick_quiz(category, difficulty)
            
            # Create quiz message
            quiz_text = f"🧠 **Football Quiz**\n\n"
            quiz_text += f"**{question.question}**\n\n"
            quiz_text += "Choose your answer below:"
            
            # Send the quiz with inline keyboard
            await update.message.reply_text(
                quiz_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # Store the correct answer for later verification
            self.active_polls[f"quiz_{update.message.message_id}"] = {
                "type": "quiz",
                "question": question,
                "correct_answer": question.correct_answer
            }
            
            return {"ok": True, "message": "Quiz created successfully"}
            
        except Exception as e:
            return {"ok": False, "message": f"Failed to create quiz: {str(e)}"}
    
    async def create_team_comparison_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE, team_a: str, team_b: str):
        """Create and send a team comparison poll in Telegram."""
        
        try:
            # Create the poll
            keyboard = self.interactive.create_team_comparison_poll(team_a, team_b)
            
            # Create poll message
            poll_text = f"⚖️ **Team Comparison Poll**\n\n"
            poll_text += f"**{team_a} vs {team_b}**\n\n"
            poll_text += "Which team do you think is better? Vote below! 🏆"
            
            # Send the poll with inline keyboard
            await update.message.reply_text(
                poll_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {"ok": True, "message": "Team comparison poll created successfully"}
            
        except Exception as e:
            return {"ok": False, "message": f"Failed to create team comparison poll: {str(e)}"}
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        callback_data = query.data
        
        try:
            # Handle different types of callbacks
            if callback_data.startswith("predict_"):
                result = await self._handle_prediction_callback(query, user_id, callback_data)
            elif callback_data.startswith("quiz_answer_"):
                result = await self._handle_quiz_callback(query, user_id, callback_data)
            elif callback_data.startswith("compare_"):
                result = await self._handle_comparison_callback(query, user_id, callback_data)
            else:
                result = {"ok": False, "message": "Unknown callback type"}
            
            # Send feedback to user
            if result.get("ok"):
                feedback = f"✅ {result.get('message', 'Vote recorded!')}"
            else:
                feedback = f"❌ {result.get('message', 'Something went wrong')}"
            
            await query.edit_message_text(
                query.message.text + f"\n\n{feedback}",
                reply_markup=query.message.reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await query.edit_message_text(
                query.message.text + f"\n\n❌ Error: {str(e)}",
                reply_markup=query.message.reply_markup,
                parse_mode='Markdown'
            )
    
    async def _handle_prediction_callback(self, query, user_id: str, callback_data: str):
        """Handle prediction poll callbacks."""
        
        parts = callback_data.split("_")
        if len(parts) < 3:
            return {"ok": False, "message": "Invalid prediction data"}
        
        prediction_type = parts[1]  # home, draw, away
        poll_id = "_".join(parts[2:])
        
        # Record the user's prediction
        if user_id not in self.user_responses:
            self.user_responses[user_id] = {}
        
        self.user_responses[user_id][poll_id] = prediction_type
        
        return {"ok": True, "message": f"Prediction recorded: {prediction_type}"}
    
    async def _handle_quiz_callback(self, query, user_id: str, callback_data: str):
        """Handle quiz callbacks."""
        
        parts = callback_data.split("_")
        if len(parts) < 4:
            return {"ok": False, "message": "Invalid quiz data"}
        
        user_answer = int(parts[2])
        correct_answer = int(parts[3])
        
        is_correct = user_answer == correct_answer
        
        # Get the question for explanation
        message_id = query.message.message_id
        quiz_key = f"quiz_{message_id}"
        
        if quiz_key in self.active_polls:
            question = self.active_polls[quiz_key]["question"]
            explanation = question.explanation
        else:
            explanation = "Good try!"
        
        if is_correct:
            message = f"🎉 Correct! {explanation}"
        else:
            message = f"❌ Incorrect. The correct answer was {chr(65 + correct_answer)}. {explanation}"
        
        return {"ok": True, "message": message}
    
    async def _handle_comparison_callback(self, query, user_id: str, callback_data: str):
        """Handle comparison poll callbacks."""
        
        parts = callback_data.split("_")
        if len(parts) < 3:
            return {"ok": False, "message": "Invalid comparison data"}
        
        choice = parts[1]
        poll_id = "_".join(parts[2:])
        
        # Record the user's choice
        if user_id not in self.user_responses:
            self.user_responses[user_id] = {}
        
        self.user_responses[user_id][poll_id] = choice
        
        return {"ok": True, "message": f"Vote recorded: {choice}"}
    
    def get_user_poll_history(self, user_id: str) -> Dict:
        """Get user's poll participation history."""
        
        user_history = self.user_responses.get(user_id, {})
        
        return {
            "user_id": user_id,
            "total_participations": len(user_history),
            "poll_history": user_history
        }
    
    def get_poll_results(self, poll_id: str) -> Dict:
        """Get results for a specific poll."""
        
        # Count votes for this poll
        poll_votes = {}
        total_votes = 0
        
        for user_id, user_polls in self.user_responses.items():
            if poll_id in user_polls:
                vote = user_polls[poll_id]
                poll_votes[vote] = poll_votes.get(vote, 0) + 1
                total_votes += 1
        
        # Calculate percentages
        percentages = {}
        for vote, count in poll_votes.items():
            percentages[vote] = (count / total_votes * 100) if total_votes > 0 else 0
        
        return {
            "poll_id": poll_id,
            "total_votes": total_votes,
            "results": poll_votes,
            "percentages": percentages
        }
