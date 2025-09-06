# Railway Deployment Guide

## 🚀 Quick Deploy Steps

### 1. Connect to Railway
- Go to [railway.app](https://railway.app)
- Connect your GitHub repository
- Select the `madridista-bot` repository

### 2. Set Environment Variables
In Railway Dashboard → Variables, set these **REQUIRED** variables:

```bash
# Core Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TZ=Africa/Lagos

# API Keys (REQUIRED)
FOOTBALL_DATA_API_KEY=your_football_data_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional APIs
RAPIDAPI_KEY=your_rapidapi_key  # For news features
SOFA_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) MadridistaBot/1.0
SOFA_TEAM_ID=2817  # Real Madrid team ID

# Feature Flags
CITATIONS=true
AI_FLAIR=false
POLL_SECONDS=25
```

### 3. Deploy
- Railway will auto-deploy from your latest commit
- Monitor the deployment logs for any errors
- The bot will start automatically

## 🔧 Troubleshooting Common Issues

### Issue 1: Environment Variables Missing
**Error**: `Missing env vars: TELEGRAM_BOT_TOKEN, FOOTBALL_DATA_API_KEY`
**Fix**: Set all required environment variables in Railway Dashboard

### Issue 2: Python Version Issues
**Error**: `Python version not supported`
**Fix**: Railway uses `runtime.txt` (already set to `python-3.8.2`)

### Issue 3: Import Errors
**Error**: `ModuleNotFoundError`
**Fix**: All dependencies are in `requirements.txt` - Railway will install them

### Issue 4: API Rate Limits
**Error**: `429 Too Many Requests`
**Fix**: The bot includes retry logic and rate limiting

### Issue 5: Memory Issues
**Error**: `Out of memory`
**Fix**: Railway provides 512MB by default - should be sufficient

## 📊 Monitoring

### Check Deployment Status
1. Go to Railway Dashboard
2. Click on your project
3. Check "Deployments" tab
4. View logs for any errors

### Health Check
The bot will log startup messages:
```
Environment validation passed
Starting MadridistaAI Bot...
```

### Test the Bot
Send these test messages to your Telegram bot:
- `/start` - Should respond with welcome message
- "next madrid fixture" - Should show upcoming match
- "compare madrid vs barcelona" - Should show recent form comparison

## 🚨 Emergency Fixes

### If Bot Crashes on Startup
1. Check Railway logs for specific error
2. Verify all environment variables are set
3. Check API key validity
4. Redeploy if needed

### If Bot Stops Responding
1. Check Railway logs for errors
2. Verify API quotas not exceeded
3. Restart the service in Railway Dashboard

### If Stale Data Appears
1. The latest fixes prevent this
2. If still happening, check API endpoints
3. Verify date windows are working

## ✅ Success Indicators

Your deployment is successful when:
- ✅ Railway shows "Deployed" status
- ✅ Bot responds to `/start` command
- ✅ Natural language queries work
- ✅ Citations appear in responses
- ✅ No stale data in responses

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test API keys independently
4. Check this troubleshooting guide

The bot is now production-ready with:
- ✅ Stale data prevention
- ✅ HTTP stability with retries
- ✅ Comprehensive error handling
- ✅ Environment validation
- ✅ Professional error messages
