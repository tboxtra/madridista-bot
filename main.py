import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from features.matches import matches_handler
from features.matches_last import last_match_handler
from features.live import live_handler
from live.monitor_providers import monitor_tick, POLL_SECONDS
from settings import validate_env

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
        self.application.add_handler(CommandHandler("lastmatch", self.lastmatch_cmd))
        self.application.add_handler(CommandHandler("table", self.table_cmd))
        self.application.add_handler(CommandHandler("form", self.form_cmd))
        self.application.add_handler(CommandHandler("scorers", self.scorers_cmd))
        self.application.add_handler(CommandHandler("squad", self.squad_cmd))
        self.application.add_handler(CommandHandler("injuries", self.injuries_cmd))
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
            "/lastmatch - Show last match result\n"
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
            "/lastmatch - Show last match result\n"
            "/live - Show live match status\n"
            "/enablelive - Subscribe to live updates\n"
            "/disablelive - Unsubscribe from live updates\n\n"
            "**Data & Stats:**\n"
            "/table - Show LaLiga table (top 5)\n"
            "/form - Show recent form (last 5 matches)\n"
            "/scorers - Show top LaLiga scorers\n"
            "/squad - Show current squad\n"
            "/injuries - Show injuries/unavailable players\n\n"
            "**Natural Questions:**\n"
            "You can also ask naturally:\n"
            "• \"Where is Madrid on the table?\"\n"
            "• \"Madrid last 5 results?\"\n"
            "• \"Who's injured?\"\n"
            "• \"Show defenders\"\n"
            "• \"Top scorers\"\n\n"
            "Ask me about Real Madrid players, history, or current events!"
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
    
    async def lastmatch_cmd(self, update, context):
        """Handle /lastmatch command"""
        try:
            from data_pipeline.football_data import FootballData
            fd = FootballData()
            await update.message.reply_text(last_match_handler(fd), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error in lastmatch command: {e}")
            await update.message.reply_text("Last match data temporarily unavailable.")
    
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
        """Handle general messages with natural language processing"""
        msg = update.message
        if not msg or not msg.text or msg.from_user.is_bot:
            return
        text = msg.text.strip()

        # 1) Try the new LLM orchestrator for natural language
        try:
            from orchestrator.brain import answer_nl_question
            reply = answer_nl_question(text)
            return await msg.reply_text(reply, parse_mode="Markdown", disable_web_page_preview=False)
        except Exception as e:
            logger.warning(f"Orchestrator error: {e}")

        # 2) Fallback to existing football router
        try:
            from features.router_football import route_football
            ans = route_football(text)
            if ans:
                return await msg.reply_text(ans, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Football router error: {e}")

        # 3) Final fallback
        return await msg.reply_text("I had trouble understanding that. Try asking about fixtures, tables, form, or use commands like /matches, /table, /live.")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting MadridistaAI Bot...")
        self.application.run_polling()

if __name__ == "__main__":
    # Validate environment variables on startup
    validate_env()
    
    bot = MadridistaBot()
    bot.run()
