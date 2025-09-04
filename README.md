# MadridistaAI — Stage 1 (MVP)

## What it does
- Generates Real Madrid / CR7 / Vini content using OpenAI
- **Primary**: Works as a Telegram bot for interactive conversations
- **Secondary**: Can post to X/Twitter via API (optional)

## Quick Start - Telegram Bot 🚀

### 1. Setup Telegram Bot
1. Message `@BotFather` on Telegram
2. Send `/newbot` and follow instructions
3. Copy your bot token

### 2. Install & Configure
```bash
pip install -r requirements.txt
cp env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN and OPENAI_API_KEY
```

### 3. Run the Bot
```bash
python main_telegram.py
```

### 4. Chat with your bot!
- `/start` - Welcome message
- `/tweet` - Generate Real Madrid content
- `/madrid` - Get club info
- Just chat about Real Madrid!

## Twitter Integration (Optional)

If you want to also post to Twitter:
1. Get API key from [TwitterAPI.io](https://twitterapi.io/)
2. Add `TWITTERAPI_KEY` to your `.env`
3. Run `python main.py` for Twitter posting

## Required Environment Variables

**For Telegram Bot:**
- `TELEGRAM_BOT_TOKEN` (from @BotFather)
- `OPENAI_API_KEY` (from OpenAI)

**For Twitter (optional):**
- `TWITTERAPI_KEY` (from TwitterAPI.io)

## Features

- 🤖 **Interactive Telegram Bot** - Chat and get commands
- ⚽ **Real Madrid Focused** - Generates club-specific content
- 🧠 **AI-Powered** - Uses OpenAI for smart responses
- 📱 **Easy to Use** - Simple commands and natural conversation
- 🐦 **Twitter Ready** - Can also post to Twitter if configured

## Documentation

- [Telegram Setup Guide](TELEGRAM_SETUP.md) - Detailed Telegram bot setup
- [Twitter Setup Guide](TWITTERAPI_SETUP.md) - Twitter integration details

## Notes

- Uses [TwitterAPI.io](https://twitterapi.io/) - 100x cheaper than official Twitter API
- Content is trimmed to fit platform limits
- Bot responds in real-time to Telegram messages

¡Hala Madrid! 🤍⚽
