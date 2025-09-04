import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from features.matches import matches_handler
from features.live import live_handler
from live.monitor_providers import monitor_tick, POLL_SECONDS

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MadridistaBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # Validate token format
        if self.token == "your_bot_token_here" or len(self.token) < 40:
            raise ValueError("TELEGRAM_BOT_TOKEN appears to be a placeholder")
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        self.setup_live_monitoring()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("live", self.live_cmd))
        self.application.add_handler(CommandHandler("matches", self.matches_cmd))
        self.application.add_handler(CommandHandler("table", self.table_cmd))
        self.application.add_handler(CommandHandler("form", self.form_cmd))
        self.application.add_handler(CommandHandler("scorers", self.scorers_cmd))
        self.application.add_handler(CommandHandler("squad", self.squad_cmd))
        self.application.add_handler(CommandHandler("injuries", self.injuries_cmd))
        self.application.add_handler(CommandHandler("next", self.next_cmd))
        self.application.add_handler(CommandHandler("last", self.last_cmd))
        self.application.add_handler(CommandHandler("enablelive", self.enablelive_cmd))
        self.application.add_handler(CommandHandler("disablelive", self.disablelive_cmd))
        
        # Message handler for general conversation
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def setup_live_monitoring(self):
        """Setup live monitoring job queue"""
        try:
            # Initialize subscribers
            self.application.bot_data["subs"] = set()
            
            # Schedule the live monitor (every POLL_SECONDS) with error handling
            try:
                self.application.job_queue.run_repeating(monitor_tick, interval=POLL_SECONDS, first=5)
                logger.info(f"Live monitoring scheduled every {POLL_SECONDS} seconds")
            except Exception as e:
                logger.warning(f"Could not schedule live monitoring: {e}")
                logger.info("Bot will work without live monitoring")
        except Exception as e:
            logger.error(f"Error setting up live monitoring: {e}")
            logger.info("Bot will work without live monitoring")
    
    async def start_command(self, update, context):
        """Handle /start command"""
        welcome_text = (
            "¡Hala Madrid! ⚽🤍\n\n"
            "I'm your Real Madrid companion! Let's talk about the greatest club in the world.\n\n"
            "Commands:\n"
            "/matches - Show upcoming fixtures\n"
            "/live - Show live match status\n"
            "/enablelive - Subscribe to live updates\n"
            "/disablelive - Unsubscribe from live updates\n"
            "/help - Show this help message\n\n"
            "Just chat with me about Real Madrid!"
        )
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update, context):
        """Handle /help command"""
        help_text = (
            "🤖 **MadridistaAI Bot Commands** 🤖\n\n"
            "**Fixtures & Live:**\n"
            "/matches - Show upcoming fixtures (next 48h)\n"
            "/live - Show live match status\n"
            "/enablelive - Subscribe to live updates\n"
            "/disablelive - Unsubscribe from live updates\n\n"
            "**Data & Stats:**\n"
            "/table - Show LaLiga table (top 5)\n"
            "/form - Show recent form (last 5 matches)\n"
            "/scorers - Show top LaLiga scorers\n"
            "/squad - Show current squad\n"
            "/injuries - Show injuries/unavailable players\n"
            "/next [team] - Next fixture (default: Madrid)\n"
            "/last [team] - Last result (default: Madrid)\n\n"
            "**Natural Questions:**\n"
            "You can also ask naturally:\n"
            "• \"Where is Madrid on the table?\"\n"
            "• \"Madrid last 5 results?\"\n"
            "• \"Next game Barcelona?\"\n"
            "• \"Top scorers UCL\"\n"
            "• \"Premier League table\"\n"
            "• \"Who's injured?\"\n"
            "• \"Show defenders\"\n\n"
            "**Coverage:** Real Madrid + LaLiga priority, then all major leagues!"
        )
        await update.message.reply_text(help_text)
    
    async def live_cmd(self, update, context):
        """Handle /live command"""
        await update.message.reply_text(live_handler(), parse_mode="Markdown")
    
    async def matches_cmd(self, update, context):
        """Handle /matches command"""
        try:
            from data_pipeline.football_data import FootballData
            fd = FootballData()
            await update.message.reply_text(matches_handler(fd), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in matches command: {e}")
            await update.message.reply_text("Fixture data temporarily unavailable.")
    
    async def table_cmd(self, update, context):
        """Handle /table command"""
        try:
            from providers.fd_wrap import league_table
            from features.answers import fmt_table
            table_data = league_table("laliga")
            await update.message.reply_text(fmt_table(table_data), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in table command: {e}")
            await update.message.reply_text("Table data temporarily unavailable.")
    
    async def form_cmd(self, update, context):
        """Handle /form command"""
        try:
            from providers.fd_wrap import team_matches
            from features.answers import fmt_form
            matches = team_matches("Real Madrid", status="FINISHED", limit=10)
            await update.message.reply_text(fmt_form(matches, k=5), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in form command: {e}")
            await update.message.reply_text("Form data temporarily unavailable.")
    
    async def scorers_cmd(self, update, context):
        """Handle /scorers command"""
        try:
            from providers.fd_wrap import scorers
            from features.answers import fmt_scorers
            scorers_data = scorers("laliga", limit=10)
            await update.message.reply_text(fmt_scorers(scorers_data), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in scorers command: {e}")
            await update.message.reply_text("Scorers data temporarily unavailable.")
    
    async def squad_cmd(self, update, context):
        """Handle /squad command"""
        try:
            from providers.sofascore import SofaScoreProvider
            from features.answers import fmt_squad
            provider = SofaScoreProvider()
            squad_data = provider.team_squad()
            await update.message.reply_text(fmt_squad(squad_data), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in squad command: {e}")
            await update.message.reply_text("Squad data temporarily unavailable.")
    
    async def injuries_cmd(self, update, context):
        """Handle /injuries command"""
        try:
            from providers.sofascore import SofaScoreProvider
            from features.answers import fmt_injuries
            provider = SofaScoreProvider()
            injuries_data = provider.team_injuries()
            await update.message.reply_text(fmt_injuries(injuries_data), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in injuries command: {e}")
            await update.message.reply_text("Injury data temporarily unavailable.")
    
    async def next_cmd(self, update, context):
        """Handle /next command - can specify team or default to Madrid"""
        try:
            from nlp.resolve import resolve_team
            from providers.unified import fd_team_matches
            from features.answers import fmt_next_from_list
            
            # Get team from command arguments or default to Madrid
            args = context.args
            team_text = " ".join(args) if args else "madrid"
            team_id = resolve_team(team_text)
            
            if team_id:
                matches = fd_team_matches(team_id, status=None, limit=20)
                if matches:
                    await update.message.reply_text(fmt_next_from_list(matches), parse_mode="Markdown")
                else:
                    await update.message.reply_text("No upcoming fixtures found.")
            else:
                await update.message.reply_text("Please specify a valid team name.")
        except Exception as e:
            logger.error(f"Error in next command: {e}")
            await update.message.reply_text("Fixture data temporarily unavailable.")
    
    async def last_cmd(self, update, context):
        """Handle /last command - can specify team or default to Madrid"""
        try:
            from nlp.resolve import resolve_team
            from providers.unified import fd_team_matches
            from features.answers import fmt_last_result
            
            # Get team from command arguments or default to Madrid
            args = context.args
            team_text = " ".join(args) if args else "madrid"
            team_id = resolve_team(team_text)
            
            if team_id:
                matches = fd_team_matches(team_id, status="FINISHED", limit=1)
                if matches:
                    await update.message.reply_text(fmt_last_result(matches[0]), parse_mode="Markdown")
                else:
                    await update.message.reply_text("No recent match found.")
            else:
                await update.message.reply_text("Please specify a valid team name.")
        except Exception as e:
            logger.error(f"Error in last command: {e}")
            await update.message.reply_text("Match data temporarily unavailable.")
    
    async def enablelive_cmd(self, update, context):
        """Handle /enablelive command"""
        subs = context.application.bot_data.setdefault("subs", set())
        chat_id = update.effective_chat.id
        subs.add(chat_id)
        
        await update.message.reply_text(
            "✅ **Live updates enabled!**\n\n"
            "You'll now receive real-time updates when Real Madrid scores or when match status changes!\n\n"
            "Use `/disablelive` to unsubscribe."
        )
    
    async def disablelive_cmd(self, update, context):
        """Handle /disablelive command"""
        subs = context.application.bot_data.setdefault("subs", set())
        chat_id = update.effective_chat.id
        subs.discard(chat_id)
        
        await update.message.reply_text(
            "🛑 **Live updates disabled.**\n\n"
            "You won't receive live match updates anymore.\n\n"
            "Use `/enablelive` to subscribe again."
        )
    
    async def handle_message(self, update, context):
        """Handle general messages about Real Madrid"""
        user_message = update.message.text.lower()
        
        # Check if message is about Real Madrid
        madrid_keywords = ['madrid', 'real madrid', 'bernabeu', 'hala madrid', 'cr7', 'ronaldo', 
                          'vinicius', 'vini', 'benzema', 'modric', 'kroos', 'carlo', 'ancelotti', 
                          'champions', 'liga', 'barcelona', 'atletico', 'sevilla', 'valencia', 
                          'squad', 'team', 'players', 'matches', 'games', 'season', 'transfer', 'news']
        
        if any(keyword in user_message for keyword in madrid_keywords):
            # Check if this is a fixture/match question and redirect to real data
            if any(word in user_message for word in ['next', 'upcoming', 'when', 'fixture', 'match', 'game', 'schedule']):
                await self.matches_cmd(update, context)
                return
            
            # Try to route to football questions first (covers all football)
            try:
                from features.router_football import route_football
                football_answer = route_football(update.message.text)
                if football_answer:
                    await update.message.reply_text(football_answer, parse_mode="Markdown")
                    return
            except Exception as e:
                logger.warning(f"Football router error: {e}")
            
            # Then try Madrid-specific handlers (injuries, squad, etc.)
            try:
                from features.router_extra import route_related
                specific_answer = route_related(update.message.text)
                if specific_answer:
                    await update.message.reply_text(specific_answer, parse_mode="Markdown")
                    return
            except Exception as e:
                logger.warning(f"Madrid router error: {e}")
                # Continue to fallback response
            
            # Generate a relevant response
            response = "¡Hala Madrid! ⚽🤍 What would you like to know about Real Madrid? Use /matches for fixtures or /live for match status!"
            await update.message.reply_text(response)
        else:
            # For non-Madrid topics, guide them to Real Madrid conversation
            await update.message.reply_text(
                "¡Hala Madrid! ⚽🤍 I'm your Real Madrid companion! Let's talk about the greatest club in the world. "
                "Ask me about players, history, matches, or anything Real Madrid related!"
            )
    
    def run(self):
        """Run the bot"""
        logger.info("Starting MadridistaAI Bot...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = MadridistaBot()
    bot.run()
