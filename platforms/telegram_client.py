import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ai_engine.gpt_engine import generate_short_post

# Import our new football services
from services.football_api import FootballAPIService
from data.football_knowledge import (
    get_player_info, get_competition_info, get_recent_achievements,
    get_banter_responses, REAL_MADRID_FACTS, LA_LIGA_TEAMS_2024
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MadridistaTelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # Validate token format (Telegram bot tokens are typically 46+ characters and contain numbers and letters)
        if self.token == "your_bot_token_here" or len(self.token) < 40 or not any(c.isdigit() for c in self.token):
            raise ValueError("TELEGRAM_BOT_TOKEN appears to be a placeholder. Please set a real bot token from @BotFather")
        
        # Initialize football API service
        self.football_api = FootballAPIService()
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tweet", self.generate_tweet_command))
        self.application.add_handler(CommandHandler("madrid", self.madrid_command))
        self.application.add_handler(CommandHandler("squad", self.squad_command))
        self.application.add_handler(CommandHandler("matches", self.matches_command))
        self.application.add_handler(CommandHandler("standings", self.standings_command))
        self.application.add_handler(CommandHandler("achievements", self.achievements_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Message handler for general conversation
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "¡Hala Madrid! 🤍\n\n"
            "Welcome to MadridistaAI, your Real Madrid companion!\n\n"
            "Available commands:\n"
            "/tweet - Generate a Real Madrid tweet\n"
            "/madrid - Get Real Madrid info\n"
            "/squad - Current squad information\n"
            "/matches - Recent and upcoming matches\n"
            "/standings - La Liga standings\n"
            "/achievements - Recent achievements\n"
            "/status - Check data source status\n"
            "/help - Show this help message\n\n"
            "Just chat with me about Real Madrid! Ask me anything about the club, players, history, or current events."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤍 MadridistaAI Commands 🤍\n\n"
            "/start - Start the bot\n"
            "/tweet - Generate a Real Madrid tweet\n"
            "/madrid - Get Real Madrid info\n"
            "/squad - Current squad information\n"
            "/matches - Recent and upcoming matches\n"
            "/standings - La Liga standings\n"
            "/achievements - Recent achievements\n"
            "/status - Check data source status\n"
            "/help - Show this help message\n\n"
            "You can also just chat with me about Real Madrid!"
        )
        await update.message.reply_text(help_text)
    
    async def generate_tweet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tweet command - generate a Real Madrid tweet"""
        try:
            await update.message.reply_text("Generating your Real Madrid tweet... ⚽")
            
            # Generate tweet using existing AI engine
            prompt = "Generate an exciting Real Madrid tweet about the club's success, players, or upcoming matches"
            tweet_text = generate_short_post(prompt, max_chars=240)
            
            # Ensure it fits in a tweet
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            await update.message.reply_text(f"📱 Here's your tweet:\n\n{tweet_text}")
            
        except Exception as e:
            logger.error(f"Error generating tweet: {e}")
            await update.message.reply_text("Sorry, I couldn't generate a tweet right now. Try again later!")
    
    async def madrid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /madrid command - provide Real Madrid info"""
        try:
            # Try to get live data first
            club_info = await self.football_api.get_real_madrid_info()
            
            if club_info:
                source_indicator = "🟢 Live Data" if club_info.get('source') == 'Live API' else "🟡 Fallback Data"
                madrid_info = (
                    f"🏆 **{club_info.get('name', 'Real Madrid')}** {source_indicator} 🏆\n\n"
                    f"Founded: {club_info.get('founded', 1902)}\n"
                    f"Stadium: {club_info.get('venue', 'Santiago Bernabéu')}\n"
                    f"Colors: {club_info.get('colors', 'White and Gold')}\n"
                    f"League: La Liga\n"
                    f"European Cups: {REAL_MADRID_FACTS['achievements']['champions_league']} (record)\n\n"
                    f"¡Hala Madrid y nada más! 🤍"
                )
            else:
                # Fallback to static data
                madrid_info = (
                    "🏆 **Real Madrid Club de Fútbol** 🏆\n\n"
                    "Founded: 1902\n"
                    "Stadium: Santiago Bernabéu\n"
                    "League: La Liga\n"
                    "European Cups: 14 (record)\n\n"
                    "¡Hala Madrid y nada más! 🤍"
                )
            
            await update.message.reply_text(madrid_info)
            
        except Exception as e:
            logger.error(f"Error in madrid command: {e}")
            await update.message.reply_text("¡Hala Madrid! 🤍")
    
    async def squad_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /squad command - show current squad"""
        try:
            await update.message.reply_text("Fetching current Real Madrid squad... ⚽")
            
            # Try to get live squad data
            squad = await self.football_api.get_real_madrid_squad()
            
            if squad and len(squad) > 0:
                # Check if this is actually live data (not fallback)
                is_live_data = squad[0].get('source') == 'Live API'
                source_indicator = "🟢 Live Data" if is_live_data else "🟡 Fallback Data"
                
                squad_text = f"🤍 **Real Madrid Current Squad** {source_indicator} 🤍\n\n"
                
                # Group by position
                positions = {}
                for player in squad:
                    pos = player.get('position', 'Unknown')
                    if pos not in positions:
                        positions[pos] = []
                    positions[pos].append(player.get('name', 'Unknown'))
                
                for pos, players in positions.items():
                    squad_text += f"**{pos}:**\n"
                    for player in players:
                        squad_text += f"• {player}\n"
                    squad_text += "\n"
                
                # Add data freshness info
                if is_live_data:
                    squad_text += f"📅 **Data Source**: Live from Football-Data.org\n"
                    squad_text += f"🕐 **Last Updated**: {squad[0].get('last_updated', 'Recent')}\n"
                else:
                    squad_text += f"📅 **Data Source**: Fallback (2024 season)\n"
                
                await update.message.reply_text(squad_text)
            else:
                # Fallback to static data
                squad_text = "🤍 **Real Madrid Current Squad 2024** 🤍\n\n"
                for position, players in REAL_MADRID_FACTS["current_squad_2024"].items():
                    squad_text += f"**{position.title()}:**\n"
                    for player in players:
                        squad_text += f"• {player}\n"
                    squad_text += "\n"
                
                squad_text += f"📅 **Data Source**: Static fallback data\n"
                await update.message.reply_text(squad_text)
                
        except Exception as e:
            logger.error(f"Error in squad command: {e}")
            await update.message.reply_text("Sorry, couldn't fetch squad information right now!")
    
    async def matches_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /matches command - show recent and upcoming matches"""
        try:
            await update.message.reply_text("Fetching Real Madrid matches... ⚽")
            
            matches = await self.football_api.get_real_madrid_matches(limit=5)
            
            if matches and len(matches) > 0:
                # Check if this is actually live data
                is_live_data = matches[0].get('source') == 'Live API'
                source_indicator = "🟢 Live Data" if is_live_data else "🟡 Fallback Data"
                
                matches_text = f"⚽ **Real Madrid Recent & Upcoming Matches** {source_indicator} ⚽\n\n"
                for match in matches:
                    matches_text += self.football_api.format_match_result(match) + "\n\n"
                
                # Add data freshness info
                if is_live_data:
                    matches_text += f"📅 **Data Source**: Live from Football-Data.org\n"
                    matches_text += f"🕐 **Last Updated**: Recent\n"
                else:
                    matches_text += f"📅 **Data Source**: Fallback data\n"
                
                await update.message.reply_text(matches_text)
            else:
                await update.message.reply_text("No recent match data available. Check back later!")
                
        except Exception as e:
            logger.error(f"Error in matches command: {e}")
            await update.message.reply_text("Sorry, couldn't fetch match information right now!")
    
    async def standings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /standings command - show La Liga standings"""
        try:
            await update.message.reply_text("Fetching La Liga standings... 🏆")
            
            standings = await self.football_api.get_la_liga_standings()
            
            if standings and len(standings) > 0:
                # Check if this is actually live data
                is_live_data = standings[0].get('source') == 'Live API'
                source_indicator = "🟢 Live Data" if is_live_data else "🟡 Fallback Data"
                
                standings_text = self.football_api.format_standings(standings, limit=10)
                
                # Add data freshness info
                if is_live_data:
                    standings_text += f"\n📅 **Data Source**: Live from Football-Data.org\n"
                    standings_text += f"🕐 **Last Updated**: Recent\n"
                else:
                    standings_text += f"\n📅 **Data Source**: Fallback data\n"
                
                await update.message.reply_text(standings_text)
            else:
                await update.message.reply_text("No standings data available. Check back later!")
                
        except Exception as e:
            logger.error(f"Error in standings command: {e}")
            await update.message.reply_text("Sorry, couldn't fetch standings right now!")
    
    async def achievements_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /achievements command - show recent achievements"""
        try:
            achievements_text = get_recent_achievements()
            await update.message.reply_text(achievements_text)
        except Exception as e:
            logger.error(f"Error in achievements command: {e}")
            await update.message.reply_text("¡Hala Madrid! 🤍")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - show data source status"""
        try:
            # Check API key status
            football_data_key = os.getenv('FOOTBALL_DATA_API_KEY')
            api_football_key = os.getenv('API_FOOTBALL_KEY')
            
            status_text = "📊 **MadridistaAI Data Source Status** 📊\n\n"
            
            # Football-Data.org status
            if football_data_key:
                status_text += "🟢 **Football-Data.org API**: Configured\n"
                status_text += "   • Live squad data available\n"
                status_text += "   • Live match results available\n"
                status_text += "   • Live standings available\n\n"
            else:
                status_text += "🟡 **Football-Data.org API**: Not configured\n"
                status_text += "   • Using fallback data\n"
                status_text += "   • Get free API key at: football-data.org\n\n"
            
            # API-Football status
            if api_football_key:
                status_text += "🟢 **API-Football**: Configured\n"
                status_text += "   • Additional data available\n\n"
            else:
                status_text += "🟡 **API-Football**: Not configured\n"
                status_text += "   • Get free API key at: api-football.com\n\n"
            
            # OpenAI status
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                status_text += "🟢 **OpenAI API**: Configured\n"
                status_text += "   • AI-powered responses available\n\n"
            else:
                status_text += "🔴 **OpenAI API**: Not configured\n"
                status_text += "   • AI responses will not work\n\n"
            
            status_text += "💡 **To get live data, add API keys to Railway environment variables**"
            
            await update.message.reply_text(status_text)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("Error checking status!")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages about Real Madrid with intelligent responses"""
        user_message = update.message.text.lower()
        
        # Check if message is about Real Madrid
        madrid_keywords = ['madrid', 'real madrid', 'bernabeu', 'hala madrid', 'cr7', 'ronaldo', 'vinicius', 'vini', 'benzema', 'modric', 'kroos', 'carlo', 'ancelotti', 'champions', 'liga', 'barcelona', 'atletico', 'sevilla', 'valencia']
        
        if any(keyword in user_message for keyword in madrid_keywords):
            try:
                # Check for specific player queries
                if any(player in user_message for player in ['cr7', 'ronaldo', 'cristiano']):
                    player_info = get_player_info("cristiano ronaldo")
                    response = f"⚽ **{player_info['name']}** - {player_info['status']}\nYears at Madrid: {player_info['years']}\nAchievements: {player_info['achievements']}"
                    await update.message.reply_text(response)
                    return
                
                elif any(player in user_message for player in ['vinicius', 'vini', 'vinícius']):
                    player_info = get_player_info("vinicius junior")
                    response = f"⚽ **{player_info['name']}** - {player_info['status']}\nPosition: {player_info['position']}\nTeam: {player_info['team']}"
                    await update.message.reply_text(response)
                    return
                
                # Check for competition queries
                elif any(comp in user_message for comp in ['champions', 'ucl', 'europe']):
                    comp_info = get_competition_info("champions league")
                    response = f"🏆 **{comp_info['name']}**\nMadrid has won {comp_info['madrid_titles']} titles!\n{comp_info['history']['recent_performance']}"
                    await update.message.reply_text(response)
                    return
                
                elif any(comp in user_message for comp in ['liga', 'la liga', 'spanish league']):
                    comp_info = get_competition_info("la liga")
                    response = f"🏆 **{comp_info['name']}**\nMadrid has won {comp_info['madrid_titles']} titles!\n{comp_info['teams']} teams, {comp_info['matches']} matches per season"
                    await update.message.reply_text(response)
                    return
                
                # Check for banter opportunities
                elif any(rival in user_message for rival in ['barcelona', 'barca', 'barça']):
                    banter = get_banter_responses()["barcelona"]
                    response = random.choice(banter)
                    await update.message.reply_text(response)
                    return
                
                elif any(rival in user_message for rival in ['atletico', 'atleti', 'atlético']):
                    banter = get_banter_responses()["atletico"]
                    response = random.choice(banter)
                    await update.message.reply_text(response)
                    return
                
                # Generate a relevant response using AI
                context_prompt = f"User asked: {update.message.text}\n\nGenerate a helpful, informative response about Real Madrid that directly addresses what they're asking. Use accurate facts and be engaging."
                
                response = generate_short_post(context_prompt, max_chars=200)
                await update.message.reply_text(f"⚽ {response}")
                
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                # Fallback to banter
                banter = get_banter_responses()["general"]
                response = random.choice(banter)
                await update.message.reply_text(response)
        else:
            # For non-Madrid topics, guide them to Real Madrid conversation
            await update.message.reply_text("¡Hala Madrid! ⚽🤍 I'm your Real Madrid companion! Let's talk about the greatest club in the world. Ask me about players, history, matches, or anything Real Madrid related!")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting MadridistaAI Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def stop(self):
        """Stop the bot gracefully"""
        await self.application.stop()
        await self.application.shutdown()
