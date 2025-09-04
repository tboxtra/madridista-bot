import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ai_engine.gpt_engine import generate_short_post
from prompts.fan_prompts import PROMPTS
import random

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
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tweet", self.generate_tweet_command))
        self.application.add_handler(CommandHandler("madrid", self.madrid_command))
        
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
            "/help - Show this help message\n\n"
            "You can also just chat with me about Real Madrid!"
        )
        await update.message.reply_text(help_text)
    
    async def generate_tweet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tweet command - generate a Real Madrid tweet"""
        try:
            await update.message.reply_text("Generating your Real Madrid tweet... ⚽")
            
            # Generate tweet using existing AI engine
            prompt = random.choice(PROMPTS)
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
        madrid_info = (
            "🏆 Real Madrid Club de Fútbol 🏆\n\n"
            "Founded: 1902\n"
            "Stadium: Santiago Bernabéu\n"
            "League: La Liga\n"
            "European Cups: 14 (record)\n\n"
            "¡Hala Madrid y nada más! 🤍"
        )
        await update.message.reply_text(madrid_info)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages about Real Madrid with intelligent responses"""
        user_message = update.message.text.lower()
        
        # Check if message is about Real Madrid
        madrid_keywords = ['madrid', 'real madrid', 'bernabeu', 'hala madrid', 'cr7', 'ronaldo', 'vinicius', 'vini', 'benzema', 'modric', 'kroos', 'carlo', 'ancelotti', 'champions', 'liga', 'barcelona', 'atletico', 'sevilla', 'valencia']
        
        if any(keyword in user_message for keyword in madrid_keywords):
            try:
                # Create a context-aware prompt based on user's message
                context_prompt = f"User asked: {update.message.text}\n\nGenerate a helpful, informative response about Real Madrid that directly addresses what they're asking. Keep it conversational and engaging."
                
                # Generate a relevant response using the user's actual question
                response = generate_short_post(context_prompt, max_chars=200)
                
                await update.message.reply_text(f"⚽ {response}")
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                # Fallback to a more specific response based on keywords
                if 'cr7' in user_message or 'ronaldo' in user_message:
                    await update.message.reply_text("⚽ Cristiano Ronaldo is a Real Madrid legend! He won 4 Champions League titles with us and scored 450+ goals. What would you like to know about CR7?")
                elif 'vinicius' in user_message or 'vini' in user_message:
                    await update.message.reply_text("⚽ Vinícius Jr. is our current superstar! He's been incredible this season with his pace and skill. What about Vini interests you?")
                elif 'champions' in user_message:
                    await update.message.reply_text("🏆 Real Madrid has won 14 Champions League titles - more than any other club! We're the kings of Europe! What would you like to know about our European success?")
                else:
                    await update.message.reply_text("¡Hala Madrid! 🤍 I'd love to help you with that Real Madrid question. Could you be more specific about what you'd like to know?")
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
