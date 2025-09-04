# MadridistaAI Telegram Bot Setup Guide

## Prerequisites
- Python 3.10+ installed
- A Telegram account
- OpenAI API key

## Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send** `/newbot` command
4. **Choose a name** for your bot (e.g., "MadridistaAI")
5. **Choose a username** (must end with 'bot', e.g., "madridista_ai_bot")
6. **Copy the bot token** that BotFather gives you

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

1. **Copy** `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. **Edit** `.env` file with your actual values:
   ```bash
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

## Step 4: Run the Bot

```bash
python main_telegram.py
```

## Step 5: Test Your Bot

1. **Search for your bot** in Telegram using the username you created
2. **Start a chat** with `/start`
3. **Try the commands**:
   - `/start` - Welcome message
   - `/help` - Show available commands
   - `/tweet` - Generate a Real Madrid tweet
   - `/madrid` - Get Real Madrid info

## Bot Features

- **Interactive Commands**: Responds to slash commands
- **Smart Chat**: Recognizes Real Madrid-related conversations
- **AI-Powered**: Generates content using OpenAI
- **Real-time**: Responds immediately to messages

## Troubleshooting

### Bot not responding?
- Check if the bot is running (`python main_telegram.py`)
- Verify your `TELEGRAM_BOT_TOKEN` is correct
- Make sure you've started a chat with `/start`

### OpenAI errors?
- Verify your `OPENAI_API_KEY` is valid
- Check your OpenAI account has credits
- Ensure the API key has proper permissions

### Import errors?
- Run `pip install -r requirements.txt` again
- Check Python version (3.10+ required)

## Security Notes

- **Never share** your bot token publicly
- **Keep your** `.env` file private
- **Don't commit** sensitive keys to version control

## Next Steps

Once your Telegram bot is working, you can:
- Customize the bot responses
- Add more commands
- Integrate with other platforms
- Deploy to a server for 24/7 operation

¡Hala Madrid! 🤍⚽
