import os
import sys
from dotenv import load_dotenv

def main():
    """Main function to run the MadridistaAI Telegram Bot"""
    load_dotenv(override=False)
    
    # Check if required environment variables are set
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        return
    
    try:
        from platforms.telegram_client import MadridistaTelegramBot
        
        print("🤖 Starting MadridistaAI Telegram Bot...")
        print("📱 Bot will respond to messages and commands")
        print("🛑 Press Ctrl+C to stop the bot")
        print("-" * 50)
        
        # Create and run the bot
        bot = MadridistaTelegramBot()
        bot.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
