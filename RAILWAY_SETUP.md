# Railway Deployment Setup Guide

## Required Environment Variables

Add these environment variables to your Railway project:

### Core API Keys (Required)
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Data Provider APIs (Required for full functionality)
```
API_FOOTBALL_KEY=your_api_football_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
ODDS_API_KEY=your_odds_api_key_here
```

### Optional APIs (for extended features)
```
SPORTMONKS_TOKEN=your_sportmonks_token_here
UPSTASH_REDIS_URL=your_redis_url_here
PERSPECTIVE_API_KEY=your_perspective_api_key_here
```

### Bot Behavior Settings
```
STRICT_FACTS=true
FAN_CREATIVE=true
FAN_SPICE=hot
HISTORY_ENABLE=true
USE_LOCAL_KB=false
CITATIONS=true
```

### Group Chat Behavior
```
AUTO_REPLY=true
AUTO_REPLY_PROB=0.45
REQUIRE_MENTION=false
BOT_NAME=madridista_bot
```

### System Settings
```
TZ=Africa/Lagos
SCOREBAT_API=https://www.scorebat.com/video-api/v3/
```

### Legacy Variables (if still using old providers)
```
FOOTBALL_DATA_API_KEY=your_football_data_api_key_here
SOFA_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) MadridistaBot/1.0
SOFA_TEAM_ID=2817
POLL_SECONDS=25
AI_FLAIR=false
```

## How to Add Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add each variable with its value
5. Click "Deploy" to restart with new variables

## Testing the Setup

After adding the variables, you can test with these queries:

### Wikipedia/History Queries
- "Who won the European Cup in 1960?"
- "Real Madrid Champions League history"
- "What happened in the 1960 final?"

### News Queries
- "Any Madrid news today?"
- "Latest football news"

### Highlights/Media
- "Show me Real Madrid highlights"
- "Latest Madrid videos"

### Predictions
- "Predict Real Madrid vs Barcelona"
- "Who will win the next Madrid match?"

## Troubleshooting

If Wikipedia queries aren't working:

1. **Check environment variables**: Make sure `OPENAI_API_KEY` is set
2. **Check logs**: Look for errors in Railway deployment logs
3. **Test locally**: Run `python3 diagnose_wikipedia.py` to verify setup
4. **Check API limits**: Ensure your OpenAI API key has sufficient credits

## Expected Behavior

With proper setup, the bot should:
- ✅ Answer historical questions using Wikipedia data
- ✅ Show source citations like "(Wikipedia)"
- ✅ Use creative AI responses with factual grounding
- ✅ Handle group chats intelligently
- ✅ Provide multi-signal predictions
- ✅ Show highlights and news when requested
